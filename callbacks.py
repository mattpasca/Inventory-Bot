# -------------------------
# Parser
# -------------------------
import json
from pathlib import Path

key_list = [
        "Formato",
        "Tipo C",
        "Mis.",
        "Altezza",
        "Alt.Tronco",
        "Circonf.",
        "Chioma",
        "Qlt",
        "PRZ1",
        "PRZ2",
        "PRZ3",
        "qta",
        "ST",
        "Disp.",
        "note",
        "collega",
]

def parse_message(colleague, user_message, mode):
    plant_dict = {}
    if mode == "t":
        columns = user_message.split("\n", 15)
    elif mode == "v":
        columns = user_message.split("poi", 15)
    for i, value in enumerate(columns):
        plant_dict[key_list[i]] = value.replace(",", "").replace(".", "") # transcript has commas and points
    plant_dict["collega"] = colleague
    return plant_dict

def save_json(plant_name, plant_dict, filename):
    base_dir = Path(__file__).parent
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / filename
    if file_path.exists() and file_path.stat().st_size > 0:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        data = []
    found = False
    for item in data:
            if item["name"] == plant_name:
                item["data"].append(plant_dict)
                found = True
                break
    if found == False:
        data.append({
            "name": plant_name,
            "data": [plant_dict]
        })
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# -------------------------
# Suggestions
# -------------------------
from rapidfuzz import process, fuzz

name_path = Path(__file__).parent / "data" / "name_list.json"
with open(name_path, "r", encoding="utf-8") as f:
    plant_names = json.load(f)

def suggestions(user_input):
    user_input = user_input.strip().lower()
    matches = process.extract(user_input, plant_names, scorer=fuzz.WRatio, limit=5)
    names = [m[0] for m in matches]
    return names

# -------------------------
# Preview
# -------------------------
from PIL import Image, ImageDraw, ImageFont
import io

max_key_len = max(len(k) for k in key_list)

def generate_preview(details_dict, plant_name):
    max_val_len = max(len(str(details_dict.get(k, "—"))) for k in key_list)

    lines = [f"🌱 Nome: {plant_name}", ""]
    lines.append("Dettagli")

    for key in key_list:
        val = str(details_dict.get(key, "—"))
        padded_key = key.ljust(max_key_len)
        padded_val = val.rjust(max_val_len)
        lines.append(f"{padded_key} : {padded_val}")

    # use both <pre><code> for monospace + spacing
    html_text = "<pre><code>" + "\n".join(lines) + "</code></pre>"

    return html_text

def generate_preview_image(details_dict, plant_name, width=1500):
    font_path = Path(__file__).parent / "data"
    semi_bold = font_path / "SpaceGrotesk-SemiBold.ttf"
    bold = font_path / "SpaceGrotesk-Bold.ttf"
    font = ImageFont.truetype(semi_bold, 90)
    key_font = ImageFont.truetype(bold, 90)
    padding = 20
    line_height = 100
    # dynamically calculate height
    height = (len(details_dict) + 2) * line_height + 2 * padding
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # draw title
    draw.text((padding, padding), f"{plant_name}", fill=(220,20,60), font=key_font)
    # draw a line under the title
    draw.line((padding, padding + line_height - 10, width - padding, padding + line_height - 10), fill="black", width=2)
    y = padding + line_height
    split_point = width // 2  # middle of image for key-value separation
    value_offset = 20          # small gap after split point for values
    for key, val in details_dict.items():
        key_text = f"{key}:"
        val_text = str(val)
        # draw key right-aligned to split point
        key_bbox = draw.textbbox((0, 0), key_text, font=font)
        key_width = key_bbox[2] - key_bbox[0]
        draw.text((split_point - key_width - value_offset, y), key_text, fill=(0, 50, 150), font=key_font)
        # draw value slightly to the right of split point
        draw.text((split_point + value_offset, y), val_text, fill="black", font=font)
        y += line_height
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# -------------------------
# Pass audio to whisper
# -------------------------

import os
import ffmpeg
from faster_whisper import WhisperModel

model = WhisperModel(
    r"C:\Program Files\small",
    device="cpu",
    compute_type="int8"
)
def transcribe():
    ogg_path = "voice_note.ogg"
    wav_path = "voice_note.wav"
    ffmpeg.input(ogg_path).output(wav_path).run(overwrite_output=True)
    segments, info = model.transcribe(
    "voice_note.wav",
    language="it",       
    task="transcribe"     
)
    result_text = "".join([seg.text for seg in segments]).strip()
    os.remove(ogg_path)
    os.remove(wav_path)
    return result_text

# -------------------------
# Fill JSON with ollama
# -------------------------
import ollama

examples_path = Path(__file__).parent / "data" / "examples.jsonl"
with open(examples_path, "r") as f:
    few_shots = "\n".join([f"### EXAMPLE\nInput: {e['input']}\nColleague: {e['collega']}\nOutput:\n{json.dumps(e['output'], ensure_ascii=False)}"
                            for e in map(json.loads, f)])
with open(examples_path, "r") as f:
    few_shots = "\n".join([f"### EXAMPLE\nInput: {e['input']}\nColleague: {e['collega']}\nOutput:\n{json.dumps(e['output'], ensure_ascii=False)}"
                            for e in map(json.loads, f)])

dict_path = Path(__file__).parent / "data" / "empty_dict.json"
with open(dict_path, "r") as f:
    empty_dict = json.load(f)

async def llm_parser(colleague, text):
    prompt = f"""
    You are a JSON parser.  
    User gives an inventory record in text or messy speech transcript.
    Records are plants of a nursery.  
    Output only a JSON object with the fixed structure below:

    ### FEW-SHOT EXAMPLES (follow them strictly)
    {few_shots}

    ### JSON SCHEMA (must always match this EXACT key set):
    {json.dumps(empty_dict)}

    ### FIELD DEFINITIONS (brief)
    - "Formato": plant form (alto fusto, mezzo fusto, cespuglio, etc.)
    - "Tipo C": type of container or rootball (CLT / zolla)
    - "Mis.": container size (liters)
    - "Altezza": plant height
    - "Alt.Tronco": trunk height
    - "Circonf.": trunk circumference
    - "Chioma": crown diameter
    - "Qlt": quality grade
    - "PRZ1, PRZ2, PRZ3": prices in €
    - "qta": quantity
    - "Disp.": availability
    - "ST": stock
    - "note": leftover text
    - "collega": colleague name

    ### RULES:
    - If a field is missing, set it to "".
    - Output ONLY valid JSON. No text, no explanation.
    - Extract numbers whenever possible.
    - Never add extra fields.
    - Never change keys.
    - Return PURE JSON, no explanation.

    
    ### NOW PARSE THE USER INPUT:
    TEXT: {text}
    COLLEGA: {colleague}
    """

    response = ollama.generate(
        model="qwen2.5:3b",
        prompt=prompt,
        options={"temperature": 0}  # deterministic
    )

    parsed = json.loads(response["response"])
    return parsed