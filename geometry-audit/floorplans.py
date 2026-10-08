import json,math,os
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle,Arc
from matplotlib.lines import Line2D
P='/workspace/geometry-audit/'
g=json.load(open(P+'geometry.json'));rooms={r['id']:r for r in g['rooms']}
fp='/workspace/apartment-furniture/furniture-manifest.json';items=json.load(open(fp))['items'] if os.path.exists(fp) else []
entry_path='/workspace/design-fidelity/entry-manifest.json'
if os.path.exists(entry_path):
 entries=json.load(open(entry_path))['items']
 items += [{**i,'room':'entry','placement_provisional':True} for i in entries]
colors={'bed':'#83ada0','sofa':'#927582','desk':'#e5c58b','cabinet':'#e5c58b','table':'#dcae78','chair':'#e3cdba','loveseat':'#927582','rug':'#eee7db','curtain':'#d56279','tv':'#666666','lamp':'#d6c484'}
labels={'living-sofa':'Existing sofa*','living-media-console':'Media console','living-coffee-table':'Coffee table','his-desk':'Desk','her-vanity':'Vanity','her-chest':'Chest','her-loveseat':'Loveseat','bedroom-king-bed':'King bed','bedroom-large-dresser':'118 in dresser','basement-sofa':'Sofa','basement-dining-table':'Dining table','entry-gold-console':'Console*','entry-rattan-shoe-cabinet':'Shoe cabinet*'}

def dim(ax,a,b,txt,off=(0,0)):
 a=np.array(a);b=np.array(b);ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='<->',lw=.9,color='#315770'));mid=(a+b)/2+off;ax.text(*mid,txt,fontsize=9,ha='center',va='center',color='#204058',bbox={'facecolor':'white','edgecolor':'none','pad':2})
def wall(ax,a,b,color='#333333',lw=3,style='-'):
 ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=lw,linestyle=style,solid_capstyle='butt')
def doorx(ax,x,y0,y1,label=None):
 wall(ax,(x,y0),(x,y1),'white',lw=5);wall(ax,(x,y0),(x,y1),'#238b9e',lw=1,style=':');L=y1-y0
 ax.add_patch(Arc((x,y0),2*L,2*L,theta1=0,theta2=90,color='#238b9e',lw=.8));wall(ax,(x,y0),(x+L,y0),'#238b9e',lw=.8)
 if label:ax.text(x+.06,y1+.05,label,fontsize=7,color='#1c6d7e')
def windowx(ax,x,y0,y1):
 wall(ax,(x,y0),(x,y1),'white',lw=5);wall(ax,(x-.025,y0),(x-.025,y1),'#2c97b1',lw=1.8);wall(ax,(x+.025,y0),(x+.025,y1),'#2c97b1',lw=1.8)
def outline(ax,r,fill='#faf8f3',label=None):
 xy=np.array(r['outline']);ax.add_patch(Polygon(xy,closed=True,facecolor=fill,edgecolor='#444444',lw=2.2,zorder=1))
 if label:ax.text(*label[:2],label[2],ha='center',va='center',fontsize=10,color='#3b3b3b')
