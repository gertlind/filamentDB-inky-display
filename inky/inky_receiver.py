from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
import json
import datetime
from pathlib import Path

app = Flask(__name__)
inky = auto()

WIDTH, HEIGHT = inky.resolution
BASE_DIR = Path("/home/gert/inky")
LABELS_FILE = BASE_DIR / "labels.json"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

DEFAULT_LABELS = {
    "color": "Färg",
    "diameter": "Diameter",
    "remaining_g": "KVAR (g)",
    "remaining_m": "LÄNGD (m)",
    "updated": "Uppdaterad",
    "id": "ID",
}


def load_labels():
    try:
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            custom = json.load(f)
        return {**DEFAULT_LABELS, **custom}
    except Exception:
        return DEFAULT_LABELS


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_or_dash(value):
    if value is None or value == "":
        return "-"
    return str(value)


def draw_centered_text(draw, box, text, font_obj, fill):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = x1 + ((x2 - x1) - text_w) // 2
    y = y1 + ((y2 - y1) - text_h) // 2
    draw.text((x, y), text, fill=fill, font=font_obj)


def draw_material_icon(draw, x, y, material):
    material = str(material).upper()

    if "PETG" in material:
        points = [
            (x + 43, y),
            (x + 86, y + 25),
            (x + 86, y + 75),
            (x + 43, y + 100),
            (x, y + 75),
            (x, y + 25),
        ]
        draw.polygon(points, fill="red", outline="black")
        draw.text((x + 17, y + 36), "PETG", fill="white", font=font(FONT_BOLD, 19))

    elif "PLA" in material:
        draw.ellipse((x, y + 10, x + 86, y + 96), fill="red", outline="black")
        draw.line((x + 22, y + 75, x + 68, y + 28), fill="white", width=5)
        draw.text((x + 23, y + 39), "PLA", fill="white", font=font(FONT_BOLD, 22))

    else:
        draw.rounded_rectangle(
            (x, y, x + 86, y + 100),
            radius=14,
            fill="red",
            outline="black",
        )
        draw.text((x + 16, y + 38), material[:4], fill="white", font=font(FONT_BOLD, 20))


def render_to_inky(data):
    labels = load_labels()

    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    title_font = font(FONT_BOLD, 48)
    subtitle_font = font(FONT_REG, 28)
    label_font = font(FONT_BOLD, 24)
    value_font_big = font(FONT_BOLD, 72)
    small_font = font(FONT_REG, 20)

    vendor = text_or_dash(data.get("vendor"))
    name = text_or_dash(data.get("name"))
    material = text_or_dash(data.get("material"))
    color_name = text_or_dash(data.get("color_name"))
    # diameter = text_or_dash(data.get("diameter"))
    nozzle = text_or_dash(data.get("nozzle_temp"))
    bed = text_or_dash(data.get("bed_temp"))
    remaining_g = text_or_dash(data.get("remaining_g"))
    remaining_m = text_or_dash(data.get("remaining_m"))
    instance_id = text_or_dash(data.get("instance_id"))

    # Header
    draw.rectangle((0, 0, WIDTH, 88), fill="black")
    # draw.text((28, 16), vendor, fill="white", font=title_font)
    # draw.text((500, 28), material, fill="red", font=title_font)
    bbox = draw.textbbox((0, 0), vendor, font=title_font)
    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) // 2
    draw.text((x, 16), vendor, fill="white", font=title_font)

    # Materialikon
    draw_material_icon(draw, 690, 104, material)

    # Filamentnamn
    draw.text((30, 112), name, fill="black", font=title_font)

    # Info-rad (centrerad)
    info_text = f"{labels['color']}: {color_name}   •   {nozzle}°C / {bed}°C"

    bbox = draw.textbbox((0, 0), info_text, font=subtitle_font)
    text_w = bbox[2] - bbox[0]

    x = (WIDTH - text_w) // 2
    draw.text((x, 172), info_text, fill="black", font=subtitle_font)

    # Kort
    card_y = 230
    card_h = 160
    gap = 24
    card_w = (WIDTH - 60 - gap) // 2

    # Gram
    x1 = 30
    draw.rounded_rectangle(
        (x1, card_y, x1 + card_w, card_y + card_h),
        radius=20,
        fill="red",
    )
    draw.text((x1 + 24, card_y + 18), labels["remaining_g"], fill="white", font=label_font)
    draw_centered_text(
        draw,
        (x1, card_y + 48, x1 + card_w, card_y + card_h),
        remaining_g,
        value_font_big,
        "white",
    )

    # Meter
    x2 = x1 + card_w + gap
    draw.rounded_rectangle(
        (x2, card_y, x2 + card_w, card_y + card_h),
        radius=20,
        fill="red",
    )
    draw.text((x2 + 24, card_y + 18), labels["remaining_m"], fill="white", font=label_font)
    draw_centered_text(
        draw,
        (x2, card_y + 48, x2 + card_w, card_y + card_h),
        remaining_m,
        value_font_big,
        "white",
    )

    # Footer
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    draw.line((30, 420, WIDTH - 30, 420), fill="black", width=2)
    draw.text((30, 438), f"{labels['id']}: {instance_id}", fill="black", font=small_font)
    draw.text((400, 438), f"{labels['updated']}: {now}", fill="black", font=small_font)

    img.save(BASE_DIR / "last_render.png")
    inky.set_image(img)
    inky.show()


@app.route("/", methods=["GET"])
def index():
    return "Inky JSON receiver is running\n"


@app.route("/filament", methods=["POST"])
def filament():
    data = request.get_json(silent=True)

    if data is None:
        return "Ingen giltig JSON\n", 400

    print(datetime.datetime.now(), "JSON mottagen")
    print(json.dumps(data, indent=2, ensure_ascii=False), flush=True)

    with open(BASE_DIR / "last_filament.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Renderar till Inky...", flush=True)
    render_to_inky(data)

    print("Klar", flush=True)
    return "OK\n"


app.run(host="0.0.0.0", port=5000)
