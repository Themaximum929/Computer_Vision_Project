"""Modern Diffusion-Based Text Overlay using FLUX"""
from diffusers import FluxPipeline
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class DiffusionTextOverlay:
    """Generate text directly using FLUX diffusion model"""
    
    def __init__(self, model_id="black-forest-labs/FLUX.1-schnell"):
        print(f"Loading FLUX text renderer: {model_id}")
        self.pipe = FluxPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16
        )
        self.pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        
        # Genre-specific text styles
        self.text_styles = {
            'action': 'bold red metallic title text, strong typography, movie poster style',
            'horror': 'dark blood-red dripping title text, horror movie typography, ominous',
            'scifi': 'glowing cyan futuristic title text, sci-fi typography, neon effect',
            'romance': 'elegant pink script title text, romantic typography, soft',
            'comedy': 'playful yellow bouncy title text, fun typography, energetic',
            'fantasy': 'golden magical title text, fantasy typography, ornate',
            'thriller': 'sharp white angular title text, thriller typography, dramatic shadow',
            'drama': 'classic white serif title text, elegant typography, professional'
        }
    
    def add_text_via_generation(self, base_image, title, genre='action', seed=None):
        """Generate new image with text baked in using FLUX"""
        # Convert base image to prompt description
        w, h = base_image.size
        
        # Get genre-specific text style
        text_style = self.text_styles.get(genre, self.text_styles['action'])
        
        # Create prompt for text overlay
        prompt = f"movie poster with {text_style} displaying '{title}', professional poster design, cinematic composition"
        
        # Generate with FLUX
        generator = torch.Generator().manual_seed(seed) if seed else None
        
        result = self.pipe(
            prompt,
            num_inference_steps=4,  # FLUX.1-schnell is fast
            guidance_scale=0.0,
            height=h,
            width=w,
            generator=generator
        ).images[0]
        
        return result
    
    def add_text_via_inpainting(self, base_image, title, genre='action', position='bottom'):
        """Add text using inpainting (requires FLUX inpainting model)"""
        w, h = base_image.size
        
        # Create mask for text region
        mask = Image.new('L', (w, h), 0)
        draw = ImageDraw.Draw(mask)
        
        # Define text region based on position
        if position == 'bottom':
            region = (0, int(h * 0.7), w, h)
        elif position == 'top':
            region = (0, 0, w, int(h * 0.3))
        else:  # center
            region = (0, int(h * 0.4), w, int(h * 0.6))
        
        draw.rectangle(region, fill=255)
        
        # Get text style
        text_style = self.text_styles.get(genre, self.text_styles['action'])
        
        # Inpainting prompt
        prompt = f"{text_style} displaying '{title}', movie poster typography"
        
        # Note: This requires FLUX inpainting model
        # For now, return composite
        return self._composite_text(base_image, title, genre, region)
    
    def _composite_text(self, base_image, title, genre, region):
        """Fallback: composite text using PIL (temporary)"""
        from src.enhanced_text_overlay import EnhancedTextOverlay
        overlay = EnhancedTextOverlay()
        return overlay.add_poster_text(base_image, title, genre)


class ControlNetTextOverlay:
    """Use ControlNet for precise text placement"""
    
    def __init__(self):
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
        
        print("Loading ControlNet for text rendering...")
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_canny",
            torch_dtype=torch.float16
        )
        
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16
        )
        self.pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    
    def add_text_with_control(self, base_image, title, genre='action'):
        """Add text using ControlNet guidance"""
        import cv2
        
        # Create edge map from base image
        img_array = np.array(base_image)
        edges = cv2.Canny(img_array, 100, 200)
        control_image = Image.fromarray(edges)
        
        # Genre-specific prompts
        text_prompts = {
            'action': f'bold red title text "{title}" on movie poster, action style',
            'horror': f'dark horror title text "{title}" on movie poster, scary typography',
            'scifi': f'futuristic cyan title text "{title}" on movie poster, sci-fi style',
        }
        
        prompt = text_prompts.get(genre, f'movie poster title text "{title}"')
        
        result = self.pipe(
            prompt,
            control_image,
            num_inference_steps=20
        ).images[0]
        
        return result


class HybridTextOverlay:
    """Hybrid: AI detection + high-quality rendering"""
    
    def __init__(self):
        self.flux_overlay = None
        self.fallback_overlay = None
    
    def add_text(self, base_image, title, genre='action', method='auto'):
        """Smart text overlay with multiple methods"""
        
        if method == 'flux' or (method == 'auto' and torch.cuda.is_available()):
            # Use FLUX for best quality
            if not self.flux_overlay:
                self.flux_overlay = DiffusionTextOverlay()
            return self.flux_overlay.add_text_via_generation(base_image, title, genre)
        
        else:
            # Fallback to enhanced PIL
            if not self.fallback_overlay:
                from src.enhanced_text_overlay import EnhancedTextOverlay
                self.fallback_overlay = EnhancedTextOverlay()
            return self.fallback_overlay.add_poster_text(base_image, title, genre)
