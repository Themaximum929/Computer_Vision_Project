"""Gradio Web Interface for Key2Poster"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from pathlib import Path
import time

def get_pipeline(baseline_style, genre_lora, add_title, remove_text, aggressive_text_removal, super_resolution):
    """Create pipeline with specified settings (no caching for accurate timing)"""
    return Key2PosterPipeline(
        baseline_style=baseline_style,
        genre_lora=genre_lora,
        add_title=add_title,
        remove_text=remove_text,
        aggressive_text_removal=aggressive_text_removal,
        super_resolution=super_resolution
    )

def generate_poster(keywords, baseline_style, genre_lora, add_title, remove_text, aggressive_text_removal, 
                   super_resolution, seed):
    """Generate poster from keywords"""
    try:
        # Show what's being processed
        processing_msg = f"⏳ Generating with: {'Baseline' if baseline_style else 'LoRA'} style"
        if add_title:
            processing_msg += " + Title"
        if aggressive_text_removal:
            processing_msg += " + Aggressive Text Removal"
        elif remove_text:
            processing_msg += " + Text Removal"
        if super_resolution:
            processing_msg += " + Super-Res"
        
        # Validate keywords
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, f"❌ Error: Please provide 2-5 keywords (you provided {len(keyword_list)})"
        
        # Create pipeline with current settings
        pipeline = get_pipeline(baseline_style, genre_lora, add_title, remove_text, aggressive_text_removal, super_resolution)
        
        # Generate
        start_time = time.time()
        output_path = f"outputs/gradio_{int(time.time())}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path=output_path,
            seed=seed if seed > 0 else None,
            evaluate=True
        )
        elapsed = time.time() - start_time
        
        # Format info
        info = f"""
✅ **Generation Complete!**

**Keywords:** {keywords}
**Sentiment:** {brief['sentiment']} (confidence: {brief['confidence']:.2f})
**Mood:** {brief['mood']}
**Themes:** {brief['themes']}

**Quality Metrics:**
- Aesthetic Score: {metrics['aesthetic']['overall']:.3f}
- Color Variance: {metrics['aesthetic']['color_variance']:.1f}
- Brightness Balance: {metrics['aesthetic']['brightness_balance']:.3f}
- Resolution: {metrics['resolution']['width']}×{metrics['resolution']['height']}
- Meets Target: {'✓' if metrics['instruction_following'] else '✗'}

**Generation Time:** {elapsed:.1f}s

**Active Enhancements:**
{'- Denoising' if super_resolution else ''}
{'- Text Removal (Aggressive)' if aggressive_text_removal else '- Text Removal (Standard)' if remove_text else ''}
{'- Title Overlay' if add_title else ''}

