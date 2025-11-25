"""Simple Gradio Interface for Key2Poster"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
import time

# Initialize pipeline once (faster)
print("Loading Key2Poster pipeline...")
pipeline = Key2PosterPipeline(
    baseline_style=True,
    add_title=False,  # Disabled - text overlay module removed
    remove_text=True,
    aggressive_text_removal=True,
    super_resolution=False  # Faster generation
)
print("✓ Pipeline ready!")

def generate(keywords, seed):
    """Generate poster from keywords"""
    try:
        # Validate
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, f"❌ Please provide 2-5 keywords (you provided {len(keyword_list)})"
        
        # Generate
        start = time.time()
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path=f"outputs/gradio_{int(time.time())}.png",
            seed=seed if seed > 0 else None
        )
        elapsed = time.time() - start
        
        info = f"""
✅ **Generated in {elapsed:.1f}s**

**Sentiment:** {brief['sentiment']} ({brief['confidence']:.0%} confidence)
**Aesthetic Score:** {metrics['aesthetic']['overall']:.3f}
**Resolution:** {metrics['resolution']['width']}×{metrics['resolution']['height']}
"""
        return image, info
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# Create interface
demo = gr.Interface(
    fn=generate,
    inputs=[
        gr.Textbox(
            label="Keywords (2-5 words)",
            placeholder="e.g., space exploration adventure",
            lines=2
        ),
        gr.Number(
            label="Seed (0 = random)",
            value=0,
            precision=0
        )
    ],
    outputs=[
        gr.Image(label="Generated Poster", height=600),
        gr.Markdown(label="Info")
    ],
    title="🎨 Key2Poster: AI Poster Generator",
    description="""
    Generate cinematic movie posters from keywords using AI.
    
    **Features:** Baseline Style • Styled Title Overlay • Denoising • Super-Resolution
    """,
    examples=[
        ["space exploration adventure", 42],
        ["dark fantasy warrior", 123],
        ["cyberpunk city noir", 456],
        ["romantic sunset beach", 789],
    ],
    theme=gr.themes.Soft(),
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch(share=False)
