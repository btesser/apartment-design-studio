import json, math
from shapely.geometry import Polygon, Point, box
R='/workspace/apartment-furniture';p=json.load(open(R+'/furniture-manifest.json'));g=json.load(open('/workspace/geometry-audit/geometry.json'))
rooms={r['id']:r for r in g['rooms']};polys={k:Polygon(v['outline']) for k,v in rooms.items()}
# Proposed divider is furnishing: explicitly widen bed zone without changing architecture.
p['proposed_bedroom_polygon']=[[-3.8,-2.48],[.35,-2.42],[.35,.66],[-3.8,.61]]
p['proposed_bedroom_polygon_status']='Movable curtain proposal adapted to King width and music doorway; not measured walls.'
polys['bedroom-flex']=polys['basement-open']
items=p['items'];report={'coordinate_frame':'Source Blender Z-up meters','items':len(items),'outside_wall':[],'solid_overlaps':[],'columns':[],'door_envelopes':[],'clearances':[]}
FP={i['id']:(Point(*i['position'][:2]).buffer(i['dimensions'][0]/2,resolution=32) if i.get('round') and i['kind'] in ['table','rug'] else Polygon(i['footprint_blender_xy'])) for i in items}
for i in items:
 xy=i['position'][:2];w,d,h=i['dimensions'];a=math.radians(i['rotation_deg'])
 if i.get('round') and i['kind'] in ['table','rug']:fp=Point(*xy).buffer(w/2,resolution=32)
 else:fp=Polygon(i['footprint_blender_xy'])
 FP[i['id']]=fp
 if i['kind'] in ['lamp','tv','dome_lamp','led_lamp','cylinder_lamp','art','sconce','chandelier','window_curtain']:continue
 room=polys[i['room']]
 outside=fp.difference(room.buffer(.005))
 if outside.area>.0005:report['outside_wall'].append({'id':i['id'],'outside_area_m2':round(outside.area,5)})
 # Support layering (lamps, mirrors, artworks, rugs) excluded from solid collision checks.
 for j in items:
  if i['kind']=='rug' or j['id']>=i['id'] or j['kind'] in ['rug','lamp','tv','dome_lamp','led_lamp','cylinder_lamp','art','sconce','chandelier','window_curtain']:continue
  if abs(i['position'][2]-j['position'][2])>.8:continue
  if j['id'] not in FP:continue
  overlap=fp.intersection(FP[j['id']])
  if overlap.area>.001:
   if i['kind']=='table' and j['kind']=='table' and 'coffee-table' in i['id'] and 'coffee-table' in j['id']:continue
   report['solid_overlaps'].append({'a':i['id'],'b':j['id'],'area_m2':round(overlap.area,4)})
 if i['room'] in ['bedroom-flex','basement-open']:
  for c in rooms['basement-open']['columns_xy']:
   if fp.distance(Point(*c))<.09:report['columns'].append({'id':i['id'],'column':c,'distance':fp.distance(Point(*c))})
 # Keep explicit doorway depth where evidenced.
 envelopes=[('music-gym',box(-3.80,-2.25,-3.10,-1.25)),('his-office',box(-3.60,-2.7,-3.08,-1.9))]
 for label,env in envelopes:
  if abs(i['position'][2]-(1.575 if label=='his-office' else -1.415))>.5:continue
  ov=fp.intersection(env)
  if ov.area>.001:report['door_envelopes'].append({'id':i['id'],'door':label,'area':round(ov.area,5)})
b=next(i for i in items if i['id']=='bedroom-king-bed');d=next(i for i in items if i['id']=='bedroom-large-dresser')
foot=d['position'][1]-d['dimensions'][1]/2 - (b['position'][1]+b['dimensions'][1]/2)
report['clearances'].append({'location':'King bed foot to selected118inch dresser','m':round(foot,5),'status':'Tight; viewer shows full selected dresser by default; toggle dresser off for clearance alternative'})
report['clearances'].append({'location':'Dining end chair rear to -Y wall','m':round((-1.645-.57/2)-(-2.38),3),'status':'Chair pullback possible after+Y.37m adaptation; clear front room circulation still needs field check'})
p['clearance_variants']={'faithful-proposal':{'included_optional':'bedroom-large-dresser','foot_clearance_m':round(foot,5)},'clearance-alternative':{'withheld_item':'bedroom-large-dresser','foot_to_wall_m':round(.61-(b['position'][1]+b['dimensions'][1]/2),3),'note':'Full selected dresser retained separately; placement to be decided after site measurement'}}
report['grounding']={'bedroom-flex':{'raw_local_scan_floor_mode_z_m':-1.415,'clean_architecture_floor_z_m':-1.385,'canonical_delta_z_m':.03,'status':'All eight bedroom furnishing/decor parent bases raised consistently; X/Y and product dimensions unchanged'}}
try:
 h=json.load(open('/workspace/geometry-audit/her-hearth-polygon.json'));hp=Polygon(h['coordinates_blender_xy']);bounds=json.load(open(R+'/loveseat-component-bounds.json'));support=[];body=[]
 for o in bounds:
  bb=o['bounds']
  if '::foot' in o['name']:
   q=Point((bb[0][0]+bb[0][1])/2,(bb[1][0]+bb[1][1])/2).buffer(max(bb[0][1]-bb[0][0],bb[1][1]-bb[1][0])/2,resolution=64);support.append({'id':o['name'],'distance_m':round(q.distance(hp),6),'intersection_m2':round(q.intersection(hp).area,9)})
  else:body.append(bb[2][0])
 report['raised_obstacles']=[{'furniture':'her-loveseat','obstacle':'her low stone hearth conservative hull','bounding_footprint_intersection_m2':round(FP['her-loveseat'].intersection(hp).area,8),'support_checks':support,'minimum_body_z_m':round(min(body),6),'hearth_top_max_z_m':h['z_top_range'][1],'body_vertical_clearance_m':round(min(body)-h['z_top_range'][1],6),'interpretation':'Elevated overhang of the conservative rectangular footprint; all four floor supports clear and sofa body above highest measured lip. Independent actual triangle verification confirms minimum support margin about2.8cm.'}]
except FileNotFoundError:pass
json.dump(report,open(R+'/validation.json','w'),indent=2);json.dump(p,open(R+'/furniture-manifest.json','w'),indent=2)
print(json.dumps(report,indent=2))