**Settings:**
- Style: {'Baseline' if baseline_style else 'Genre-LoRA' if genre_lora else 'Standard'}
- Genre Detection: {'✓' if genre_lora else '✗'}
- Title Overlay: {'✓' if add_title else '✗'}
- Text Removal: {'Aggressive' if aggressive_text_removal else 'Standard' if remove_text else 'Disabled'}
- Super-Resolution: {'✓' if super_resolution else '✗'}
- Seed: {seed if seed > 0 else 'Random'}
"""
        
        return image, info + f"\n\n{processing_msg}"
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Key2Poster: AI Poster Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎨 Key2Poster: Creative Poster Generator
    
    Generate cinematic movie posters from 2-5 keywords using AI with LoRA fine-tuning.
    
    **Multi-Agent System:** Concept Expander → Visual Designer → Text Remover → Quality Enhancer → Evaluator
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            
            keywords_input = gr.Textbox(
                label="Keywords (2-5 words)",
                placeholder="e.g., space exploration adventure",
                lines=2
            )
            
            gr.Markdown("### Generation Settings")
            
            baseline_style = gr.Checkbox(
                label="Baseline Style",
                value=False,
                info="Use baseline SD (no LoRA)"
            )
            
            genre_lora = gr.Checkbox(
                label="Genre-Based LoRA (Recommended)",
                value=True,
                info="Auto-detect genre and use genre-specific LoRA"
            )
            
            add_title = gr.Checkbox(
                label="Add Styled Title",
                value=True,
                info="Add movie title with cinematic styling"
            )
            
            gr.Markdown("### Enhancement Settings")
            
            remove_text = gr.Checkbox(
                label="Enable Text Removal",
                value=True,
                info="Detect and remove artificial text"
            )
            
            aggressive_text_removal = gr.Checkbox(
                label="Aggressive Text Removal",
                value=True,
                info="Use 3-pass multi-method detection (recommended)"
            )
            
            super_resolution = gr.Checkbox(
                label="Super-Resolution Enhancement",
                value=True,
                info="Apply advanced sharpening and detail enhancement"
            )
            
            gr.Markdown("### Advanced")
            
            seed_input = gr.Number(
                label="Seed (0 = random)",
                value=0,
                precision=0,
                info="Use same seed for reproducible results"
            )
            
            generate_btn = gr.Button("🎨 Generate Poster", variant="primary", size="lg")
            
            gr.Markdown("""
            ### Quick Presets
            """)
            
            with gr.Row():
                preset_best = gr.Button("⭐ Best Quality", size="sm")
                preset_fast = gr.Button("⚡ Fast", size="sm")
                preset_experimental = gr.Button("🧪 Experimental", size="sm")
        
        with gr.Column(scale=2):
            gr.Markdown("### Generated Poster")
            
            output_image = gr.Image(
                label="Output",
                type="pil",
                height=600
            )
            
            output_info = gr.Markdown(
                label="Generation Info",
                value="*Generate a poster to see results*"
            )
    
    # Examples
    gr.Markdown("### 📚 Example Keywords")
    gr.Examples(
        examples=[
            ["space exploration adventure", False, True, True, True, True, True, 42],
            ["dark fantasy warrior", False, True, True, True, True, True, 123],
            ["cyberpunk city noir", False, True, True, True, True, True, 456],
            ["romantic sunset beach", False, True, True, True, True, True, 789],
            ["epic battle scene", False, True, True, True, True, True, 999],
        ],
        inputs=[keywords_input, baseline_style, genre_lora, add_title, remove_text, 
                aggressive_text_removal, super_resolution, seed_input],
        label="Click to try"
    )
    
    # Event handlers
    generate_btn.click(
        fn=generate_poster,
        inputs=[keywords_input, baseline_style, genre_lora, add_title, remove_text, 
                aggressive_text_removal, super_resolution, seed_input],
        outputs=[output_image, output_info]
    )
    
    # Preset handlers
    def set_best_quality():
        return False, True, True, True, True, True
    
    def set_fast():
        return False, True, True, False, False, False
    
    def set_experimental():
        return True, False, True, True, True, True
    
    preset_best.click(
        fn=set_best_quality,
        outputs=[baseline_style, genre_lora, add_title, remove_text, aggressive_text_removal, super_resolution]
    )
    
    preset_fast.click(
        fn=set_fast,
        outputs=[baseline_style, genre_lora, add_title, remove_text, aggressive_text_removal, super_resolution]
    )
    
    preset_experimental.click(
        fn=set_experimental,
        outputs=[baseline_style, genre_lora, add_title, remove_text, aggressive_text_removal, super_resolution]
    )
    
    gr.Markdown("""
    ---
    ### 📖 Tips
    - **Best Quality:** Genre-LoRA + Title Overlay + Aggressive Text Removal
    - **Fast Generation:** Disable text removal and super-resolution
    - **Genre-Specific:** Enable Genre-LoRA for style matching
    - **Reproducible:** Set a seed value (any number > 0)
    
    ### 🎯 Features
    - ✅ Multi-agent architecture (7 specialized agents)
    - ✅ Genre-specific LoRA fine-tuning
    - ✅ Automatic genre detection from keywords
    - ✅ Sentiment analysis and semantic expansion
    - ✅ Aggressive text detection and removal
    - ✅ Denoising and super-resolution enhancement
    - ✅ Styled title overlay
    - ✅ Comprehensive quality metrics
    """)

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
