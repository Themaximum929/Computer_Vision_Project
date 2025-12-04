"""Visual Design Agent - Generates poster using FLUX.1"""
import torch
import os
from diffusers import FluxPipeline
from PIL import Image

class VisualGeneratorFlux:
    def __init__(self, model_id="black-forest-labs/FLUX.1-schnell", hf_token=None):
        """
        Initialize FLUX.1 generator
        
        Models:
        - black-forest-labs/FLUX.1-schnell (fast, 4 steps)
        - black-forest-labs/FLUX.1-dev (quality, 20-50 steps, requires auth)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Get token from env or parameter
        if hf_token is None:
            hf_token = os.getenv("HF_TOKEN")
        
        self.pipe = FluxPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
            token=hf_token
        )
        
        # Balanced: Speed + Memory efficiency
        if self.device == "cuda":
            # Use sequential offload (faster than model_cpu_offload)
            self.pipe.enable_sequential_cpu_offload()
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            print("✓ FLUX loaded with sequential offload (balanced mode)")
        else:
            self.pipe = self.pipe.to(self.device)
    
    def generate(self, prompt, width=None, height=None, num_inference_steps=4, guidance_scale=0.0, seed=None):
        """Generate poster image from prompt"""
        # Local: 512x768 (faster), HF Space: 720x1280 (quality)
        if width is None:
            width = 720 if os.getenv('SPACE_ID') else 512
        if height is None:
            height = 1280 if os.getenv('SPACE_ID') else 768
        
        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        
        image = self.pipe(
            prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        return image