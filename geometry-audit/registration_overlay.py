from PIL import Image
import numpy as np,json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
p='/workspace/geometry-audit/'
img=np.array(Image.open('/workspace/apartment-design/designer-boards/Lana & Ben FLOOR PLAN.png').convert('RGB'))
g=json.load(open(p+'geometry.json'));rooms={r['id']:r for r in g['rooms']}
config=[
 dict(id='living',crop=[42,42,560,692],u0=55,v0=63,x0=-3.08,y0=-2.79,sx=6.70/610,sy=3.18/300,anchors=[('sofa back',(64,372),(-.0,-2.79)),('bath/stair indent',(355,437),(1.03,.39)),('rear entry',(124,64),(-3.08,-2.06)),('front entry',(292,674),(3.62,-.28))]),
 dict(id='his-office',crop=[540,834,886,1324],u0=560,v0=855,x0=-7.98,y0=-2.79,sx=4.20/385,sy=3.10/309,anchors=[('exterior entry',(641,855),(-7.98,-1.98)),('brick side',(560,1190),(-3.72,-2.79)),('closet indent',(708,1239),(-3.09,-1.31)),('desk back',(862,943),(-6.86,.24))]),
 dict(id='her-office',crop=[15,838,394,1305],u0=35,v0=874,x0=3.62,y0=-2.77,sx=4.26/413,sy=3.62/343,anchors=[('brick fireplace',(37,1080),(5.75,-2.75)),('closet/entry',(220,875),(3.63,-.82)),('window end',(203,1287),(7.88,-1.00)),('vanity back',(372,1088),(5.83,.79))]),
 dict(id='bedroom-flex',crop=[966,170,1314,1052],u0=990,v0=195,x0=-3.8,y0=-2.45,sx=11.1/845,sy=3.10/307,anchors=[('bed headboard',(990,352),(-1.74,-2.45)),('divider',(1120,514),(.39,-1.14)),('sofa back',(1090,528),(.57,-1.44)),('table',(1105,873),(5.11,-1.29))])
]
# Coordinates above were read from 1824x1368 displayed preview; convert to native2048x1536.
scale=2048/1824
for c in config:
 c['crop']=[int(round(v*scale)) for v in c['crop']]
 c['u0']*=scale;c['v0']*=scale;c['sx']/=scale;c['sy']/=scale
 c['anchors']=[(label,(u*scale,v*scale),ref) for label,(u,v),ref in c['anchors']]
# Last basement mapping annotated only topology: no reliable source global scale due cropped subplan geometry.
fig,axs=plt.subplots(4,2,figsize=(17,19))
registered={}
for row,cfg in enumerate(config):
 rid=cfg['id'];crop=cfg['crop']; ax=axs[row,0];ax.imshow(img);ax.set_xlim(crop[0],crop[2]);ax.set_ylim(crop[3],crop[1]);ax.set_aspect('equal');ax.set_title('Amy schematic: '+rid)
 for label,(u,v),ref in cfg['anchors']:
  ax.scatter([u],[v],s=30,color='crimson');ax.annotate(label,(u,v),xytext=(5,5),textcoords='offset points',fontsize=8,color='crimson')
 ax.set_xlabel('source u→right');ax.set_ylabel('source v→down')
 ax=axs[row,1];floor='upstairs' if rid!='bedroom-flex' else 'basement';d=np.load(p+floor+'_surface.npz');cc=d['c'];nn=d['n'];aa=d['a'];fz=rooms[rid]['floor_z_m'];q=(np.abs(cc[:,2]-fz)<.2)&(np.abs(nn[:,2])>.8)
 ax.scatter(cc[q,0],cc[q,1],s=.25,color='#a99b78',alpha=.7)
 q=(np.abs(cc[:,2]-(fz+1.25))<.5)&(np.abs(nn[:,2])<.4)
 ax.scatter(cc[q,0],cc[q,1],s=.35,color='#333333',alpha=.7)
 umin,vmin,umax,vmax=crop;sx=cfg['sx'];sy=cfg['sy'];xy=lambda u,v:(cfg['x0']+(v-cfg['v0'])*sx,cfg['y0']+(u-cfg['u0'])*sy)
 xlo,ylo=xy(umin,vmin);xhi,yhi=xy(umax,vmax)
 roi=img[vmin:vmax,umin:umax]
 if rid!='bedroom-flex':
  ax.imshow(np.rot90(roi),extent=[xlo,xhi,ylo,yhi],origin='upper',alpha=.36)
  regs=[]
  for label,(u,v),ref in cfg['anchors']:
   x,y=xy(u,v);ax.scatter([x],[y],s=24,color='crimson');ax.annotate(label,(x,y),xytext=(5,4),textcoords='offset points',fontsize=8,color='crimson');regs.append({'source_label':label,'source_pixel':[u,v],'registered_xyz':[x,y,fz]})
  registered[rid]={'x_from_v':[sx,cfg['x0']-cfg['v0']*sx],'y_from_u':[sy,cfg['y0']-cfg['u0']*sy],'anchors':regs,'note':'Schematic independently fitted to observed main room boundary; affine/nonuniform scale. Graphic is correspondence check, not measured furniture placement.'}
 else:
  ax.text(-3.55,2.2,'Basement fragment fixes facing and zone order.\nNo unique metric global registration:\nopen space widens; curtain line is provisional.',fontsize=10,color='#7a2929')
  ax.arrow(-2.05,-2.45,0,1.9,width=.035,color='crimson',length_includes_head=True);ax.text(-3.6,-1.3,'head→foot +Y',fontsize=9)
  ax.arrow(-.4,-1.6,2,0,width=.035,color='crimson',length_includes_head=True);ax.text(-.4,-1.3,'lounge faces +X',fontsize=9)
 if rid=='living':ax.set_xlim(-3.5,4);ax.set_ylim(-3.2,2)
 elif rid=='his-office':ax.set_xlim(-8.5,-2.5);ax.set_ylim(-3.2,.8)
 elif rid=='her-office':ax.set_xlim(3.1,8.4);ax.set_ylim(-3.2,1.3)
 else:ax.set_xlim(-4.4,8.4);ax.set_ylim(-3,3.1)
 ax.set_aspect('equal');ax.grid(alpha=.3);ax.set_xlabel('scan X meters (positive toward front)');ax.set_ylabel('scan Y meters (positive bath/stair side)');ax.set_title('Registered onto measured mesh: '+rid)
fig.suptitle('Independent source-to-scan audit: image u→+Y and v→+X; no mirroring',fontsize=17)
plt.tight_layout(rect=[0,0,1,.98]);fig.savefig(p+'amy_scan_registration.png',dpi=165)
json.dump(registered,open(p+'amy_affine_registration.json','w'),indent=2)
