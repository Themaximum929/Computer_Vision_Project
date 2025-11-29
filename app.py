"""HuggingFace Space - Template-based Poster Generator with Canvas Editor"""
import gradio as gr
import spaces
from src.pipeline import Key2PosterPipeline
from PIL import Image, ImageDraw, ImageFont
import json
import random
import glob
import re

pipeline = Key2PosterPipeline(use_flux=True, add_title=False, remove_text=True, super_resolution=False)

template_files = glob.glob("templates/template*_layers.json")
template_files.sort(key=lambda x: int(re.search(r'template(\d+)', x).group(1)))
templates = [json.load(open(f)) for f in template_files]

# State components will be managed via Gradio State
import copy

@spaces.GPU
def generate_poster(keywords, seed, template_num):
    print(f"[DEBUG] generate_poster called: keywords={keywords}, seed={seed}, template_num={template_num}")
    keyword_list = [k.strip() for k in keywords.split() if k.strip()]
    if len(keyword_list) < 2 or len(keyword_list) > 5:
        print("[DEBUG] Invalid keyword count")
        return None, None, None, None, "❌ Provide 2-5 keywords", None, None, "", 360, 900, 37, "#043bb4", "", 360, 950, 20, "#043bb4", "", 360, 1000, 20, "#043bb4"
    
    template = random.choice(templates) if template_num == 0 else templates[int(template_num)-1] if 0 < template_num <= len(templates) else templates[0]
    print(f"[DEBUG] Template selected: {template.get('size')}")
    poster, brief, _ = pipeline.generate_poster(keywords, seed=seed if seed > 0 else None, template=template)
    print(f"[DEBUG] Poster generated: {type(poster)}, size={poster.size if poster else None}")
    
    flux_image = brief.get('flux_image')
    rendered_texts = brief.get('rendered_texts', [])
    print(f"[DEBUG] flux_image={type(flux_image)}, rendered_texts={len(rendered_texts)}")
    
    title = brief.get('story title', brief.get('title', keywords.title()))
    captions = brief.get('captions', [])
    info = f"✅ Generated\n**Title:** {title}\n**Captions:** {', '.join(captions) if captions else 'None'}"
    
    defaults = [(r['text'].replace('\n', '\\n'), r.get('ref_x', (r['bbox'][0]+r['bbox'][2])//2), (r['bbox'][1]+r['bbox'][3])//2, r['size'], r['color']) for r in rendered_texts[:3]]
    while len(defaults) < 3:
        defaults.append(('', 360, 900+len(defaults)*50, 37, '#043bb4'))
    
    state = {"flux_image": flux_image, "template": copy.deepcopy(template)}
    print(f"[DEBUG] Returning 4 poster copies + state")
    return poster, poster, poster, poster, info, state, flux_image, *defaults[0], *defaults[1], *defaults[2]

def apply_edits(state, flux_img, t1_text, t1_x, t1_y, t1_size, t1_color, t2_text, t2_x, t2_y, t2_size, t2_color, t3_text, t3_x, t3_y, t3_size, t3_color):
    print(f"[DEBUG] apply_edits called: t1_text={t1_text[:20] if t1_text else 'None'}..., flux_img={type(flux_img)}")
    if not flux_img or not state:
        print("[DEBUG] No flux_image, returning None")
        return None, None, None
    
    template = state.get("template")
    poster = Image.new('RGB', tuple(template['size']), tuple(int(template.get('background_color', '#faefcf').lstrip('#')[i:i+2], 16) for i in (0,2,4)))
    
    img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
    if img_layer:
        poster.paste(flux_img, (img_layer['bbox'][0], img_layer['bbox'][1]))
    
    draw = ImageDraw.Draw(poster)
    fonts_config = template.get('fonts', {})
    
    for idx, (text, x, y, size, color) in enumerate([(t1_text, t1_x, t1_y, t1_size, t1_color), (t2_text, t2_x, t2_y, t2_size, t2_color), (t3_text, t3_x, t3_y, t3_size, t3_color)]):
        if text.strip():
            font_info = fonts_config.get(['title', 'caption', 'caption2'][idx], {})
            try:
                font = ImageFont.truetype(f"fonts/{font_info.get('family', 'Graduate-Regular.ttf')}", int(size))
            except:
                font = ImageFont.load_default()
            
            rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0,2,4)) if isinstance(color, str) and color.startswith('#') else (0,0,0)
            text = text.replace('\\n', '\n')
            bbox = draw.multiline_textbbox((0, 0), text, font=font)
            y_pos = int(y) - (bbox[3] - bbox[1]) // 2
            
            for line in text.split('\n'):
                line_bbox = draw.textbbox((0, 0), line, font=font)
                x_pos = int(x) - (line_bbox[2] - line_bbox[0]) // 2
                draw.text((x_pos, y_pos), line, font=font, fill=rgb)
                y_pos += line_bbox[3] - line_bbox[1] + 5
    
    print(f"[DEBUG] apply_edits returning poster: {type(poster)}, size={poster.size}")
    return poster, poster, poster

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 Key2Poster: AI Poster Generator\nGenerate → Edit → Export")
    
    state = gr.State()
    flux_state = gr.State()
    
    with gr.Row():
        with gr.Column(scale=1):
            keywords = gr.Textbox(label="Keywords (2-5 words)", placeholder="anime love story japanese")
            template_num = gr.Number(label=f"Template (0=random, 1-{len(templates)})", value=0, precision=0)
            seed = gr.Number(label="Seed (0=random)", value=0, precision=0)
            gen_btn = gr.Button("🎨 Generate", variant="primary")
        
        with gr.Column(scale=2):
            with gr.Tab("Preview"):
                preview = gr.Image(label="Poster", height=700)
                status = gr.Markdown("Ready...")
            
            with gr.Tab("Title"):
                with gr.Row():
                    out1 = gr.Image(label="Poster", height=700)
                    with gr.Column():
                        t1_text = gr.Textbox(label="Text", lines=3)
                        t1_x = gr.Slider(0, 720, label="X", value=360)
                        t1_y = gr.Slider(0, 1080, label="Y", value=900)
                        t1_size = gr.Slider(10, 200, label="Size", value=37, step=1)
                        t1_color = gr.ColorPicker(label="Color", value="#043bb4")
            
            with gr.Tab("Caption 1"):
                with gr.Row():
                    out2 = gr.Image(label="Poster", height=700)
                    with gr.Column():
                        t2_text = gr.Textbox(label="Text", lines=3)
                        t2_x = gr.Slider(0, 720, label="X", value=360)
                        t2_y = gr.Slider(0, 1080, label="Y", value=950)
                        t2_size = gr.Slider(10, 200, label="Size", value=20, step=1)
                        t2_color = gr.ColorPicker(label="Color", value="#043bb4")
            
            with gr.Tab("Caption 2"):
                with gr.Row():
                    out3 = gr.Image(label="Poster", height=700)
                    with gr.Column():
                        t3_text = gr.Textbox(label="Text", lines=3)
                        t3_x = gr.Slider(0, 720, label="X", value=360)
                        t3_y = gr.Slider(0, 1080, label="Y", value=1000)
                        t3_size = gr.Slider(10, 200, label="Size", value=20, step=1)
                        t3_color = gr.ColorPicker(label="Color", value="#043bb4")
    
    text_inputs = [t1_text, t1_x, t1_y, t1_size, t1_color, t2_text, t2_x, t2_y, t2_size, t2_color, t3_text, t3_x, t3_y, t3_size, t3_color]
    
    gen_btn.click(generate_poster, [keywords, seed, template_num], [preview, out1, out2, out3, status, state, flux_state] + text_inputs)
    
    for inp in [t1_x, t1_y, t1_size, t1_color, t2_x, t2_y, t2_size, t2_color, t3_x, t3_y, t3_size, t3_color]:
        inp.change(apply_edits, [state, flux_state] + text_inputs, [out1, out2, out3])
    
    t1_text.blur(apply_edits, [state, flux_state] + text_inputs, [out1, out2, out3])
    t2_text.blur(apply_edits, [state, flux_state] + text_inputs, [out1, out2, out3])
    t3_text.blur(apply_edits, [state, flux_state] + text_inputs, [out1, out2, out3])
    
    gr.Examples([["anime love story japanese", 0, 42], ["cyberpunk neon city", 1, 123]], [keywords, template_num, seed])

if __name__ == "__main__":
    demo.launch()
