"""Template-based Poster Generator"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from src.color_contrast import get_average_color, adjust_text_color
from PIL import Image, ImageDraw, ImageFont
import json
import time
import random
import glob

pipeline = Key2PosterPipeline(use_flux=True, add_title=False, genre_lora=False, remove_text=True, super_resolution=False, aggressive_text_removal=True)

# Load all templates (sorted numerically)
import re
templates = []
template_files = glob.glob("templates/template*_layers.json")
template_files.sort(key=lambda x: int(re.search(r'template(\d+)', x).group(1)))
for template_file in template_files:
    with open(template_file) as f:
        templates.append(json.load(f))
print(f"Loaded {len(templates)} templates")

# Store current poster state
poster_state = {"image": None, "flux_image": None, "title": "", "bg_color": "#faefcf", "text_color": "#043bb4", "template": None, "fonts": {}}

def hex_to_rgb(color):
    """Convert color to RGB tuple"""
    print(f"Converting color: {color} (type: {type(color)})")
    try:
        if isinstance(color, str) and color.startswith('#'):
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            print(f"  -> RGB: {rgb}")
            return rgb
        elif isinstance(color, str) and color.startswith('rgb'):
            import re
            nums = re.findall(r'\d+', color)
            rgb = tuple(min(255, int(n)) for n in nums[:3])
            print(f"  -> RGB: {rgb}")
            return rgb
        elif isinstance(color, dict):
            # Gradio ColorPicker returns dict with 'r', 'g', 'b' keys
            rgb = (int(color.get('r', 250)), int(color.get('g', 239)), int(color.get('b', 207)))
            print(f"  -> RGB: {rgb}")
            return rgb
    except Exception as e:
        print(f"  -> Error: {e}")
    return (250, 239, 207)



def generate_with_template(keywords, seed, template_num):
    try:
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, None, "❌ Provide 2-5 keywords"
        
        # Select template
        if template_num == 0:
            template = random.choice(templates)
        else:
            template_idx = int(template_num) - 1
            if 0 <= template_idx < len(templates):
                template = templates[template_idx]
            else:
                return None, None, f"❌ Template {template_num} not found (available: 1-{len(templates)})"
        
        # Generate complete poster with template
        poster, brief, _ = pipeline.generate_poster(keywords, seed=seed if seed > 0 else None, template=template)
        
        # Store both final poster and FLUX image for canvas editing
        poster_state["image"] = poster
        poster_state["flux_image"] = brief.get('flux_image')  # Raw FLUX image without text
        poster_state["title"] = brief.get('title', " ".join(keyword_list[:3]).title())
        poster_state["captions"] = brief.get('captions', [])
        poster_state["template"] = template
        poster_state["rendered_texts"] = brief.get('rendered_texts', [])
        
        print(f"\n=== Poster State Debug ===")
        print(f"flux_image exists: {poster_state['flux_image'] is not None}")
        if poster_state['flux_image']:
            print(f"flux_image size: {poster_state['flux_image'].size}")
        
        # Get template colors and update state
        bg_color = template.get('background_color', '#faefcf')
        font_info = template.get('font', {})
        text_color = font_info.get('color', '#043bb4')
        
        poster_state['bg_color'] = bg_color
        poster_state['fonts'] = template.get('fonts', {})
        
        # Display LLM results
        captions_text = "\n".join([f"  {i+1}. {cap}" for i, cap in enumerate(poster_state['captions'])]) if poster_state['captions'] else "  None"
        info = f"""✅ Generated

