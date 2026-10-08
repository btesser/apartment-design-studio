import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union

ROOT = Path('/workspace/his-office-redesign')

def file_info(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def nominal_obstacles(layout, features, secondary_y=None):
    out = []
    for item in layout['items']:
        x, y, z = item['position_blender_m']
        w, d, h = item['external_dimensions_m']
        kind = item['kind']
        if kind in ['rug', 'art', 'closet_shoe_rack', 'kept_lamp']:
            continue
        if item['id'] == 'branch-secondary' and secondary_y is not None:
            y = secondary_y
        if kind == 'task_chair':
            shape = Point(x, y).buffer(item['rolling_base_diameter_m'] / 2, quad_segs=64)
        else:
            shape = box(x-w/2, y-d/2, x+w/2, y+d/2)
        out.append((item['id'], shape))
    for feature in features:
        if feature['id'] in ['rear-radiator', 'closed-fireplace', 'rear-pipe']:
            a = feature.get('hearth_keepout_xy') or feature['bounds_blender_xyz_m'][:4]
            out.append((feature['id'], box(a[0], a[2], a[1], a[3])))
    return out

def check(room, obstacles, radius):
    free = room.buffer(-radius).difference(unary_union([shape.buffer(radius, quad_segs=64) for _, shape in obstacles]))
    polys = list(free.geoms) if hasattr(free, 'geoms') else [free]
    def component(point):
        return next((i for i, p in enumerate(polys) if p.covers(Point(point))), None)
    a = component((-3.4, -2.1))
    b = component((-7.3, -1.9))
    return {
        'assumed_person_diameter_m': radius * 2,
        'entry_component': a,
        'rear_component': b,
        'continuous_nominal_route': a is not None and a == b,
        'free_component_areas_m2': [float(p.area) for p in polys]
    }

def run():
    lp = ROOT / 'model/layout.json'
    rp = ROOT / 'geometry/room-measurements.json'
    fp = ROOT / 'geometry/fixed-features.json'
    layout = json.loads(lp.read_text())
    room = Polygon(json.loads(rp.read_text())['outline_blender_xy_m'])
    features = json.loads(fp.read_text())['features']
    variants = []
    for label, pullback in [('current_canonical_working', 0), ('both_task_chairs_pulled_back_0_45m', .45)]:
        scenario = json.loads(json.dumps(layout))
        for item in scenario['items']:
            if item['kind'] == 'task_chair':
                item['position_blender_m'][1] -= pullback
        obstacles = nominal_obstacles(scenario, features)
        variants.append({'variant': label, 'chair_backward_translation_m': pullback, 'chair_positions_blender_m': {i['id']: i['position_blender_m'] for i in scenario['items'] if i['kind']=='task_chair'}, 'checks': [check(room, obstacles, r) for r in [.20, .225, .25, .275, .30]]})
    result = {
        'inputs': [file_info(p) for p in [lp, rp, fp]],
        'method': 'Continuous polygon free-space connectivity with conservative furniture envelopes and exact nominal caster circles expanded by a planning person circle. Door leaves assumed open for passage. Entry point[-3.4,-2.1],rear point[-7.3,-1.9].',
        'scope': 'Independent nominal circulation planning. This is not measured shoulder width, access-code verification, ergonomics certification or a guarantee of real installed clearance.',
        'limits': ['Room outline generalized with5-12cm uncertainty.', 'Boxes conservatively fill empty spaces in visitor-chair/desk shapes. Actual component geometry may permit more space; person sizes are scenario assumptions.', 'Cat-tree upper branches and lamp upper panel require separate part-height review; this floor routing uses the confirmed cat base only. Lamp base is omitted here because its dimensions are unverified; it lies away from identified visitor/secondary-chair bottleneck.', 'Door swings are inferred from observed closed leaves. This route presumes door leaves open and available.'],
        'variants': variants
    }
    (ROOT / 'qa/routing-analysis.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'proof': str(ROOT / 'qa/routing-analysis.json'), 'working_50cm_route': variants[0]['checks'][2]['continuous_nominal_route'], 'pulled_back_50cm_route': variants[1]['checks'][2]['continuous_nominal_route'], 'working_55cm_route': variants[0]['checks'][3]['continuous_nominal_route']}))

if __name__ == '__main__':
    run()
