import urllib.request,json,re,pathlib,concurrent.futures,html
ROOT=pathlib.Path('/workspace/his-office-redesign/products/candidates');(ROOT/'official-images').mkdir(exist_ok=True);(ROOT/'source-pages').mkdir(exist_ok=True)
PAGES={
'lagkapten-alex-double':'https://www.ikea.com/us/en/p/lagkapten-alex-desk-black-brown-white-s09432189/',
'lagkapten-alex-single':'https://www.ikea.com/us/en/p/lagkapten-alex-desk-black-brown-white-s59432163/',
'alex-drawers':'https://www.ikea.com/us/en/p/alex-drawer-unit-white-00473546/',
'storklinta-low-drawers':'https://www.ikea.com/us/en/p/storklinta-3-drawer-dresser-oak-effect-anchor-unlock-function-80559292/',
'bissa-shoes':'https://www.ikea.com/us/en/p/bissa-shoe-cabinet-with-2-compartments-black-brown-20530206/',
'ekenaset-turquoise':'https://www.ikea.com/us/en/p/ekenaeset-armchair-kelinge-gray-turquoise-90533485/',
'ekenaset-beige':'https://www.ikea.com/us/en/p/ekenaeset-armchair-kilanda-light-beige-30533493/',
'branch-pro':'https://www.branchfurniture.com/products/ergonomic-chair-pro',
'branch-verve':'https://www.branchfurniture.com/products/verve-chair',
'ruggable-inkdrop':'https://ruggable.com/products/jonathan-adler-inkdrop-slate-blue-rug',
'rug-christie':'https://www.rugsusa.com/products/christie-washable-modern-rug-charcoal',
'art-blue-geometric':'https://desenio.com/p/posters-prints/art-prints/graphical/blue-geometric-print/',
'art-blue-bold':'https://desenio.com/p/posters-prints/art-prints/abstract-art/bold-blue-print/',
'article-otio':'https://www.article.com/product/22021/otio-26-lounge-chair-walnut-and-welsh-taupe',
}
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/xhtml+xml,image/avif,image/webp,*/*'})
 with urllib.request.urlopen(req,timeout=30) as r:return r.read(),r.status,r.headers.get('content-type','')
def one(it):
 k,url=it;result={'id':k,'source_url':url}
 try:
  data,status,ct=get(url);p=ROOT/'source-pages'/f'{k}.html';p.write_bytes(data);s=data.decode('utf8','replace');result.update(status=status,html_file=str(p),bytes=len(data))
  ld=[]
  for raw in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',s,re.S|re.I):
   try:ld.append(json.loads(raw))
   except:pass
  result['json_ld']=ld
  img=[]
  for tag in re.findall(r'<meta[^>]+>',s,re.I):
   if 'og:image' in tag:
    m=re.search(r'content=["\'](.*?)["\']',tag,re.I)
    if m:img.append(html.unescape(m.group(1)))
  result['official_image_urls']=img
  if img:
   raw,st,ct=get(img[0]);ext='.png' if 'png' in ct else '.webp' if 'webp' in ct else '.jpg';ip=ROOT/'official-images'/(k+ext);ip.write_bytes(raw);result['official_image_file']=str(ip)
 except Exception as e:result['error']=str(e)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:results=list(ex.map(one,PAGES.items()))
(ROOT/'official-source-extracts.json').write_text(json.dumps(results,indent=2))
for r in results:print(json.dumps({k:r.get(k) for k in ['id','status','bytes','official_image_file','error']}))
