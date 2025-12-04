"""Gradio App using HuggingFace API (no local GPU needed)"""
import gradio as gr
from src.postero_generalized_api import PosterOGeneralizedAPI
from PIL import Image, ImageDraw
import os

HF_TOKEN = os.getenv("HF_TOKEN", "")
DATASET_ROOT = "/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"

def visualize_layout(layout):
    """Visualize layout as image"""
    canvas_size = layout['canvas_size']
    img = Image.new('RGB', canvas_size, 'white')
    draw = ImageDraw.Draw(img)
    
    colors = {'text': 'green', 'logo': 'red', 'underlay': 'orange', 'embellishment': 'blue'}
    
    for bbox, label in zip(layout['bboxes'], layout['labels']):
        x1, y1, x2, y2 = bbox
        color = 'green' if 'T-' in label else colors.get(label, 'gray')
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        draw.text((x1+5, y1+5), label, fill=color)
    
    return img

def generate_with_api(hf_token, category, num_elements, sample_size):
    """Generate using HuggingFace API"""
    if not hf_token:
        return None, "⚠️ Please enter your HuggingFace token"
    
    try:
        generator = PosterOGeneralizedAPI(hf_token, DATASET_ROOT)
        
        layout = generator.generate_layout(
            category=category,
            num_elements=num_elements,
            sample_size=sample_size
        )
        
        layout_img = visualize_layout(layout)
        
        info = f"""✓ Layout Generated via HuggingFace API!

Category: {category}
Canvas: {layout['canvas_size']}
Elements: {len(layout['bboxes'])}
Labels: {', '.join(layout['labels'])}

SVG:
{layout['svg'][:400]}...
"""
        return layout_img, info
        
    except Exception as e:
        return None, f"Error: {str(e)}"

with gr.Blocks(title="PosterO API") as demo:
    gr.Markdown("# PosterO Generalized (HuggingFace API)")
    gr.Markdown("No local GPU needed! Uses HuggingFace Inference API")
    
    with gr.Row():
        with gr.Column():
            hf_token = gr.Textbox(
                label="HuggingFace Token",
                placeholder="hf_...",
                type="password",
                value=HF_TOKEN
            )
            gr.Markdown("[Get token here](https://huggingface.co/settings/tokens)")
            
            category = gr.Dropdown(
                choices=list(PosterOGeneralizedAPI.CATEGORIES.keys()),
                value="movie-poster",
                label="Category"
            )
            num_elements = gr.Slider(2, 5, value=3, step=1, label="Elements")
            sample_size = gr.Slider(3, 10, value=5, step=1, label="Sample Size")
            generate_btn = gr.Button("Generate Layout", variant="primary")
        
        with gr.Column():
            layout_img = gr.Image(label="Generated Layout")
            info_text = gr.Textbox(label="Info", lines=12)
    
    generate_btn.click(
        generate_with_api,
        inputs=[hf_token, category, num_elements, sample_size],
        outputs=[layout_img, info_text]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
