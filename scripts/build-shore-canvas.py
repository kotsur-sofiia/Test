"""Embed the finished beach photographs in one width-stable document canvas."""
from base64 import b64encode
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'


def image(name):
    return 'data:image/webp;base64,' + b64encode((ASSETS / name).read_bytes()).decode()


# Shells, stars, their contact shadows, sand and water are already part of the
# photographs. No cut-out ornaments or clipping masks are placed over the shore.
phone = image('shore-phone.webp')
desktop = image('shore-desktop.webp')
sand = image('shore-sand-continuation.webp')

# No viewBox: the photo scale depends on width, never on document length. The
# capped photo heights keep the water above the dial even on wide screens.
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
<style>
.coast {{ width:100%; height:min(300vw,1000px); }}
.coast-wide,.sand-wide {{ display:none; }}
@media(min-width:768px) {{ .coast-phone,.sand-phone {{ display:none; }} .sand-wide {{ display:block; }} .coast-wide {{ display:block; height:min(100vw,1100px); }} }}
</style>
<defs>
<image id="sand-photo" href="{sand}" width="1000" height="1000"/>
<pattern id="natural-sand-phone" patternUnits="userSpaceOnUse" width="100%" height="100vw">
<svg width="100%" height="100vw" viewBox="0 0 1000 1000"><use href="#sand-photo"/></svg>
</pattern>
<pattern id="natural-sand-wide" patternUnits="userSpaceOnUse" width="33.333333%" height="33.333333vw">
<svg width="33.333333%" height="33.333333vw" viewBox="0 0 1000 1000"><use href="#sand-photo"/></svg>
</pattern>
<linearGradient id="sand-join" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="white"/><stop offset=".92" stop-color="white"/><stop offset="1" stop-color="black"/>
</linearGradient>
<mask id="join" maskUnits="objectBoundingBox" maskContentUnits="objectBoundingBox">
<rect width="1" height="1" fill="url(#sand-join)"/>
</mask>
</defs>
<rect width="100%" height="100%" fill="#eee6dc"/>
<rect class="sand-continuation sand-phone" y="680" width="100%" height="100%" fill="url(#natural-sand-phone)"/>
<rect class="sand-continuation sand-wide" y="680" width="100%" height="100%" fill="url(#natural-sand-wide)"/>
<image class="coast coast-phone" href="{phone}" width="100%" height="1000" preserveAspectRatio="none" mask="url(#join)"/>
<image class="coast coast-wide" href="{desktop}" width="100%" height="1100" preserveAspectRatio="none" mask="url(#join)"/>
</svg>'''
(ASSETS / 'shore-canvas.svg').write_text(svg)
print('Built assets/shore-canvas.svg')