def furniture(ax,level):
 include=['his-office','her-office','living','entry'] if level=='upper' else ['bedroom-flex','basement','basement-lounge','basement-dining','music-gym']
 for i in sorted(items,key=lambda i:0 if i['kind']=='rug' else 1):
  if not ((level=='upper' and i['room'] in include) or (level=='lower' and (i['room'] in include or i['room'].startswith('basement')))):continue
  if i['kind'] in ['lamp','tv','art','mirror','plant']:continue
  x,y=i['position'][:2];dx,dy=i['dimensions'][:2];angle=np.deg2rad(i['rotation_deg']);R=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);verts=np.array([[-dx/2,-dy/2],[dx/2,-dy/2],[dx/2,dy/2],[-dx/2,dy/2]])@R.T+[x,y]
  if i['kind']=='curtain':
   ax.plot(verts[[0,1,2,3,0],0],verts[[0,1,2,3,0],1],color='#bd4160',ls='--',lw=2.3,zorder=7);ax.text(x+.1,y-.1,'Movable\ncurtain',fontsize=8,color='#96344c');continue
  uncertain=i.get('placement_provisional',False) or any(q in i['dimension_confidence'].lower() for q in ['assum','unmeasured','inferred','placeholder']);ax.add_patch(Polygon(verts,closed=True,facecolor=colors.get(i['kind'],'#cdbeac'),edgecolor='#b86e29' if i.get('placement_provisional',False) else '#806b55',lw=1.3 if i.get('placement_provisional',False) else .65,ls='--' if uncertain else '-',alpha=.3 if i['kind']=='rug' else .83,zorder=3))
  if i['kind'] in ['bed','sofa','chair','loveseat']:
   vec=np.array(i.get('facing_blender_xy',(R@np.array([0,1])).tolist()));ax.annotate('',xy=[x+vec[0]*min(dy*.35,.5),y+vec[1]*min(dy*.35,.5)],xytext=[x,y],arrowprops=dict(arrowstyle='->',lw=1.5,color='#863c32'),zorder=6)
  label=labels.get(i['id'])
  if not label and i['kind'] in ['desk','loveseat','bed']:label=i['kind'].capitalize()
  if label:ax.text(x,y,label,fontsize=7.5,ha='center',va='center',zorder=8,bbox=dict(facecolor='white',edgecolor='none',alpha=.6,pad=1))
