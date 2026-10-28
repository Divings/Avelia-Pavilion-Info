import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from publish_releases import publish_one, verify_asset


class FakeGitHub:
    repo = 'owner/repo'
    def __init__(self, release=None, fail_upload=False):
        self.release = release
        self.calls = []
        self.fail_upload = fail_upload

    def api(self, endpoint, payload=None, missing_ok=False):
        self.calls.append((endpoint, payload))
        if endpoint.startswith('releases/tags/'):
            return self.release
        if endpoint == 'releases':
            self.release = {'id': 1, 'draft': True, 'assets': [], 'html_url': 'https://github.com/owner/repo/releases/tag/test'}
        elif payload is not None:
            self.release.update(payload)
        return self.release

    def upload(self, tag, paths):
        if self.fail_upload:
            raise RuntimeError('upload interrupted')
        self.release['assets'].extend({'name': p.name, 'digest': 'sha256:' + hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths)


class ReleasesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        folder = Path(self.tmp.name)
        archive = folder / 'patch.zip'
        archive.write_bytes(b'checked archive bytes')
        readme = folder / 'README.md'
        readme.write_text('# Test patch', encoding='utf-8')
        self.item = {'tag': 'patch-test-abc', 'title': 'Test', 'path': archive, 'readme': readme,
                     'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'date': '2026-10-28'}

    def test_new_release_is_draft_until_all_assets_verified(self):
        api = FakeGitHub()
        publish_one(api, self.item, 'commit')
        self.assertTrue(api.calls[1][1]['draft'])
        self.assertFalse(api.release['draft'])
        self.assertEqual(len(api.release['assets']), 3)

    def test_published_same_archive_is_not_republished(self):
        api = FakeGitHub()
        publish_one(api, self.item, 'commit')
        api.calls.clear()
        publish_one(api, self.item, 'new-commit')
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(len(api.release['assets']), 3)

    def test_interrupted_upload_stays_draft_and_resumes(self):
        api = FakeGitHub(fail_upload=True)
        with self.assertRaises(RuntimeError):
            publish_one(api, self.item, 'commit')
        self.assertTrue(api.release['draft'])
        api.fail_upload = False
        publish_one(api, self.item, 'commit')
        self.assertFalse(api.release['draft'])
        self.assertEqual(len(api.release['assets']), 3)

    def test_completed_draft_assets_are_not_uploaded_twice(self):
        api = FakeGitHub()
        publish_one(api, self.item, 'commit')
        api.release['draft'] = True
        api.upload = Mock(side_effect=AssertionError('unexpected reupload'))
        publish_one(api, self.item, 'commit')
        self.assertFalse(api.release['draft'])
        api.upload.assert_not_called()

    def test_existing_different_digest_is_never_overwritten(self):
        api = FakeGitHub({'id': 1, 'draft': False, 'assets': [{'name': 'patch.zip', 'digest': 'sha256:wrong'}]})
        with self.assertRaises(RuntimeError):
            publish_one(api, self.item, 'commit')
        self.assertEqual(len(api.calls), 1)

    def test_missing_asset_digest_is_rejected(self):
        with self.assertRaises(RuntimeError):
            verify_asset({'name': 'patch.zip'}, self.item['sha256'])


if __name__ == '__main__':
    unittest.main()
