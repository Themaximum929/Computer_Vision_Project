"""Gradio App for PosterO Generalized Layout Generation + FLUX"""
import gradio as gr
from src.postero_generalized import PosterOGeneralized
from src.pipeline import Key2PosterPipeline
from PIL import Image, ImageDraw
import numpy as np

# Configuration
MISTRAL_PATH = "/home/themaximum/models/mistral-7b-instruct"
DATASET_ROOT = "/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"

def visualize_layout(layout):
    """Visualize layout as image"""
    canvas_size = layout['canvas_size']
    img = Image.new('RGB', canvas_size, 'white')
    draw = ImageDraw.Draw(img)
    
    colors = {'text': 'green', 'logo': 'red', 'underlay': 'orange', 'embellishment': 'blue'}
    
    for bbox, label in zip(layout['bboxes'], layout['labels']):
        x1, y1, x2, y2 = bbox
        color = colors.get(layout['category'], 'gray')
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        draw.text((x1+5, y1+5), label, fill=color)
    
    return img

def generate_with_postero(keywords, category, num_elements, sample_size):
    """Generate poster using PosterO layout + FLUX"""
    try:
        # Generate layout
        generator = PosterOGeneralized(MISTRAL_PATH, DATASET_ROOT)
        layout = generator.generate_layout(
            category=category,
            num_elements=num_elements,
            sample_size=sample_size
        )
        
        # Visualize layout
        layout_img = visualize_layout(layout)
        
        # Generate poster with FLUX (optional)
        # pipeline = Key2PosterPipeline(use_flux=True)
        # poster, brief, metrics = pipeline.generate_poster(
        #     keywords,
        #     custom_layout=layout,
        #     output_path=f"poster_{category}.png"
        # )
        
        info = f"""
        ✓ Layout Generated!
        
        Category: {category}
        Canvas Size: {layout['canvas_size']}
        Elements: {len(layout['bboxes'])}
        Labels: {', '.join(layout['labels'])}
        
        SVG Preview:
        {layout['svg'][:300]}...
        """
        
        return layout_img, info
        
    except Exception as e:
        return None, f"Error: {str(e)}"

# Gradio Interface
with gr.Blocks(title="PosterO Generalized + FLUX") as demo:
    gr.Markdown("# PosterO Generalized Layout Generation")
    gr.Markdown("Generate content-aware layouts using LLM-based in-context learning")
    
    with gr.Row():
        with gr.Column():
            keywords = gr.Textbox(label="Keywords", placeholder="cyberpunk neon city")
            category = gr.Dropdown(
                choices=list(PosterOGeneralized.CATEGORIES.keys()),
                value="movie-poster",
                label="Category"
            )
            num_elements = gr.Slider(2, 5, value=3, step=1, label="Number of Elements")
            sample_size = gr.Slider(5, 20, value=10, step=1, label="RAG Sample Size")
            generate_btn = gr.Button("Generate Layout", variant="primary")
        
        with gr.Column():
            layout_img = gr.Image(label="Generated Layout")
            info_text = gr.Textbox(label="Layout Info", lines=10)
    
    # Category descriptions
    gr.Markdown("### Categories")
    for cat, desc in PosterOGeneralized.CATEGORIES.items():
        gr.Markdown(f"- **{cat}**: {desc}")
    
    generate_btn.click(
        generate_with_postero,
        inputs=[keywords, category, num_elements, sample_size],
        outputs=[layout_img, info_text]
    )

if __name__ == "__main__":
    print("⚠️  Update MISTRAL_PATH before running!")
    print(f"Current path: {MISTRAL_PATH}")
    demo.launch(server_name="0.0.0.0", server_port=7860)
