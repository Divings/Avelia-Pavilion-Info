"""Discover patch ZIPs; no network or publication side effects."""
from pathlib import Path
import hashlib
import re
import subprocess
import zipfile


def collect(root):
    root = Path(root).resolve()
    patches = []
    for folder in sorted((root / 'patches').iterdir()):
        if not folder.is_dir():
            continue
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', folder.name):
            raise ValueError(f'Invalid patch directory: {folder.name}')
        archives = sorted(folder.glob('*.zip'))
        if not archives:
            continue
        readme = folder / 'README.md'
        text = readme.read_text(encoding='utf-8')
        title = next((line.lstrip('#').strip() for line in text.splitlines() if line.startswith('# ')), folder.name)
        for archive in archives:
            if archive.is_symlink() or len(archive.name) > 50:
                raise ValueError(f'Archive must be a regular file with a name <=50 characters: {archive.name}')
            with zipfile.ZipFile(archive) as z:
                bad = z.testzip()
                if bad:
                    raise ValueError(f'Corrupt ZIP: {archive.name}: {bad}')
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            result = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', archive.relative_to(root).as_posix()], cwd=root, capture_output=True, text=True, check=True)
            date = result.stdout.strip() or '未コミット'
            patches.append({'slug': folder.name, 'title': title, 'path': archive, 'readme': readme,
                            'sha256': digest, 'size': archive.stat().st_size, 'date': date,
                            'tag': f'patch-{folder.name}-{digest[:12]}'})
    return patches
