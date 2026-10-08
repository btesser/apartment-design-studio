"""Validate and summarize the current canonical geometry; do not regenerate seed estimates."""
import json
from pathlib import Path
p=Path(__file__).parent
g=json.loads((p/'geometry.json').read_text())
assert g['coordinate_system']['up_axis']=='Z'
assert len(g['rooms'])==8
for room in g['rooms']:
 assert len(room['outline'])>=4
 assert room['ceiling_z_m']>room['floor_z_m']
print('Canonical geometry valid:',len(g['rooms']),'room/zone records, original metric coordinates retained.')
