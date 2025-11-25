"""Template-based Poster Generator"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from PIL import Image, ImageDraw, ImageFont
import json
import time

pipeline = Key2PosterPipeline(use_flux=True, add_title=False, genre_lora=False, remove_text=True, super_resolution=False, aggressive_text_removal=True)

# Store current poster state
poster_state = {"image": None, "title": "", "bg_color": "#faefcf", "text_color": "#043bb4"}

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

# Load template
with open("templates/template1_layers.json") as f:
    template = json.load(f)

def generate_with_template(keywords, seed):
    try:
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, None, "❌ Provide 2-5 keywords"
        
        # Generate FLUX image (no text)
        image, brief, _ = pipeline.generate_poster(keywords, seed=seed if seed > 0 else None)
        
        # Store for editing
        poster_state["image"] = image
        poster_state["title"] = " ".join(keyword_list[:3]).title()
        
        # Create poster
        poster = compose_poster(image, poster_state["title"], poster_state["bg_color"], poster_state["text_color"])
        
        info = f"✅ Generated\n\n**Title:** {poster_state['title']}\n**Font:** Graduate-Regular (37px)\n**BG:** {poster_state['bg_color']}\n**Text:** {poster_state['text_color']}"
        
        return poster, poster, info
        
    except Exception as e:
        return None, None, f"❌ Error: {str(e)}"

def compose_poster(image, title, bg_color, text_color):
    """Compose poster from layers"""
    # Background layer - solid color only
    bg_rgb = hex_to_rgb(bg_color)
    poster = Image.new('RGB', tuple(template['size']), bg_rgb)
    
    # Image layer (center area) - paste on top of background
    img_bbox = [54, 59, 655, 873]
    img_w, img_h = img_bbox[2] - img_bbox[0], img_bbox[3] - img_bbox[1]
    center_img = image.resize((img_w, img_h))
    poster.paste(center_img, (img_bbox[0], img_bbox[1]))
    
    # Text layer
    draw = ImageDraw.Draw(poster)
    font = ImageFont.truetype("fonts/Graduate-Regular.ttf", 37)
    text_bbox = [240, 930, 472, 989]
    text_x = (text_bbox[0] + text_bbox[2]) // 2
    text_y = text_bbox[1]
    
    # Draw text (replace newlines with space for single line)
    title_single = title.replace('\n', ' ').replace('\r', ' ')
    bbox = draw.textbbox((text_x, text_y), title_single, font=font, anchor='mt')
    draw.text((text_x, text_y), title_single, font=font, fill=hex_to_rgb(text_color), anchor='mt')
    
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
                left: 54,
                top: 59,
                selectable: true,
                hasControls: true,
                hasBorders: true,
                borderColor: 'blue',
                cornerColor: 'blue',
                cornerSize: 10
            }});
            
            // Scale to fit
            fabricImg.scaleToWidth(601);
            canvas.add(fabricImg);
            canvas.renderAll();
            
            document.getElementById('status').innerText = 'Image added! Adding text...';
            console.log('Image added, objects count:', canvas.getObjects().length);
            
            // Add text after image loads
            var textObj = new fabric.IText('{poster_state["title"]}', {{
                left: 360,
                top: 930,
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
    
    gen_btn.click(generate_with_template, [keywords, seed], [output_image, preview_image, status]).then(
        lambda: poster_state.get("title", ""), None, title_input
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
        [["anime love story japanese", 42], ["cyberpunk neon city", 123]],
        [keywords, seed]
    )

if __name__ == "__main__":
    demo.launch()
