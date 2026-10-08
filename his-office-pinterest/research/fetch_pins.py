import urllib.request,re,json,pathlib,concurrent.futures,html,time
root=pathlib.Path('/workspace/his-office-pinterest/research');(root/'pins').mkdir(exist_ok=True)
pins=[('japandi-1','112801165661077409'),('japandi-stillness','607493437271382718'),('japandi-work','1036742776715452888'),('japandi-2','298011700363513170'),('japandi-3','592786369738226966'),('double-wall-desk','818740407293933462'),('white-wood-office','76420524923625798'),('warm-naturalwood','908460556119478256'),('clean-ultrawide','389702174011180959'),('wood-panel-wall','383580093246985677'),('minimal-wall-wood','511580838919727442'),('walnut-simple','461196818109099025'),('minimal-wall-decor','749145719282026330'),('warm-minimal-desk','957859414475071779'),('warm-standing-desk','762515780700805161'),('wall-storage','329466528987642779'),('monochrome-office','492651646743363660'),('industrial-darkwood','365002744822690990'),('brick-wall-desk','5348093277836021'),('minimal-office-storage','3870349671214104'),('hidden-storage','586101339044421549')]
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
