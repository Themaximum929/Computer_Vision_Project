"""Text-free poster generation using multi-stage approach"""
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import numpy as np

class NoTextGenerator:
    def __init__(self, model_id="runwayml/stable-diffusion-v1-5", lora_path=None, use_lora=False):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None
        ).to(self.device)
        
        if use_lora and lora_path:
            import os
            weights_file = os.path.join(lora_path, "lora_weights.pth")
            if os.path.exists(weights_file):
                state_dict = torch.load(weights_file, map_location=self.device)
                self.pipe.unet.load_state_dict(state_dict, strict=False)
    
    def generate(self, prompt, width=720, height=1280, seed=None):
        """Generate text-free poster with high quality"""
        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        
        # Ultra-strong negative prompt
        negative_prompt = (
            "text, words, letters, font, typography, writing, alphabet, numbers, "
            "title, caption, subtitle, label, watermark, logo, signature, banner, "
            "headline, tagline, credits, names, readable, written, printed, "
            "characters, symbols, signs, calligraphy, handwriting, "
            "any text of any kind, any words whatsoever, any letters at all"
        )
        
        # Add explicit instruction in prompt
        clean_prompt = f"{prompt}, no text, no words, no letters, clean visual composition, high quality"
        
        # Generate at 576x1024 (closer to target, maintains aspect ratio, reduces blur)
        image = self.pipe(
            clean_prompt,
            negative_prompt=negative_prompt,
            width=576,
            height=1024,
            num_inference_steps=60,  # More steps for better quality
            guidance_scale=10.0,
            generator=generator
        ).images[0]
        
        # Upscale to exact target with LANCZOS
        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        return image
