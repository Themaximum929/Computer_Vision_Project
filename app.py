"""Hugging Face Space - FLUX Poster Generator"""
import gradio as gr
import spaces
from src.pipeline import Key2PosterPipeline
import time
import os
import torch

# HF Space optimizations
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

print("🚀 Loading FLUX pipeline for HF Space...")
pipeline = None

def load_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = Key2PosterPipeline(
            use_flux=True,
            add_title=True,
            genre_lora=False,
            remove_text=False,
            super_resolution=False
        )
    return pipeline

print("✅ Ready!")

@spaces.GPU
def generate(keywords, poster_type, style_preset, seed, progress=gr.Progress()):
    try:
        progress(0, desc="Validating input...")
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, f"❌ Provide 2-5 keywords (got {len(keyword_list)})"
        
        progress(0.1, desc="Selecting template...")
        # Template is randomly selected inside pipeline
        
        progress(0.3, desc="Enhancing prompt...")
        # TODO: Advanced prompt enhancement (teammates will implement)
        
        progress(0.5, desc="Generating with FLUX...")
        start = time.time()
        
        pipe = load_pipeline()
        pipe.style_preset = style_preset
        pipe.poster_type = poster_type
        
        image, brief, metrics = pipe.generate_poster(
            keywords,
            output_path=f"outputs/poster_{int(time.time())}.png",
            seed=seed if seed > 0 else None
        )
        
        progress(1.0, desc="Complete!")
        elapsed = time.time() - start
        
        info = f"""### ✅ Generated in {elapsed:.1f}s

**Type:** {poster_type.title()} | **Style:** {style_preset.title()} | **Genre:** {getattr(pipe, '_current_genre', 'N/A')}  
**Sentiment:** {brief['sentiment']} ({brief['confidence']:.0%}) | **Aesthetic:** {metrics['aesthetic']['overall']:.3f}

> 🎨 Template-based composition with FLUX-generated image
"""
        return image, info
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

with gr.Blocks(theme=gr.themes.Soft(), title="Key2Poster FLUX") as demo:
    gr.Markdown("""
    # 🎨 Key2Poster: AI Poster Generator
    Generate professional posters from 2-5 keywords using **FLUX.1-schnell** with native text rendering.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            keywords = gr.Textbox(
                label="Keywords (2-5 words)",
                placeholder="cyberpunk neon city",
                lines=2
            )
            
            with gr.Row():
                poster_type = gr.Dropdown(
                    choices=["movie", "advertise", "event", "education", "social", "music", "sports"],
                    value="movie",
                    label="Poster Type"
                )
                style_preset = gr.Dropdown(
                    choices=["cinematic", "minimalist", "neon", "dark", "vintage", "bright", "professional"],
                    value="cinematic",
                    label="Style"
                )
            
            seed = gr.Number(label="Seed (0 = random)", value=0, precision=0)
            generate_btn = gr.Button("🎨 Generate Poster", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 📋 Poster Types
            **Movie** • **Advertise** • **Event** • **Education** • **Social** • **Music** • **Sports**
            
            ### 🎭 Style Presets
            **Cinematic** • **Minimalist** • **Neon** • **Dark** • **Vintage** • **Bright** • **Professional**
            """)
        
        with gr.Column(scale=2):
            output_image = gr.Image(label="Generated Poster", height=600)
            output_info = gr.Markdown(label="Generation Info")
    
    gr.Examples(
        examples=[
            ["space exploration adventure", "movie", "cinematic", 42],
            ["summer music festival", "event", "bright", 123],
            ["fresh organic food", "advertise", "professional", 456],
            ["save the ocean", "social", "minimalist", 789],
        ],
        inputs=[keywords, poster_type, style_preset, seed],
        outputs=[output_image, output_info],
        fn=generate,
        cache_examples=False
    )
    
    generate_btn.click(
        fn=generate,
        inputs=[keywords, poster_type, style_preset, seed],
        outputs=[output_image, output_info]
    )
    
    gr.Markdown("""
    ---
    **Features:** FLUX.1 Text Generation • 7 Poster Types • 7 Style Presets • Multi-Agent System  
    **Models:** FLUX.1-schnell (4-step inference) • Genre Classification • Aesthetic Scoring
    """)

if __name__ == "__main__":
    demo.queue(max_size=20).launch()
