"""Unified Web Interface - Best of All Projects"""
import gradio as gr
from src.unified_pipeline import UnifiedPosterPipeline
from pathlib import Path
import time

pipeline = UnifiedPosterPipeline(use_lora=True, genre_detection=True)

def generate_unified(keywords, template, add_effects, seed):
    """Generate poster using unified pipeline"""
    try:
        # Validate
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, None, f"❌ Error: Provide 2-5 keywords (got {len(keyword_list)})"
        
        # Generate
        result = pipeline.generate(
            keywords=keywords,
            template=template,
            add_effects=add_effects,
            seed=seed if seed > 0 else None
        )
        
        # Save
        output_path = f"outputs/unified_{int(time.time())}.png"
        pipeline.save(result, output_path)
        
        # Format info
        info = f"""
✅ **Generation Complete!**

**Keywords:** {keywords}
**Genre:** {result['genre']}
**Sentiment:** {result['brief']['sentiment']} ({result['brief']['confidence']:.2f})
**Mood:** {result['brief']['mood']} → Color Mood: {result['mood']}

**Color Palette:**
{', '.join([f'RGB{c}' for c in result['palette'][:3]])}

**Template:** {template.title()}
**Effects:** {'Enabled' if add_effects else 'Disabled'}
**Generation Time:** {result['time']:.1f}s

**Pipeline Flow:**
1. ✓ Concept Analysis (sentiment + genre)
2. ✓ Image Generation (genre-specific LoRA)
3. ✓ Color Extraction (palette analysis)
4. ✓ Background Processing (vignette + enhancement)
5. ✓ Text Composition (smart placement)

**Saved:** {output_path}
"""
        
        # Create composition guide
        from src.composition_engine import CompositionEngine
        comp = CompositionEngine()
        guide = comp.apply_rule_of_thirds_grid(result['image'], show_grid=True)
        
        return result['image'], guide, info
        
    except Exception as e:
        import traceback
        return None, None, f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"

# Create interface
with gr.Blocks(title="Unified Poster Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎬 Unified Poster Generator
    
    **Combining Best Practices From:**
    - 🎨 PosterCraft: Clean 5-step flow
    - 📐 poster-generator-ai: Template system  
    - ✍️ digitalmovieposter: Text styling
    - 🎯 Key2Poster: Genre-specific LoRA
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            keywords = gr.Textbox(
                label="Keywords (2-5 words)",
                placeholder="cyberpunk neon city",
                lines=2
            )
            
            gr.Markdown("### Settings")
            template = gr.Dropdown(
                choices=["minimal", "classic", "modern", "split"],
                value="minimal",
                label="Template Style"
            )
            
            add_effects = gr.Checkbox(
                label="Add Visual Effects",
                value=True,
                info="Vignette + quality enhancement"
            )
            
            seed = gr.Number(
                label="Seed (0 = random)",
                value=0,
                precision=0
            )
            
            generate_btn = gr.Button("🎨 Generate Poster", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 🎯 Features
            - Genre-specific LoRA models
            - Smart color palette extraction
            - Intelligent text placement
            - Professional templates
            - Vignette effects
            """)
        
        with gr.Column(scale=2):
            gr.Markdown("### Generated Poster")
            
            with gr.Tabs():
                with gr.Tab("Final Result"):
                    output_image = gr.Image(label="Poster", type="pil", height=600)
                with gr.Tab("Composition Guide"):
                    guide_image = gr.Image(label="Rule of Thirds", type="pil", height=600)
            
            output_info = gr.Markdown(value="*Generate a poster to see results*")
    
    # Examples
    gr.Examples(
        examples=[
            ["cyberpunk neon city", "modern", True, 42],
            ["dark fantasy warrior", "classic", True, 123],
            ["space exploration adventure", "minimal", True, 456],
            ["romantic sunset beach", "split", True, 789],
        ],
        inputs=[keywords, template, add_effects, seed]
    )
    
    generate_btn.click(
        fn=generate_unified,
        inputs=[keywords, template, add_effects, seed],
        outputs=[output_image, guide_image, output_info]
    )

if __name__ == "__main__":
    demo.launch(share=False)
