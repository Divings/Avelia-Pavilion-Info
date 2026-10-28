"""Regenerate ZIP manifests after adding or updating a patch; never edits ZIPs."""
from pathlib import Path
import hashlib
from release_catalog import collect

root = Path(__file__).resolve().parents[1]
items = collect(root)
for folder in [root, *(root / 'patches').iterdir()]:
    if not folder.is_dir():
        continue
    archives = [item['path'] for item in items if folder == root or item['path'].parent == folder]
    if archives:
        lines = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(folder).as_posix() + '\n' for p in archives)
        (folder / 'SHA256SUMS.txt').write_text(lines, encoding='utf-8', newline='\n')
print('Updated manifests for', len(items), 'ZIPs')
