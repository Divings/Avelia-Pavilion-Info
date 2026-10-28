from pathlib import Path
import html
import shutil
from release_catalog import collect

root = Path(__file__).resolve().parents[1]
site = root / '_site'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(root / 'doc', site)
shutil.copytree(root / 'patches', site / 'patches')
items = collect(root)
cards = []
for item in items:
    title = html.escape(item['title'])
    name = html.escape(item['path'].name)
    relative = item['path'].relative_to(root).as_posix()
    tag = item['tag']
    release = 'https://github.com/Divings/Avelia-Pavilion-Info/releases/tag/' + tag
    cards.append(f'''<article class="card" data-patch data-search="{title} {name} {item['slug']}"><span class="tag">{item['date']}</span><h2>{title}</h2><p><code>{name}</code> · {item['size'] / 1024:.1f} KB</p><p>識別子：<code>{tag}</code></p><code class="hash">{item['sha256']}</code><div class="buttons"><a class="button" href="{relative}" download>ZIPをダウンロード ↓</a><a class="button secondary" href="{release}">GitHub Release ↗</a></div></article>''')
p = site / 'releases.html'
s = p.read_text(encoding='utf-8').replace('<!-- RELEASE_CATALOG -->', '<div class="patch-grid">' + ''.join(cards) + '</div>').replace('<!-- RELEASE_COUNT -->', str(len(items)) + '件')
p.write_text(s, encoding='utf-8', newline='\n')
print('Built:', site)
