"""Preview the generated static site on this computer."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8767)
args = parser.parse_args()
directory = Path(__file__).resolve().parents[1] / 'dist'
if not (directory / 'index.html').exists():
    parser.error('Primero ejecuta scripts/build_site.py')
server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(directory)))
print(f'Vista previa: http://127.0.0.1:{args.port}/', flush=True)
server.serve_forever()
