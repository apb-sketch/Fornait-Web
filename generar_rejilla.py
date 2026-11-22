"""Dibuja la textura original. Solo este generador necesita Pillow."""

from pathlib import Path
from PIL import Image, ImageDraw


PITCH = 256
OUTPUT_SIZE = 1024
FILL_TOP = (24, 88, 158, 176)
FILL_BOTTOM = (12, 30, 84, 218)
LINE = (87, 176, 240, 214)
ACCENT = (146, 221, 255, 255)


def mix(top, bottom, amount):
    return tuple(round(a + (b - a) * amount) for a, b in zip(top, bottom))


def draw_tile():
    scale = 2
    width = PITCH * scale
    shape = [(31, 9), (230, 9), (246, 25), (246, 225), (225, 246), (26, 246), (9, 229), (9, 31)]
    points = [(x * scale, y * scale) for x, y in shape]
    mask = Image.new("L", (width, width))
    ImageDraw.Draw(mask).polygon(points, fill=255)
    gradient = Image.new("RGBA", (width, width))
    drawing = ImageDraw.Draw(gradient)
    for y in range(width):
        drawing.line((0, y, width - 1, y), fill=mix(FILL_TOP, FILL_BOTTOM, y / (width - 1)))
    tile = Image.new("RGBA", gradient.size)
    tile.paste(gradient, mask=mask)

    detail = Image.new("RGBA", tile.size)
    drawing = ImageDraw.Draw(detail)
    drawing.line([*points, points[0]], fill=LINE, width=2 * scale)

    for y in range(34, 230, 12):
        for x in range(34, 230, 12):
            if 99 < x < 157 and 99 < y < 157:
                continue
            drawing.ellipse(
                (x * scale, y * scale, (x + 1) * scale, (y + 1) * scale),
                fill=(142, 209, 250, 75),
            )

    def stroke(coords, color=ACCENT, thickness=2):
        drawing.line([(x * scale, y * scale) for x, y in coords], fill=color, width=thickness * scale)

    stroke([(17, 57), (17, 36), (36, 17), (66, 17)], thickness=3)
    stroke([(189, 238), (221, 238), (238, 221), (238, 199)], thickness=3)
    stroke([(33, 53), (33, 43), (43, 33), (53, 33)], color=LINE)
    stroke([(203, 222), (215, 222), (222, 215), (222, 203)], color=LINE)
    stroke([(107, 128), (128, 107), (149, 128), (128, 149), (107, 128)], color=LINE)
    stroke([(122, 128), (134, 128)], color=ACCENT)
    return Image.alpha_composite(tile, detail)


def main():
    tile = draw_tile()
    pitch = tile.width
    grid = Image.new("RGBA", (pitch * 3, pitch * 3))
    for row in range(3):
        for column in range(3):
            grid.paste(tile, (column * pitch, row * pitch))
    folder = Path(__file__).resolve().parent / "recursos"
    folder.mkdir(exist_ok=True)
    grid.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS).save(
        folder / "Rejilla_de_edicion_azul.png", optimize=True
    )


if __name__ == "__main__":
    main()
