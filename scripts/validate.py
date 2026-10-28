from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,zipfile
root=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:
   assert attrs['id'] not in self.ids,('duplicate id',attrs['id'])
   self.ids.add(attrs['id'])
  for a in ('href','src'):
   if a in attrs:self.links.append(attrs[a])
for p in (root/'doc').rglob('*.html'):
 parser=Parser();parser.feed(p.read_text(encoding='utf-8'))
 for url in parser.links:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  if not target.exists():
   relative=target.relative_to(root/'doc');target=root/relative
  assert target.exists(),(p,url)
  if u.fragment and target.suffix=='.html':
   other=Parser();other.feed(target.read_text(encoding='utf-8'));assert u.fragment in other.ids,(p,url)
for manifest in (root/'SHA256SUMS.txt',*(root/'patches').glob('*/SHA256SUMS.txt')):
 for line in manifest.read_text(encoding='utf-8').splitlines():
  h,rel=line.split('  ',1);p=manifest.parent/rel
  assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(manifest,rel)
for p in (root/'patches').rglob('*.zip'):
 with zipfile.ZipFile(p) as z:assert z.testzip() is None,p
print('HTML links/fragments, archive CRC and SHA-256: OK')