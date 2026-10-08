import urllib.request,pathlib,json,re,html,concurrent.futures
R=pathlib.Path('/workspace/his-office-pinterest/products')
PAGES={'lagkapten-top-black':'https://www.ikea.com/us/en/p/lagkapten-tabletop-black-brown-80487016/','alex-black-drawers':'https://www.ikea.com/us/en/p/alex-drawer-unit-black-brown-60473548/','adils-black-leg':'https://www.ikea.com/us/en/p/adils-leg-black-70217973/','black-frame-landscape':'https://desenio.com/p/frames/wood-frames/black-wood-frames/black-picture-frame-28-x-39-in/'}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as s:return s.read(),s.headers.get('content-type','')
def f(it):
 k,u=it;d,c=get(u);p=R/'source-pages'/(k+'.html');p.write_bytes(d);s=d.decode();ld=[]
 for x in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',s,re.I|re.S):
  try:ld.append(json.loads(x))
  except:pass
 imgs=[]
 for tag in re.findall('<meta[^>]+>',s,re.I):
  if 'og:image' in tag:
   m=re.search('content=["\'](.*?)["\']',tag,re.I)
   if m:imgs.append(html.unescape(m.group(1)))
 rec={'id':k,'source_url':u,'html_file':str(p),'json_ld':ld,'official_image_urls':imgs}
 if imgs:
  url=imgs[0].split('?')[0];raw,ct=get(url);ext='.png' if 'png' in ct else '.jpg';ip=R/'photos'/(k+ext);ip.write_bytes(raw);rec['image_file']=str(ip);rec['download_url']=url
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(f,PAGES.items()))
(R/'additional-source-extracts.json').write_text(json.dumps(results,indent=2))
for x in results:
 print(x['id'],x['official_image_urls'])
 for d in x['json_ld']:
  if isinstance(d,dict) and d.get('@type')=='Product': print(d.get('offers'),d.get('image'))
