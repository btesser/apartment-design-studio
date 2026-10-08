import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
scene_file=ROOT/'his-office-pinterest-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene_file));s=bpy.context.scene
poses=[]
labels={'room-a':'Entry toward desks, lamp and rear window','room-b':'Rear doorway toward clear project bench and closet','room-c':'White wall toward unadorned brick arch and visitor chair','room-d':'Window side toward project bench and visitor chair'}
for name in ['room-a','room-b','room-c','room-d']:
 cam=bpy.data.objects['CAM '+name];f=cam.matrix_world.to_quaternion()@Vector((0,0,-1));t=cam.location+f
 poses.append({'id':name,'label':labels[name],'filename':'renders/'+name+'.jpg','eye_blender_m':list(cam.location),'look_direction_blender':list(f),'eye_gltf_m':[cam.location.x,cam.location.z,-cam.location.y],'target_gltf_m':[t.x,t.z,-t.y],'eye':[cam.location.x,cam.location.z,-cam.location.y],'target':[t.x,t.z,-t.y],'lens_mm':cam.data.lens,'sensor_width_mm':cam.data.sensor_width,'horizontal_FOV_deg':math.degrees(2*math.atan(cam.data.sensor_width/(2*cam.data.lens))),'pixels':[1440,1000],'unit':'metres; native Blender Z-up; GLTF X,Z,-Y','scene_sha256':hashlib.sha256(scene_file.read_bytes()).hexdigest()})
(ROOT/'camera-poses.json').write_text(json.dumps(poses,indent=2))
