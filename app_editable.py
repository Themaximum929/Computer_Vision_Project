"""Adobe-like Editable Poster System"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from PIL import Image, ImageDraw, ImageFont
import json
import time
import os

pipeline = Key2PosterPipeline(use_flux=True, add_title=False, genre_lora=False, remove_text=False, super_resolution=False)

# Store poster state
poster_state = {"background": None, "elements": [], "metadata": {}}

def generate_background(keywords, poster_type, style_preset, seed):
    """Generate FLUX background without text"""
    try:
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, None, "❌ Provide 2-5 keywords"
        
        pipeline.style_preset = style_preset
        pipeline.poster_type = poster_type
        
        # Generate background only (no text in FLUX)
        image, brief, metrics = pipeline.generate_poster(
            keywords, seed=seed if seed > 0 else None
        )
        
        poster_state["background"] = image
        poster_state["metadata"] = {"keywords": keywords, "type": poster_type, "style": style_preset, "brief": brief}
        poster_state["elements"] = []
        
        # Auto-generate title suggestion
        title = " ".join(keyword_list[:3]).upper()
        
        return image, title, f"✅ Background generated | Suggested title: {title}"
    except Exception as e:
        return None, None, f"❌ Error: {str(e)}"

def add_text_element(image, text, font_size, color, x_pos, y_pos, font_style):
    """Add editable text layer"""
    if image is None:
        return None, "❌ Generate background first"
    
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    # Font selection
    font_map = {
        "Bold": "arialbd.ttf",
        "Impact": "impact.ttf", 
        "Times": "times.ttf",
        "Courier": "cour.ttf"
    }
    
    try:
        font_path = f"C:/Windows/Fonts/{font_map.get(font_style, 'arial.ttf')}"
        font = ImageFont.truetype(font_path, int(font_size))
    except:
        font = ImageFont.load_default()
    
    # Convert percentage to pixels
    w, h = img.size
    x = int(w * x_pos / 100)
    y = int(h * y_pos / 100)
    
    # Add text with outline
    outline_color = "black" if color != "black" else "white"
    for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((x+adj[0], y+adj[1]), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=color)
    
    # Store element
    poster_state["elements"].append({
        "type": "text", "content": text, "font_size": font_size,
        "color": color, "x": x_pos, "y": y_pos, "font_style": font_style
    })
    
    return img, f"✅ Text added: '{text}'"

def export_poster(image, format_type):
    """Export with metadata"""
    if image is None:
        return None, "❌ No poster to export"
    
    timestamp = int(time.time())
    
    if format_type == "PNG (Flattened)":
        path = f"outputs/editable_{timestamp}.png"
        image.save(path)
    elif format_type == "JSON (With Metadata)":
        path = f"outputs/editable_{timestamp}.json"
        poster_state["background"].save(f"outputs/editable_{timestamp}_bg.png")
        with open(path, 'w') as f:
            json.dump({
                "background": f"editable_{timestamp}_bg.png",
                "elements": poster_state["elements"],
                "metadata": poster_state["metadata"]
            }, f, indent=2)
    
    return image, f"✅ Exported: {path}"

def reload_from_json(json_file):
    """Reload editable poster from JSON"""
    try:
        data = json.load(open(json_file))
        bg = Image.open(f"outputs/{data['background']}")
        poster_state.update({"background": bg, "elements": data["elements"], "metadata": data["metadata"]})
        
        # Reconstruct poster
        img = bg.copy()
        for elem in data["elements"]:
            if elem["type"] == "text":
                img, _ = add_text_element(img, elem["content"], elem["font_size"], 
                                         elem["color"], elem["x"], elem["y"], elem["font_style"])
        return img, "✅ Poster reloaded"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

with gr.Blocks(theme=gr.themes.Soft(), title="Editable Poster Creator") as demo:
    gr.Markdown("# 🎨 Adobe-like Editable Poster Creator\nGenerate FLUX background → Add editable text layers → Export with metadata")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1️⃣ Generate Background")
            keywords = gr.Textbox(label="Keywords", placeholder="cyberpunk neon city")
            with gr.Row():
                poster_type = gr.Dropdown(["movie", "advertise", "event", "education", "social", "music", "sports"], value="movie", label="Type")
                style_preset = gr.Dropdown(["cinematic", "minimalist", "neon", "dark", "vintage", "bright", "professional"], value="cinematic", label="Style")
            seed = gr.Number(label="Seed", value=0, precision=0)
            gen_btn = gr.Button("🎨 Generate Background", variant="primary")
            
            gr.Markdown("### 2️⃣ Add Text Elements")
            text_input = gr.Textbox(label="Text", placeholder="CYBERPUNK 2077")
            with gr.Row():
                font_size = gr.Slider(20, 200, 80, label="Font Size")
                font_style = gr.Dropdown(["Bold", "Impact", "Times", "Courier"], value="Bold", label="Font")
            with gr.Row():
                text_color = gr.Dropdown(["white", "black", "red", "yellow", "cyan"], value="white", label="Color")
            with gr.Row():
                x_pos = gr.Slider(0, 100, 50, label="X Position (%)")
                y_pos = gr.Slider(0, 100, 20, label="Y Position (%)")
            add_text_btn = gr.Button("➕ Add Text Layer")
            
            gr.Markdown("### 3️⃣ Export")
            export_format = gr.Dropdown(["PNG (Flattened)", "JSON (With Metadata)"], value="PNG (Flattened)", label="Format")
            export_btn = gr.Button("💾 Export Poster")
        
        with gr.Column(scale=2):
            output_image = gr.Image(label="Poster Preview", height=700)
            status_text = gr.Markdown("Ready to create poster...")
    
    # Event handlers
    gen_btn.click(generate_background, [keywords, poster_type, style_preset, seed], [output_image, text_input, status_text])
    add_text_btn.click(add_text_element, [output_image, text_input, font_size, text_color, x_pos, y_pos, font_style], [output_image, status_text])
    export_btn.click(export_poster, [output_image, export_format], [output_image, status_text])
    
    gr.Markdown("""
    ---
    **Features:** FLUX Background • Editable Text Layers • Position Control • Export with Metadata • Reload from JSON
    
    **Workflow:** Generate → Add Text → Adjust Position → Export → Reload & Edit Later
    """)

if __name__ == "__main__":
    demo.launch()
