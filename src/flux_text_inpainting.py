"""FLUX Text Overlay via Inpainting"""
import torch
from diffusers import FluxInpaintPipeline
from PIL import Image, ImageDraw
import numpy as np

class FluxTextInpainting:
    """Add text to existing images using FLUX inpainting"""
    
    def __init__(self):
        # Note: FLUX inpainting requires specific model
        # black-forest-labs/FLUX.1-Fill or similar
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # For now, use img2img approach with FLUX
        from diffusers import FluxPipeline
        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16
        )
        self.pipe.enable_sequential_cpu_offload()
    
    def add_text(self, image, title, genre='action'):
        """Add text by regenerating bottom portion with text"""
        w, h = image.size
        
        # Create mask for text region (bottom 20%)
        mask = Image.new('L', (w, h), 0)
        draw = ImageDraw.Draw(mask)
        text_region_start = int(h * 0.75)
        draw.rectangle([(0, text_region_start), (w, h)], fill=255)
        
        # Genre-specific text styles
        styles = {
            'action': 'bold red metallic title text',
            'horror': 'dark blood-red dripping title text',
            'scifi': 'glowing cyan neon title text',
            'romance': 'elegant pink script title text',
            'comedy': 'playful yellow bouncy title text',
            'fantasy': 'golden magical title text',
            'thriller': 'sharp white angular title text',
            'drama': 'classic white serif title text'
        }
        style = styles.get(genre, 'cinematic title text')
        
        # Prompt for text generation
        prompt = f"movie poster with {style} displaying '{title}', professional typography, centered at bottom"
        
        # Use img2img to add text
        # Note: This regenerates the masked region
        result = self.pipe(
            prompt,
            image=image,
            strength=0.5,  # Keep most of original
            num_inference_steps=4,
            guidance_scale=0.0
        ).images[0]
        
        return result


class FluxTextPrompt:
    """Generate poster WITH text in one pass"""
    
    def __init__(self):
        from diffusers import FluxPipeline
        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16
        )
        self.pipe.enable_sequential_cpu_offload()
    
    def generate_with_text(self, base_prompt, title, genre='action', seed=None):
        """Generate poster with text baked in from start"""
        
        styles = {
            'action': 'bold red metallic title text',
            'horror': 'dark blood-red dripping title text',
            'scifi': 'glowing cyan neon title text',
            'romance': 'elegant pink script title text',
            'comedy': 'playful yellow bouncy title text',
            'fantasy': 'golden magical title text',
            'thriller': 'sharp white angular title text',
            'drama': 'classic white serif title text'
        }
        style = styles.get(genre, 'cinematic title text')
        
        # Combined prompt
        full_prompt = f"movie poster, {base_prompt}, with {style} displaying '{title}' at bottom, professional poster design, cinematic composition"
        
        generator = torch.Generator().manual_seed(seed) if seed else None
        
        result = self.pipe(
            full_prompt,
            width=720,
            height=1280,
            num_inference_steps=4,
            guidance_scale=0.0,
            generator=generator
        ).images[0]
        
        return result
