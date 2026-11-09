#!/usr/bin/env python3
"""Pack the readable source back into the single-file game.

    python3 build.py            ->  index.html (one self-contained file)

Reads app.html and zork1.z3 from this folder, gzips each, stores them as
base64 inside a tiny loader that unpacks them in the browser. Uses Zopfli
for the smallest output if installed (pip install zopfli), otherwise gzip.
Because app.html is formatted for reading, the rebuilt file is a little
bigger than the published one, which was built from the minified original.
"""
import base64, gzip, pathlib, re

here = pathlib.Path(__file__).parent
page = (here / "app.html").read_text(encoding="utf-8")
page = re.sub(r'\s*<script src="zork1-story\.js"></script>', "", page)  # the loader supplies the story
story = (here / "zork1.z3").read_bytes()

try:
    import zopfli.gzip as zg
    pack = lambda b: zg.compress(b, numiterations=60)
except ImportError:
    pack = lambda b: gzip.compress(b, 9)

b64 = lambda b: base64.b64encode(pack(b)).decode()

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Zork Retro Edition</title>
<meta name="claude:viewport-fit-sides" content="cover">
<!--
Zork: The Retro Edition
Version 0.4. Developed by Mark Dowling, Melbourne, Australia, November 2026.
Hacks and remixes welcome: please keep this credit with any version you share.
-->
<meta name="author" content="Mark Dowling, Melbourne, Australia">
<!-- Zork I source and story file: github.com/historicalsource/zork1
MIT License

Copyright (c) 2025 Microsoft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-->
<style>html,body{height:100%;margin:0;background:#111316}#zld{padding:16px;color:#8a929e;font:13px ui-monospace,Menlo,monospace}</style></head><body>
<div id="zld">Unpacking Zork…</div>
"""
LOADER = """<script>
(async()=>{
const A="%%PAGE%%",B="%%STORY%%";
const ld=document.getElementById('zld');
if(typeof DecompressionStream!=='function'){ld.textContent='This browser is too old to unpack the game (needs Safari 16.4, Chrome 80, Firefox 113 or newer).';return;}
const inflate=s=>new Response(new Blob([Uint8Array.from(atob(s),c=>c.charCodeAt(0))]).stream().pipeThrough(new DecompressionStream('gzip')));
const [html,bytes]=await Promise.all([inflate(A).text(),inflate(B).arrayBuffer()]);
window.__ZSTORY=new Uint8Array(bytes);
const doc=new DOMParser().parseFromString(html,'text/html');
ld.remove();
const put=(n,parent)=>{
  if(n.nodeName==='SCRIPT'){const s=document.createElement('script');s.textContent=n.textContent;parent.append(s);}
  else if(n.nodeName==='TITLE'){}
  else parent.append(document.importNode(n,true));
};
for(const n of [...doc.head.childNodes])put(n,document.head);
for(const n of [...doc.body.childNodes])put(n,document.body);
})();
</script>
</body></html>"""

out = HEAD + LOADER.replace("%%PAGE%%", b64(page.encode("utf-8"))).replace("%%STORY%%", b64(story))
(here / "index.html").write_text(out, encoding="utf-8")
print(f"index.html written: {len(out):,} bytes")
