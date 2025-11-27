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
poster_state = {"image": None, "flux_image": None, "title": "", "bg_color": "#faefcf", "text_color": "#043bb4", "template": None}

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
        
        print(f"\n=== Poster State Debug ===")
        print(f"flux_image exists: {poster_state['flux_image'] is not None}")
        if poster_state['flux_image']:
            print(f"flux_image size: {poster_state['flux_image'].size}")
        
        # Get template colors and update state
        bg_color = template.get('background_color', '#faefcf')
        font_info = template.get('font', {})
        text_color = font_info.get('color', '#043bb4')
        
        poster_state['bg_color'] = bg_color
        poster_state['text_color'] = text_color
        
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
    """Apply text edits and regenerate poster"""
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
    
    # Paste FLUX image
    img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
    if img_layer:
        img_bbox = img_layer['bbox']
        poster.paste(flux_image, (img_bbox[0], img_bbox[1]))
    
    draw = ImageDraw.Draw(poster)
    
    # Draw texts
    texts = [
        (title_text, title_x, title_y, title_size, title_color),
        (caption1_text, caption1_x, caption1_y, caption1_size, caption1_color),
        (caption2_text, caption2_x, caption2_y, caption2_size, caption2_color)
    ]
    
    for text, center_x, center_y, size, color in texts:
        if text.strip():
            try:
                font = ImageFont.truetype("fonts/Graduate-Regular.ttf", int(size))
            except:
                font = ImageFont.load_default()
            
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Handle multi-line text
            lines = text.split('\n')
            
            # Calculate total text bbox
            max_width = 0
            total_height = 0
            for line in lines:
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                line_height = line_bbox[3] - line_bbox[1]
                max_width = max(max_width, line_width)
                total_height += line_height
            
            # Convert center position to top-left corner
            x = int(center_x) - max_width // 2
            y = int(center_y) - total_height // 2
            
            draw.multiline_text((x, y), text, font=font, fill=rgb, align='center')
    
    poster_state["image"] = poster
    return poster, poster, poster

def get_text_defaults():
    """Get default text values from poster state"""
    template = poster_state.get("template") or templates[0]
    text_layers = [l for l in template['layers'] if 'text' in l['name'].lower() or 'title' in l['name'].lower() or 'caption' in l['name'].lower()]
    fonts_config = template.get('fonts', {})
    
    texts = [poster_state.get('title', '')] + poster_state.get('captions', [])
    defaults = []
    
    for idx in range(3):
        if idx < len(text_layers) and idx < len(texts):
            layer = text_layers[idx]
            text = texts[idx]
            bbox = layer['bbox']
            layer_name = layer['name'].lower()
            
            if 'caption2' in layer_name:
                font_info = fonts_config.get('caption2', {})
            elif 'caption' in layer_name:
                font_info = fonts_config.get('caption', {})
            else:
                font_info = fonts_config.get('title', {})
            
            # Convert top-left to center position
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            defaults.append((text, center_x, center_y, font_info.get('size', 37), font_info.get('color', '#043bb4')))
        else:
            defaults.append(('', 100, 100 + idx * 100, 37, '#043bb4'))
    
    return defaults

