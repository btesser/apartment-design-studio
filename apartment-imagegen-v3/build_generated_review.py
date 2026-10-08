#!/usr/bin/env python3
"""Lay out final generated concepts beside unchanged model and Amy-board references.

No source pixels are edited. Images are scaled only for their PDF display boxes.
The exact final filenames are required; rejected *-first.png attempts are excluded.
"""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
MODELS = Path('/workspace/apartment-v2/room-views')
BOARDS = Path('/workspace/apartment-v2/evidence/Amy-design-boards')
OUTPUT = ROOT / 'Amy-design-generated-images.pdf'

ROOMS = [
    ('living', 'Living room', 'LIVING ROOM',
     'The existing sofa size is estimated. Preserve the narrow living bay and the sofa facing the media wall.'),
    ('his-office', 'His office', 'HIS OFFICE',
     'The existing desk size is estimated. Its wall, facing direction and nearby openings follow the model.'),
    ('her-office', 'Her office', 'HER OFFICE',
     'The modeled room width is 3.62 m; the listing gives 3.20 m. This approximately 13% discrepancy remains unresolved.'),
    ('bedroom-flex', 'Bedroom / flex area', 'BEDROOM',
     'The full-size dresser leaves approximately 0.47 m at the bed foot. The curtain is a movable room divider.'),
    ('basement-open', 'Basement lounge / dining', 'BASEMENT',
     'Keep the model’s lounge, dining, columns and stair positions. Finish and stair details in the concept are illustrative.'),
    ('entry', 'Entryway', 'ENTRYWAY',
     'Furniture positions are provisional. Wallpaper is an option from Amy’s board; the small entry geometry stays model-based.'),
]

INK = colors.HexColor('#243C34')
MUTED = colors.HexColor('#5A6B63')
PAPER = colors.HexColor('#F8F7F2')
RULE = colors.HexColor('#D5DBD4')
ACCENT = colors.HexColor('#A1764C')


def register_fonts():
    base = Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('ReviewSans', str(base / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('ReviewSansBold', str(base / 'DejaVuSans-Bold.ttf')))


def wrap(text, width, font='ReviewSans', size=8.6):
    words = text.split()
    lines = []
    line = ''
    for word in words:
        candidate = f'{line} {word}'.strip()
        if line and pdfmetrics.stringWidth(candidate, font, size) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def text_block(c, text, x, y, width, size=8.6, leading=12.5, color=MUTED, font='ReviewSans'):
    c.setFillColor(color)
    c.setFont(font, size)
    lines = wrap(text, width, font, size)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def fitted_image(c, path, x, y, width, height, frame=False):
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (width - dw) / 2, y + (height - dh) / 2
    if frame:
        c.setFillColor(colors.white)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.55)
        c.rect(x, y, width, height, stroke=1, fill=1)
    c.drawImage(ImageReader(str(path)), dx, dy, width=dw, height=dh, mask='auto')
    return {'source_size_px': [iw, ih], 'display_box_pt': [round(dx, 3), round(dy, 3), round(dw, 3), round(dh, 3)]}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def make_pages():
    pages = []
    for stem, title, board, caution in ROOMS:
        for angle in ('a', 'b'):
            name = f'{stem}-{angle}'
            pages.append({
                'room': stem, 'title': title, 'angle': angle.upper(),
                'generated': ROOT / f'{name}.png',
                'model': MODELS / f'{name}.jpg',
                'board': BOARDS / f'Lana & Ben {board}.jpeg',
                'caution': caution,
            })
    return pages


def source_files(pages):
    sources = []
    seen = set()
    for p in pages:
        for key in ('model', 'board'):
            path = p[key]
            if str(path) not in seen:
                sources.append(path)
                seen.add(str(path))
    return sources


def visible_caution(page):
    note = page['caution']
    if page['room'] == 'her-office' and page['angle'] == 'A':
        note += ' In this concept, the vanity and mirror remain wider and farther left than the target.'
    if page['room'] == 'bedroom-flex':
        note += ' The generated headboard and bedding profiles remain fuller than the model.'
    return note


