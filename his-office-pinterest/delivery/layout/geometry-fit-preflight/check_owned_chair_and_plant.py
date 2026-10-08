import json,hashlib,math,copy,heapq
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,Point,box,LineString
from shapely.ops import unary_union
from shapely import contains_xy
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPolygon,Rectangle,Circle
ROOT=Path('/workspace/his-office-pinterest');OUT=ROOT/'layout/geometry-fit-preflight';OUT.mkdir(parents=True,exist_ok=True)
ROOMP=Path('/workspace/his-office-redesign/geometry/room-measurements.json');FEATP=Path('/workspace/his-office-redesign/geometry/fixed-features.json');ACCESSP=Path('/workspace/his-office-redesign/geometry/access-and-feasible-zones.json');OWNEDP=ROOT/'products/owned-chair/owned-aeron-size-c-mineral.json'
R=json.loads(ROOMP.read_text());ROOM=Polygon(R['outline_blender_xy_m']);FEATURES=json.loads(FEATP.read_text())['features'];ACCESS=json.loads(ACCESSP.read_text())['zones'];OWNED=json.loads(OWNEDP.read_text());ENTRY=(-3.50,-2.10);REAR=(-7.50,-2.10)
NORMAL=(.71882,.71882);MAXARM=(.80264,.71882)
def info(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def dims(it):
 if 'world_axis_dimensions_m' in it:return it['world_axis_dimensions_m'][:2]
 w,d=it['external_dimensions_m'][:2];a=math.radians(it.get('rotation_z_deg',0));return [abs(w*math.cos(a))+abs(d*math.sin(a)),abs(w*math.sin(a))+abs(d*math.cos(a))]
def rect(center,wh):x,y=center;w,d=wh;return box(x-w/2,y-d/2,x+w/2,y+d/2)
def features():
 out=[]
 for f in FEATURES:
  if f['id'] not in ['rear-radiator','closed-fireplace','rear-pipe','front-shelf-nook','closet-door']:continue
  b=f.get('hearth_keepout_xy')or f['bounds_blender_xyz_m'][:4];out.append((f['id'],box(b[0],b[2],b[1],b[3])))
 return out
def make_obstacles(layout,wh,pullback=0,include_chair=True):
 out=features();chair=None
 for it in layout['items']:
  x,y,z=it['position_blender_m'];kind=it['kind']
  if kind in ['rug','art','closet_shoe_rack']:continue
  if kind=='task_chair':
   chair=(it['id'],rect((x,y-pullback),wh))
   if include_chair:out.append(chair)
  elif kind=='kept_lamp':
   # Source protected keeper U-base: approximate shape, not a vendor-CAD claim.
   shapes=[]
   for dx,dy,w,d in [(0,-.196,.247,.07),(-.084,.018,.079,.438),(.084,.018,.079,.438)]:shapes.append(rect((x+dx,y+dy),(w,d)))
   out.append((it['id'],unary_union(shapes)))
  else:out.append((it['id'],rect((x,y),dims(it))))
 if layout['workwall_finish'].get('panel_count'):
  out.append(('current-checkpoint-B-wallpanels',box(-6.45,.238,-4.65,.31)))
 return out,chair

def free_shape(obs,diam):return ROOM.buffer(-diam/2,quad_segs=96).difference(unary_union([sh.buffer(diam/2,quad_segs=96)for _,sh in obs]))
def connected(free):
 pieces=[g for g in free.geoms if g.geom_type=='Polygon']if hasattr(free,'geoms')else[free]
 a=next((i for i,g in enumerate(pieces)if g.covers(Point(ENTRY))),None);b=next((i for i,g in enumerate(pieces)if g.covers(Point(REAR))),None)
 return a is not None and a==b, a,b

def witness(free,obs,diam):
 # Independent concrete path witness,5mm grid with2mm conservative inset.
 safe=free.buffer(-.002);step=.005;xs=np.arange(-8.0,-3.0+step,step);ys=np.arange(-2.8,.32+step,step);xx,yy=np.meshgrid(xs,ys);inside=contains_xy(safe,xx,yy)
 def closest(p):
  dist=(xx-p[0])**2+(yy-p[1])**2;dist[~inside]=np.inf;k=np.unravel_index(np.argmin(dist),dist.shape);return k
 start=closest(ENTRY);goal=closest(REAR);heap=[(0,start)];cost={start:0};prev={};seen=set()
 while heap:
  _,q=heapq.heappop(heap)
  if q in seen:continue
  if q==goal:break
  seen.add(q)
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
   n=(q[0]+dy,q[1]+dx)
   if not(0<=n[0]<len(ys)and 0<=n[1]<len(xs)and inside[n]):continue
   new=cost[q]+step
   if new<cost.get(n,1e9):cost[n]=new;prev[n]=q;heur=math.hypot((n[1]-goal[1])*step,(n[0]-goal[0])*step);heapq.heappush(heap,(new+heur,n))
 if goal not in cost:return {'witness_found':False}
 q=goal;nodes=[q]
 while q!=start:q=prev[q];nodes.append(q)
 nodes.reverse();pts=[ENTRY]+[(float(xs[x]),float(ys[y]))for y,x in nodes]+[REAR]
 # Greedy string-pull only accepts segments fully inside exact free space.
 keep=[pts[0]];j=0
 while j<len(pts)-1:
  k=len(pts)-1
  while k>j+1 and not free.covers(LineString([pts[j],pts[k]])):k-=1
  keep.append(pts[k]);j=k
 line=LineString(keep);clear=min(line.distance(sh)for _,sh in obs);wallclear=line.distance(ROOM.boundary)
 return {'witness_found':True,'centerline_xy_m':keep,'length_m':line.length,'exact_free_space_covers_witness':bool(free.covers(line)),'minimum_centerline_distance_to_obstacle_m':clear,'minimum_centerline_distance_to_room_boundary_m':wallclear,'person_diameter_m':diam,'extra_grid_inset_m':.002}

def transfer(layout,wh,extra=None):
 obs,_=make_obstacles(layout,wh,include_chair=False);obs+=extra or [];chair=next(it for it in layout['items']if it['kind']=='task_chair');start=chair['position_blender_m'][:2]
 # Feasible candidate operating location at the clear right knee bay of fixed bench.
 way=[start,[start[0],start[1]-.45],[-5.70,-1.30],[-5.70,-1.10],[-5.35,-.85]];segments=[]
 for a,b in zip(way,way[1:]):
  sweep=unary_union([rect(a,wh),rect(b,wh)]).convex_hull;hits=[name for name,s in obs if sweep.intersection(s).area>1e-9];segments.append({'start':a,'end':b,'conservative_rectangle_sweep_m2':sweep.area,'room_covers_sweep':bool(ROOM.covers(sweep)),'obstacle_overlap_names':hits,'minimum_obstacle_distance_m':min(sweep.distance(s)for _,s in obs)})
 radius=math.hypot(wh[0]/2,wh[1]/2);turns=[]
 for center in [(-5.70,-1.30),(-5.70,-1.10)]:
  turn=Point(center).buffer(radius,quad_segs=128);hits=[name for name,sh in obs if turn.intersection(sh).area>1e-9];turns.append((not hits and ROOM.covers(turn),min(turn.distance(sh)for _,sh in obs),center,turn,hits))
 _,_,center,turn,hits=max(turns,key=lambda t:(t[0],t[1]))
 return {'method':'Exact convex swept rectangle for straight translations; full circumscribed circle proves all yaw angles at a separate turn location. No furnishings moved; target bench chair location is an operational candidate, not canonical placement.','product_profile_width_depth_m':wh,'candidate_waypoints_xy_m':way,'translations':segments,'all_translations_pass_nominal':all(s['room_covers_sweep']and not s['obstacle_overlap_names']for s in segments),'full_rotation':{'center_xy_m':center,'conservative_diameter_m':2*radius,'room_covers_full_turn_circle':bool(ROOM.covers(turn)),'obstacle_overlap_names':hits,'minimum_obstacle_distance_m':min(turn.distance(s)for _,s in obs),'pass':ROOM.covers(turn)and not hits}}

def plant_screen(layout,wh):
 # Conditional screening: no plant selection or dimensions implied.
 obs_work,_=make_obstacles(layout,wh,0);obs_pull,_=make_obstacles(layout,wh,.45);hard=unary_union([s for _,s in obs_work+obs_pull]);preserve=[]
 for z in ACCESS:
  if z['id']in['closet-approach','living-entry-approach','rear-door-approach']:
   b=z['bounds_xy_m'];preserve.append(box(b[0],b[2],b[1],b[3]))
 dresser=next(it for it in layout['items']if it['kind']=='clothes_dresser');x,y=dresser['position_blender_m'][:2];w,d=dims(dresser);front=y+d/2+ dresser['drawer_pullout_m'];preserve.append(box(x-.45,y+d/2,x+.45,front+.60));keepout=unary_union(preserve)
 candidates=[]
 for dia in [.30,.45,.60,.75]:
  feasible=[];geofit=[]
  for x in np.arange(-6.15,-3.85+.001,.05):
   for y in np.arange(-2.50,-.80+.001,.05):
    plant=Point(x,y).buffer(dia/2,quad_segs=48)
    if not ROOM.covers(plant)or plant.intersects(hard)or plant.intersects(keepout):continue
    geofit.append([round(float(x),3),round(float(y),3)])
    mov=transfer(layout,wh,[('conditional-full-foliage-plant',plant)])
    if mov['all_translations_pass_nominal'] and mov['full_rotation']['pass'] and all(connected(free_shape(obs+[('conditional-full-foliage-plant',plant)],.60))[0] for obs in [obs_work,obs_pull]):feasible.append([round(float(x),3),round(float(y),3)])
  candidates.append({'full_foliage_diameter_m':dia,'geometric_fit_candidate_count':len(geofit),'retains_60cm_route_both_states_count':len(feasible),'candidate_centers_xy_m':feasible,'geometry_only_centers_xy_m':geofit})
 return {'status':'Checkpoint screening only; final plant product crown/height and added composition pieces not frozen. All listed diameters are scenario assumptions, not product measurements.','ROI_blender_xy_m':[-6.15,-3.85,-2.50,-.80],'grid_spacing_m':.05,'requirements':['Full foliage circle clears all conservative existing furniture in bothchair states','Preserve actual closet/living/rear approach rectangles and conservative fireplace projection','Preserve open-drawer and.60m standing zone (sequential-use chair state remains separate)','A .60m nominal person circle keeps entry-to-rear connectivity in working and45cm pullback states','Max-arm chair swept transfer to bench and full360deg rotation at either explicit turn location remain clear'],'results':candidates}

result={'route_endpoints':{'entry_xy_m':ENTRY,'rear_door_approach_xy_m':REAR,'previous_rear_target_xy_m':[-7.30,-1.90],'note':'Previous rear target can lie in the expanded owned-chair/person exclusion zone when pulled back. New target is centered toward the actual exterior-door approach; no furniture moved.'},'status':'PROVISIONAL checkpoint analysis with independently sourced owned-Aeron envelope; fuller composition pending; no final circulation claim','sources':[info(p)for p in[ROOMP,FEATP,ACCESSP,OWNEDP]],'method':'Conservative full-chair rectangles, independent continuous configuration space and explicit collision-free path witness. Owned chair vintage/options not confirmed; published manufacturer Size C envelope used.','limits':['Generalized room5–12cm uncertainty; current source insidewall face may be~5cm inside nominal room edge.','Primary arm positions/actual owned configuration unmeasured. Maximum published arms tested separately.','Door leaves presumed open for routing; inferred swing hardware not simulated.','Current upper cat branches and shelf/desk stroke are separate exact3DQA, not guaranteed by floor routing.','No selected plant dimensions or final new wall/shelf composition yet.'],'variants':[]}
for variant in ['b-charcoal-slat','c-ink-studio']:
 lp=ROOT/'variants'/variant/'model/layout.json';layout=json.loads(lp.read_text());ch=next(i for i in layout['items']if i['kind']=='task_chair');actual_owned='aeron' in ch.get('product_id','').lower();entry={'variant':variant,'source_layout':info(lp),'layout_version':layout['layout_version'],'canonical_has_owned_Aeron':actual_owned,'chair_current_canonical':ch,'profiles':[]}
 for name,wh in [('normal_width_max_depth',NORMAL),('maximum_expanded_arms',MAXARM)]:
  checks=[]
  for label,pull in [('working',0),('primary45cmrearward',.45)]:
   obs,_=make_obstacles(layout,wh,pull);cases=[]
   for dia in [.50,.55,.60,.61,.62,.65,.70]:
    free=free_shape(obs,dia);ok,a,b=connected(free);cases.append({'person_circle_diameter_m':dia,'route_pass':ok,'entry_component':a,'rear_component':b})
   free=free_shape(obs,.60);check={'chair_state':label,'checks':cases,'witness60cm':witness(free,obs,.60)if connected(free)[0]else None};checks.append(check)
  dresser=next(i for i in layout['items']if i['kind']=='clothes_dresser');front=dresser['position_blender_m'][1]+dims(dresser)[1]/2+dresser['drawer_pullout_m'];normalback=ch['position_blender_m'][1]-wh[1]/2;ops={'dresser_drawer_pullout_m':dresser['drawer_pullout_m'],'open_drawer_front_y_m':front,'gap_to_working_chair_back_m':normalback-front,'gap_to45cmrearward_chair_back_m':normalback-.45-front,'interpretation':'Maximum-depth rectangles overlap drawerXrun; simultaneous fullopen+chairpullback gap is not a useful person passage. Defaultworking chair allows drawer use; keep sequential operations.'}
  entry['profiles'].append({'profile':name,'chair_W_D_m':wh,'circulation':checks,'drawer_operations':ops,'bench_transfer_and_rotation':transfer(layout,wh)})
 entry['conditional_plant_screen']=plant_screen(layout,MAXARM)
 obs_work,_=make_obstacles(layout,MAXARM,0);obs_pull,_=make_obstacles(layout,MAXARM,.45);spots=[]
 for center in [(-5.60,-2.40),(-5.80,-2.40),(-5.60,-2.15),(-5.80,-2.15)]:
  for dia in [.30,.45,.60,.75]:
   plant=Point(center).buffer(dia/2,quad_segs=96);hits=sorted(set(name for name,sh in obs_work+obs_pull if plant.intersection(sh).area>1e-9));mov=transfer(layout,MAXARM,[('plant-full-foliage',plant)]);hearth=next(sh for name,sh in obs_work if name=='closed-fireplace');route=[connected(free_shape(obs+[('plant-full-foliage',plant)],.60))[0]for obs in[obs_work,obs_pull]]
   best=mov['full_rotation'];tc=Point(best['center_xy_m']).buffer(best['conservative_diameter_m']/2,quad_segs=128);spots.append({'center_xy_m':center,'full_foliage_diameter_m':dia,'modeled_height_range_m':[.8,1.2],'fixed_furniture_overlap_names':hits,'room_covers_crown':ROOM.covers(plant),'hearth_clearance_m':plant.distance(hearth),'nominal60cm_route_working_pullback':route,'chair_swept_transfer_pass':mov['all_translations_pass_nominal'],'fullturn_pass':best['pass'],'chosen_turn_center':best['center_xy_m'],'plant_to_full_turn_clearance_m':plant.distance(tc),'practical_note':'Full-foliage envelope is hypothetical; real productspread must beverified. Smaller45cm crown gives materiallybetter architectural/movement margins than60cm at proposedforward center.'})
 entry['requested_plant_spot_checks']=spots
 result['variants'].append(entry)
OUT.joinpath('checkpoint-owned-chair-and-plant-fit.json').write_text(json.dumps(result,indent=2))
# readable summary + proof diagram
lines=[result['status']]
for v in result['variants']:
 lines.append('\n'+v['variant']+' | canonicalOwnedAeron='+str(v['canonical_has_owned_Aeron']))
 for pr in v['profiles']:
  lines.append(pr['profile']+': '+', '.join(c['chair_state']+'60cm='+str(c['checks'][2]['route_pass'])for c in pr['circulation'])+'; transfer='+str(pr['bench_transfer_and_rotation']['all_translations_pass_nominal'])+'; fullturn='+str(pr['bench_transfer_and_rotation']['full_rotation']['pass']))
  lines.append('Drawer working/pulled gaps'+str([round(pr['drawer_operations'][k],3)for k in ['gap_to_working_chair_back_m','gap_to45cmrearward_chair_back_m']]))
 lines.append('Plantfullfoliage nominaldiameters / retained60cm-route centers: '+str([(c['full_foliage_diameter_m'],c['retains_60cm_route_both_states_count'])for c in v['conditional_plant_screen']['results']]))
OUT.joinpath('checkpoint-owned-chair-and-plant-fit.txt').write_text('\n'.join(lines)+'\n')
for v in result['variants']:
 layout=json.loads(Path(v['source_layout']['path']).read_text());fig,axes=plt.subplots(1,2,figsize=(15,6));pr=v['profiles'][1]
 for ax,c,pull in zip(axes,pr['circulation'],[0,.45]):
  obs,_=make_obstacles(layout,MAXARM,pull);ax.add_patch(MPolygon(R['outline_blender_xy_m'],fc='#f7f5ef',ec='#334b63',lw=2))
  for name,s in obs:
   for a in s.geoms if hasattr(s,'geoms')else[s]:
    if a.geom_type=='Polygon':ax.add_patch(MPolygon(np.asarray(a.exterior.coords),fc='#b0bdc6'if name!=ch['id']else'#7d94b0',ec='#697780',alpha=.8))
  w=c['witness60cm']
  if w and w['witness_found']:
   line=np.asarray(w['centerline_xy_m']);ax.plot(line[:,0],line[:,1],color='#398363',lw=2);ax.add_patch(Circle(ENTRY,.30,fc='#398363',alpha=.14));ax.add_patch(Circle(REAR,.30,fc='#398363',alpha=.14))
  turn=pr['bench_transfer_and_rotation'];line=np.asarray(turn['candidate_waypoints_xy_m']);ax.plot(line[:,0],line[:,1],color='#7e599d',ls='--',lw=1.3);t=turn['full_rotation'];ax.add_patch(Circle(t['center_xy_m'],t['conservative_diameter_m']/2,fill=False,ec='#7e599d',ls=':',lw=1.2))
  ax.set_aspect('equal');ax.set_xlim(-8.2,-2.9);ax.set_ylim(-3.05,.55);ax.set_title(c['chair_state']+' | maxarm80.264×71.882cm\n60cm nominal route '+str(c['checks'][2]['route_pass']),fontsize=11);ax.set_xlabel('Xmetres (+front / -rear)');ax.set_ylabel('Ymetres (+white / -brick)')
 fig.suptitle('PROVISIONAL '+v['variant']+' checkpoint with owned-Aeron envelope substituted\nGreen: exact60cm route witness. Purple: chairtransfer / fullturn circle. Final composition pending.',fontsize=12);fig.tight_layout();fig.savefig(OUT/(v['variant']+'-checkpoint-proof.png'),dpi=150);plt.close(fig)
print('\n'.join(lines))
