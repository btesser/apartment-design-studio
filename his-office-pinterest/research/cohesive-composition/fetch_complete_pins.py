import urllib.request,re,json,pathlib,concurrent.futures,html,time
root=pathlib.Path('/workspace/his-office-pinterest/research/cohesive-composition');(root/'pins').mkdir(exist_ok=True)
pins=[('moody-complete','691513717824164023'),('moody-refined','479703797832033753'),('navy-library-lounge','169025792262469612'),('dark-shelves-office','55028426685351096'),('moody-small-office','774124930296201'),('modern-complete','261279215870122923')]
def fetch_pin(pair):
 label,pid=pair;u=f'https://www.pinterest.com/pin/{pid}/';req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
 try:
  with urllib.request.urlopen(req,timeout=30) as r: s=r.read().decode();status=r.status
  (root/'pins'/f'{label}.html').write_text(s)
  metas={}
  for x in re.findall(r'<meta\b[^>]*>',s):
   attrs={k:html.unescape(v) for k,_,v in re.findall(r'(\w+)=(\"|\x27)(.*?)\2',x)}
   if 'property'in attrs and 'content'in attrs:metas[attrs['property']]=attrs['content']
  data={'label':label,'pin_id':pid,'url':u,'status':status,'metadata':metas}
  m=re.search(r'<script id="__PWS_INITIAL_PROPS__"[^>]*>(.*?)</script>',s)
  if m:
   d=json.loads(m.group(1));p=d.get('initialReduxState',{}).get('pins',{});data['pin_objects']=p
  iu=metas.get('og:image')
  if iu:
   ext='.jpg' if '.jpg' in iu else '.png';fn=root/'pins'/f'{label}{ext}'
   with urllib.request.urlopen(urllib.request.Request(iu,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:fn.write_bytes(r.read())
   data['local_image_path']=str(fn);data['image_source_url']=iu
  return data
 except Exception as e:return{'label':label,'pin_id':pid,'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: out=list(ex.map(fetch_pin,pins))
(root/'pin-records.json').write_text(json.dumps(out,indent=2))
for d in out:print(d['label'], d.get('metadata',{}).get('og:title'),d.get('image_source_url'),d.get('error'))
