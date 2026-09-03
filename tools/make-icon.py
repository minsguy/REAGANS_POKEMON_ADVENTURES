"""Generate the Pokeball home-screen icons (icon-512.png, icon-180.png). Requires Pillow."""
from PIL import Image, ImageDraw
import pathlib

def pokeball(size):
    s = size * 4  # supersample for smooth edges
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(s * 0.06)
    box = [pad, pad, s - pad, s - pad]
    # background rounded square (iOS masks its own corners; keep a soft tint so the ball pops)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=(255, 245, 230, 255))
    # red top half, white bottom half
    d.pieslice(box, 180, 360, fill=(226, 44, 44, 255))
    d.pieslice(box, 0, 180, fill=(250, 250, 250, 255))
    # black band
    band = int(s * 0.055)
    cy = s // 2
    d.rectangle([pad, cy - band, s - pad, cy + band], fill=(30, 30, 30, 255))
    # outline
    d.ellipse(box, outline=(30, 30, 30, 255), width=int(s * 0.035))
    # center button
    r_outer = int(s * 0.16)
    r_inner = int(s * 0.10)
    d.ellipse([s//2 - r_outer, cy - r_outer, s//2 + r_outer, cy + r_outer], fill=(30, 30, 30, 255))
    d.ellipse([s//2 - r_inner, cy - r_inner, s//2 + r_inner, cy + r_inner], fill=(250, 250, 250, 255))
    r_dot = int(s * 0.06)
    d.ellipse([s//2 - r_dot, cy - r_dot, s//2 + r_dot, cy + r_dot], fill=(225, 225, 225, 255))
    return img.resize((size, size), Image.LANCZOS)

root = pathlib.Path(__file__).resolve().parent.parent
for size in (512, 180):
    pokeball(size).save(root / ("icon-%d.png" % size))
    print("wrote icon-%d.png" % size)