def load_to_canvas(image, title):
    """Load poster to Fabric.js canvas"""
    if poster_state["image"] is None:
        return "<p style='color:red;font-size:20px;padding:50px'>❌ Generate poster first!</p>"
    
    # Use FLUX image if available, otherwise use full poster
    canvas_image = poster_state.get("flux_image") or poster_state["image"]
    
    import base64
    from io import BytesIO
    
    template = poster_state.get("template") or templates[0]
    img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
    text_layers = [l for l in template['layers'] if 'text' in l['name'].lower() or 'title' in l['name'].lower() or 'caption' in l['name'].lower()]
    
    img_bbox = img_layer['bbox'] if img_layer else [0, 0, 720, 1080]
    
    print(f"Loading canvas with title: {poster_state['title']}")
    print(f"Canvas image size: {canvas_image.size}")
    print(f"Found {len(text_layers)} text layers")
    
    # Save image as base64
    buffered = BytesIO()
    canvas_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    print(f"Base64 length: {len(img_str)}")
    
    # Generate text layers JavaScript
    text_layers_js = _generate_text_layers_js()
    
    html = f"""
    <div style="text-align:center;padding:20px">
        <div style="margin-bottom:10px;color:#666;font-weight:bold">Click elements to select • Drag to move • Drag corners to resize • Double-click text to edit</div>
        <div id="status" style="margin-bottom:10px;color:#2196F3">Initializing...</div>
        <canvas id="posterCanvas" width="720" height="1080" style="border:2px solid #333;background:#faefcf"></canvas>
        <br>
        <button onclick="exportCanvas()" style="margin:10px;padding:10px 20px;background:#4CAF50;color:white;border:none;cursor:pointer;border-radius:5px">💾 Export PNG</button>
        <button onclick="deleteSelected()" style="margin:10px;padding:10px 20px;background:#f44336;color:white;border:none;cursor:pointer;border-radius:5px">🗑️ Delete Selected</button>
        <button onclick="bringToFront()" style="margin:10px;padding:10px 20px;background:#2196F3;color:white;border:none;cursor:pointer;border-radius:5px">⬆️ Bring to Front</button>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js"></script>
    <script>
        document.getElementById('status').innerText = 'Script loaded';
        document.getElementById('status').style.color = 'orange';
        console.log('Script executing...');
        
        // Wait for Fabric.js to load
        if(typeof fabric === 'undefined') {{
            document.getElementById('status').innerText = '❌ Fabric.js not loaded';
            document.getElementById('status').style.color = 'red';
            console.error('Fabric.js not available');
        }} else {{
            document.getElementById('status').innerText = 'Fabric.js loaded';
            console.log('Fabric.js version:', fabric.version);
            
            if(window.posterCanvas) {{
                window.posterCanvas.dispose();
            }}
            
            window.posterCanvas = new fabric.Canvas('posterCanvas');
            var canvas = window.posterCanvas;
        
        // Set background color
        canvas.backgroundColor = '{poster_state["bg_color"]}';
        canvas.renderAll();
        document.getElementById('status').innerText = 'Background loaded';
        console.log('Background set to {poster_state["bg_color"]}');
        
        // Load FLUX image
        var imgElement = new Image();
        imgElement.crossOrigin = 'anonymous';
        
        imgElement.onload = function() {{
            document.getElementById('status').innerText = 'Image loaded, adding to canvas...';
            console.log('Image dimensions:', imgElement.width, 'x', imgElement.height);
            
            var fabricImg = new fabric.Image(imgElement, {{
                left: {img_bbox[0]},
                top: {img_bbox[1]},
                selectable: true,
                hasControls: true,
                hasBorders: true,
                borderColor: 'blue',
                cornerColor: 'blue',
                cornerSize: 10
            }});
            
            // Scale to fit
            fabricImg.scaleToWidth({img_bbox[2] - img_bbox[0]});
            canvas.add(fabricImg);
            canvas.renderAll();
            
            document.getElementById('status').innerText = 'Image added! Adding text...';
            console.log('Image added, objects count:', canvas.getObjects().length);
            
            // Add all text layers
            {text_layers_js}
            
            document.getElementById('status').innerText = '✅ Ready! Click elements to edit';
            document.getElementById('status').style.color = 'green';
            console.log('All elements added, total objects:', canvas.getObjects().length);
        }};
        
        imgElement.onerror = function(e) {{
            document.getElementById('status').innerText = '❌ Failed to load image';
            document.getElementById('status').style.color = 'red';
            console.error('Image load error:', e);
        }};
        
        console.log('Starting image load...');
        imgElement.src = 'data:image/png;base64,{img_str}';
        
        function exportCanvas() {{
            var dataURL = canvas.toDataURL({{format: 'png', quality: 1}});
            var link = document.createElement('a');
            link.download = 'poster_edited_' + Date.now() + '.png';
            link.href = dataURL;
            link.click();
        }}
        
        function deleteSelected() {{
            var active = canvas.getActiveObject();
            if(active) {{
                canvas.remove(active);
                canvas.renderAll();
            }} else {{
                alert('Select an element first');
            }}
        }}
        
        function bringToFront() {{
            var active = canvas.getActiveObject();
            if(active) {{
                canvas.bringToFront(active);
                canvas.renderAll();
            }}
        }}
        
        // Debug info
        setTimeout(function() {{
            console.log('Final canvas state:');
            console.log('- Objects:', canvas.getObjects().length);
            console.log('- Background:', canvas.backgroundColor);
            console.log('- Size:', canvas.width, 'x', canvas.height);
        }}, 2000);
        }}
    </script>
    """
    return html

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
                        title_size = gr.Slider(10, 100, label="Font Size", value=37, step=1)
                        title_color = gr.ColorPicker(label="Color", value="#043bb4")
            
            with gr.Tab("Caption 1"):
                with gr.Row():
                    output_image2 = gr.Image(label="Poster Preview", height=700)
                    with gr.Column():
                        caption1_text = gr.Textbox(label="Text (use \\n for line break)", value="", lines=3)
                        caption1_x = gr.Slider(0, 720, label="X Center", value=360)
                        caption1_y = gr.Slider(0, 1080, label="Y Center", value=950)
                        caption1_size = gr.Slider(10, 100, label="Font Size", value=20, step=1)
                        caption1_color = gr.ColorPicker(label="Color", value="#043bb4")
            
            with gr.Tab("Caption 2"):
                with gr.Row():
                    output_image3 = gr.Image(label="Poster Preview", height=700)
                    with gr.Column():
                        caption2_text = gr.Textbox(label="Text (use \\n for line break)", value="", lines=3)
                        caption2_x = gr.Slider(0, 720, label="X Center", value=360)
                        caption2_y = gr.Slider(0, 1080, label="Y Center", value=1000)
                        caption2_size = gr.Slider(10, 100, label="Font Size", value=20, step=1)
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
    
    gen_btn.click(generate_with_template, [keywords, seed, template_num], [preview_image, output_image, status]).then(
        lambda img: (img, img, img), output_image, [output_image2, output_image3]
    ).then(
        update_ui_colors, None, [title_input, bg_color, text_color]
    ).then(
        load_defaults, None, [title_text, title_x, title_y, title_size, title_color,
                              caption1_text, caption1_x, caption1_y, caption1_size, caption1_color,
                              caption2_text, caption2_x, caption2_y, caption2_size, caption2_color]
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
