from pathlib import Path
import hashlib, json, shutil, zipfile
from datetime import datetime, timezone
from PIL import Image
import fitz

root = Path('/workspace/apartment-imagegen-v3')
source = Path('/workspace/apartment-v2')
rooms = [('living','LIVING ROOM','Living room'), ('his-office','HIS OFFICE','His office'), ('her-office','HER OFFICE','Her office'), ('bedroom-flex','BEDROOM','Bedroom / flex area'), ('basement-open','BASEMENT','Basement living / dining'), ('entry','ENTRYWAY','Entry')]
refs = root / 'references'
(refs / 'modeled-views').mkdir(parents=True, exist_ok=True)
(refs / 'Amy-design-boards').mkdir(parents=True, exist_ok=True)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

images = []
for key, board, name in rooms:
    board_src = source / 'evidence/Amy-design-boards' / f'Lana & Ben {board}.jpeg'
    board_dst = refs / 'Amy-design-boards' / board_src.name
    shutil.copy2(board_src, board_dst)
    for angle in 'ab':
        shutil.copy2(source / 'room-views' / f'{key}-{angle}.jpg', refs / 'modeled-views' / f'{key}-{angle}.jpg')
    for angle in 'ab':
        out = root / f'{key}-{angle}.png'
        assert out.exists(), f'Missing image: {out}'
        with Image.open(out) as im:
            im.verify()
        with Image.open(out) as im:
            size = list(im.size)
        ordered_refs = [refs / 'modeled-views' / f'{key}-{angle}.jpg', refs / 'modeled-views' / f"{key}-{'b' if angle=='a' else 'a'}.jpg", board_dst]
        images.append({'room':key,'room_label':name,'angle':angle,'file':out.name,'pixels':size,'sha256':digest(out),'generation_method':'Image generation edit with target model camera, opposite model camera, and Amy Wu design board','reference_order':[{'file':str(p.relative_to(root)),'sha256':digest(p)} for p in ordered_refs]})

pdf = root / 'Amy-design-generated-images.pdf'
assert pdf.exists(), 'Missing review PDF'
with fitz.open(pdf) as doc:
    assert len(doc)==12, f'Expected 12 pages, got{len(doc)}'

qa = root / 'image-QA.json'
assert qa.exists(), 'Missing final independent visual QA'
json.loads(qa.read_text())
notes = '''12 generated concept images: two angles for each of the six areas covered by Amy Wu's design mockups.

Start with Amy-design-generated-images.pdf. Each page shows one generated image with its modeled camera and Amy board. Individual full-resolution PNGs are in this folder.

Reference priority: the final scan-registered 3D model controls room geometry, camera, openings, furniture placement and orientation. Amy's boards control materials, colors, finishes and furniture appearance. Both modeled camera angles were supplied to every image-generation call. Reference files and exact generation prompts are included.

These are generated concept images. Independent review checks visible layout and orientation, not measured dimensional accuracy. Use the existing dimensioned 3D model and plans for physical fit. The image generator may add finish details, decorative accessories and conceptual lighting. Artwork or textiles can vary between generated angles. Her office vanity/mirror appear somewhat wider or shifted in the generated image; bedroom headboard and bedding profiles remain fuller than the model after correction. These approximations are disclosed in image-QA.txt; retain the modeled envelopes for fit decisions.

Entry: yellow botanical wallpaper is an option from Amy's board, not a confirmed finish selection. Entry furniture placement remains provisional. The opposite shoe-cabinet wall stays white.
Bedroom: the full-size proposed dresser leaves about 0.47 m at the bed foot; this model limitation remains. Divider placement/height is provisional.
Her office: the scan width differs from the approximate listing by about 13%; verify with physical measurement. Loveseat clearance at the hearth is tight.
Existing living sofa and standing desk dimensions remain estimates. Other unrecorded areas and source uncertainties retain the labels in the original model package.

This image package accompanies the previously delivered apartment-design-v2.zip and apartment-walkthrough.html; it does not replace or modify the editable 3D model.
'''
(root/'START-HERE.txt').write_text(notes)
provenance = {'created_utc':datetime.now(timezone.utc).isoformat(),'image_count':12,'room_count':6,'angles_per_room':2,'model_authority_file':'/workspace/apartment-v2/models/apartment-design.glb','model_authority_sha256':digest(source/'models/apartment-design.glb'),'source_dimensions':[1440,1000],'note':'Generated image aspect ratios may differ slightly from source. Images are concept finish visualizations; visual review is not metric validation.','images':images}
(root/'generation-provenance.json').write_text(json.dumps(provenance,indent=2))

named = ['Amy-design-generated-images.pdf','START-HERE.txt','generation-provenance.json','image-QA.json','image-QA.txt','geometry-reference-findings.json','geometry-reference-findings.txt','root-generation-prompts.json','root-generation-record.json','living-his-office-prompts.json','office-bedroom-prompts-final.json','office-bedroom-generation-record.json']
files = [root/f'{key}-{angle}.png' for key,_,_ in rooms for angle in 'ab'] + [root/n for n in named] + sorted(refs.rglob('*'))
files = [p for p in files if p.is_file()]
assert all((root/n).exists() for n in named), 'Missing required report/prompt file'
inventory = [{'file':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files]
(root/'FILE-INVENTORY.json').write_text(json.dumps(inventory,indent=2))
files.append(root/'FILE-INVENTORY.json')
archive = Path('/workspace/apartment-imagegen-v3.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:
        z.write(p,Path('apartment-imagegen-v3')/p.relative_to(root))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(files)
print(json.dumps({'status':'PASS','images':12,'rooms':6,'pdf_pages':12,'archive':str(archive),'archive_bytes':archive.stat().st_size,'files':len(files)}))
