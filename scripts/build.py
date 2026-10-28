from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
site=root/'_site'
if site.exists():shutil.rmtree(site)
shutil.copytree(root/'doc',site)
shutil.copytree(root/'patches',site/'patches')
print('Built:',site)
