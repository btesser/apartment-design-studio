from pathlib import Path
import json,hashlib,math
import numpy as np
from shapely.geometry import Polygon,Point,box,LineString
from shapely.ops import unary_union
from shapely import affinity
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP,Circle
# Reuse independently established geometry/path algorithm, not old proof results.
code=Path('/workspace/his-office-pinterest/layout/geometry-fit-preflight/check_owned_chair_and_plant.py').read_text().split("result={'route_endpoints'")[0]
# .1mm conservative polygon-buffer guard; actual native tail is included below.
code=code.replace("def free_shape(obs,diam):return ROOM.buffer(-diam/2,quad_segs=96).difference(unary_union([sh.buffer(diam/2,quad_segs=96)for _,sh in obs]))", "def free_shape(obs,diam):return ROOM.buffer(-diam/2-.0001,quad_segs=192).difference(unary_union([sh.buffer(diam/2+.0001,quad_segs=192)for _,sh in obs]))")
code=code.replace('def witness(free,obs,diam):','def witness(free,obs,diam,inset=.002,gridstep=.005):')
code=code.replace('safe=free.buffer(-.002);step=.005;xs=', "safe=free.buffer(-inset)\n if not connected(safe)[0]:return {'witness_found':False,'reason':'extra grid inset disconnects thin nominal route'}\n step=gridstep;xs=")
code=code.replace("'extra_grid_inset_m':.002", "'extra_grid_inset_m':inset,'grid_spacing_m':gridstep")
exec(code)
OUT=Path('/workspace/his-office-pinterest/layout/final-variants');EXPECTED={'b-charcoal-slat':'baa403be9d085f76109c42c9f962506ee2841f15421f43d374a90ce8a33aced9','c-ink-studio':'0540a3f7eb1bccfda5192df900b538009f0d334e7a35a0355fd6664b14a9bd54'}

def final_obstacles(layout,native_bounds,wh,pull=0,drawer_open=False):
 obs=features();ci=next(i for i in layout['items']if i['kind']=='task_chair');x,y,z=ci['position_blender_m'];lo,hi=native_bounds;native=box(lo[0],lo[1]-pull,hi[0],hi[1]-pull);published=rect((x,y-pull),wh);chair=unary_union([native,published])
 for it in layout['items']:
  x,y,z=it['position_blender_m'];kind=it['kind']
  if kind in ['rug','art','closet_shoe_rack']:continue
  if kind=='task_chair':shape=chair
  elif kind=='kept_lamp':shape=unary_union([rect((x+dx,y+dy),(w,d))for dx,dy,w,d in[(0,-.196,.247,.07),(-.084,.018,.079,.438),(.084,.018,.079,.438)]])
  else:
   w,d=dims(it);shape=rect((x,y),(w,d))
   if kind=='clothes_dresser' and drawer_open:shape=box(x-w/2,y-d/2,x+w/2,y+d/2+it['drawer_pullout_m'])
  # Tabletop/ledge/mat projections are conservatively included. Their existing desk/dresser footprints already dominate the usable-floor exclusions.
  obs.append((it['id'],shape))
 finish=layout['workwall_finish']
 if finish.get('panel_count'):
  bw=finish['bay_W_H_m'][0];cx=finish['bay_center_X_m'];th=finish['panel_W_D_H_m'][1];obs.append(('final-B-five-panel-bay',box(cx-bw/2,.26-th,cx+bw/2,.31)))
 return obs,chair

def path_proof(free,obs,diam):
 for inset,step in[(.002,.005),(.0001,.005),(0,.005),(0,.0025)]:
  w=witness(free,obs,diam,inset,step)
  if w.get('witness_found')and w['exact_free_space_covers_witness']:
   assert w['minimum_centerline_distance_to_obstacle_m']>=diam/2-1e-8
   assert w['minimum_centerline_distance_to_room_boundary_m']>=diam/2-1e-8
   return w
 return {'witness_found':False,'reason':'continuous component exists but no discrete validated centerline found at attempted grids'}

