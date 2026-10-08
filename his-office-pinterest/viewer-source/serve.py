#!/usr/bin/env python3
"""Serve the private office viewer without installing dependencies."""
import argparse
import functools
import http.server
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port',type=int,default=8773)
parser.add_argument('--bind',default='127.0.0.1')
args=parser.parse_args()
root=Path(__file__).resolve().parent
class ViewerHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        # The source UI stays at /. Editable model links refer to the complete
        # accompanying project; the standalone HTML uses relative file links.
        route=path.split('?',1)[0].split('#',1)[0]
        allowed={f'/variants/{id}/model/his-office-design.blend'for id in ('b-charcoal-slat','c-ink-studio')}
        if route in allowed:return str(root.parent/route.lstrip('/'))
        return super().translate_path(path)
handler=functools.partial(ViewerHandler,directory=str(root))
http.server.ThreadingHTTPServer.allow_reuse_address=True
with http.server.ThreadingHTTPServer((args.bind,args.port),handler) as server:
    print(f'His Office viewer: http://{args.bind}:{args.port}',flush=True)
    server.serve_forever()
