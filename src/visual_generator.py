"""Visual Design Agent - Generates poster using Stable Diffusion + LoRA"""
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import os

class VisualGenerator:
    def __init__(self, model_id="runwayml/stable-diffusion-v1-5", lora_path=None, use_lora=False):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None
        )
        
        # Use faster scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe = self.pipe.to(self.device)
        
        # Load fine-tuned weights if available
        self.use_lora = use_lora
        if use_lora and lora_path:
            weights_file = os.path.join(lora_path, "lora_weights.pth")
            if os.path.exists(weights_file):
                print(f"Loading fine-tuned weights from {lora_path}")
                state_dict = torch.load(weights_file, map_location=self.device)
                self.pipe.unet.load_state_dict(state_dict, strict=False)
            else:
                print(f"Warning: No weights found at {weights_file}")
    
    def generate(self, prompt, width=720, height=1280, num_inference_steps=60, guidance_scale=7.5, seed=None):
        """Generate poster image from prompt"""
        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        
        # VERY strong negative prompt - absolutely no text
        negative_prompt = (
            "text, words, letters, typography, font, title, subtitle, caption, label, "
            "watermark, logo, signature, writing, alphabet, characters, numbers, digits, "
            "symbols, signs, banner, headline, tagline, slogan, credits, names, "
            "readable text, written words, printed text, handwriting, calligraphy, "
            "oversaturated, neon colors, artificial colors, digital art, 3d render, "
            "blurry, low quality, distorted, deformed, ugly, bad anatomy"
        )
        
        # Generate at slightly higher resolution for better quality
        gen_width = int(width * 1.1)
        gen_height = int(height * 1.1)
        
        image = self.pipe(
            prompt,
            negative_prompt=negative_prompt,
            width=gen_width,
            height=gen_height,
            num_inference_steps=num_inference_steps,
            guidance_scale=9.5,
            generator=generator
        ).images[0]
        
        # Downscale to target (improves sharpness)
        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        return image
