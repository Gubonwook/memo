#!/usr/bin/env python3
"""
GPU-free molecular structure viewer server for HPC.

- Python standard library only (Python 3.6+). No pip install needed.
- The HPC side only serves files. Rendering (WebGL) happens in the
  desktop browser, so the HPC needs no GPU, no DISPLAY, no OpenGL.
- If ASE is installed, extra formats (OUTCAR, vasprun.xml, traj, xsf, ...)
  are converted on the fly. Without ASE those formats are simply listed as
  "needs ASE".

Usage:
    python3 serve.py [ROOT_DIR] [--port 8765] [--host 127.0.0.1]

Then on the desktop:
    ssh -L 8765:localhost:8765 user@hpc
    open http://localhost:8765 in a browser
"""
import argparse
import io
import json
import mimetypes
import os
import socket
import socketserver
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))

# extension -> 3Dmol.js format name (natively parsed in the browser)
NATIVE_EXT = {
    ".xyz": "xyz",
    ".pdb": "pdb",
    ".ent": "pdb",
    ".cif": "cif",
    ".mol2": "mol2",
    ".sdf": "sdf",
    ".mol": "sdf",
    ".cube": "cube",
    ".cub": "cube",
    ".gro": "gro",
    ".pqr": "pqr",
    ".vasp": "vasp",
    ".poscar": "vasp",
    ".contcar": "vasp",
    ".extxyz": "xyz",
}
# file names (no extension) that are VASP structures
VASP_NAMES = ("POSCAR", "CONTCAR")
# formats that need ASE on the server side
ASE_EXT = {".traj", ".xsf", ".lammps", ".data", ".in", ".gen", ".xml", ".json", ".db"}
ASE_NAMES = ("OUTCAR", "XDATCAR", "vasprun.xml")

MAX_FILE_MB = 200
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".ipynb_checkpoints"}

try:
    import ase.io  # noqa: F401
    HAS_ASE = True
except Exception:
    HAS_ASE = False


def detect_format(path):
    """Return (format, how) where how is 'native', 'ase' or None."""
    name = os.path.basename(path)
    low = name.lower()
    ext = os.path.splitext(low)[1]
    up = name.upper()
    if "XDATCAR" in up:
        return ("xdatcar", "native")  # parsed by our own JS
    for v in VASP_NAMES:
        if v in up:
            return ("vasp", "native")
    if ext in NATIVE_EXT:
        return (NATIVE_EXT[ext], "native")
    for v in ASE_NAMES:
        if name.startswith(v):
            return ("pdb", "ase")
    if ext in ASE_EXT:
        return ("pdb", "ase")
    return (None, None)


def safe_join(root, rel):
    full = os.path.realpath(os.path.join(root, rel.lstrip("/")))
    root_real = os.path.realpath(root)
    if full != root_real and not full.startswith(root_real + os.sep):
        raise PermissionError("outside root")
    return full


def list_structures(root, max_depth=6, limit=5000):
    out = []
    root_real = os.path.realpath(root)
    base_depth = root_real.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root_real):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        if dirpath.count(os.sep) - base_depth >= max_depth:
            dirnames[:] = []
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            fmt, how = detect_format(full)
            if fmt is None:
                continue
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            out.append({
                "path": os.path.relpath(full, root_real).replace(os.sep, "/"),
                "format": fmt,
                "how": how,
                "available": how == "native" or HAS_ASE,
                "size": size,
            })
            if len(out) >= limit:
                return out
    return out


def convert_with_ase(full):
    """Read any ASE-supported file, return multi-model PDB text (cell kept)."""
    import ase.io
    frames = ase.io.read(full, index=":")
    if not isinstance(frames, list):
        frames = [frames]
    if len(frames) > 2000:  # keep the browser responsive
        step = len(frames) // 2000 + 1
        frames = frames[::step]
    buf = io.StringIO()
    ase.io.write(buf, frames, format="proteindatabank")
    return buf.getvalue()


class Handler(BaseHTTPRequestHandler):
    root = "."
    server_version = "MolViewer/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[viewer] " + (fmt % args) + "\n")

    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        try:
            if url.path in ("/", "/index.html"):
                return self._static("index.html")
            if url.path.startswith("/lib/"):
                return self._static(url.path.lstrip("/"))
            if url.path == "/favicon.ico":
                return self._send(204, "")
            if url.path == "/api/info":
                return self._json({"root": os.path.realpath(self.root), "ase": HAS_ASE})
            if url.path == "/api/list":
                return self._json(list_structures(self.root))
            if url.path == "/api/file":
                rel = unquote(q.get("path", [""])[0])
                return self._file(rel)
            self._send(404, "not found")
        except PermissionError:
            self._send(403, "forbidden")
        except Exception as e:  # report errors to the browser
            self._send(500, "error: %s" % e)

    def _static(self, rel):
        full = os.path.realpath(os.path.join(HERE, rel))
        if not full.startswith(os.path.realpath(HERE) + os.sep) or not os.path.isfile(full):
            return self._send(404, "not found")
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            ctype += "; charset=utf-8"
        with open(full, "rb") as f:
            self._send(200, f.read(), ctype)

    def _file(self, rel):
        full = safe_join(self.root, rel)
        if not os.path.isfile(full):
            return self._send(404, "not found")
        if os.path.getsize(full) > MAX_FILE_MB * 1024 * 1024:
            return self._send(413, "file larger than %d MB" % MAX_FILE_MB)
        fmt, how = detect_format(full)
        if how == "ase":
            if not HAS_ASE:
                return self._send(415, "this format needs ASE on the HPC (pip install --user ase)")
            text = convert_with_ase(full)
        else:
            with open(full, "rb") as f:
                text = f.read().decode("utf-8", errors="replace")
        self.send_response(200)
        body = text.encode("utf-8")
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("X-Format", fmt or "")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


class ThreadingServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description="GPU-free structure viewer server")
    ap.add_argument("root", nargs="?", default=".", help="directory to browse (default: current)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1",
                    help="127.0.0.1 (default, use ssh -L) or 0.0.0.0 to expose on the network")
    args = ap.parse_args()

    root = os.path.realpath(args.root)
    if not os.path.isdir(root):
        sys.exit("not a directory: %s" % root)
    Handler.root = root

    httpd = None
    for port in range(args.port, args.port + 20):
        try:
            httpd = ThreadingServer((args.host, port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        sys.exit("no free port in %d-%d" % (args.port, args.port + 19))

    port = httpd.server_address[1]
    host = socket.gethostname()
    n = len(list_structures(root))
    print("=" * 64)
    print(" Molecular viewer server is running")
    print("   root   : %s  (%d structure files)" % (root, n))
    print("   ASE    : %s" % ("available" if HAS_ASE else "not installed (OUTCAR / vasprun.xml / traj off)"))
    print("   listen : %s:%d" % (args.host, port))
    print("")
    print(" On your DESKTOP run:")
    print("   ssh -L %d:localhost:%d <user>@%s" % (port, port, host))
    print(" then open:  http://localhost:%d" % port)
    print(" Stop with Ctrl+C")
    print("=" * 64)
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
