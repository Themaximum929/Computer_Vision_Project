"""Visual Design Agent - Generates poster using FLUX.1"""
import torch
from diffusers import FluxPipeline
from PIL import Image

class VisualGeneratorFlux:
    def __init__(self, model_id="black-forest-labs/FLUX.1-schnell"):
        """
        Initialize FLUX.1 generator
        
        Models:
        - black-forest-labs/FLUX.1-schnell (fast, 4 steps)
        - black-forest-labs/FLUX.1-dev (quality, 20-50 steps, requires auth)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.pipe = FluxPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32
        )
        self.pipe = self.pipe.to(self.device)
        
        # Enable memory optimizations
        if self.device == "cuda":
            self.pipe.enable_model_cpu_offload()
    
    def generate(self, prompt, width=720, height=1280, num_inference_steps=4, guidance_scale=0.0, seed=None):
        """Generate poster image from prompt"""
        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        
        # Enhanced prompt for movie poster style
        enhanced_prompt = f"cinematic movie poster, {prompt}, dramatic lighting, professional photography, high quality, detailed, epic composition, vibrant colors, no text, no words, no letters"
        
        image = self.pipe(
            enhanced_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        return image
