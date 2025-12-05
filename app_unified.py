#!/usr/bin/env python3
"""
Unified Key2Poster App with 3 Modes:
1. Template Mode (Editable)
2. LayoutGAN Mode
3. PosterO Mode
"""

import gradio as gr
import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')

# Import pipelines
from src.pipeline import Key2PosterPipeline
from src.pipeline_postero import Key2PosterPosterO

# Global state
current_mode = "template"


# Global state for template editing
template_state = {"image": None, "brief": None}

def generate_template_mode(keywords, poster_type, style_preset, seed):
    """Mode 1: Template-based with editing"""
    try:
        pipeline = Key2PosterPipeline(
            use_flux=True,
            use_template=True,
            add_title=False,  # Generate clean background without text
            remove_text=False,  # Don't remove text (there is none)
            poster_type=poster_type.lower(),
            style_preset=style_preset.lower()
        )
        
        output_path = f"outputs/template_{seed}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords=keywords,
            output_path=output_path,
            seed=seed
        )
        
        # Ensure 720x1280 output
        if image.size != (720, 1280):
            from PIL import Image as PILImage
            image = image.resize((720, 1280), PILImage.LANCZOS)
            image.save(output_path)
        
        # Store clean background for editing (no text on it)
        template_state["background"] = image  # This is already clean (add_title=False)
        template_state["brief"] = brief
        
        info = f"""
**Mode**: Template-based (Editable)
**Title**: {brief.get('story title', 'N/A')}
**Aesthetic Score**: {metrics['aesthetic']['overall']:.3f}
**Resolution**: 720x1280 (standardized)
**Template**: {brief.get('template', {}).get('layout_type', 'Random')}

✏️ Use editing controls below to customize text
        """
        
        # Return suggested title
        suggested_title = brief.get('story title', keywords.upper())
        return image, info, suggested_title
        
    except Exception as e:
        return None, f"Error: {str(e)}", ""


def edit_template_text(title_text, title_size, title_color, title_x, title_y, 
                       caption_text, caption_size, caption_color, caption_x, caption_y, font_style):
    """Edit text on template with position control"""
    if template_state.get("background") is None:
        return None, "Generate a poster first"
    
    from PIL import ImageDraw, ImageFont
    import glob
    
    # Start from clean background (no text)
    img = template_state["background"].copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Font selection
    font_files = glob.glob("fonts/*.ttf")
    if font_files:
        font_path = font_files[0]  # Use first available font
    else:
        font_path = "fonts/Graduate-Regular.ttf"
    
    # Color map
    color_map = {
        "White": (255,255,255), "Black": (0,0,0), "Red": (255,0,0), 
        "Yellow": (255,255,0), "Cyan": (0,255,255), "Green": (0,255,0),
        "Blue": (0,0,255), "Magenta": (255,0,255)
    }
    
    # Draw title
    if title_text:
        try:
            font = ImageFont.truetype(font_path, int(title_size))
        except:
            font = ImageFont.load_default()
        
        text_color = color_map.get(title_color, (255,255,255))
        outline_color = (0,0,0) if title_color == "White" else (255,255,255)
        
        # Convert percentage to pixels
        x = int(w * title_x / 100)
        y = int(h * title_y / 100)
        
        # Draw with outline
        outline_width = max(2, int(title_size / 20))
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    draw.text((x+dx, y+dy), title_text, font=font, fill=outline_color)
        draw.text((x, y), title_text, font=font, fill=text_color)
    
    # Draw caption
    if caption_text:
        try:
            font = ImageFont.truetype(font_path, int(caption_size))
        except:
            font = ImageFont.load_default()
        
        text_color = color_map.get(caption_color, (255,255,255))
        outline_color = (0,0,0) if caption_color == "White" else (255,255,255)
        
        x = int(w * caption_x / 100)
        y = int(h * caption_y / 100)
        
        outline_width = max(2, int(caption_size / 25))
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    draw.text((x+dx, y+dy), caption_text, font=font, fill=outline_color)
        draw.text((x, y), caption_text, font=font, fill=text_color)
    
    return img, "✅ Text updated"


