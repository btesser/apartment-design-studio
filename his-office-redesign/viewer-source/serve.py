#!/usr/bin/env python3
"""Serve the private office viewer without installing dependencies."""
import argparse
import functools
import http.server
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port',type=int,default=8770)
parser.add_argument('--bind',default='127.0.0.1')
args=parser.parse_args()
root=Path(__file__).resolve().parent
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
http.server.ThreadingHTTPServer.allow_reuse_address=True
with http.server.ThreadingHTTPServer((args.bind,args.port),handler) as server:
    print(f'His Office viewer: http://{args.bind}:{args.port}',flush=True)
    server.serve_forever()
