import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));from scene_tools import *
read_source()
a={}
for id in ['secondary-workspace','visitor-chair','rug','blue-bold-art','branch-primary']:
 r=resolve_root(id);a[id]=[{'name':o.name,'type':o.type,'local':list(o.location),'dims':list(o.dimensions),'roles':{k:list(v) if hasattr(v,'to_list') else v for k,v in o.items()},'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'uv':[list(l.uv) for l in o.data.uv_layers.active.data] if o.type=='MESH' and o.data.uv_layers.active else None} for o in descendants(r)]
write_json('changed-components-source.json',a)
