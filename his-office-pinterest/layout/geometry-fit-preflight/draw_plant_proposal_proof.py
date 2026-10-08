from pathlib import Path
import json
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP,Circle
code=Path('/workspace/his-office-pinterest/layout/geometry-fit-preflight/check_owned_chair_and_plant.py').read_text().split("result={'route_endpoints'")[0]
exec(code)
lp=ROOT/'variants/b-charcoal-slat/model/layout.json';layout=json.loads(lp.read_text());center=(-5.60,-2.15);diam=.45;plant=Point(center).buffer(diam/2,quad_segs=96);proof={'status':'PROPOSAL ONLY. Existing B/C are checkpoints; fuller composition and owned-chair canonical update pending. No furniture or model positions changed.','sources':[info(p)for p in[lp,ROOMP,FEATP,ACCESSP,OWNEDP]],'plant':{'proposed_center_xy_m':center,'maximum_practical_full_foliage_diameter_m':diam,'height_range_m':[.8,1.2],'source_status':'Not selected or measured. Purchase candidate must verify entire foliage spread, not pot diameter. If unverified, choose shelf/bench greenery.'},'chair_profile':{'name':'Owned Aeron Size C maximum published arms','W_D_m':MAXARM,'owned_vintage_options':'unconfirmed'},'cases':[]}
fig,axs=plt.subplots(1,2,figsize=(15,6.8))
for ax,label,pull in zip(axs,['Working chair','Chair pulled back45cm'],[0,.45]):
 obs,_=make_obstacles(layout,MAXARM,pull);obs.append(('full-foliage-plant-proposal',plant));free=free_shape(obs,.60);w=witness(free,obs,.60);passing,a,b=connected(free);assert passing and w['witness_found']and w['exact_free_space_covers_witness'];proof['cases'].append({'state':label,'route60cm':passing,'route61cm':connected(free_shape(obs,.61))[0],'route62cm':connected(free_shape(obs,.62))[0],'witness':w})
 ax.add_patch(MP(R['outline_blender_xy_m'],fc='#faf6ef',ec='#304b63',lw=2))
 for name,sh in obs:
  col='#5f966f'if name=='full-foliage-plant-proposal'else'#99adc0'if name=='branch-primary'else'#c3c9cb'
  for part in sh.geoms if hasattr(sh,'geoms')else[sh]:
   if part.geom_type=='Polygon':ax.add_patch(MP(np.asarray(part.exterior.coords),fc=col,ec='#6d7981',lw=.8))
 pts=np.asarray(w['centerline_xy_m']);ax.plot(pts[:,0],pts[:,1],color='#2e855f',lw=2.2);ax.add_patch(Circle(ENTRY,.30,fc='#2e855f',alpha=.15));ax.add_patch(Circle(REAR,.30,fc='#2e855f',alpha=.15));ax.text(-5.6,-2.15,'Ø45cm\nfull crown',ha='center',va='center',color='white',fontsize=8,fontweight='bold')
 move=transfer(layout,MAXARM,[('full-foliage-plant-proposal',plant)]);p=np.asarray(move['candidate_waypoints_xy_m']);ax.plot(p[:,0],p[:,1],color='#80569e',lw=1.2,ls='--');turn=move['full_rotation'];ax.add_patch(Circle(turn['center_xy_m'],turn['conservative_diameter_m']/2,fill=False,ec='#80569e',lw=1.1,ls=':'))
 ax.set_aspect('equal');ax.set_xlim(-8.2,-2.9);ax.set_ylim(-3.0,.65);ax.set_title(label+' | max-arm chair80.264×71.882cm',fontsize=11);ax.set_xlabel('Xmetres: rear ← → front');ax.set_ylabel('Ymetres: brick ← → white wall')
proof['max_arm_chair_transfer_and_full_turn']=transfer(layout,MAXARM,[('full-foliage-plant-proposal',plant)])
obs,_=make_obstacles(layout,MAXARM,0);hearth=next(sh for name,sh in obs if name=='closed-fireplace');proof['hearth_conservative_projection_clearance_m']=plant.distance(hearth)
proof['comparison']={'examples_at_y_minus2_4':'Overlap conservative fireplace projection even at30cm foliage; reject.','alternative_x_minus5_8_y_minus2_15':'45cm crown blocks pulled-back60cm nominal route; reject at that size.','60cm_at_chosen_center':'Nominal route passes but only3cm to hearthbuffer; not recommended as practical purchase envelope.','drawer_operation':'Full-depth Aeron leaves.785m before open dresser at working pose,.335m after45cm pullback; use sequentially.'}
proof['limits']=['Door leaves open for passage; swings inferred.','Room generalized5–12cm; not measured installation clearance.','60cm is a hypothetical person circle, not measured shoulderwidth or guaranteed accessible passage.','Final added floor/height objects must be retested after canonical freeze; B/C current checkpoint features share furniture anchors.']
fig.suptitle('OPTIONAL FLOOR PLANT — proposal screen before modeling\nGreen:60cm person-circle route. Purple: conservative chair transfer /360°turn. No geometry moved.',fontsize=13);fig.text(.06,.022,'Proposed(-5.60,-2.15), full foliage≤45cm, H.8–1.2m. Hearthbuffer clearance10.5cm. True plant spread/vintage chair and installed room dimensions remain unmeasured.',fontsize=9,color='#5d6e7a');fig.tight_layout(rect=[0,.045,1,.91]);fig.savefig(OUT/'optional-floor-plant-proposal-proof.png',dpi=180);fig.savefig(OUT/'optional-floor-plant-proposal-proof.pdf');plt.close(fig)
OUT.joinpath('optional-floor-plant-proposal-proof.json').write_text(json.dumps(proof,indent=2))
print('Proposal proof written',proof['hearth_conservative_projection_clearance_m'],[(q['state'],q['route60cm'],q['route61cm'],q['route62cm'])for q in proof['cases']])