**LLM Title:** {poster_state['title']}
**LLM Captions:**
{captions_text}
**Enhanced Prompt:** {brief.get('prompt', 'N/A')[:80]}...
**Template:** {templates.index(template)+1}/{len(templates)}
**BG:** {bg_color} | **Text:** {text_color}"""
        
        return poster, poster, info
        
    except Exception as e:
        import traceback
        return None, None, f"❌ Error: {str(e)}\n{traceback.format_exc()}"

def compose_poster(image, title, bg_color, text_color):
    """Compose poster from layers"""
    template = poster_state.get("template") or templates[0]
    
    # Background layer
    bg_rgb = hex_to_rgb(bg_color)
    poster = Image.new('RGB', tuple(template['size']), bg_rgb)
    
    # Image layer - find image layer in template (case-insensitive)
    img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
    if img_layer:
        img_bbox = img_layer['bbox']
        img_w, img_h = img_bbox[2] - img_bbox[0], img_bbox[3] - img_bbox[1]
        center_img = image.resize((img_w, img_h), Image.Resampling.LANCZOS)
        poster.paste(center_img, (img_bbox[0], img_bbox[1]))
        print(f"  ✓ Pasted {image.size} image resized to {center_img.size} at {img_bbox}")
    
    # Text layer - find text layer in template (case-insensitive)
    text_layer = next((l for l in template['layers'] if 'text' in l['name'].lower()), None)
    if text_layer:
        draw = ImageDraw.Draw(poster)
        font_info = template.get('font', {})
        font_family = font_info.get('family', 'Graduate-Regular.ttf')
        font_size = font_info.get('size', 37)
        font_align = font_info.get('align', 'center')
        
        font = ImageFont.truetype(f"fonts/{font_family}", font_size)
        text_bbox = text_layer['bbox']
        
        if font_align == 'left':
            text_x = text_bbox[0]
            anchor = 'lt'
        else:
            text_x = (text_bbox[0] + text_bbox[2]) // 2
            anchor = 'mt'
        
        # Auto-adjust text color for contrast
        print(f"  Original text color: {hex_to_rgb(text_color)}")
        bg_avg_color = get_average_color(poster, text_bbox)
        text_rgb = hex_to_rgb(text_color)
        text_rgb = adjust_text_color(bg_avg_color, text_rgb)
        print(f"  Final text color: {text_rgb}")
        
        # Text wrapping
        max_width = text_bbox[2] - text_bbox[0]
        words = title.replace('\n', ' ').replace('\r', ' ').split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        text_y = text_bbox[1]
        
        if font_align == 'left':
            draw.multiline_text((text_bbox[0], text_y), '\n'.join(lines), font=font, fill=text_rgb, align='left')
        elif font_align == 'right':
            y_offset = text_y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = text_bbox[2] - line_width
                draw.text((text_x, y_offset), line, font=font, fill=text_rgb)
                y_offset += bbox[3] - bbox[1] + 5
        else:
            y_offset = text_y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = text_bbox[0] + (max_width - line_width) // 2
                draw.text((text_x, y_offset), line, font=font, fill=text_rgb)
                y_offset += bbox[3] - bbox[1] + 5
    
    return poster

def edit_poster(title, bg_color, text_color):
    """Edit poster attributes"""
    if poster_state["image"] is None:
        return None, "❌ Generate poster first"
    
    # Since pipeline handles all text rendering, editing requires regeneration
    # For now, just return the current poster
    return poster_state["image"], "❌ Editing not supported yet - regenerate with new keywords instead"

def apply_text_edits(title_text, title_x, title_y, title_size, title_color, 
                     caption1_text, caption1_x, caption1_y, caption1_size, caption1_color,
                     caption2_text, caption2_x, caption2_y, caption2_size, caption2_color):
    """Apply text edits - sliders control center position"""
    if poster_state["image"] is None:
        return None, None, None
    
    flux_image = poster_state.get("flux_image") or poster_state["image"]
    template = poster_state.get("template") or templates[0]
    
    from PIL import ImageDraw, ImageFont
    
    poster_size = tuple(template['size'])
    bg_color_hex = poster_state.get('bg_color', '#faefcf')
    hex_color = bg_color_hex.lstrip('#')
    bg_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    poster = Image.new('RGB', poster_size, bg_rgb)
    
    img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
    if img_layer:
        img_bbox = img_layer['bbox']
        poster.paste(flux_image, (img_bbox[0], img_bbox[1]))
    
    draw = ImageDraw.Draw(poster)
    
    texts = [
        (title_text, title_x, title_y, title_size, title_color),
        (caption1_text, caption1_x, caption1_y, caption1_size, caption1_color),
        (caption2_text, caption2_x, caption2_y, caption2_size, caption2_color)
    ]
    
    fonts_config = poster_state.get('fonts', {})
    font_names = ['title', 'caption', 'caption2']
    text_layers = [l for l in template['layers'] if 'text' in l['name'].lower() or 'title' in l['name'].lower() or 'caption' in l['name'].lower()]
    
    for idx, (text, center_x, center_y, size, color) in enumerate(texts):
        if text.strip():
            font_info = fonts_config.get(font_names[idx], {})
            font_family = font_info.get('family', 'Graduate-Regular.ttf')
            align = font_info.get('align', 'center')
            
            try:
                font = ImageFont.truetype(f"fonts/{font_family}", int(size))
            except:
                font = ImageFont.load_default()
            
            if isinstance(color, str) and color.startswith('#'):
                hex_color = color.lstrip('#')
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) if len(hex_color) == 6 else (0, 0, 0)
            elif isinstance(color, dict):
                rgb = (int(color.get('r', 0)), int(color.get('g', 0)), int(color.get('b', 0)))
            else:
                rgb = (0, 0, 0)
            
            text = text.replace('\\n', '\n')
            
            # Calculate text bbox to convert center to top-left
            bbox = draw.multiline_textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Convert center position to top-left based on alignment
            if align == 'left':
                x = int(center_x)
                y = int(center_y) - text_height // 2
            elif align == 'right':
                x = int(center_x) - text_width
                y = int(center_y) - text_height // 2
            else:  # center
                x = int(center_x) - text_width // 2
                y = int(center_y) - text_height // 2
            
            draw.multiline_text((x, y), text, font=font, fill=rgb, align=align)
    
    poster_state["image"] = poster
    return poster, poster, poster

def get_text_defaults():
    """Get default text values from rendered poster"""
    rendered_texts = poster_state.get('rendered_texts', [])
    defaults = []
    
    for idx in range(3):
        if idx < len(rendered_texts):
            rendered = rendered_texts[idx]
            bbox = rendered['bbox']
            # Return center position for intuitive slider control
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            text_display = rendered['text'].replace('\n', '\\n')
            defaults.append((text_display, center_x, center_y, rendered['size'], rendered['color']))
        else:
            defaults.append(('', 360, 900 + idx * 50, 37, '#043bb4'))
    
    return defaults

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 Adobe-like Poster Editor\nGenerate → Drag & Edit → Export")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1️⃣ Generate")
            keywords = gr.Textbox(label="Keywords (2-5 words)", placeholder="anime love story japanese")
            template_num = gr.Number(label=f"Template (0=random, 1-{len(templates)})", value=0, precision=0)
            seed = gr.Number(label="Seed (0 = random)", value=0, precision=0)
            gen_btn = gr.Button("🎨 Generate Poster", variant="primary")
            
            gr.Markdown("### 2️⃣ Quick Edit")
            title_input = gr.Textbox(label="Title", placeholder="Anime Love Story")
            bg_color = gr.ColorPicker(label="Background Color", value="#faefcf")
            text_color = gr.ColorPicker(label="Text Color", value="#043bb4")
            edit_btn = gr.Button("✏️ Update")
            

        
        with gr.Column(scale=2):
            with gr.Tab("Preview"):
                preview_image = gr.Image(label="Poster Preview", height=700)
                status = gr.Markdown("Ready...")
            
            with gr.Tab("Title"):
                with gr.Row():
                    output_image = gr.Image(label="Poster Preview", height=700)
                    with gr.Column():
                        title_text = gr.Textbox(label="Text (use \\n for line break)", value="", lines=3)
                        title_x = gr.Slider(0, 720, label="X Center", value=360)
                        title_y = gr.Slider(0, 1080, label="Y Center", value=900)
                        title_size = gr.Slider(10, 200, label="Font Size", value=37, step=1)
                        title_color = gr.ColorPicker(label="Color", value="#043bb4")
            
            with gr.Tab("Caption 1"):
                with gr.Row():
                    output_image2 = gr.Image(label="Poster Preview", height=700)
                    with gr.Column():
                        caption1_text = gr.Textbox(label="Text (use \\n for line break)", value="", lines=3)
                        caption1_x = gr.Slider(0, 720, label="X Center", value=360)
                        caption1_y = gr.Slider(0, 1080, label="Y Center", value=950)
                        caption1_size = gr.Slider(10, 200, label="Font Size", value=20, step=1)
                        caption1_color = gr.ColorPicker(label="Color", value="#043bb4")
            
            with gr.Tab("Caption 2"):
                with gr.Row():
                    output_image3 = gr.Image(label="Poster Preview", height=700)
                    with gr.Column():
                        caption2_text = gr.Textbox(label="Text (use \\n for line break)", value="", lines=3)
                        caption2_x = gr.Slider(0, 720, label="X Center", value=360)
                        caption2_y = gr.Slider(0, 1080, label="Y Center", value=1000)
                        caption2_size = gr.Slider(10, 200, label="Font Size", value=20, step=1)
                        caption2_color = gr.ColorPicker(label="Color", value="#043bb4")
    
    def update_ui_colors():
        title = poster_state.get("title", "")
        captions = poster_state.get("captions", [])
        if captions:
            title += "\n" + "\n".join(captions[:2])  # Show first 2 captions
        return title, poster_state.get("bg_color", "#faefcf"), poster_state.get("text_color", "#043bb4")
    
    def load_defaults():
        defaults = get_text_defaults()
        return defaults[0] + defaults[1] + defaults[2]
    
    def load_and_render():
        defaults = get_text_defaults()
        # Immediately render with correct positions
        result = apply_text_edits(
            defaults[0][0], defaults[0][1], defaults[0][2], defaults[0][3], defaults[0][4],
            defaults[1][0], defaults[1][1], defaults[1][2], defaults[1][3], defaults[1][4],
            defaults[2][0], defaults[2][1], defaults[2][2], defaults[2][3], defaults[2][4]
        )
        return defaults[0] + defaults[1] + defaults[2] + result
    
    gen_btn.click(generate_with_template, [keywords, seed, template_num], [preview_image, output_image, status]).then(
        update_ui_colors, None, [title_input, bg_color, text_color]
    ).then(
        load_and_render, None, [title_text, title_x, title_y, title_size, title_color,
                                caption1_text, caption1_x, caption1_y, caption1_size, caption1_color,
                                caption2_text, caption2_x, caption2_y, caption2_size, caption2_color,
                                output_image, output_image2, output_image3]
    )
    
    edit_btn.click(edit_poster, [title_input, bg_color, text_color], [preview_image, status])
    
    # Real-time updates on slider/input change
    inputs = [title_text, title_x, title_y, title_size, title_color,
              caption1_text, caption1_x, caption1_y, caption1_size, caption1_color,
              caption2_text, caption2_x, caption2_y, caption2_size, caption2_color]
    
    for inp in inputs:
        inp.change(apply_text_edits, inputs, [output_image, output_image2, output_image3])
    
    gr.Examples(
        [["anime love story japanese", 0, 42], ["cyberpunk neon city", 1, 123]],
        [keywords, template_num, seed]
    )

if __name__ == "__main__":
    demo.launch()
