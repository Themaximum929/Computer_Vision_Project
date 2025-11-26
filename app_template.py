"""Template-based Poster Generator"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from PIL import Image, ImageDraw, ImageFont
import json
import time
import random
import glob

pipeline = Key2PosterPipeline(use_flux=True, add_title=False, genre_lora=False, remove_text=True, super_resolution=False, aggressive_text_removal=True)

# Load all templates
templates = []
for template_file in glob.glob("templates/template*_layers.json"):
    with open(template_file) as f:
        templates.append(json.load(f))
print(f"Loaded {len(templates)} templates")

# Store current poster state
poster_state = {"image": None, "title": "", "bg_color": "#faefcf", "text_color": "#043bb4", "template": None}

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
        
        # Generate FLUX image (no text) - pass template to pipeline
        image, brief, _ = pipeline.generate_poster(keywords, seed=seed if seed > 0 else None, template=template)
        
        # Extract FLUX image from composed poster
        img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
        if img_layer:
            img_bbox = img_layer['bbox']
            flux_image = image.crop((img_bbox[0], img_bbox[1], img_bbox[2], img_bbox[3]))
        else:
            flux_image = image
        
        # Store for editing
        poster_state["image"] = flux_image
        poster_state["title"] = " ".join(keyword_list[:3]).title()
        poster_state["template"] = template
        
        # Get template colors and update state
        bg_color = template.get('background_color', '#faefcf')
        font_info = template.get('font', {})
        text_color = font_info.get('color', '#043bb4')
        
        poster_state['bg_color'] = bg_color
        poster_state['text_color'] = text_color
        
        # Recompose with template colors
        poster = compose_poster(flux_image, poster_state["title"], bg_color, text_color)
        
        info = f"✅ Generated\n\n**Title:** {poster_state['title']}\n**Template:** {templates.index(template)+1}/{len(templates)}\n**Font:** {font_info.get('family', 'Graduate-Regular.ttf')} ({font_info.get('size', 37)}px)\n**BG:** {bg_color}\n**Text:** {text_color}"
        
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
            draw.multiline_text((text_bbox[0], text_y), '\n'.join(lines), font=font, fill=hex_to_rgb(text_color), align='left')
        elif font_align == 'right':
            y_offset = text_y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = text_bbox[2] - line_width
                draw.text((text_x, y_offset), line, font=font, fill=hex_to_rgb(text_color))
                y_offset += bbox[3] - bbox[1] + 5
        else:
            y_offset = text_y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = text_bbox[0] + (max_width - line_width) // 2
                draw.text((text_x, y_offset), line, font=font, fill=hex_to_rgb(text_color))
                y_offset += bbox[3] - bbox[1] + 5
    
    return poster

def edit_poster(title, bg_color, text_color):
    """Edit poster attributes"""
    if poster_state["image"] is None:
        return None, "❌ Generate poster first"
    
    poster_state["title"] = title
    poster_state["bg_color"] = bg_color
    poster_state["text_color"] = text_color
    
    poster = compose_poster(poster_state["image"], title, bg_color, text_color)
    info = f"✅ Updated\n\n**Title:** {title}\n**BG:** {bg_color}\n**Text:** {text_color}"
    
    return poster, info

def load_to_canvas(image, title):
    """Load poster to Fabric.js canvas"""
    if poster_state["image"] is None:
        return "<p style='color:red;font-size:20px;padding:50px'>❌ Generate poster first!</p>"
    
    import base64
    from io import BytesIO
    
    template = poster_state.get("template") or templates[0]
    img_layer = next((l for l in template['layers'] if l['name'] == 'image'), None)
    text_layer = next((l for l in template['layers'] if l['name'] == 'text'), None)
    
    img_bbox = img_layer['bbox'] if img_layer else [54, 59, 655, 873]
    text_bbox = text_layer['bbox'] if text_layer else [240, 930, 472, 989]
    
    print(f"Loading canvas with title: {poster_state['title']}")
    print(f"Image size: {poster_state['image'].size}")
    
    # Save FLUX image as base64
    buffered = BytesIO()
    poster_state["image"].save(buffered, format="PNG")
    flux_img_str = base64.b64encode(buffered.getvalue()).decode()
    print(f"Base64 length: {len(flux_img_str)}")
    
    html = f"""
    <div style="text-align:center;padding:20px">
        <div style="margin-bottom:10px;color:#666;font-weight:bold">Click elements to select • Drag to move • Drag corners to resize • Double-click text to edit</div>
        <div id="status" style="margin-bottom:10px;color:#2196F3">Loading canvas...</div>
        <canvas id="posterCanvas" width="720" height="1080" style="border:2px solid #333;background:#faefcf"></canvas>
        <br>
        <button onclick="exportCanvas()" style="margin:10px;padding:10px 20px;background:#4CAF50;color:white;border:none;cursor:pointer;border-radius:5px">💾 Export PNG</button>
        <button onclick="deleteSelected()" style="margin:10px;padding:10px 20px;background:#f44336;color:white;border:none;cursor:pointer;border-radius:5px">🗑️ Delete Selected</button>
        <button onclick="bringToFront()" style="margin:10px;padding:10px 20px;background:#2196F3;color:white;border:none;cursor:pointer;border-radius:5px">⬆️ Bring to Front</button>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js"></script>
    <script>
        console.log('Initializing canvas...');
        
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
            
            // Add text after image loads
            var textObj = new fabric.IText('{poster_state["title"]}', {{
                left: {(text_bbox[0] + text_bbox[2]) // 2},
                top: {text_bbox[1]},
                fontSize: 37,
                fill: '{poster_state["text_color"]}',
                fontFamily: 'Arial, sans-serif',
                selectable: true,
                editable: true,
                hasControls: true,
                borderColor: 'red',
                cornerColor: 'red',
                cornerSize: 10
            }});
            
            canvas.add(textObj);
            canvas.renderAll();
            
            document.getElementById('status').innerText = '✅ Ready! Click elements to edit';
            document.getElementById('status').style.color = 'green';
            console.log('Text added, total objects:', canvas.getObjects().length);
        }};
        
        imgElement.onerror = function(e) {{
            document.getElementById('status').innerText = '❌ Failed to load image';
            document.getElementById('status').style.color = 'red';
            console.error('Image load error:', e);
        }};
        
        console.log('Starting image load...');
        imgElement.src = 'data:image/png;base64,{flux_img_str}';
        
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
            
            load_canvas_btn = gr.Button("🎨 Open Canvas Editor", variant="secondary")
        
        with gr.Column(scale=2):
            with gr.Tab("Preview"):
                output_image = gr.Image(label="Poster Preview", height=700)
                preview_image = gr.Image(label="Editable Preview", visible=False)
                status = gr.Markdown("Ready...")
            
            with gr.Tab("Canvas Editor") as canvas_tab:
                canvas_html = gr.HTML("<p style='padding:50px;font-size:18px'>Generate poster first, then click 'Open Canvas Editor'</p>")
                gr.Markdown("""
                **Instructions:**
                - 🖱️ Drag elements to move
                - 🔄 Drag corners to resize
                - 🖊️ Double-click text to edit
                - 💾 Click Export to download
                """)
    
    def update_ui_colors():
        return poster_state.get("title", ""), poster_state.get("bg_color", "#faefcf"), poster_state.get("text_color", "#043bb4")
    
    gen_btn.click(generate_with_template, [keywords, seed, template_num], [output_image, preview_image, status]).then(
        update_ui_colors, None, [title_input, bg_color, text_color]
    )
    edit_btn.click(edit_poster, [title_input, bg_color, text_color], [output_image, status])
    def load_and_log():
        print("\n=== Loading Canvas ===")
        print(f"Image exists: {poster_state['image'] is not None}")
        print(f"Title: {poster_state['title']}")
        print(f"BG Color: {poster_state['bg_color']}")
        print(f"Text Color: {poster_state['text_color']}")
        return load_to_canvas(None, None)
    
    load_canvas_btn.click(load_and_log, None, canvas_html)
    
    gr.Examples(
        [["anime love story japanese", 0, 42], ["cyberpunk neon city", 1, 123]],
        [keywords, template_num, seed]
    )

if __name__ == "__main__":
    demo.launch()
