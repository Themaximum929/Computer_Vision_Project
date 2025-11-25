"""Unified Web Interface"""
import gradio as gr
from src.pipeline import Key2PosterPipeline
from pathlib import Path
import time

pipeline = Key2PosterPipeline(use_lora=True, genre_lora=True, add_title=False, super_resolution=False)

def generate_unified(keywords, seed):
    """Generate poster using pipeline"""
    try:
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            return None, f"❌ Error: Provide 2-5 keywords (got {len(keyword_list)})"
        
        start = time.time()
        output_path = f"outputs/unified_{int(time.time())}.png"
        
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path=output_path,
            seed=seed if seed > 0 else None
        )
        
        elapsed = time.time() - start
        genre = getattr(pipeline, '_current_genre', 'N/A')
        
        info = f"""
✅ **Generation Complete!**

**Keywords:** {keywords}
**Genre:** {genre}
**Sentiment:** {brief['sentiment']} ({brief['confidence']:.2f})
**Mood:** {brief['mood']}
**Aesthetic:** {metrics['aesthetic']['overall']:.3f}
**Time:** {elapsed:.1f}s

**Saved:** {output_path}
"""
        return image, info
        
    except Exception as e:
        import traceback
        return None, f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"

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
            
            seed = gr.Number(
                label="Seed (0 = random)",
                value=0,
                precision=0
            )
            
            generate_btn = gr.Button("🎨 Generate Poster", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 🎯 Features
            - Genre-specific LoRA models
            - Sentiment analysis
            - Text removal
            - Quality enhancement
            """)
        
        with gr.Column(scale=2):
            gr.Markdown("### Generated Poster")
            output_image = gr.Image(label="Poster", type="pil", height=600)
            output_info = gr.Markdown(value="*Generate a poster to see results*")
    
    # Examples
    gr.Examples(
        examples=[
            ["cyberpunk neon city", 42],
            ["dark fantasy warrior", 123],
            ["space exploration adventure", 456],
            ["romantic sunset beach", 789],
        ],
        inputs=[keywords, seed]
    )
    
    generate_btn.click(
        fn=generate_unified,
        inputs=[keywords, seed],
        outputs=[output_image, output_info]
    )

if __name__ == "__main__":
    demo.launch(share=False)
