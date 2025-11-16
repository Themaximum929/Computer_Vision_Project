import gradio as gr
from PIL import Image
from src.cinematic_text_overlay import CinematicTextOverlay
from pathlib import Path

overlay_engine = CinematicTextOverlay()

def update_text_overlay(image, text, font_category, font_name, font_size, color_r, color_g, color_b,
                        position, stroke_width, shadow_offset, letter_spacing, 
                        genre, auto_adapt):
    if image is None:
        return None
    
    font_path = None
    if font_name != "Auto" and font_name in overlay_engine.available_fonts:
        font_path = overlay_engine.available_fonts[font_name]
    
    color = (int(color_r), int(color_g), int(color_b)) if not auto_adapt else None
    
    result = overlay_engine.add_text(
        image, text,
        font_path=font_path,
        font_size=int(font_size),
        color=color,
        position=position,
        stroke_width=int(stroke_width) if stroke_width is not None else None,
        shadow_offset=int(shadow_offset) if shadow_offset is not None else None,
        letter_spacing=int(letter_spacing),
        genre=genre,
        auto_adapt=auto_adapt
    )
    
    return result

def load_sample_poster():
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        posters = list(outputs_dir.glob("*.png"))
        if posters:
            return Image.open(posters[0])
    return None

with gr.Blocks(title="Cinematic Text Overlay Studio") as demo:
    gr.HTML("<h1 style='text-align: center;'>🎬 Cinematic Text Overlay Studio</h1>")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("<h3>Input</h3>")
            input_image = gr.Image(label="Upload Poster", type="pil", height=300)
            load_sample_btn = gr.Button("Load Sample Poster", size="sm")
            
            text_input = gr.Textbox(label="Title Text", value="EPIC ADVENTURE", 
                                   placeholder="Enter poster title")
            
            gr.HTML("<h3>Auto Settings</h3>")
            auto_adapt = gr.Checkbox(label="Auto-Adapt Colors", value=True,
                                    info="Automatically pick colors based on background")
            genre_select = gr.Dropdown(
                label="Genre",
                choices=["action", "horror", "scifi", "drama", "comedy", 
                        "thriller", "fantasy", "romance", "epic", "historical",
                        "modern", "minimalist", "cinematic"],
                value="cinematic",
                info="Auto-selects font category: serif/sans-serif/display"
            )
            
            gr.HTML("<h3>Font Settings</h3>")
            
            font_category = gr.Radio(
                label="Font Category",
                choices=["Auto (Genre-Based)", "Serif", "Sans-Serif", "Display", "Decorative"],
                value="Auto (Genre-Based)",
                info="Serif: epic/drama | Sans: scifi/modern | Display: action | Decorative: horror/fantasy"
            )
            
            font_select = gr.Dropdown(
                label="Specific Font (Optional)",
                choices=["Auto"] + list(overlay_engine.available_fonts.keys()),
                value="Auto",
                info="Leave as Auto to use genre-based selection"
            )
            font_size = gr.Slider(20, 200, value=80, step=5, label="Font Size")
            letter_spacing = gr.Slider(0, 20, value=5, step=1, label="Letter Spacing")
            
            gr.HTML("<h3>Color Settings</h3>")
            with gr.Row():
                color_r = gr.Slider(0, 255, value=255, step=1, label="Red")
                color_g = gr.Slider(0, 255, value=255, step=1, label="Green")
                color_b = gr.Slider(0, 255, value=255, step=1, label="Blue")
            
            gr.HTML("<h3>Position & Effects</h3>")
            position_select = gr.Radio(
                choices=["top", "center", "bottom"],
                value="bottom",
                label="Position"
            )
            stroke_width = gr.Slider(0, 10, value=2, step=1, label="Stroke Width")
            shadow_offset = gr.Slider(0, 20, value=4, step=1, label="Shadow Offset")
            
            apply_btn = gr.Button("Apply Text Overlay", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.HTML("<h3>Live Preview</h3>")
            output_image = gr.Image(label="Result", type="pil", height=600)
    
    inputs = [input_image, text_input, font_category, font_select, font_size, color_r, color_g, color_b,
              position_select, stroke_width, shadow_offset, letter_spacing, 
              genre_select, auto_adapt]
    
    apply_btn.click(fn=update_text_overlay, inputs=inputs, outputs=output_image)
    
    for component in [text_input, font_category, font_select, font_size, color_r, color_g, color_b,
                     position_select, stroke_width, shadow_offset, letter_spacing,
                     genre_select, auto_adapt]:
        component.change(fn=update_text_overlay, inputs=inputs, outputs=output_image)
    
    load_sample_btn.click(fn=load_sample_poster, outputs=input_image)
    
    gr.Examples(
        examples=[
            ["SPACE ODYSSEY", "scifi", "bottom", True],
            ["DARK NIGHT", "horror", "center", True],
            ["EPIC BATTLE", "epic", "bottom", True],
            ["LOVE STORY", "romance", "bottom", True],
            ["MODERN CITY", "modern", "center", True],
        ],
        inputs=[text_input, genre_select, position_select, auto_adapt]
    )

if __name__ == "__main__":
    demo.launch()
