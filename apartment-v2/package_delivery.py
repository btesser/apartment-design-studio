from pathlib import Path
import shutil, json, hashlib, zipfile

ROOT = Path('/workspace/apartment-v2')

def copy(source, target):
    source = Path(source); target = ROOT/target
    if not source.is_file(): raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

copy('/workspace/apartment-walkthrough.html', 'apartment-walkthrough.html')
copy('/workspace/apartment-walkthrough-source.zip', 'viewer-source.zip')
copy('/workspace/apartment-model/integrated.blend', 'models/apartment-design.blend')
copy('/workspace/apartment-model/integrated-apartment.glb', 'models/apartment-design.glb')

for s,t in [
    ('/workspace/apartment-model/architectural-shell.glb','architecture.glb'),
    ('/workspace/apartment-model/repair-shell.glb','inferred-surface-repairs.glb'),
    ('/workspace/apartment-model/observed-fixtures.glb','existing-fixtures.glb'),
    ('/workspace/apartment-model/inferred-utility-shell.glb','inferred-utility-interiors.glb'),
    ('/workspace/apartment-furniture/furniture.glb','furniture.glb'),
    ('/workspace/apartment-furniture/proposed-dresser.glb','proposed-dresser.glb'),
    ('/workspace/design-fidelity/entry-design.glb','provisional-entry.glb'),
]: copy(s, 'models/layers/'+t)

for name in ['upper-dimensioned-plan.png','lower-dimensioned-plan.png','amy_scan_registration.png']:
    copy('/workspace/geometry-audit/'+name,name)

for source in ['/workspace/geometry-audit/geometry.json',
               '/workspace/geometry-audit/registration-findings.json',
               '/workspace/geometry-audit/amy_affine_registration.json',
               '/workspace/geometry-audit/audit-report.txt',
               '/workspace/geometry-audit/fireplace-anchors.json',
               '/workspace/geometry-audit/her-hearth-polygon.json',
               '/workspace/geometry-audit/surface_plane_fits.json',
               '/workspace/apartment-model/repair-log.json',
               '/workspace/apartment-model/model-metadata.json',
               '/workspace/apartment-model/fixture-confidence.json',
               '/workspace/apartment-model/MODEL-REPAIR-REPORT.txt',
               '/workspace/apartment-furniture/furniture-manifest.json',
               '/workspace/apartment-furniture/validation.json',
               '/workspace/apartment-furniture/FURNITURE-NOTES.txt',
               '/workspace/design-fidelity/entry-manifest.json',
               '/workspace/design-fidelity/fidelity-checklist.json',
               '/workspace/source-evidence/product-dimensions.json',
               '/workspace/source-evidence/shopping-items.json',
               '/workspace/source-evidence/listing-floorplan.jpg',
               '/workspace/apartment-walkthrough/tests/standalone-results.json',
               '/workspace/apartment-walkthrough/assets/source-hashes.json',
               '/workspace/independent-qa/final-keyboard-proof.json',
               '/workspace/independent-qa/vertical-grounding.json',
               '/workspace/independent-qa/integrated-inventory.json',
               '/workspace/independent-qa/layer-hashes.json',
               '/workspace/independent-qa/door-approaches.json',
               '/workspace/independent-qa/stair-roundtrip.json',
               '/workspace/independent-qa/hearth-actual-geometry.json',
               '/workspace/independent-qa/artifact-checks.json',
               '/workspace/independent-qa/source-wall-measurements.json']:
    copy(source,'evidence/'+Path(source).name)

for p in Path('/workspace/apartment-design/designer-boards').iterdir():
    if p.suffix.lower() in ['.jpeg','.png','.jpg']:
        copy(p,'evidence/Amy-design-boards/'+p.name)

# Only final deterministic views are included; earlier generative outputs and
# development previews are deliberately outside the revised deliverable.
room_boards = {
    'living':'Lana & Ben LIVING ROOM.jpeg',
    'his-office':'Lana & Ben HIS OFFICE.jpeg',
    'her-office':'Lana & Ben HER OFFICE.jpeg',
    'entry':'Lana & Ben ENTRYWAY.jpeg',
    'bedroom-flex':'Lana & Ben BEDROOM.jpeg',
    'basement-open':'Lana & Ben BASEMENT.jpeg',
    'music-gym':None, 'kitchen':None, 'bathroom':None,
}
briefs=[]
for room,board in room_boards.items():
    for angle in ['a','b']:
        name=room+'-'+angle+'.jpg'
        copy('/workspace/apartment-model/renders/'+name,'room-views/'+name)
    briefs.append({
        'room':room,
        'geometry_references':['room-views/'+room+'-'+a+'.jpg' for a in ['a','b']],
        'designer_reference':'evidence/Amy-design-boards/'+board if board else None,
        'instruction':'Use the two fixed 3D views together for room geometry and furniture orientation. Preserve doors, windows, columns, floor height, wall positions, product footprints and camera perspective. Use the designer board only for material and decorative appearance. Do not infer alternative architecture from a mood board. Any furniture dimensions marked estimated remain unconfirmed.',
        'geometry_authority':'models/apartment-design.glb and evidence/geometry.json',
        'furniture_authority':'evidence/furniture-manifest.json',
    })

(ROOT/'image-generator-reference-briefs.json').write_text(json.dumps(briefs,indent=2))

for name in ['stairs-a.jpg','upper-plan.jpg','lower-plan.jpg']:
    source = Path('/workspace/apartment-model/renders')/name
    if source.exists(): copy(source,'room-views/'+name)

camera_candidates = [Path('/workspace/apartment-model/camera-poses.json'),Path('/workspace/apartment-model/render-cameras.json'),Path('/workspace/apartment-model/renders/camera-poses.json')]
cams = next((p for p in camera_candidates if p.exists()),None)
if not cams: raise FileNotFoundError('Final deterministic camera pose catalog is missing')
copy(cams, 'evidence/camera-poses.json')
catalog_path=ROOT/'evidence/camera-poses.json'
catalog=json.loads(catalog_path.read_text())
for camera in catalog.get('cameras',[]):
    camera['source_filename']=camera.get('filename')
    camera['filename']=camera.get('filename','').replace('renders/','room-views/',1)
    camera['source_scene']=camera.get('scene')
    camera['scene']='models/apartment-design.blend'
catalog['package_note']='Camera poses and optics are unchanged. Image and scene paths are mapped to this download; original source names are retained.'
catalog_path.write_text(json.dumps(catalog,indent=2))

qa = Path('/workspace/independent-qa/QA-REPORT.txt')
if not qa.exists(): raise FileNotFoundError('Final independent QA report is missing')
copy(qa,'QA-REPORT.txt')

# Archive itself and development scripts are omitted from its inventory.
files=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name not in ['build_review.py','package_delivery.py','FILE-INVENTORY.json']:
        files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'FILE-INVENTORY.json').write_text(json.dumps(files,indent=2))
archive = Path('/workspace/apartment-design-v2.zip')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and p.name not in ['build_review.py','package_delivery.py']:
            z.write(p, 'apartment-design-v2/'+str(p.relative_to(ROOT)))
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(files),'room_pairs':len(room_boards)}))