result={'status':'Authoritative final frozen-layout nominal routing refresh; source-guided displayed chair native bbox unioned with published normal/max-arm envelopes.','method':'Continuous metric polygon configuration space. Each chair profile is the union of actual final native evaluated XY bbox and published normal or expanded-arm reference rectangle. Obstacles expand by a hypothetical person-circle radius plus.1mm numerical guard. A validated centerline witness is supplied for every passing60/61/62cm route.','coordinate_system':'Original BlenderZ-up metres; +X front/living,-X rear,+Y whitewall,-Y brick; glTF[X,Z,-Y].','endpoints':{'entry_xy_m':ENTRY,'actual_rear_door_approach_xy_m':REAR,'note':'The rear target is within the actual exterior-door approach; it does not use the former rear-room point inside a pulled chair/person exclusion zone.'},'source_geometry':[info(p)for p in[ROOMP,FEATP,ACCESSP,OWNEDP]],'limits':['Nominal room/fixed-fixture outlines have5–12cm field uncertainty; these results are not surveyed passage widths or accessibility/ergonomic guarantees.','Actual owned Aeron vintage, arm/cylinder/caster options and settings remain unconfirmed; native dimensions describe the displayed source-guided proxy only.','Door leaves presumed open for circulation; exact swings are inferred.','Cat upper branches and lamp upper-head geometry require the separate final native3Dproof; lamp floor U-base is an approximate source-guided shape.','Closet interior is unrecorded;3shoe racks are conditional and excluded from usable-room routing.','Fullheight projections of ledges/tabletopdecor/mat are conservatively included; final nativeheight/stroke/mesh checks remain separate.'],'variants':[]}
for variant,sha in EXPECTED.items():
 lp=ROOT/'variants'/variant/'model/layout.json';data=lp.read_bytes();assert hashlib.sha256(data).hexdigest()==sha;layout=json.loads(data);assert len(layout['items'])==17;chair=next(i for i in layout['items']if i['kind']=='task_chair');assert chair['product_id']=='aeron-size-c-mineral';assert sum(i['kind']=='task_chair'for i in layout['items'])==1
 motionp=ROOT/'qa/final-variants'/variant/'owned-chair-motion.json';motion=json.loads(motionp.read_text());assert motion['canonical_layout_sha256']==sha;native=motion['actual_proxy_world_bounds_blender_m'];normal_wh=chair['external_dimensions_m'][:2];max_wh=chair['collision_footprint_m'];vd={'variant':variant,'layout':info(lp),'layout_version':layout['layout_version'],'item_count':17,'chair_native_proof':info(motionp),'chair_native_source_blend_sha256':motion['source_sha256'],'chair_canonical':chair,'actual_native_bounds_blender_m':native,'actual_native_dimensions_m':[native[1][k]-native[0][k]for k in range(3)],'profiles':[]}
 for name,wh in [('normal_published_plus_actual_native',normal_wh),('max_arm_published_plus_actual_native',max_wh)]:
  pr={'profile':name,'published_width_depth_m':wh,'cases':[]}
  for state,pull in [('working',0),('45cmrearward',.45)]:
   obs,shape=final_obstacles(layout,native,wh,pull);checks=[]
   for dia in[.60,.61,.62]:
    free=free_shape(obs,dia);ok,a,b=connected(free);w=path_proof(free,obs,dia)if ok else None
    assert not ok or w['witness_found'],(variant,name,state,dia)
    checks.append({'person_circle_diameter_m':dia,'route_pass':ok,'entry_component':a,'rear_component':b,'path_witness':w})
   pr['cases'].append({'chair_state':state,'rearward_translation_m':pull,'chair_union_xy_bounds_m':list(shape.bounds),'routing_checks':checks})
  dresser=next(i for i in layout['items']if i['kind']=='clothes_dresser');front=dresser['position_blender_m'][1]+dims(dresser)[1]/2+dresser['drawer_pullout_m'];actualback=min(native[0][1],chair['position_blender_m'][1]-wh[1]/2);gaps={'exact_drawer_pullout_m':dresser['drawer_pullout_m'],'dresser_open_front_y_m':front,'working_chair_union_rear_y_m':actualback,'gap_open_drawer_to_working_chair_m':actualback-front,'gap_open_drawer_to45cmrearward_chair_m':actualback-.45-front,'catalog_only_gap_working_m':chair['position_blender_m'][1]-wh[1]/2-front,'catalog_only_gap45cmrearward_m':chair['position_blender_m'][1]-.45-wh[1]/2-front,'restriction':'Use full drawer opening and full chair pullback sequentially; the modeled simultaneous gap does not admit the tested60cm person circle.'}
  gapstates=[]
  for state,pull in [('working',0),('45cmrearward',.45)]:
   obs,_=final_obstacles(layout,native,wh,pull,drawer_open=True);gapstates.append({'chair_state':state,'dresser_fully_open_60cm_route':connected(free_shape(obs,.60))[0]})
  gaps['optional_dresser_open_route_checks']=gapstates;pr['drawer_operations']=gaps
  vd['profiles'].append(pr)
 assert lp.read_bytes()==data,'Frozen layout changed during route test'
 result['variants'].append(vd)
