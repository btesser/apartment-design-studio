"""Photo/spec-guided owned Mineral Aeron Size C proxy, native metres.

Creates geometry only when add_aeron is called by the authorized builder.
No scene loading/saving, export, image edits, CAD conversion or Branch reuse.
Detailed forms, current-reference options and the displayed height are disclosed
approximations; this is not a supplier CAD model of the actual owned chair.
"""
import hashlib
import json
import math
from pathlib import Path

PHOTO = Path('/workspace/his-office-pinterest/products/owned-chair/aeron-c-mineral-official.png')
RECORD = Path('/workspace/his-office-pinterest/products/owned-chair/owned-aeron-size-c-mineral.json')
PHOTO_SHA = '78123f016902ee3f54551e45813605fe8059878516782dac88858835291902ec'
W = D = .71882
H = 1.0922
SEAT_H = .45
SEAT_DEPTH = .4699
ARM_TOP = SEAT_H + .1905
BASE_DIAMETER = .6731
CASTER_DIAMETER = .0635


def add_aeron(bpy, collection, spec):
    """Return a furniture EMPTY with locally modelled meshes; front is +Y.

    spec may supply id, position_blender_m, rotation_z_deg and provenance.
    Nominal display envelope is W/D718.82mm,H1092.2mm. Maximum802.64mm
    expanded-arm operation width is metadata, never applied to this normal pose.
    """
    from mathutils import Vector, Matrix
    if PHOTO.exists() and hashlib.sha256(PHOTO.read_bytes()).hexdigest() != PHOTO_SHA:
        raise ValueError('Owned Aeron reference photo hash changed')
    rid = spec.get('id', 'aeron-primary')
    root = bpy.data.objects.new(rid, None)
    collection.objects.link(root)
    root.location = spec.get('position_blender_m', [-6.82, -.85, 1.575])
    root.rotation_euler.z = math.radians(spec.get('rotation_z_deg', 0))
    root['role'] = 'furniture'
    root['canonical_layout_id'] = rid
    root['product_id'] = 'aeron-size-c-mineral'
    root['product_name'] = 'Owned Herman Miller Aeron Large / Size C, Mineral light gray'
    root['product_url'] = 'https://www.hermanmiller.com/products/seating/office-chairs/aeron-chair/specs/'
    root['external_dimensions_m'] = [W, D, H]
    root['front_vector_blender'] = [0., 1., 0.]
    root['proxy_form'] = 'Photo/spec-guided normal-width proxy; detailed geometry approximate, not vendor CAD'
    root['dimension_confidence'] = 'Current manufacturer Size C normal width/depth; illustrative43in display height independent of chosen seat pose'
    root['dimension_source'] = str(RECORD)
    root['source_photo'] = str(PHOTO)
    root['source_photo_sha256'] = PHOTO_SHA
    root['seat_height_m'] = SEAT_H
    root['seat_depth_m'] = SEAT_DEPTH
    root['arm_height_above_seat_m'] = .1905
    root['arm_top_above_floor_m'] = ARM_TOP
    root['base_diameter_m'] = BASE_DIAMETER
    root['caster_diameter_m'] = CASTER_DIAMETER
    root['expanded_arm_operation_envelope_m'] = [.80264, D]
    root['owned_options_status'] = 'Owned model/Size C/Mineral confirmed; Classic/Remastered vintage, base polish, arms/back/casters/cylinder options unconfirmed'
    root['reference_finish_status'] = 'Mineral frame/mesh and satin-aluminum five-spoke current-photo reference; not proof of actual owned base/options'
    root['pose_status'] = 'Seat450mm and lowest published190.5mm arm rise are illustrative settings within ranges; total1092.2mm height is a separate display assumption'
    root['mesh_status'] = 'Actual open woven strip geometry, no opaque slab back/seat; thread pitch and detailed ergonomic profiles approximate'
    parts = []

    def linear(c):
        return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4

    def mat(label, srgb, rough=.6, metal=0.):
        m = bpy.data.materials.new(rid + ' :: ' + label)
        m.use_nodes = True
        rgba = tuple(linear(c) for c in srgb) + (1.,)
        m.diffuse_color = rgba
        p = m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value = rgba
        p.inputs['Roughness'].default_value = rough
        p.inputs['Metallic'].default_value = metal
        m.use_backface_culling = False
        return m

    mineral = mat('Mineral light gray sculpted frame', (.76, .775, .76), .57)
    thread = mat('Mineral fine open Pellicle weave proxy', (.68, .70, .685), .84)
    arm = mat('Mineral gray arm pads reference', (.60, .625, .61), .82)
    base = mat('Satin aluminum Mineral reference base', (.65, .67, .65), .43, .55)
    mechanism = mat('Gray underseat mechanism', (.32, .34, .32), .58)
    wheel = mat('Dark gray caster tire', (.12, .135, .125), .87)
    stem = mat('Cylinder satin metal', (.55, .575, .56), .3, .75)

    def mesh(label, vertices, faces, material, smooth=True):
        data = bpy.data.meshes.new(rid + ' :: ' + label)
        data.from_pydata(vertices, [], faces)
        data.update()
        obj = bpy.data.objects.new(rid + ' :: ' + label, data)
        collection.objects.link(obj)
        obj.parent = root
        data.materials.append(material)
        for poly in data.polygons:
            poly.use_smooth = smooth
        parts.append(obj)
        return obj

    def tube(label, points, radius, material, sides=10, closed=False):
        """Small round/elliptic rods following sculpted paths, all local metres."""
        pts = [Vector(p) for p in points]
        verts, faces = [], []
        for i, p in enumerate(pts):
            previous = pts[(i - 1) % len(pts)] if closed or i else p
            following = pts[(i + 1) % len(pts)] if closed or i < len(pts)-1 else p
            tangent = (following - previous).normalized()
            seed = Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((0, 1, 0))
            side = tangent.cross(seed).normalized()
            up = tangent.cross(side).normalized()
            r = radius[i] if isinstance(radius, list) else radius
            rx, ry = r if isinstance(r, tuple) else (r, r)
            for j in range(sides):
                a = 2 * math.pi * j / sides
                verts.append(tuple(p + side * (rx*math.cos(a)) + up * (ry*math.sin(a))))
        links = len(pts) if closed else len(pts)-1
        for i in range(links):
            for j in range(sides):
                faces.append((i*sides+j, i*sides+(j+1)%sides,
                              ((i+1)%len(pts))*sides+(j+1)%sides,
                              ((i+1)%len(pts))*sides+j))
        if not closed:
            faces += [tuple(range(sides-1,-1,-1)),
                      tuple((len(pts)-1)*sides+j for j in range(sides))]
        return mesh(label, verts, faces, material)

    def ellipsoid(label, center, radii, material, rings=14, sides=32):
        vertices, faces = [], []
        for i in range(rings+1):
            phi = math.pi*i/rings
            for j in range(sides):
                a = 2*math.pi*j/sides
                vertices.append((center[0]+radii[0]*math.sin(phi)*math.cos(a),
                                 center[1]+radii[1]*math.sin(phi)*math.sin(a),
                                 center[2]+radii[2]*math.cos(phi)))
        for i in range(rings):
            for j in range(sides):
                faces.append((i*sides+j,i*sides+(j+1)%sides,
                              (i+1)*sides+(j+1)%sides,(i+1)*sides+j))
        return mesh(label, vertices, faces, material)

    # Five sculpted metal spokes; the stated base circle concerns the base,
    # while casters extend into the normal overall chair depth.
    caster_r = CASTER_DIAMETER/2
    radial = D/2-caster_r
    for k in range(5):
        a = math.pi/2 + 2*math.pi*k/5
        v = Vector((math.cos(a), math.sin(a), 0))
        t = Vector((-math.sin(a), math.cos(a), 0))
        tube('five-star spoke '+str(k+1),[(0,0,.142),tuple(v*.17+Vector((0,0,.134))),
             tuple(v*radial+Vector((0,0,.083)))],[.029,.023,.00889],base,12)
        c = v*radial+Vector((0,0,caster_r))
        for pair in (-1,1):
            wc = c+t*(pair*.012)
            tube('caster '+str(k+1)+' wheel '+str(pair),
                 [tuple(wc-t*.008),tuple(wc+t*.008)],caster_r,wheel,24)
        tube('caster '+str(k+1)+' swivel',
             [tuple(v*radial+Vector((0,0,.052))),tuple(v*radial+Vector((0,0,.092)))],.00889,base,12)
    tube('base hub',[(0,0,.065),(0,0,.185)],.041,base,32)
    tube('gas lift cylinder',[(0,0,.17),(0,0,.359)],.022,stem,32)
    ellipsoid('tilt mechanism housing',(0,-.03,.366),(.145,.12,.05),mechanism)
    tube('underseat cross support',[(-.22,-.06,.407),(0,-.09,.396),(.22,-.06,.407)],.022,mechanism,14)
    tube('right tilt control stem',[(.1,.015,.35),(.198,.015,.35)],.011,mechanism,12)
    ellipsoid('tilt control knob',(.204,.015,.35),(.02,.023,.023),mineral)

    # Rounded rectangular/oval open rims mimic the source shell. The back is
    # tapered, gently reclined, and curved through the lumbar region.
    signed = lambda x: math.copysign(abs(x)**.5,x)
    outer_center = (.55+H-.015)/2
    outer_half = (H-.015-.55)/2
    def back(u,v):
        z = .808 + .247*v
        x = .250*(1+.06*v-.025*v*v)*u
        y = -.255-.08941*v+.032*math.exp(-((v+.25)/.5)**2)-.01*u*u
        return x,y,z
    rim=[]
    for k in range(128):
        a = 2*math.pi*k/128
        u,v = signed(math.cos(a)),signed(math.sin(a))
        x = .274*(1+.05*v-.02*v*v)*u
        y = -.255-.08941*v+.032*math.exp(-((v+.25)/.5)**2)-.01*u*u
        if k==32:y=-.34441
        rim.append((x,y,outer_center+outer_half*v))
    tube('sculpted open oval back perimeter',rim,.015,mineral,12,True)
    seat_rim=[]
    for k in range(128):
        a=2*math.pi*k/128;u,v=signed(math.cos(a)),signed(math.sin(a))
        seat_rim.append((.272*u,.015+(.23495-.013)*v,
                         SEAT_H+.010+.008*u*u-.018*max(v,0)))
    tube('sculpted open seat perimeter',seat_rim,.013,mineral,12,True)
    def seat(u,v):
        return .245*u,.015+.207*v,SEAT_H+.008*u*u-.008*max(v,0)

    def weave(label, surface, nx, ny, du, dv):
        verts, faces = [], []
        def patch(corners):
            if any(abs(u)**4+abs(v)**4>.95 for u,v in corners):return
            start=len(verts);verts.extend(surface(u,v) for u,v in corners)
            faces.append((start,start+1,start+2,start+3))
        # Fine vertical ribs plus fine cross threads leave real open holes.
        for i in range(-nx,nx+1):
            u=i/nx
            for j in range(-ny,ny):
                v0,v1=j/ny,(j+1)/ny
                patch([(u-du,v0),(u+du,v0),(u+du,v1),(u-du,v1)])
        for j in range(-ny,ny+1):
            v=j/ny
            for i in range(-nx,nx):
                u0,u1=i/nx,(i+1)/nx
                patch([(u0,v-dv),(u1,v-dv),(u1,v+dv),(u0,v+dv)])
        return mesh(label,verts,faces,thread,False)
    weave('fine open curved back weave',back,54,62,.0019,.00125)
    weave('fine open suspended seat weave',seat,52,46,.0019,.0016)

    # Rear carrier/lumbar detail remains behind the mesh rather than replacing
    # it with an opaque panel. Current photo support option is a reference.
    tube('rear central back carrier',[(0,-.19,.415),(0,-.223,.57),(0,-.30,.76)],.014,mineral,12)
    tube('reference lumbar support',[(-.18,-.25,.665),(0,-.277,.68),(.18,-.25,.665)],.014,mineral,12)
    for s in (-1,1):
        tube('seat hinge and back carrier '+str(s),[(s*.245,-.06,.414),(s*.259,-.16,.47),
             (s*.245,-.193,.575)],.019,mineral,12)
        ellipsoid('seat pivot cap '+str(s),(s*.265,-.1,.455),(.015,.032,.032),base)
        tube('adjustable arm support '+str(s),[(s*.245,-.095,.43),(s*.268,-.13,.55),
             (s*.29641,-.067,.599)],.021,mineral,14)
        # Arm cap outer edge defines the normal 718.82mm width, not max arms.
        ellipsoid('gray arm pad '+str(s),(s*.29641,.025,ARM_TOP-.019),(.063,.136,.019),arm)

    # Exact generated bounds, evaluated directly from native local vertices;
    # no scene execution/save/export is performed by this module at import.
    local=[v.co.copy() for o in parts for v in o.data.vertices]
    lo=[min(p[i] for p in local) for i in range(3)]
    hi=[max(p[i] for p in local) for i in range(3)]
    matrix=Matrix.Translation(root.location)@root.rotation_euler.to_matrix().to_4x4()
    world=[matrix@p for p in local]
    root['generated_bbox_local_m_json']=json.dumps([lo,hi])
    root['generated_dimensions_m']=[hi[i]-lo[i] for i in range(3)]
    root['generated_bbox_world_m_json']=json.dumps([[min(p[i] for p in world) for i in range(3)],
                                                  [max(p[i] for p in world) for i in range(3)]])
    root['generated_mesh_count']=len(parts)
    root['geometry_limits']='Native-meter detailed-shape proxy. Nominal product envelope retained as metadata; exact generated bbox separately recorded. Published ranges do not establish actual owned adjustment settings or option/vintage.'
    root['source_images_modified']=False
    root['reuse_of_Branch_geometry']=False
    return root
