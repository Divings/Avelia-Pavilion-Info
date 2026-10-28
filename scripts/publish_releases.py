"""Publish one immutable-content release per patch ZIP hash using GitHub CLI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from release_catalog import collect


class GitHub:
    def __init__(self, repo):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            raise ValueError('Invalid repository')
        self.repo = repo

    def api(self, endpoint, payload=None, missing_ok=False):
        args = ['gh', 'api', f'repos/{self.repo}/{endpoint}']
        if payload is not None:
            args += ['--method', 'POST' if endpoint == 'releases' else 'PATCH', '--input', '-']
        result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                                text=True, capture_output=True)
        if result.returncode:
            if missing_ok and 'HTTP 404' in result.stderr:
                return None
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout)

    def upload(self, tag, paths):
        subprocess.run(['gh', 'release', 'upload', tag, *map(str, paths), '--repo', self.repo], check=True)


def verify_asset(asset, expected):
    digest = asset.get('digest')
    if digest != 'sha256:' + expected:
        raise RuntimeError(f'Asset digest missing or different: {asset["name"]}; refusing overwrite')


def publish_one(github, item, target):
    tag = item['tag']
    release = github.api(f'releases/tags/{tag}', missing_ok=True)
    if release and not release['draft']:
        asset = next((a for a in release['assets'] if a['name'] == item['path'].name), None)
        if asset is None:
            raise RuntimeError(f'Published release is missing ZIP: {tag}')
        verify_asset(asset, item['sha256'])
        print(f'Unchanged: {release["html_url"]}')
        return
    if release is None:
        body = (f"{item['title']}の配布ZIPです。\n\n"
                f"- ファイル: `{item['path'].name}`\n"
                f"- SHA-256: `{item['sha256']}`\n"
                f"- 配布ファイルの更新日: {item['date']}\n\n"
                "添付のREADMEと適用ガイドを確認してください。バージョン名はZIPのSHA-256から自動生成しています。"
                "同じZIPは重複発行せず、内容が変わると別リリースになります。\n\n"
                f"[適用ガイド](https://divings.github.io/{github.repo.split('/')[1]}/guide.html)\n\n"
                + item['readme'].read_text(encoding='utf-8'))
        release = github.api('releases', {'tag_name': tag, 'target_commitish': target,
                              'name': f"{item['title']} · {item['date']} · {item['sha256'][:8]}",
                              'body': body, 'draft': True, 'prerelease': False})
    with tempfile.TemporaryDirectory() as tmp:
        checksum = Path(tmp) / 'SHA256SUMS.txt'
        checksum.write_text(item['sha256'] + '  ' + item['path'].name + '\n', encoding='utf-8')
        assets = [item['path'], item['readme'], checksum]
        existing = {a['name']: a for a in release['assets']}
        missing = []
        for path in assets:
            if path.name in existing:
                verify_asset(existing[path.name], hashlib.sha256(path.read_bytes()).hexdigest())
            else:
                missing.append(path)
        if missing:
            github.upload(tag, missing)
        release = github.api(f'releases/{release["id"]}')
        uploaded = {a['name']: a for a in release['assets']}
        for path in assets:
            if path.name not in uploaded:
                raise RuntimeError(f'Upload incomplete: {path.name}')
            verify_asset(uploaded[path.name], hashlib.sha256(path.read_bytes()).hexdigest())
    published = github.api(f'releases/{release["id"]}', {'draft': False, 'make_latest': 'false'})
    print(f'Published: {published["html_url"]}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY', 'Divings/Avelia-Pavilion-Info'))
    parser.add_argument('--publish', action='store_true', help='Create/upload/publish on GitHub; omitted means read-only plan')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    items = collect(root)
    target = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if not args.publish:
        for item in items:
            print(json.dumps({k: str(item[k]) for k in ('title', 'path', 'sha256', 'tag', 'date')}, ensure_ascii=False))
        return
    github = GitHub(args.repo)
    for item in items:
        publish_one(github, item, target)


if __name__ == '__main__':
    main()
