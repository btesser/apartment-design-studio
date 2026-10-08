import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

BASE = Path('/workspace/apartment-imagegen-v3')
VIEWS = Path('/workspace/apartment-v2/room-views')
BOARDS = Path('/workspace/apartment-v2/evidence/Amy-design-boards')

def fingerprint(path):
    with Image.open(path) as im:
        size = list(im.size)
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'dimensions_px': size}

ROOMS = [
    ('basement-open', 'BASEMENT', [
        'Beam, two columns and stair mass stay on the same sides in both reverse views; kitchenette and its two high openings remain in A.',
        'Six dining chairs, cream sofa, two rust swivel chairs, black tables, shared side lamp, rug and curtain divider retain modeled arrangement and facing, allowing normal occlusion.',
        'Amy\'s warm wood, cream upholstery, rust chairs, black marble, patterned rug and dark curtains are recognizable in both angles.'
    ]),
    ('entry', 'ENTRYWAY', [
        'Console and clipped-corner mirror remain on their target wall in A; two-door cane shoe cabinet remains in its alcove in B.',
        'Neighboring living area and Her-office glimpse retain the modeled door edges and furniture sides; no added room opening found.',
        'A applies Amy\'s yellow botanical wallpaper only to the console wall as an intentional option. B keeps the cabinet wall white. Amy\'s brass/glass console, mirror and natural cane cabinet style are recognizable.'
    ]),
    ('living', 'LIVING ROOM', [
        'Black sofa remains along brick, facing the TV/media wall across the pink border rug; oval coffee table and small side table remain in their target areas.',
        'Reverse views preserve rear office door openings and the kitchen-side gap; B preserves the Her-office pink-chair/teal-table/window glimpse.',
        'Amy\'s abstract artwork, brass/white sconces, patterned pink/cream pillows, plum throw and fluted white media cabinet are recognizable.'
    ]),
    ('his-office', 'HIS OFFICE', [
        'Desk stays against the same white wall with chair facing its monitor; three shelf columns remain on the same wall, with correct dome lamp at window and slim LED lamp by shelving.',
        'A retains one visible tall window and dark rear/closet door; B retains the right-side living doorway and sofa glimpse. No extra window or doorway found.',
        'Amy\'s walnut worktop and shelves, black mesh chair, black lamps and distressed cream/black rug are coherent between both views.'
    ]),
    ('her-office', 'HER OFFICE', []),
    ('bedroom-flex', 'BEDROOM', [])
]

def build(extra_checks):
    rooms = []
    for room_id, board_name, checks in ROOMS:
        paths = [BASE / f'{room_id}-{angle}.png' for angle in 'ab']
        missing = [str(p) for p in paths if not p.exists()]
        if missing:
            raise RuntimeError('Final images missing: ' + ', '.join(missing))
        rooms.append({
            'room': room_id,
            'decision': 'PASS FOR CONCEPT VISUALIZATION',
            'generated_images': [fingerprint(p) for p in paths],
            'target_model_views': [fingerprint(VIEWS / f'{room_id}-{angle}.jpg') for angle in 'ab'],
            'amy_board': fingerprint(BOARDS / f'Lana & Ben {board_name}.jpeg'),
            'evidence_checks': checks + extra_checks.get(room_id, []),
            'major_topology_or_facing_failures_found': [],
            'residual_furniture_silhouette_drift': {
                'her-office': 'In A, vanity and mirror remain somewhat wider and shifted left from their exact target envelopes after one correction. Furniture remains on the correct wall and chair faces the vanity.',
                'bedroom-flex': 'Headboard arches and bedding remain somewhat fuller/taller in profile than their proxy envelopes after one correction; bed axis, headboard wall, nightstands and constrained foot passage remain coherent.'
            }.get(room_id)
        })
    data = {
        'reviewed_at_utc': datetime.now(timezone.utc).isoformat(),
        'reviewer': 'Independent visual QA agent',
        'scope': 'Twelve final image-generator outputs, two angles each of six designed areas, compared visually to their exact modeled target views, companion views and corresponding Amy Wu boards.',
        'method': 'Semantic visual inspection of architecture/openings, framing and apparent room proportions, furniture location/facing/quantity with genuine occlusion allowed, A/B continuity and selected design style. This is not pixel registration or metric validation of generated photographs. Precise dimensions and clearance remain properties of the separately audited 3D model.',
        'overall_decision': 'PASS FOR CONCEPT VISUALIZATION. No major room-topology or furniture-facing failure found in the final twelve images. Residual furniture-silhouette drift remains in Her-office A and bedroom headboards/bedding; these are approximate concept images, not exact geometry or dimension validation.',
        'blockers': [],
        'advisories': [
            'Final output pixels are recorded individually below. Reviewed outputs preserve approximately the target modeled-view aspect of 1.44:1. Framing and apparent proportions are close but not pixel-identical.',
            'Basement photos add ceiling/under-cabinet light strips, recessed lights and small tabletop decor as concept lighting/styling; these are not evidence of installed fixtures.',
            'Entry A intentionally shows yellow botanical wallpaper only on the console wall; entry B shows the separate white cabinet wall. Entry furniture locations remain provisional in the underlying model.',
            'The living artwork visible in entry A remains a pastel-shape interpretation of the proxy, while the dedicated living pair uses Amy\'s painterly collage. Mounted position/size agree; the exact artwork finish varies across these concept views.',
            'Some generated living/office backgrounds retain a sharp horizontal gray proxy shading band. It reads as a finish/lighting edge, not a new partition; wall finish should be selected separately.',
            'Her-office A vanity/mirror remain somewhat wider and left-shifted from their model envelopes. Bedroom headboard arches and bedding remain fuller/taller in profile than the proxies. Final images retain these residual approximations after one correction per affected image.',
            'Small decor, textile draping, wood grain, texture, trim and product detail vary between angles. Do not use generated texture details, reflections or outdoor greenery as evidence of actual site conditions.',
            'The bedroom has a modeled 0.46988m bed-foot/dresser aisle. Visual appearance cannot validate that dimension or drawer usability; keep the model/clearance note alongside the images.'
        ],
        'rooms': rooms,
        'excluded_rejected_iterations': sorted(p.name for p in BASE.glob('*-first.png'))
    }
    (BASE / 'image-QA.json').write_text(json.dumps(data, indent=2) + '\n')
    lines = [
        'INDEPENDENT VISUAL QA — FINAL IMAGE GENERATOR OUTPUTS',
        '',
        data['overall_decision'],
        '',
        data['scope'],
        data['method'],
        '',
        'ROOM PAIR FINDINGS'
    ]
    for room in rooms:
        lines.append('\n' + room['room'] + ' A/B: PASS FOR CONCEPT VISUALIZATION')
        lines.extend('- ' + s for s in room['evidence_checks'])
        if room['residual_furniture_silhouette_drift']:
            lines.append('- Residual approximation: ' + room['residual_furniture_silhouette_drift'])
    lines.extend(['', 'LIMITS AND MINOR CONSISTENCY NOTES'])
    lines.extend('- ' + s for s in data['advisories'])
    lines.extend(['', 'Rejected *-first.png iterations were excluded. JSON records exact final output/reference SHA256 fingerprints and dimensions.', ''])
    (BASE / 'image-QA.txt').write_text('\n'.join(lines))
    print(json.dumps({'rooms': len(rooms), 'images': 12, 'report': str(BASE / 'image-QA.txt'), 'blockers': 0}))

if __name__ == '__main__':
    checks = json.loads((BASE / 'final-extra-checks.json').read_text())
    build(checks)
