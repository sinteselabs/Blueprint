"""Draws the Blueprint plugin icon: blueprint paper and a compass needle.

The needle is the 🧭 of the README; the grid is the paper the plan is drawn on.
Flat shapes and one strong diagonal, so it still reads at 32 px in a list.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 1024
SUPER = 4  # draw big, shrink down: cheap antialiasing
S = SIZE * SUPER

INK = (16, 42, 74)        # deep blueprint blue, the background
GRID = (56, 94, 140)      # the paper's ruling
GRID_STRONG = (78, 124, 176)
NEEDLE_N = (240, 246, 252)  # the half that points north
NEEDLE_S = (108, 160, 214)  # the other half
RING = (158, 198, 236)


def rounded_background(draw: ImageDraw.ImageDraw) -> None:
    draw.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.18), fill=INK)


def grid(draw: ImageDraw.ImageDraw) -> None:
    step = S // 12
    thin, thick = max(1, S // 400), max(2, S // 190)
    for i in range(1, 12):
        at = i * step
        strong = i % 4 == 0
        width = thick if strong else thin
        colour = GRID_STRONG if strong else GRID
        draw.line([at, 0, at, S], fill=colour, width=width)
        draw.line([0, at, S, at], fill=colour, width=width)


def needle(draw: ImageDraw.ImageDraw) -> None:
    """Two triangles meeting at the centre: north light, south muted."""
    c = S / 2
    reach, half = S * 0.30, S * 0.075
    # The long axis runs north-east; the short axis is perpendicular to it. Both
    # halves share the two side points, so they meet with no seam and no notch.
    ax, ay = 0.7071, -0.7071
    px, py = -ay, ax
    tip = (c + ax * reach, c + ay * reach)
    tail = (c - ax * reach, c - ay * reach)
    left = (c + px * half, c + py * half)
    right = (c - px * half, c - py * half)
    draw.polygon([tip, left, right], fill=NEEDLE_N)
    draw.polygon([tail, left, right], fill=NEEDLE_S)
    r = S * 0.047
    draw.ellipse([c - r, c - r, c + r, c + r], fill=INK, outline=RING, width=max(2, S // 150))


def ring(draw: ImageDraw.ImageDraw) -> None:
    pad = S * 0.135
    draw.ellipse([pad, pad, S - pad, S - pad], outline=RING, width=max(3, S // 95))


def main() -> int:
    out = Path(sys.argv[1])
    image = Image.new("RGB", (S, S), INK)
    draw = ImageDraw.Draw(image)
    rounded_background(draw)
    grid(draw)
    ring(draw)
    needle(draw)
    image = image.resize((SIZE, SIZE), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, "PNG", optimize=True)
    print(f"{out}  {SIZE}x{SIZE}  {out.stat().st_size / 1024:.0f} kB")
    # a small render too, to judge how it holds up in a list
    preview = out.with_name("icon-32.png")
    image.resize((32, 32), Image.LANCZOS).save(preview, "PNG")
    print(f"{preview}  32x32")
    return 0


if __name__ == "__main__":
    sys.exit(main())
