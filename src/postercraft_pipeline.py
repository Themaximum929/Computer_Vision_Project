"""PosterCraft-Inspired Complete Pipeline"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from pathlib import Path
import time

class PosterCraftPipeline:
    """Complete poster generation following PosterCraft architecture"""
    
    def __init__(self, model_path="runwayml/stable-diffusion-v1-5"):
        self.model_path = model_path
        self._load_models()
    
    def _load_models(self):
        """Load all required models"""
        from diffusers import StableDiffusionPipeline
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        self.device = device
    
    def generate(self, prompt, style="cinematic", size=(768, 1024), seed=None):
        """
        Complete generation flow:
        1. Prompt Enhancement
        2. Image Generation
        3. Background Processing
        4. Text Overlay
        5. Final Composition
        """
        print(f"\n🎨 PosterCraft Pipeline Started")
        print(f"Prompt: {prompt}")
        print(f"Style: {style}")
        
        # Step 1: Enhance prompt
        enhanced_prompt = self._enhance_prompt(prompt, style)
        print(f"\n[1/5] Enhanced Prompt: {enhanced_prompt}")
        
        # Step 2: Generate base image
        print(f"[2/5] Generating base image...")
        image = self._generate_image(enhanced_prompt, size, seed)
        
        # Step 3: Process background
        print(f"[3/5] Processing background...")
        image = self._process_background(image, style)
        
        # Step 4: Add text overlay
        print(f"[4/5] Adding text overlay...")
        image = self._add_text_overlay(image, prompt, style)
        
        # Step 5: Final composition
        print(f"[5/5] Final composition...")
        image = self._final_composition(image, style)
        
        print(f"✅ Generation complete!")
        return image
    
    def _enhance_prompt(self, prompt, style):
        """Enhance prompt with style-specific keywords"""
        style_keywords = {
            "cinematic": "cinematic lighting, dramatic composition, movie poster style",
            "minimalist": "clean design, minimal elements, modern aesthetic",
            "vintage": "retro style, vintage colors, classic poster design",
            "modern": "contemporary design, bold colors, sleek composition"
        }
        
        base = f"professional movie poster, {prompt}"
        enhancement = style_keywords.get(style, style_keywords["cinematic"])
        return f"{base}, {enhancement}, high quality, detailed"
    
    def _generate_image(self, prompt, size, seed):
        """Generate base image using Stable Diffusion"""
        import torch
        
        generator = torch.Generator(device=self.device)
        if seed:
            generator.manual_seed(seed)
        
        result = self.pipe(
            prompt=prompt,
            negative_prompt="text, words, letters, watermark, low quality, blurry",
            height=size[1],
            width=size[0],
            num_inference_steps=30,
            guidance_scale=7.5,
            generator=generator
        )
        
        return result.images[0]
    
    def _process_background(self, image, style):
        """Process background with style-specific effects"""
        # Add subtle vignette
        w, h = image.size
        mask = Image.new('L', (w, h), 255)
        draw = ImageDraw.Draw(mask)
        
        for i in range(int(min(w, h) * 0.2)):
            alpha = int(255 * (1 - 0.3 * (1 - i / (min(w, h) * 0.2))))
            draw.rectangle([i, i, w-i, h-i], outline=alpha)
        
        mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.03))
        vignette = Image.new('RGB', (w, h), (0, 0, 0))
        image = Image.composite(image, vignette, mask)
        
        # Enhance based on style
        if style == "cinematic":
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
        elif style == "vintage":
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(0.8)
        
        return image
    
    def _add_text_overlay(self, image, text, style):
        """Add text overlay with style-specific design"""
        w, h = image.size
        
        # Create gradient overlay for text area
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Bottom gradient
        for i in range(int(h * 0.3)):
            alpha = int(180 * (i / (h * 0.3)))
            draw.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
        
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        # Add title text
        draw = ImageDraw.Draw(image)
        try:
            font_size = int(h * 0.08)
            font = ImageFont.truetype("fonts/cinematic/BebasNeueRegular.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Center text at bottom
        title = text.upper()
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (w - text_w) // 2
        y = int(h * 0.85)
        
        # Draw text with outline
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            draw.text((x + offset[0], y + offset[1]), title, font=font, fill=(0, 0, 0))
        draw.text((x, y), title, font=font, fill=(255, 255, 255))
        
        return image
    
    def _final_composition(self, image, style):
        """Final composition and quality enhancement"""
        # Sharpen
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        # Adjust brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def batch_generate(self, prompts, style="cinematic", output_dir="outputs/postercraft"):
        """Generate multiple posters"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"\n{'='*60}")
            print(f"Generating {i+1}/{len(prompts)}")
            
            image = self.generate(prompt, style=style, seed=42+i)
            output_path = Path(output_dir) / f"poster_{i:03d}.png"
            image.save(output_path, quality=95)
            
            results.append({
                "prompt": prompt,
                "path": str(output_path),
                "style": style
            })
            
            print(f"Saved: {output_path}")
        
        return results
