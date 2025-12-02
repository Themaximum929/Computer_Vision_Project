"""CLG-LO Poster Generator - AI Layout with Gradio UI"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from src.clg_lo_engine import CLGLOEngine
import time
from pathlib import Path
import torch
import gc

# Initialize once and reuse
clg_lo = CLGLOEngine()
pipeline = Key2PosterPipeline(
    use_flux=True,
    remove_text=True,
    add_title=False,
    poster_type='movie'
)

poster_state = {"image": None, "template": None}

def generate_with_clg_lo(keywords, seed, optimize):
    try:
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, "❌ Provide 2-5 keywords"
        
        start = time.time()
        
        # Use pipeline's generator (it's called 'generator', not 'visual_generator')
        flux_image = pipeline.generator.generate(
            keywords, 
            seed=seed if seed > 0 else None, 
            width=600, 
            height=800
        )
        
        # Generate layout with CLG-LO
        template = clg_lo.generate_layout(flux_image, keywords, optimize=optimize)
        
        # Compose poster using pipeline's generate_poster with template
        # Save flux_image temporarily and pass template
        output_path = f"outputs/clg_lo_{int(time.time())}.png"
        
        # Use pipeline's generate_poster but with CLG-LO template
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path=output_path,
            seed=seed if seed > 0 else None,
            evaluate=True,
            template=template
        )
        
        poster_state["image"] = image
        poster_state["template"] = template
        
        # Cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
        elapsed = time.time() - start
        
        # Check if model is trained
        model_status = "✅ Trained" if Path("models/layout_gan.pth").exists() else "⚠️ Untrained (random)"
        
        info = f"""✅ Generated with CLG-LO

**Method:** {'Optimized' if optimize else 'Direct'} LayoutGAN
**Model:** {model_status}
**Layout:** AI-generated (infinite variety)
**Aesthetic:** {metrics['aesthetic']['overall']:.3f}
**Time:** {elapsed:.1f}s

**Enhanced Prompt:** {brief.get('prompt', keywords)[:100]}...
**Template Size:** {template['size']}
**Layers:** {len(template['layers'])}"""
        
        return image, info
        
    except Exception as e:
        import traceback
        return None, f"❌ Error: {str(e)}\n{traceback.format_exc()}"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""# 🤖 CLG-LO: AI Poster Layout Generator
**Constrained LayoutGAN with Latent Optimization**

Generate posters with neural network layouts (infinite variety!)""")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎨 Generate")
            keywords = gr.Textbox(label="Keywords (2-5 words)", placeholder="cyberpunk neon city")
            seed = gr.Number(label="Seed (0 = random)", value=0, precision=0)
            optimize = gr.Checkbox(label="Enable Latent Optimization", value=True)
            gen_btn = gr.Button("🚀 Generate with CLG-LO", variant="primary")
            
            gr.Markdown("""### ℹ️ About CLG-LO
**LayoutGAN:** Neural network trained on poster layouts
**Latent Optimization:** Constraint-based refinement
**Constraints:** Overlap, Alignment, Hierarchy, Border, Balance

**Advantages:**
- ✅ Infinite layout variety
- ✅ Content-aware design
- ✅ Professional quality
- ✅ Constraint-optimized

**Note:** Train model first with `python train_layout_gan.py`""")
        
        with gr.Column(scale=2):
            output_image = gr.Image(label="Generated Poster", height=700)
            status = gr.Markdown("Ready...")
    
    gen_btn.click(generate_with_clg_lo, [keywords, seed, optimize], [output_image, status])
    
    gr.Examples(
        [["cyberpunk neon city", 42, True], 
         ["anime love story japanese", 123, True],
         ["summer music festival", 0, False]],
        [keywords, seed, optimize]
    )
    
    gr.Markdown("""---
### 📊 CLG-LO vs Template Comparison

| Metric | Template | CLG-LO |
|--------|----------|--------|
| Variety | ~10 layouts | Infinite |
| Adaptability | Static | Dynamic |
| Optimization | None | Constrained |
| Speed | 12-18s | 15-23s |
""")

if __name__ == "__main__":
    demo.launch()
