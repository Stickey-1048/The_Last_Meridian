"""Keep only numerical/model provenance for the eight selected owned assets."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
plan=json.loads((H/'stations.json').read_text());wanted={int(p['donorId'],16)for p in plan['props']}|{0x118f79}
sources=[R.parents[1]/'work/reviews/mercy-working-yard-001/mesh-metadata.json',R.parents[1]/'work/reviews/weathered-yard-fence-001/mesh-metadata.json',R/'tools/OpeningProductionFinish/models.json']
assets={}
for path in sources:
 for name,value in json.loads(path.read_text())['assets'].items():
  try:ident=int(value['id'],16)
  except (KeyError,ValueError):continue
  if ident in wanted:assets[name]=value
assert {int(a['id'],16)for a in assets.values()}==wanted,'Selected model metadata is incomplete'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
result={'scope':'Selected owned numeric metadata only; no mesh/material/texture payload','sources':{str(p.relative_to(R.parents[1])).replace('\\','/'):sha(p)for p in sources},'assets':assets}
(H/'models.json').write_text(json.dumps(result,indent=2)+'\n')
print('Prepared selected owned-asset metadata:',len(assets))
