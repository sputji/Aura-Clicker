from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def make_logo(out_png: Path, out_ico: Path) -> None:
    size = 1024
    img = Image.new("RGBA", (size, size), (15, 24, 43, 255))
    draw = ImageDraw.Draw(img)

    # Background radial glow
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((120, 90, 900, 870), fill=(47, 107, 255, 150))
    glow = glow.filter(ImageFilter.GaussianBlur(85))
    img.alpha_composite(glow)

    # Outer ring
    draw.ellipse((120, 120, 904, 904), outline=(126, 166, 255, 220), width=28)
    draw.ellipse((165, 165, 859, 859), outline=(65, 111, 238, 220), width=10)

    # Inner shield/diamond
    points = [(512, 210), (760, 512), (512, 814), (264, 512)]
    draw.polygon(points, fill=(36, 67, 150, 230), outline=(170, 197, 255, 255), width=12)

    # Stylized click-cursor triangle
    cursor = [(442, 390), (442, 658), (582, 578), (656, 736), (722, 704), (648, 546), (788, 546)]
    draw.polygon(cursor, fill=(230, 240, 255, 255), outline=(24, 43, 89, 255), width=8)

    # AC initials
    try:
        font = ImageFont.truetype("segoeuib.ttf", 190)
    except OSError:
        font = ImageFont.load_default()
    draw.text((260, 70), "AC", fill=(236, 244, 255, 220), font=font)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png, "PNG")

    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(out_ico, format="ICO", sizes=icon_sizes)


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    assets = base / "aura_clicker" / "assets"
    make_logo(assets / "logo_aura_clicker.png", assets / "logo_aura_clicker.ico")
    print("LOGO_OK")
