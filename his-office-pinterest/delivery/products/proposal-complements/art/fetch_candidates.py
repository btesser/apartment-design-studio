"""Official retailer evidence for additive art proposals only."""
import concurrent.futures
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
ROOT.mkdir(parents=True, exist_ok=True)
PAGES = {
    'abstract-no1': 'https://desenio.com/p/posters-prints/art-prints/abstract-no1-print/',
    'grey-graphics-no2': 'https://desenio.com/p/posters-prints/art-prints/abstract-art/grey-graphics-no2-print/',
    'black-brush-strokes-no1': 'https://desenio.com/p/posters-prints/art-prints/abstract-art/black-brush-strokes-no1-print/',
    'contemporary-abstract-no1': 'https://desenio.com/p/posters-prints/art-prints/contemporary-abstract-no1-print/',
    'abstract-graphic-no1': 'https://desenio.com/p/posters-prints/art-prints/abstract-graphic-no1-print/',
    'black-abstract-shapes-no1': 'https://desenio.com/p/posters-prints/art-prints/abstract-art/black-abstract-shapes-no1-print/',
    'monochrome-waves': 'https://desenio.com/p/posters-prints/art-prints/monochrome-waves-print/',
}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=35) as response:
        return response.read()

def fetch(pair):
    key, url = pair
    try:
        raw = get(url)
        (ROOT / (key + '-source.html')).write_bytes(raw)
        html = raw.decode()
        script = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        data = json.loads(script.group(1))['props']['pageProps']
        page = data['payload']['page']
        result = {'id': key, 'source_url': url, 'currency': data['commerce']['currencyCode'],
                  'title': page['title'], 'description_html': page['description'],
                  'available_combinations': [{k: c.get(k) for k in ['id', 'size', 'sizeTitle', 'articleNumber', 'stock', 'price', 'campaignPrice', 'images']} for c in page['combinations']]}
        candidates = [c for c in page['combinations'] if c.get('size') == '70x100' and c.get('stock', 0) > 0]
        if candidates:
            c = candidates[0]
            photo = next((im for im in c.get('images', []) if im.get('systemCode') == 'variant_main_image'), None)
            if photo:
                image_url = 'https://media.desenio.com/site_images/' + photo['URL']
                pixels = get(image_url)
                file = ROOT / (key + '-70x100-official.jpg')
                file.write_bytes(pixels)
                im = Image.open(io.BytesIO(pixels))
                result['selected_70x100'] = {**c, 'image_url': image_url, 'image_file': str(file), 'image_sha256': hashlib.sha256(pixels).hexdigest(), 'actual_image_dimensions': list(im.size), 'pixels_edited': False}
        (ROOT / (key + '-evidence.json')).write_text(json.dumps(result, indent=2))
        return result
    except Exception as error:
        return {'id': key, 'source_url': url, 'error': repr(error)}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(fetch, PAGES.items()))
(ROOT / 'art-discovery-evidence.json').write_text(json.dumps(results, indent=2))
for result in results:
    print(json.dumps({'id': result['id'], 'title': result.get('title'), 'error': result.get('error'),
                      'available_sizes': [(c['size'], c['stock']) for c in result.get('available_combinations', [])],
                      'selected': {k: v for k, v in result.get('selected_70x100', {}).items() if k in ['articleNumber', 'id', 'size', 'price', 'campaignPrice', 'stock', 'actual_image_dimensions', 'image_file']}}))
