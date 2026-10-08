#!/usr/bin/env python3
"""Serve this portable apartment viewer without installing dependencies."""
import argparse
import functools
import http.server
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=8765)
parser.add_argument('--bind', default='127.0.0.1', help='Use 0.0.0.0 only if you want access from another device.')
args = parser.parse_args()
root = Path(__file__).resolve().parent
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
http.server.ThreadingHTTPServer.allow_reuse_address = True
with http.server.ThreadingHTTPServer((args.bind, args.port), handler) as server:
    print(f'Apartment viewer: http://{args.bind}:{args.port}', flush=True)
    print('Keep this terminal open. Ctrl+C stops the viewer.', flush=True)
    server.serve_forever()
