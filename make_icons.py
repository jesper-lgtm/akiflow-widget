"""
Generate PNG icons for the PWA — black T on white background.
Uses only stdlib (struct + zlib), no third-party deps needed.
"""
import struct, zlib, os

def make_png(size):
    """Return raw bytes of a PNG file: white bg, bold black T centred."""
    w = h = size

    # --- rasterise a bold T ---
    pixels = [[255] * w for _ in range(h)]   # white canvas (greyscale)

    # Proportions scale with size
    stroke  = max(1, round(size * 0.13))      # stem/crossbar thickness
    top     = round(size * 0.20)              # top of crossbar
    bot     = round(size * 0.82)              # bottom of stem
    left    = round(size * 0.17)              # crossbar left
    right   = round(size * 0.83)              # crossbar right
    cx      = w // 2                          # horizontal centre

    # Draw crossbar (horizontal)
    for y in range(top, top + stroke):
        for x in range(left, right):
            pixels[y][x] = 0

    # Draw stem (vertical)
    stem_l = cx - stroke // 2
    stem_r = stem_l + stroke
    for y in range(top, bot):
        for x in range(stem_l, stem_r):
            pixels[y][x] = 0

    # --- encode as PNG (RGBA, 32-bit for maximum compatibility) ---
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    raw_rows = b''
    for row in pixels:
        rgba_row = b''
        for v in row:
            # white (255) → RGBA(255,255,255,255), black (0) → RGBA(0,0,0,255)
            rgba_row += bytes([v, v, v, 255])
        raw_rows += b'\x00' + rgba_row            # filter type 0 per row

    png = (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))  # color type 6 = RGBA
        + chunk(b'IDAT', zlib.compress(raw_rows, 9))
        + chunk(b'IEND', b'')
    )
    return png

base = os.path.dirname(os.path.abspath(__file__))
for size, name in [(192, 'icon-192.png'), (512, 'icon-512.png')]:
    path = os.path.join(base, name)
    with open(path, 'wb') as f:
        f.write(make_png(size))
    print(f"Written {path}  ({os.path.getsize(path)} bytes)")