def generate_layoutgan_mode(keywords, poster_type, style_preset, seed):
    """Mode 2: LayoutGAN"""
    try:
        # Check if LayoutGAN is available
        if not os.path.exists("app_clg_lo.py"):
            return None, "LayoutGAN mode not available. Please ensure app_clg_lo.py exists."
        
        # Use template mode with auto-generation
        pipeline = Key2PosterPipeline(
            use_flux=True,
            auto_template=True,
            add_title=True,
            poster_type=poster_type.lower(),
            style_preset=style_preset.lower()
        )
        
        output_path = f"outputs/layoutgan_{seed}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords=keywords,
            output_path=output_path,
            seed=seed
        )
        
        # Ensure 720x1280 output
        if image.size != (720, 1280):
            from PIL import Image as PILImage
            image = image.resize((720, 1280), PILImage.LANCZOS)
            image.save(output_path)
        
        info = f"""
**Mode**: LayoutGAN
**Title**: {brief.get('story title', 'N/A')}
**Aesthetic Score**: {metrics['aesthetic']['overall']:.3f}
**Resolution**: 720x1280 (standardized)
**Layout**: Auto-generated
        """
        
        return image, info
        
    except Exception as e:
        return None, f"Error: {str(e)}"


def generate_postero_mode(keywords, poster_type, style_preset, seed):
    """Mode 3: PosterO (CVPR 2025)"""
    try:
        pipeline = Key2PosterPosterO(
            poster_type=poster_type.lower(),
            style_preset=style_preset.lower()
        )
        
        output_path = f"outputs/postero_{seed}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords=keywords,
            output_path=output_path,
            seed=seed
        )
        
        # PosterO already outputs 720x1280, but verify
        if image.size != (720, 1280):
            from PIL import Image as PILImage
            image = image.resize((720, 1280), PILImage.LANCZOS)
            image.save(output_path)
        
        info = f"""
**Mode**: PosterO (CVPR 2025)
**Title**: {brief.get('story title', 'N/A')}
**Aesthetic Score**: {metrics['aesthetic']['overall']:.3f}
**Resolution**: 720x1280 (standardized)
**Layout**: Content-aware AI
        """
        
        return image, info
        
    except Exception as e:
        return None, f"Error: {str(e)}"


def generate_poster(mode, keywords, poster_type, style_preset, seed):
    """Main generation function"""
    if not keywords or len(keywords.split()) < 2:
        return None, "Please enter 2-5 keywords", ""
    
    if mode == "Template Mode (Editable)":
        return generate_template_mode(keywords, poster_type, style_preset, seed)
    elif mode == "LayoutGAN Mode":
        img, info = generate_layoutgan_mode(keywords, poster_type, style_preset, seed)
        return img, info, ""
    elif mode == "PosterO Mode (CVPR 2025)":
        img, info = generate_postero_mode(keywords, poster_type, style_preset, seed)
        return img, info, ""
    else:
        return None, "Invalid mode selected", ""


