import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path
out=Path('/workspace/apartment-design/orientation');out.mkdir(exist_ok=True)
fig,axs=plt.subplots(1,3,figsize=(15,5))
def box(ax,xy,w,h,label,color='#dfd1b8'):
 ax.add_patch(Rectangle(xy,w,h,facecolor=color,edgecolor='#444',linewidth=1.5));ax.text(xy[0]+w/2,xy[1]+h/2,label,ha='center',va='center',fontsize=9)
def arrow(ax,a,b):ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='#b34e31',lw=3))
for ax in axs:
 ax.set_xlim(0,6);ax.set_ylim(0,4);ax.set_aspect('equal');ax.axis('off');box(ax,(0,0),6,4,'', '#faf8f3')
ax=axs[0];ax.set_title('Living room: sofa faces media wall',pad=35)
box(ax,(.9,.15),4,.8,'SOFA');box(ax,(2.2,1.7),1.7,.6,'Coffee table');box(ax,(2.2,3.5),1.8,.35,'Media console');arrow(ax,(3,1),(3,1.65));ax.text(3,-.35,'Brick wall / sofa back',ha='center');ax.text(3,4.15,'White wall / door openings',ha='center')
ax=axs[1];ax.set_title('His office: chair faces desk / wall',pad=35)
box(ax,(4.9,1.1),.8,1.8,'Desk');box(ax,(3.9,1.7),.6,.6,'Chair');arrow(ax,(4.45,2),(4.9,2));ax.text(-.15,2,'Window /\nexterior door',ha='right');box(ax,(1,.15),2,.5,'Low bookshelves');ax.text(3,-.35,'Brick side wall',ha='center');ax.text(5.8,4.15,'Desk wall opposite window',ha='right')
ax=axs[2];ax.set_title('Her office: chair faces vanity',pad=35)
box(ax,(.2,1.2),.65,1.8,'Vanity');box(ax,(1.15,1.8),.6,.6,'Chair');arrow(ax,(1.15,2.1),(.85,2.1));box(ax,(.2,.2),.65,.7,'Chest');box(ax,(4.1,.25),1.4,.75,'Loveseat');arrow(ax,(4.5,1),(3.7,1.8));ax.text(6.1,2,'Two windows /\nradiator',ha='left');ax.text(3,-.35,'Brick fireplace wall',ha='center');ax.text(3,4.15,'Closet / entry side',ha='center')
fig.suptitle('Furniture facing directions aligned to Polycam orientation — schematic, not to scale',fontsize=14)
fig.tight_layout();fig.savefig(out/'upstairs-facing.png',dpi=150,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(14,5));ax.set_xlim(-4,8);ax.set_ylim(-3,3);ax.set_aspect('equal');ax.axis('off')
box(ax,(-3.8,-2.6),11.6,5.2,'','#faf8f3')
box(ax,(-3.55,-2.3),2.8,2.1,'King bed\nHEADBOARD at bottom wall');arrow(ax,(-2.15,-.15),(-2.15,.55))
ax.plot([-.3,-.3],[-2.6,.45],color='#806957',lw=6);ax.text(-.3,-2.9,'Curtain divider',ha='center')
box(ax,(-.05,-2.05),.75,2.35,'SOFA\nback at\ndivider');arrow(ax,(.75,-.9),(1.5,-.9))
box(ax,(1.7,-1.4),1,.7,'Coffee\ntables');box(ax,(3.2,-2.1),.7,.65,'Chair');arrow(ax,(3.2,-1.8),(2.7,-1.2));box(ax,(3.2,-.55),.7,.65,'Chair');arrow(ax,(3.2,-.2),(2.7,-.7))
box(ax,(4.3,-1.7),2,1.15,'Dining table\nlong axis along room');ax.text(7,1.5,'Kitchen end',ha='center');ax.text(-2.7,2,'Bathroom / bed end',ha='center');ax.text(2.5,2.3,'Stairs + columns side: keep circulation open',ha='center');ax.text(-2.6,-2.9,'Long perimeter wall',ha='center')
ax.set_title('Basement: bed faces across room; sofa faces toward dining/kitchen\nPositions schematic; preserve actual columns, doors and clearances',fontsize=14)
fig.tight_layout();fig.savefig(out/'basement-facing.png',dpi=150,bbox_inches='tight')
