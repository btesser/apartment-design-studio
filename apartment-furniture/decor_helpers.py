"""Source-board decor approximations in furniture parent local +Y front.
Factory takes primitive/material helpers. Builders use dimensions [width,depth,height]
and local minimum Z=0; external parent placement/rotation stays with main builder.
"""
import math

def make_builders(ctx):
    cube,cyl,rod,cone,sphere,own=[ctx[k] for k in ('cube','cyl','rod','cone','sphere','own')]
    bpy=ctx['bpy'];mats=ctx['MAT']
    def add_mat(name,rgb):
        if name in mats:return
        m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
        b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Roughness'].default_value=.65;mats[name]=m
    for name,col in [('Art blush',(.66,.35,.39)),('Art pale pink',(.78,.58,.54)),('Art cream',(.85,.78,.63)),('Art ochre',(.49,.27,.075)),('Art forest',(.04,.14,.10)),('Art dusty blue',(.28,.40,.45)),('Art orange light',(.63,.14,.018)),('Art copper shadow',(.13,.035,.008)),('Crystal warm ivory',(.82,.83,.77)),('Lamp warm diffuser',(.9,.84,.6))]:add_mat(name,col)

    def art(it):
        w,d,h=it['dimensions'];gold=it.get('frame_material','Gold brushed metal');edge=min(.021,w*.025,h*.025)
        cube('picture backing',(0,0,h/2),(w,max(d*.42,.012),h),'Art cream',.004)
        for x in [-w/2+edge/2,w/2-edge/2]:cube('picture frame side',(x,d*.26,h/2),(edge,max(.025,d*.8),h),gold,.003)
        for z in [edge/2,h-edge/2]:cube('picture frame edge',(0,d*.26,z),(w,max(.025,d*.8),edge),gold,.003)
        front=d*.68+.006;mode=it.get('art_palette','living')
        if mode=='orange-window':
            cube('warm window-light photograph',(0,front,h/2),(w-2.4*edge,.009,h-2.4*edge),'Art copper shadow')
            cube('orange cast light',(w*.075,front+.008,h*.54),(w*.65,.007,h*.82),'Art orange light')
            for x in [-w*.22,w*.13]:cube('window bar',(x,front+.014,h*.54),(w*.06,.005,h*.82),'Art copper shadow')
            cube('window crossbar',(w*.075,front+.015,h*.64),(w*.65,.005,h*.053),'Art copper shadow')
        else:
            colors=['Art blush','Art pale pink','Art cream','Art ochre','Art forest','Art dusty blue'] if mode=='living' else ['Art cream','Art pale pink','Art blush','Art ochre']
            patches=[(-.28,.74,.28,.16),(.04,.83,.35,.11),(.31,.69,.24,.23),(-.19,.52,.37,.19),(.13,.54,.26,.12),(.31,.41,.29,.17),(-.31,.26,.19,.23),(-.06,.28,.24,.15),(.17,.20,.28,.15),(-.30,.89,.22,.09),(.06,.68,.18,.20),(-.03,.43,.31,.07)]
            for i,(x,z,ww,hh) in enumerate(patches):
                o=cube('abstract palette patch '+str(i),(x*w,front+.0002*i,h*z),(ww*w,.0006,hh*h),colors[i%len(colors)],0);o.rotation_euler.y=math.radians((i%5-2)*9)
            for i,(x,z,rx,rz) in enumerate([(-.26,.66,.17,.09),(.26,.30,.14,.10),(.06,.75,.17,.065),(-.12,.17,.12,.07),(.10,.47,.21,.035)]):
                sphere('flat organic painted stroke '+str(i),(x*w,front+.003+i*.0002,h*z),(rx*w,.0003,rz*h),colors[(i+3)%len(colors)])
        it.setdefault('appearance_confidence','Procedural source-board palette approximation; exact selected artwork not reproduced')

    def chandelier(it):
        w,d,h=it['dimensions'];gold='Gold brushed metal';zbase=h*.27
        cyl('ceiling canopy',(0,0,h-.012),min(w,d)*.14,.025,gold)
        rod('hanging chain approximation',(0,0,h*.58),(0,0,h-.03),.009,gold)
        sphere('central brass body',(0,0,zbase),(.055,.055,.09),gold)
        for i in range(10):
            a=2*math.pi*i/10;r=(.40 if i%2==0 else .31)*min(w,d)
            points=[(0,0,zbase),(.35*r*math.cos(a),.35*r*math.sin(a),h*.31),(.7*r*math.cos(a),.7*r*math.sin(a),h*.40),(r*math.cos(a),r*math.sin(a),h*(.60 if i%2==0 else .53))]
            for p,q in zip(points,points[1:]):rod('curling brass branch',p,q,.006,gold)
            for j,t in enumerate([.58,.78,1.]):
                r2=r*t;z=h*(.35+.25*t);side=a+(1 if j%2 else -1)*.42
                end=(r2*math.cos(a)+.075*math.cos(side),r2*math.sin(a)+.075*math.sin(side),z+.055)
                rod('leaf sprig',(r2*math.cos(a),r2*math.sin(a),z),end,.004,gold)
                o=sphere('warm crystal leaf',end,(.028,.014,.056),'Crystal warm ivory');o.rotation_euler.y=.5*math.cos(side);o.rotation_euler.x=.5*math.sin(side)
            sphere('small warm bulb',points[-1],(.021,.021,.037),'Lamp warm diffuser')

    def dome_mesh(name,radius,height,base_z,material):
        verts=[];faces=[];nr=12;ns=40
        for j in range(nr+1):
            theta=(math.pi/2)*j/nr
            for i in range(ns):
                a=i*2*math.pi/ns;verts.append((radius*math.sin(theta)*math.cos(a),radius*math.sin(theta)*math.sin(a),base_z+height*math.cos(theta)))
        for j in range(nr):
            for i in range(ns):faces.append((j*ns+i,j*ns+(i+1)%ns,(j+1)*ns+(i+1)%ns,(j+1)*ns+i))
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);own(o,name,material)
        for p in me.polygons:p.use_smooth=True
        return o

    def dome_lamp(it):
        w,d,h=it['dimensions'];r=min(w,d)/2;z=h-r*.7
        cyl('black weighted disk base',(0,0,.024),r*.64,.048,'Black steel')
        rod('slim black floor-lamp stem',(0,0,.04),(0,0,z+.05),.009,'Black steel')
        dome_mesh('black dome shade',r,r*.7,z,'Black steel')
        cyl('gold dome underside',(0,0,z+.006),r*.92,.008,'Gold brushed metal')
        sphere('warm concealed bulb',(0,0,z-.012),(.02,.02,.028),'Lamp warm diffuser')

    def led_lamp(it):
        w,d,h=it['dimensions'];cyl('low black disk base',(0,0,.015),min(w,d)*.4,.03,'Black steel')
        cube('slim LED upright',(0,0,(h+.04)/2),(.018,.019,h-.04),'Black steel',.003)
        cube('warm LED strip',(0,.011,(h+.05)/2),(.008,.003,h-.055),'Lamp warm diffuser',.001)

    def cylinder_lamp(it):
        w,d,h=it['dimensions'];r=min(w,d)/2;material=it.get('material','Natural oak')
        cyl('natural bedside base',(0,0,.018),r*.67,.036,material)
        rod('thin bedside lamp stem',(0,0,.03),(0,0,h*.68),.006,'Gold brushed metal')
        cyl('tall cylindrical linen shade',(0,0,h*.73),r,h*.52,'Off white shade')
        cyl('shade top',(0,0,h-.003),r*.96,.006,'Art cream')

    def sconce(it):
        w,d,h=it['dimensions'];gold='Gold brushed metal'
        cube('sconce wall plate',(0,-d*.35,h*.3),(w*.15,.018,h*.27),gold,.01)
        rod('sconce curved support',(0,-d*.34,h*.34),(0,d*.18,h*.48),.009,gold)
        verts=[(-w/2,-d*.22,h),(-w*.32,d*.45,h*.89),(0,d*.48,h),(w*.32,d*.45,h*.89),(w/2,-d*.22,h),(-w*.12,-d*.10,h*.44),(w*.12,-d*.10,h*.44)]
        faces=[(0,1,5),(1,2,5),(2,6,5),(2,3,6),(3,4,6)]
        me=bpy.data.meshes.new('folded ivory fan shade');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('folded ivory fan shade',me);bpy.context.collection.objects.link(o);own(o,'folded ivory fan shade','Off white shade');mod=o.modifiers.new('Thin fan shade','SOLIDIFY');mod.thickness=.002

    return {'art':art,'chandelier':chandelier,'dome_lamp':dome_lamp,'led_lamp':led_lamp,'cylinder_lamp':cylinder_lamp,'sconce':sconce}
