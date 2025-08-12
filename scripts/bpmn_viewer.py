#!/usr/bin/env python3
"""
Lightweight BPMN viewer using bpmn-js via a tiny Flask server.

Usage:
  python3 scripts/bpmn_viewer.py  # serves http://127.0.0.1:5001

Endpoints:
  /                 - Index of BPMN files under src/processes
  /viewer?file=...  - Render a specific BPMN in browser via bpmn-js
  /bpmn/<filename>  - Raw BPMN XML content
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from flask import Flask, send_from_directory, request, abort, render_template_string


ROOT = Path(__file__).resolve().parents[1]
PROC_DIR = ROOT / "src" / "processes"

app = Flask(__name__)
@app.route("/static_bpmn/<path:filename>")
def serve_static_bpmn(filename: str):
    base = ROOT / "scripts" / "static" / "bpmn"
    if ".." in filename or filename.startswith("/"):
        abort(400)
    return send_from_directory(base, filename)



def list_bpmn_files() -> List[str]:
    if not PROC_DIR.exists():
        return []
    return sorted([p.name for p in PROC_DIR.glob("*.bpmn")])


@app.route("/")
def index():
    files = list_bpmn_files()
    items = "".join(
        f'<li><a href="/viewer?file={name}">{name}</a></li>' for name in files
    )
    return f"""
    <html>
      <head>
        <title>ProcOS BPMN Files</title>
        <style>body{{font-family:sans-serif;margin:24px}}</style>
      </head>
      <body>
        <h1>ProcOS BPMN Files</h1>
        <ul>
          {items}
        </ul>
      </body>
    </html>
    """


@app.route("/bpmn/<path:filename>")
def serve_bpmn(filename: str):
    # Basic path safety
    if ".." in filename or filename.startswith("/"):
        abort(400)
    return send_from_directory(PROC_DIR, filename)


VIEWER_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>BPMN Viewer - {{ filename }}</title>
    <style>
      html, body, #canvas { height: 100%; margin: 0; padding: 0; }
      body { font-family: sans-serif; }
    </style>
    <!-- Local static assets fallback first, then CDN as backup -->
    <link rel="stylesheet" href="/static_bpmn/diagram-js.css" />
    <link rel="stylesheet" href="/static_bpmn/bpmn-font/css/bpmn.css" />
    <script src="/static_bpmn/bpmn-viewer.js"></script>
    <script>
      if (!window.BpmnJS) {
        document.write('<script src="https://unpkg.com/bpmn-js@14.7.0/dist/bpmn-viewer.development.js"><\/script>');
      }
    </script>
  </head>
  <body>
    <div id="canvas"></div>
    <script>
      (async function() {
        const urlParams = new URLSearchParams(window.location.search);
        const file = urlParams.get('file');
        if (!file) { document.body.innerHTML = '<p>No file provided.</p>'; return; }
        const res = await fetch('/bpmn/' + file);
        if (!res.ok) { document.body.innerHTML = '<p>Failed to fetch BPMN.</p>'; return; }
        const xml = await res.text();

        const BpmnCtor = window.BpmnJS;
        if (!BpmnCtor) {
          document.body.innerHTML = '<p>Failed to load bpmn-js from CDN. If you are on WSL or a restricted network, allow <code>unpkg.com</code> or ask me to switch to a local copy.</p>';
          return;
        }
        const viewer = new BpmnCtor({ container: '#canvas' });
        try {
          await viewer.importXML(xml);
          const canvas = viewer.get('canvas');
          canvas.zoom('fit-viewport', 'auto');
        } catch (err) {
          console.error(err);
          document.body.innerHTML = '<pre>' + (err && err.message ? err.message : err) + '</pre>';
        }
      })();
    </script>
  </body>
  </html>
"""


@app.route("/viewer")
def viewer():
    filename = request.args.get("file")
    if not filename:
        abort(400)
    # Validate exists
    if not (PROC_DIR / filename).exists():
        abort(404)
    return render_template_string(VIEWER_HTML, filename=filename)


if __name__ == "__main__":
    port = int(os.getenv("BPMN_VIEWER_PORT", "5001"))
    app.run(host="127.0.0.1", port=port, debug=False)


