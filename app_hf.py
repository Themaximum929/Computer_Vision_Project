"""Hugging Face Space with ZeroGPU support"""
import gradio as gr
import spaces
from src.pipeline import Key2PosterPipeline
import time

# Initialize pipeline (will be moved to GPU on-demand)
pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=False,  # Disable for HF Space
    remove_text=False,
    super_resolution=False
)

@spaces.GPU(duration=60)  # Request GPU for 60 seconds
def generate(keywords, poster_type, style_preset, seed):
    try:
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, f"❌ Provide 2-5 keywords (got {len(keyword_list)})"
        
        start = time.time()
        pipeline.style_preset = style_preset
        pipeline.poster_type = poster_type
        
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path=f"outputs/flux_{int(time.time())}.png",
            seed=seed if seed > 0 else None
        )
        elapsed = time.time() - start
        
        info = f"""✅ Generated in {elapsed:.1f}s | {poster_type.title()} | {style_preset.title()}"""
        return image, info
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

demo = gr.Interface(
    fn=generate,
    inputs=[
        gr.Textbox(label="Keywords (2-5 words)", placeholder="cyberpunk neon city", lines=2),
        gr.Dropdown(choices=["movie", "advertise", "event", "education", "social", "music", "sports"], value="movie", label="Poster Type"),
        gr.Dropdown(choices=["cinematic", "minimalist", "neon", "dark", "vintage", "bright", "professional"], value="cinematic", label="Style"),
        gr.Number(label="Seed (0 = random)", value=0, precision=0)
    ],
    outputs=[gr.Image(label="Generated Poster", height=600), gr.Markdown()],
    title="🎨 Key2Poster FLUX",
    description="Generate professional posters from 2-5 keywords using FLUX.1",
    examples=[
        ["space exploration adventure", "movie", "cinematic", 42],
        ["summer music festival", "event", "bright", 123],
    ],
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch()