def build(preview=False):
    register_fonts()
    pages = make_pages()
    missing = sorted({str(p[k]) for p in pages for k in ('generated', 'model', 'board') if not p[k].is_file()})
    qa_json, qa_txt = ROOT / 'image-QA.json', ROOT / 'image-QA.txt'
    if not preview and (not qa_json.is_file() or not qa_txt.is_file()):
        missing.extend(str(p) for p in (qa_json, qa_txt) if not p.is_file())
    if missing:
        raise SystemExit('Waiting for final files:\n' + '\n'.join(missing))

    # Read the final QA record before producing the review. The concise room caveats
    # remain visible on the pages; full QA is preserved in an attached text record.
    qa_data = json.loads(qa_json.read_text()) if qa_json.exists() else None
    qa_text = qa_txt.read_text() if qa_txt.exists() else None
    if qa_data is not None and not qa_text.strip():
        raise SystemExit('Final image QA text is empty.')
    if not preview and qa_data:
        if qa_data.get('blockers'):
            raise SystemExit('Final QA lists unresolved blockers.')
        checked_paths = set()
        for room in qa_data.get('rooms', []):
            refs = room.get('generated_images', []) + room.get('target_model_views', [])
            refs += [room['amy_board']] if room.get('amy_board') else []
            for ref in refs:
                path = Path(ref['path'])
                if sha256(path) != ref['sha256']:
                    raise SystemExit(f'Source changed after final image QA: {path}')
                checked_paths.add(str(path))
        required = {str(p[k]) for p in pages for k in ('generated', 'model', 'board')}
        if not required.issubset(checked_paths):
            raise SystemExit('Final QA does not cover every PDF image and reference.')

    width, height = A4
    margin = 32
    inner = width - margin * 2
    tmp = ROOT / '.generated-review-layout.pdf'
    c = canvas.Canvas(str(tmp), pagesize=A4, pageCompression=1)
    c.setTitle('Amy Wu design concepts — generated images and source references')
    c.setAuthor('Apartment design review')
    c.setSubject('Generated finish concepts with measured model references and Amy Wu design boards')
    audit = []

    for index, p in enumerate(pages, 1):
        c.setFillColor(PAPER)
        c.rect(0, 0, width, height, stroke=0, fill=1)
        c.setFillColor(ACCENT)
        c.rect(margin, height - 39, 25, 2.5, stroke=0, fill=1)
        c.setFont('ReviewSansBold', 20)
        c.setFillColor(INK)
        c.drawString(margin, height - 69, p['title'])
        c.setFont('ReviewSans', 8.1)
        c.setFillColor(MUTED)
        c.drawRightString(width - margin, height - 66, f'ANGLE {p["angle"]}  /  {index:02d} OF 12')
        c.setFont('ReviewSans', 9)
        c.drawString(margin, height - 87, 'Amy Wu proposal · Generated finish concept')

        hero = fitted_image(c, p['generated'], margin, 371, inner, 369)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.line(margin, 355, width - margin, 355)

        gap = 18
        col = (inner - gap) / 2
        bx = margin + col + gap
        c.setFont('ReviewSansBold', 9)
        c.setFillColor(INK)
        c.drawString(margin, 335, 'TARGET MODEL · SAME VIEW')
        c.drawString(bx, 335, 'AMY’S DESIGN BOARD')
        reference = fitted_image(c, p['model'], margin, 167, col, 157, frame=True)
        board = fitted_image(c, p['board'], bx, 167, col, 157, frame=True)
        c.setFont('ReviewSans', 6.8)
        c.setFillColor(MUTED)
        c.drawString(margin, 154, p['model'].name)
        c.drawString(bx, 154, p['board'].name)

        y = text_block(c, 'Concept finishes; the model controls layout. Generated images do not verify metric dimensions.', margin, 127, inner,
                       size=8.6, leading=12.3, color=INK)
        y = text_block(c, visible_caution(p), margin, y - 7, inner, size=8.4, leading=12.1)
        if y < 60:
            raise RuntimeError(f'Page note exceeds its area: {p["generated"].name}')
        c.setStrokeColor(RULE)
        c.line(margin, 49, width - margin, 49)
        c.setFont('ReviewSans', 6.9)
        c.setFillColor(MUTED)
        c.drawString(margin, 35, '8 October 2026 · Original model views and boards are attached to this PDF.')
        c.drawRightString(width - margin, 23, p['generated'].name)
        c.bookmarkPage(p['generated'].stem)
        c.addOutlineEntry(f'{p["title"]} — angle {p["angle"]}', p['generated'].stem, level=0)
        c.showPage()

        audit.append({
            'page': index, 'room': p['room'], 'angle': p['angle'],
            'generated_image': str(p['generated']), 'model_reference': str(p['model']),
            'Amy_board_reference': str(p['board']), 'generated_sha256': sha256(p['generated']),
            'model_sha256': sha256(p['model']), 'board_sha256': sha256(p['board']),
            'hero': hero, 'model_thumbnail': reference, 'board_thumbnail': board,
        })

    c.save()
    writer = PdfWriter()
    writer.append(str(tmp))
    attachments = []
    attachment_hashes = {}
    for path in source_files(pages):
        name = f'model-reference_{path.name}' if path.parent == MODELS else path.name
        writer.add_attachment(name, path.read_bytes())
        attachments.append(name)
        attachment_hashes[name] = sha256(path)
    if qa_txt.exists():
        writer.add_attachment('image-QA.txt', qa_txt.read_bytes())
        attachments.append('image-QA.txt')
        attachment_hashes['image-QA.txt'] = sha256(qa_txt)
    writer.add_metadata({
        '/Title': 'Amy Wu design concepts — generated images and source references',
        '/Author': 'Apartment design review',
        '/Subject': 'Finish concepts; model layout reference; not metric verification',
    })
    output = ROOT / '.review-layout-preview.pdf' if preview else OUTPUT
    output_tmp = ROOT / '.Amy-design-generated-images.pdf'
    with output_tmp.open('wb') as f:
        writer.write(f)
    os.replace(output_tmp, output)
    tmp.unlink()

    final = PdfReader(str(output))
    if len(final.pages) != 12:
        raise RuntimeError(f'Expected 12 pages, found {len(final.pages)}')
    if len(final.attachments) != len(attachments):
        raise RuntimeError('PDF attachment count differs from the source file list.')
    for expected in attachments:
        if expected not in final.attachments:
            raise RuntimeError(f'Missing PDF attachment: {expected}')
        if hashlib.sha256(final.attachments[expected][0]).hexdigest() != attachment_hashes[expected]:
            raise RuntimeError(f'PDF attachment differs from the original source: {expected}')
    for index, page in enumerate(final.pages):
        text = page.extract_text()
        if pages[index]['generated'].name not in text or pages[index]['model'].name not in text:
            raise RuntimeError(f'Missing source label on page {index + 1}')

    record = {
        'output': str(output), 'pages': len(final.pages),
        'built_utc': datetime.now(timezone.utc).isoformat(),
        'sha256': sha256(output), 'bytes': output.stat().st_size,
        'source_pixels_edited': False, 'image_display_scaling_only': True,
        'rejected_first_attempts_excluded': True,
        'source_attachment_count': len(attachments), 'attachments': attachments,
        'source_attachment_sha256': attachment_hashes,
        'final_QA_read': qa_json.exists() and qa_txt.exists(),
        'final_QA_decision': qa_data.get('overall_decision') if qa_data else None,
        'page_sources': audit,
    }
    if not preview:
        (ROOT / 'pdf-verification.json').write_text(json.dumps(record, indent=2))
        (ROOT / 'pdf-verification.txt').write_text(
            f'PDF: {output.name}\nPages: 12\nSource attachments: {len(attachments)}\n'
            'One final generated image per page, with target model and Amy board references below.\n'
            'Original image pixels are unchanged; PDF display uses proportional scaling without cropping.\n'
            'All attached source bytes match their original SHA-256 fingerprints.\n'
            'Rejected first attempts are excluded. Final image QA was read and attached.\n'
            'The concepts do not verify dimensions. Room-specific uncertainties remain visible on the pages.\n'
            f'SHA-256: {record["sha256"]}\n'
        )
    print(json.dumps({k: record[k] for k in ('output', 'pages', 'bytes', 'source_attachment_count', 'sha256')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Build a hidden layout preview without final QA; not for delivery.')
    args = parser.parse_args()
    build(preview=args.preview)
