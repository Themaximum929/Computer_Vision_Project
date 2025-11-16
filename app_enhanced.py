"""Enhanced Gradio Interface with Advanced Features"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from src.template_manager import TemplateManager
from src.color_palette_extractor import ColorPaletteExtractor
from src.composition_engine import CompositionEngine
from pathlib import Path
import time

template_manager = TemplateManager()
color_extractor = ColorPaletteExtractor()
composition_engine = CompositionEngine()

def generate_with_enhancements(keywords, template, use_color_extraction, add_vignette, 
                               genre_lora, add_title, aggressive_text_removal, 
                               super_resolution, seed):
    """Generate poster with enhanced features"""
    try:
        # Validate keywords
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, None, f"❌ Error: Please provide 2-5 keywords (you provided {len(keyword_list)})"
        
        # Create pipeline
        pipeline = Key2PosterPipeline(
            genre_lora=genre_lora,
            add_title=add_title,
            remove_text=True,
            aggressive_text_removal=aggressive_text_removal,
            super_resolution=super_resolution
        )
        
        # Generate base poster
        start_time = time.time()
        output_path = f"outputs/enhanced_{int(time.time())}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path=output_path,
            seed=seed if seed > 0 else None,
            evaluate=True
        )
        
        # Apply enhancements
        if use_color_extraction:
            palette = color_extractor.extract_palette(image)
            mood = color_extractor.analyze_mood_from_colors()
            palette_info = f"\n**Color Palette:** {', '.join([f'RGB{c}' for c in palette[:3]])}\n**Mood:** {mood}"
        else:
            palette_info = ""
        
        if add_vignette:
            image = composition_engine.add_vignette(image, strength=0.3)
        
        if template != "none":
            image = template_manager.apply_template(image, template, keywords)
        
        # Detect safe zones for composition analysis
        safe_zones = composition_engine.detect_safe_zones(image)
        best_zone = safe_zones[0] if safe_zones else None
        
        # Save enhanced version
        image.save(output_path, quality=95)
        elapsed = time.time() - start_time
        
        # Format info
        info = f"""
✅ **Generation Complete!**

**Keywords:** {keywords}
**Sentiment:** {brief['sentiment']} (confidence: {brief['confidence']:.2f})
**Mood:** {brief['mood']}
**Themes:** {brief['themes']}
{palette_info}

**Quality Metrics:**
- Aesthetic Score: {metrics['aesthetic']['overall']:.3f}
- Color Variance: {metrics['aesthetic']['color_variance']:.1f}
- Brightness Balance: {metrics['aesthetic']['brightness_balance']:.3f}
- Resolution: {metrics['resolution']['width']}×{metrics['resolution']['height']}

**Composition Analysis:**
- Best Text Zone: {best_zone['position'] if best_zone else 'N/A'}
- Zone Score: {best_zone['score']:.3f if best_zone else 0}

**Generation Time:** {elapsed:.1f}s

**Active Enhancements:**
- Template: {template.title()}
- Color Extraction: {'✓' if use_color_extraction else '✗'}
- Vignette Effect: {'✓' if add_vignette else '✗'}
- Genre-LoRA: {'✓' if genre_lora else '✗'}
- Super-Resolution: {'✓' if super_resolution else '✗'}
"""
        
        # Create composition guide
        guide_image = composition_engine.apply_rule_of_thirds_grid(image, show_grid=True)
        
        return image, guide_image, info
        
    except Exception as e:
        return None, None, f"❌ Error: {str(e)}"

# Create enhanced interface
with gr.Blocks(title="Key2Poster Enhanced", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎨 Key2Poster Enhanced: AI Poster Generator
    
    **New Features:** Template System • Color Palette Extraction • Composition Analysis • Smart Layouts
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            keywords_input = gr.Textbox(
                label="Keywords (2-5 words)",
                placeholder="e.g., space exploration adventure",
                lines=2
            )
            
            gr.Markdown("### Enhanced Features")
            template_select = gr.Dropdown(
                choices=["none", "minimal", "classic", "modern", "split"],
                value="minimal",
                label="Poster Template",
                info="Choose layout style"
            )
            
            use_color_extraction = gr.Checkbox(
                label="Smart Color Extraction",
                value=True,
                info="Extract and analyze color palette"
            )
            
            add_vignette = gr.Checkbox(
                label="Add Vignette Effect",
                value=True,
                info="Focus attention on center"
            )
            
            gr.Markdown("### Generation Settings")
            genre_lora = gr.Checkbox(label="Genre-Based LoRA", value=True)
            add_title = gr.Checkbox(label="Add Styled Title", value=True)
            aggressive_text_removal = gr.Checkbox(label="Aggressive Text Removal", value=True)
            super_resolution = gr.Checkbox(label="Super-Resolution", value=True)
            seed_input = gr.Number(label="Seed (0 = random)", value=0, precision=0)
            
            generate_btn = gr.Button("🎨 Generate Enhanced Poster", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("### Generated Poster")
            with gr.Tabs():
                with gr.Tab("Final Result"):
                    output_image = gr.Image(label="Output", type="pil", height=600)
                with gr.Tab("Composition Guide"):
                    guide_image = gr.Image(label="Rule of Thirds Grid", type="pil", height=600)
            
            output_info = gr.Markdown(value="*Generate a poster to see results*")
    
    # Examples
    gr.Examples(
        examples=[
            ["cyberpunk neon city", "modern", True, True, True, True, True, True, 42],
            ["dark fantasy warrior", "classic", True, True, True, True, True, True, 123],
            ["romantic sunset beach", "minimal", True, True, True, True, True, True, 456],
        ],
        inputs=[keywords_input, template_select, use_color_extraction, add_vignette,
                genre_lora, add_title, aggressive_text_removal, super_resolution, seed_input]
    )
    
    generate_btn.click(
        fn=generate_with_enhancements,
        inputs=[keywords_input, template_select, use_color_extraction, add_vignette,
                genre_lora, add_title, aggressive_text_removal, super_resolution, seed_input],
        outputs=[output_image, guide_image, output_info]
    )

if __name__ == "__main__":
    demo.launch(share=False)
