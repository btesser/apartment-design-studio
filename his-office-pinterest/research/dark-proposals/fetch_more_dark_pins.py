import urllib.request,re,json,pathlib,concurrent.futures,html,time
root=pathlib.Path('/workspace/his-office-pinterest/research/dark-proposals');(root/'pins').mkdir(exist_ok=True)
pins=[('midnight-workstation','641411171966283250'),('navy-two-desks','380976449749094962'),('bluegray-beadboard','494621971589422574'),('navy-white-workwall','53832158043506099'),('dark-simple-desk','482659285071249591'),('navy-minimalwall','780389441673907334'),('alex-bluewall','339036678193033336'),('dark-cement-paper','488922103315018879')]
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
(root/'pin-records-more.json').write_text(json.dumps(out,indent=2))
for d in out:print(d['label'], d.get('metadata',{}).get('og:title'),d.get('image_source_url'),d.get('error'))