for level in ['upper','lower']:
 fig,ax=plt.subplots(figsize=(22,10));fig.patch.set_facecolor('white');ax.set_facecolor('white')
 if level=='upper':
  for rid in ['upper-kitchen','living','his-office','her-office','bathroom-upper']:outline(ax,rooms[rid])
  # Stairs upper hole is observed tread/stair envelope; corridor boundaries partly reconstructed.
  x0,x1,y0,y1=g['stair']['upper_floor_void'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor='#d8eaf0',edgecolor='#2787a1',lw=1.4,zorder=2))
  for x in np.linspace(x0,x1,15):ax.plot([x,x],[y0,y1],color='#7596a1',lw=.65)
  ax.annotate('Stairs: down toward front',xy=(x1-.1,(y0+y1)/2),xytext=(x0+.05,(y0+y1)/2),fontsize=8,arrowprops=dict(arrowstyle='->',color='#1a5669'),color='#1a5669')
  for rid in ['his-office','her-office','living']:
   for op in rooms[rid].get('openings',[]):
    x=op.get('x',op.get('wall_x'));yy=op.get('y_range')
    if x is None or yy is None:continue
    if op['type']=='window':windowx(ax,x,*yy)
    else:doorx(ax,x,*yy)
  ax.add_patch(Rectangle((-3.78,-1.35),.70,1.66,facecolor='#e6e3dd',edgecolor='#555555',lw=1.2,zorder=2));ax.text(-3.43,-.5,'Closet',rotation=90,fontsize=8,ha='center')
  ax.add_patch(Rectangle((3.62,-2.77),.60,1.79,facecolor='#e6e3dd',edgecolor='#555555',lw=1.2,zorder=2));ax.text(3.92,-1.87,'Closet',rotation=90,fontsize=8,ha='center')
  wall(ax,(-3.08,-2.81),(3.62,-2.77),'#9f5636',lw=5);wall(ax,(-7.98,-2.79),(-3.08,-2.79),'#9f5636',lw=5);wall(ax,(4.22,-2.77),(7.88,-2.77),'#9f5636',lw=5)
  ax.add_patch(Rectangle((-5.75,-2.82),.88,.22,facecolor='#bb704d',edgecolor='#9d4d29',zorder=7));ax.text(-5.31,-3.03,'Fireplace',fontsize=8,ha='center')
  ax.add_patch(Rectangle((5.20,-2.82),.82,.22,facecolor='#bb704d',edgecolor='#9d4d29',zorder=7));ax.text(5.61,-3.03,'Fireplace',fontsize=8,ha='center')
  wall(ax,(1.70,1.84),(2.78,1.84),'white',lw=5);wall(ax,(1.70,1.84),(2.78,1.84),'#238b9e',lw=1,style=':');ax.text(2.24,1.65,'Entry doorway',ha='center',fontsize=7,color='#1c6d7e')
  ax.text(-5.25,-1.35,'HIS OFFICE',fontsize=12,ha='center',color='#2b2b2b');ax.text(6.18,-.6,'HER OFFICE',fontsize=12,ha='center',color='#2b2b2b');ax.text(.4,-1.4,'LIVING',fontsize=12,ha='center',color='#2b2b2b');ax.text(-5.4,1.55,'UPPER KITCHEN',fontsize=10,ha='center');ax.text(-.03,2.1,'BATH',fontsize=10,ha='center');ax.text(2.53,.75,'ENTRY',fontsize=10,ha='center')
  dim(ax,(-7.98,-3.45),(-3.08,-3.45),'Rear overall 4.90 m');dim(ax,(-3.08,-3.45),(3.62,-3.45),'Central clear span 6.70 m');dim(ax,(3.62,-3.45),(7.88,-3.45),'Front overall 4.26 m');dim(ax,(-8.45,-2.79),(-8.45,.31),'3.10 m',off=(-.15,0));dim(ax,(8.4,-2.77),(8.4,.85),'3.62 m',off=(.15,0))
  notes='Scan dimensions shown in meters; generalized observed wall coordinates, about 0.05–0.12 m uncertainty. Door swings are schematic.\nListing rear office: X 4.72 × Y 3.00 m (3–4% difference). Front office: X 4.14 × Y 3.20 m; scan short axis is 13% larger.\nLiving/dining listing labels subdivide open space differently, so central 6.70 m span is not the listing living-room length.\nCeiling above floor: rear office ≈3.02 m; living ≈2.65 m; front office ≈3.08 m. Desk and vanity face +Y, following registered Amy diagram.\nOrange dashed entry footprints (*) are provisional staging; Amy plan does not assign their positions.'
 else:
  outline(ax,rooms['basement-open']);outline(ax,rooms['music-gym'])
  # Adjacent utility volume constrained by scan boundary; internal split inferred from listing only.
  for x0,x1,name in [(-3.80,-2.15,'Bath'),(-2.15,-.65,'Laundry')]:
   ax.add_patch(Rectangle((x0,.61),x1-x0,1.79,facecolor='#e6e6e6',edgecolor='#888888',lw=1.1,ls='--',hatch='//',alpha=.6,zorder=2));ax.text((x0+x1)/2,1.65,name+'\n(inferred)',ha='center',fontsize=9)
  ax.add_patch(Rectangle((-6.58,.52),2.78,1.43,facecolor='#e6e6e6',edgecolor='#888888',lw=1.1,ls='--',hatch='//',alpha=.6,zorder=2));ax.text(-5.20,1.23,'Utility closet\n(inferred interior)',ha='center',fontsize=9)
  for op in rooms['music-gym']['openings']:doorx(ax,op['x'],*op['y_range'])
  bx=rooms['music-gym']['openings'][0]['clear_approach_xy'];ax.add_patch(Rectangle((bx[0],bx[2]),bx[1]-bx[0],bx[3]-bx[2],facecolor='none',edgecolor='#238b9e',ls=':',lw=1.5,zorder=6));ax.text(-3.36,-1.68,'Door\napproach',fontsize=7,ha='center',color='#176a7c')
  for x,y in rooms['basement-open']['columns_xy']:ax.add_patch(Rectangle((x-.09,y-.09),.18,.18,facecolor='#343434',zorder=7));ax.text(x,y+.24,'Column',fontsize=7,ha='center')
  x0,x1,y0,y1=g['stair']['bounds_xy'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor='#d8eaf0',edgecolor='#2787a1',lw=1.4,zorder=2))
  for x in np.linspace(x0,x1,15):ax.plot([x,x],[y0,y1],color='#7596a1',lw=.65)
  ax.annotate('Up toward rear',xy=(x0+.1,(y0+y1)/2),xytext=(x1-.5,(y0+y1)/2),fontsize=8,arrowprops=dict(arrowstyle='->',color='#1a5669'),color='#1a5669')
  ax.text(-5.55,-1.0,'MUSIC / GYM',fontsize=12,ha='center');ax.text(-1.3,-.4,'BEDROOM ZONE',fontsize=11,ha='center');ax.text(2.35,-1.5,'LOUNGE',fontsize=11,ha='center');ax.text(5.1,-1.5,'DINING',fontsize=11,ha='center');ax.text(7,1.0,'KITCHEN',fontsize=10,ha='center')
  dim(ax,(-7.8,-3.25),(-3.80,-3.25),'Irregular rear bounds X 4.00 m');dim(ax,(-3.80,-3.25),(5.7,-3.25),'Main flex span X ≈9.50 m');dim(ax,(-8.2,-2.65),(-8.2,1.95),'Y 4.60 m',off=(-.18,0));dim(ax,(8.4,-2.34),(8.4,2.43),'Flex Y ≈4.88 m',off=(.12,0))
  notes='Listing rear-bedroom label 15 ft 11 in ×12 ft 5 in rotates to Y 4.851 × X 3.785 m. Whole irregular scan bounds X 4.00 × Y 4.60 m agree within 6%.\nIts carved main rectangle is only X 3.56 × Y 3.05 m; using that rectangle as the entire listing dimension caused the earlier mismatch.\nGrey hatched bath/laundry/utility interiors are inferred from listing topology and were not recorded inside. Do not treat proxy fixtures as surveyed.\nDashed red curtain is movable proposed furniture, not a fixed wall; shifted toward +X so king bed, stands and gym doorway can fit. Bed-to-dresser clearance remains tight.\nMain basement ceiling height ≈2.63 m; rear soffit height ≈2.40 m. Stairs retain their scan position, ascend toward −X. Existing kitchen is preserved from scan.'
 furniture(ax,level)
 ax.annotate('FRONT / STREET   +X',xy=(7.8,3.65),xytext=(3.8,3.65),fontsize=11,color='#24465c',arrowprops=dict(arrowstyle='->',color='#24465c',lw=1.8));ax.annotate('REAR / BACKYARD   −X',xy=(-7.8,3.65),xytext=(-3.8,3.65),fontsize=11,ha='right',color='#24465c',arrowprops=dict(arrowstyle='->',color='#24465c',lw=1.8))
 ax.text(0,3.27,'+Y: bath / stair side     |     −Y: brick / long perimeter side',fontsize=10,ha='center',color='#445c69')
 ax.set_aspect('equal');ax.set_xlim(-9,9);ax.set_ylim(-3.8,4.05);ax.set_xlabel('Measured scan X (meters)',fontsize=10);ax.set_ylabel('Measured scan Y (meters)',fontsize=10);ax.grid(alpha=.12);ax.set_xticks(np.arange(-8,9));ax.set_yticks(np.arange(-3,4));ax.tick_params(labelsize=9)
 legend=[Line2D([0],[0],color='#333333',lw=3,label='Observed wall outline'),Line2D([0],[0],color='#2c97b1',lw=2,label='Window / door'),Line2D([0],[0],color='#9f5636',lw=4,label='Brick / fireplace'),Line2D([0],[0],color='#bd4160',ls='--',lw=2,label='Proposed movable divider'),Line2D([0],[0],color='#863c32',marker='>',lw=1,label='Furniture facing')]
 ax.legend(handles=legend,loc='upper center',bbox_to_anchor=(.5,-.09),ncol=5,frameon=False,fontsize=9)
 fig.suptitle(('UPPER LEVEL' if level=='upper' else 'LOWER LEVEL')+' — measured geometry + furniture proposal',fontsize=20,y=.98)
 fig.text(.055,.018,notes,fontsize=10,va='bottom',linespacing=1.4)
 fig.subplots_adjust(top=.91,bottom=.29,left=.05,right=.95)
 fig.savefig(P+level+'-dimensioned-plan.png',dpi=180);plt.close(fig)
print('Plans saved with',len(items),'furniture footprints')