# Create Gradio interface
with gr.Blocks(title="Key2Poster - Unified App") as app:
    gr.Markdown("""
    # 🎨 Key2Poster - Unified Poster Generation
    
    Generate professional posters with AI using 3 different modes:
    - **Template Mode**: Fixed templates with editing capabilities
    - **LayoutGAN Mode**: Auto-generated layouts
    - **PosterO Mode**: Content-aware AI layout (CVPR 2025)
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input Settings")
            
            mode = gr.Radio(
                choices=[
                    "Template Mode (Editable)",
                    "LayoutGAN Mode",
                    "PosterO Mode (CVPR 2025)"
                ],
                value="PosterO Mode (CVPR 2025)",
                label="Generation Mode",
                info="Select poster generation method"
            )
            
            keywords = gr.Textbox(
                label="Keywords (2-5 words)",
                placeholder="e.g., cyberpunk neon city",
                lines=2
            )
            
            with gr.Row():
                poster_type = gr.Dropdown(
                    choices=["Movie", "Event", "Product", "Music", "Sports", "Book", "Theater", "Conference", "Festival", "Game"],
                    value="Movie",
                    label="Poster Type"
                )
                
                style_preset = gr.Dropdown(
                    choices=["Cinematic", "Minimalist", "Neon", "Dark", "Vintage", "Bright", "Professional"],
                    value="Cinematic",
                    label="Style Preset"
                )
            
            seed = gr.Slider(
                minimum=0,
                maximum=10000,
                value=42,
                step=1,
                label="Random Seed",
                info="For reproducible results"
            )
            
            generate_btn = gr.Button("🎨 Generate Poster", variant="primary", size="lg")
            
            gr.Markdown("""
            ### Mode Comparison
            
            | Mode | Speed | Quality | Editability |
            |------|-------|---------|-------------|
            | Template | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | ✅ Full* |
            | LayoutGAN | ⚡⚡ Medium | ⭐⭐⭐⭐ Great | ⚠️ Limited |
            | PosterO | ⚡ Slow | ⭐⭐⭐⭐⭐ Best | ❌ None |
            
            *For full editing, use `app_editable.py`
            """)
        
        with gr.Column(scale=2):
            gr.Markdown("### Generated Poster")
            
            output_image = gr.Image(
                label="Result",
                type="pil",
                height=600
            )
            
            output_info = gr.Markdown(
                label="Generation Info",
                value="*Generate a poster to see details*"
            )
            
            # Template editing controls (only visible for Template Mode)
            with gr.Group(visible=True) as edit_group:
                gr.Markdown("### ✏️ Edit Text (Template Mode Only)")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**Title**")
                        title_text = gr.Textbox(label="Text", placeholder="CYBERPUNK")
                        with gr.Row():
                            title_size = gr.Slider(20, 120, 60, label="Size")
                            title_color = gr.Dropdown(
                                choices=["White", "Black", "Red", "Yellow", "Cyan", "Green", "Blue", "Magenta"],
                                value="White",
                                label="Color"
                            )
                        with gr.Row():
                            title_x = gr.Slider(0, 100, 50, label="X Position (%)")
                            title_y = gr.Slider(0, 100, 20, label="Y Position (%)")
                    
                    with gr.Column():
                        gr.Markdown("**Caption**")
                        caption_text = gr.Textbox(label="Text", placeholder="Coming Soon")
                        with gr.Row():
                            caption_size = gr.Slider(15, 80, 30, label="Size")
                            caption_color = gr.Dropdown(
                                choices=["White", "Black", "Red", "Yellow", "Cyan", "Green", "Blue", "Magenta"],
                                value="White",
                                label="Color"
                            )
                        with gr.Row():
                            caption_x = gr.Slider(0, 100, 50, label="X Position (%)")
                            caption_y = gr.Slider(0, 100, 60, label="Y Position (%)")
                
                font_style = gr.Dropdown(
                    choices=["Default"],
                    value="Default",
                    label="Font Style",
                    visible=False
                )
                
                edit_btn = gr.Button("✏️ Update Text", variant="secondary", size="lg")
                edit_status = gr.Markdown("")
            
            gr.Markdown("""
            ### Tips
            - Use 2-5 descriptive keywords
            - Choose appropriate poster type for your content
            - Experiment with different style presets
            - Try different seeds for variations
            """)
    
    # Examples
    gr.Examples(
        examples=[
            ["PosterO Mode (CVPR 2025)", "cyberpunk neon city", "Movie", "Neon", 42],
            ["Template Mode (Editable)", "vintage travel mountains", "Event", "Vintage", 123],
            ["LayoutGAN Mode", "food restaurant elegant", "Product", "Minimalist", 456],
            ["PosterO Mode (CVPR 2025)", "rock concert festival", "Music", "Dark", 789],
            ["Template Mode (Editable)", "sports championship finals", "Sports", "Bright", 101],
        ],
        inputs=[mode, keywords, poster_type, style_preset, seed],
        label="Example Prompts"
    )
    
    # Event handlers
    generate_btn.click(
        fn=generate_poster,
        inputs=[mode, keywords, poster_type, style_preset, seed],
        outputs=[output_image, output_info, title_text]
    )
    
    edit_btn.click(
        fn=edit_template_text,
        inputs=[title_text, title_size, title_color, title_x, title_y,
                caption_text, caption_size, caption_color, caption_x, caption_y, font_style],
        outputs=[output_image, edit_status]
    )
    
    gr.Markdown("""
    ---
    ### About the Modes
    
    **Template Mode (Editable)**
    - Uses pre-designed templates
    - Fast generation (~10-15s)
    - Full editing: Run `python app_editable.py`
    - Consistent layouts
    
    **LayoutGAN Mode**
    - Auto-generates layouts with GAN
    - Medium speed (~20-30s)
    - Adaptive to content
    - Limited editing
    
    **PosterO Mode (CVPR 2025)**
    - State-of-the-art AI layout
    - Content-aware positioning
    - Highest quality (~30-40s)
    - No manual editing needed
    
    ---
    **Powered by**: FLUX.1 + PosterO (CVPR 2025) + LayoutGAN
    """)


if __name__ == "__main__":
    # Create outputs directory
    Path("outputs").mkdir(exist_ok=True)
    
    # Launch app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
