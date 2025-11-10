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
        
        # Load LoRA if available
        self.use_lora = use_lora
        if use_lora and lora_path and os.path.exists(lora_path):
            print(f"Loading LoRA from {lora_path}")
            self.pipe.load_lora_weights(lora_path)
    
    def generate(self, prompt, width=512, height=768, num_inference_steps=30, guidance_scale=7.5, seed=None):
        """Generate poster image from prompt"""
        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        
        negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, text, watermark"
        
        image = self.pipe(
            prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]
        return image