OUT.joinpath('final-nominal-routing.json').write_text(json.dumps(result,indent=2))
summary=['Final frozen B/C owned-Aeron routing and drawer refresh','', 'Method: actual native XY chair bbox unioned with published normal/max-arm reference envelopes; conservative metric furniture/fixed-feature projections. Door leaves open for routing.']
for v in result['variants']:
 summary +=['',v['variant'], 'Layout SHA256 '+v['layout']['sha256']]
 for pr in v['profiles']:
  summary.append(pr['profile'])
  for c in pr['cases']:summary.append('  '+c['chair_state']+': '+', '.join(str(round(t['person_circle_diameter_m']*100))+'cm '+('PASS'if t['route_pass']else'FAIL')for t in c['routing_checks']))
  d=pr['drawer_operations'];summary.append('  Open drawer/working-chair gap '+str(round(d['gap_open_drawer_to_working_chair_m'],5))+'m; with45cm pullback '+str(round(d['gap_open_drawer_to45cmrearward_chair_m'],5))+'m. Sequential use.')
summary+=['','Field geometry uncertainty remains5–12cm. Owned chair vintage/options/settings and conditional closet interior are unmeasured. Native body extends1.02mm farther rearward than nominal depth; the final proof includes it. Person circles are hypothetical planning scenarios, not measured passage guarantees. Every passing case has an exact free-space-covered centerline witness in the JSON.','Final native chair-motion/full-turn/standing-stroke/export proofs are separate QA files; no model positions changed by this refresh.']
OUT.joinpath('final-nominal-routing.txt').write_text('\n'.join(summary)+'\n')
# concise current final proof diagram, maximum-arm profile
for v in result['variants']:
 layout=json.loads(Path(v['layout']['path']).read_text());fig,axs=plt.subplots(1,2,figsize=(15,6.8));profile=v['profiles'][1]
 for ax,c in zip(axs,profile['cases']):
  obs,cs=final_obstacles(layout,v['actual_native_bounds_blender_m'],profile['published_width_depth_m'],c['rearward_translation_m']);ax.add_patch(MP(R['outline_blender_xy_m'],fc='#faf6ef',ec='#334b62',lw=2))
  for name,sh in obs:
   col='#87a0b6'if name=='aeron-primary'else'#c3ccce'
   for part in sh.geoms if hasattr(sh,'geoms')else[sh]:
    if part.geom_type=='Polygon':ax.add_patch(MP(np.asarray(part.exterior.coords),fc=col,ec='#79888f',lw=.7))
  w=c['routing_checks'][0]['path_witness'];pts=np.asarray(w['centerline_xy_m']);ax.plot(pts[:,0],pts[:,1],color='#32815f',lw=2);ax.add_patch(Circle(ENTRY,.30,fc='#32815f',alpha=.13));ax.add_patch(Circle(REAR,.30,fc='#32815f',alpha=.13))
  for id,label in [('standing-main-desk','Tria'),('secondary-workspace','Clear bench'),('clothes-dresser','Dresser'),('visitor-chair','Visitor')]:
   it=next(i for i in layout['items']if i['id']==id);ax.text(*it['position_blender_m'][:2],label,ha='center',va='center',fontsize=8,color='#41515b')
  ax.set_title(c['chair_state'].replace('45cmrearward','45cm pullback')+'\n'+', '.join(str(round(t['person_circle_diameter_m']*100))+'cm '+('pass'if t['route_pass']else'fail')for t in c['routing_checks']),fontsize=11);ax.set_aspect('equal');ax.set_xlim(-8.2,-2.9);ax.set_ylim(-3.05,.6);ax.set_xlabel('X metres (rear ← → front)');ax.set_ylabel('Y metres (brick ← → white)')
 fig.suptitle(v['variant']+' — FINAL frozen layout, owned Aeron Size C\nMaximum-arm reference unioned with actual native proxy extent. Green: validated 60cm-circle route.',fontsize=12);fig.text(.06,.022,'Nominal planning only: room 5–12cm uncertainty; doors presumed open; owned options/closet interior unmeasured. Drawer opening and full pullback use sequentially.',fontsize=9,color='#697a84');fig.tight_layout(rect=[0,.045,1,.91]);fig.savefig(OUT/(v['variant']+'-final-route-proof.png'),dpi=170);fig.savefig(OUT/(v['variant']+'-final-route-proof.pdf'));plt.close(fig)
print('\n'.join(summary))
