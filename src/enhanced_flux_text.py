"""Enhanced FLUX Text Generation with Artifact Removal"""
import torch
from diffusers import FluxPipeline
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

class EnhancedFluxText:
    """FLUX text generation with post-processing to remove artifacts"""
    
    def __init__(self):
        from src.visual_generator_flux import VisualGeneratorFlux
        self.generator = VisualGeneratorFlux()
        
        # Load OCR for artifact detection
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            self.ocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.ocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
        except:
            self.ocr_processor = None
            self.ocr_model = None
    
    def generate_with_clean_text(self, base_prompt, title, genre='action', seed=None):
        """Generate poster with FLUX, then add clean PIL text overlay"""
        
        # Step 1: Generate base poster WITHOUT text artifacts
        clean_prompt = f"professional movie poster, {base_prompt}, cinematic composition, no text, no words, no letters"
        
        result = self.generator.pipe(
            clean_prompt,
            width=720,
            height=1280,
            num_inference_steps=4,
            guidance_scale=0.0,
            generator=torch.Generator().manual_seed(seed) if seed else None
        ).images[0]
        
        # Step 2: Remove any text artifacts that slipped through
        result = self._remove_text_artifacts(result)
        
        # Step 3: Add clean styled title overlay
        result = self._add_clean_title(result, title, genre)
        
        return result
    
    def _remove_text_artifacts(self, image):
        """Detect and blur text artifacts in generated image"""
        if not self.ocr_processor:
            return image
        
        # Simple approach: blur bottom 15% where artifacts usually appear
        w, h = image.size
        img_array = np.array(image)
        
        # Blur potential text regions
        artifact_region = int(h * 0.85)
        bottom_section = img_array[artifact_region:, :]
        
        # Apply Gaussian blur to remove artifacts
        bottom_pil = Image.fromarray(bottom_section)
        blurred = bottom_pil.filter(ImageFilter.GaussianBlur(5))
        
        img_array[artifact_region:, :] = np.array(blurred)
        
        return Image.fromarray(img_array)
    
    def _add_clean_title(self, image, title, genre):
        """Add professional styled title with no artifacts"""
        w, h = image.size
        
        # Genre-specific styling
        styles = {
            'action': {'color': (255, 50, 50), 'glow': (255, 0, 0, 200), 'font': 'BebasNeueRegular.ttf'},
            'horror': {'color': (150, 0, 0), 'glow': (80, 0, 0, 220), 'font': 'TrajanPro-Regular.ttf'},
            'scifi': {'color': (0, 220, 255), 'glow': (0, 150, 255, 200), 'font': 'Blocksmith.otf'},
            'romance': {'color': (255, 180, 200), 'glow': (255, 100, 150, 180), 'font': 'PlayfairDisplay-Regular.ttf'},
            'comedy': {'color': (255, 220, 0), 'glow': (255, 180, 0, 180), 'font': 'Lobster-Regular.ttf'},
            'fantasy': {'color': (255, 215, 0), 'glow': (255, 140, 0, 200), 'font': 'CinzelDecorative-Bold.ttf'},
            'thriller': {'color': (255, 255, 255), 'glow': (0, 0, 0, 250), 'font': 'Arvo-Bold.ttf'},
            'drama': {'color': (240, 240, 240), 'glow': (100, 100, 100, 150), 'font': 'bodoni_[allfont.net].ttf'}
        }
        
        style = styles.get(genre, styles['action'])
        font_size = int(h * 0.10)
        
        try:
            font = ImageFont.truetype(f'fonts/cinematic/{style["font"]}', font_size)
        except:
            font = ImageFont.load_default()
        
        # Create text layer
        txt_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Calculate position
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        x_pos = (w - text_w) // 2
        y_pos = int(h * 0.82)
        
        # Add glow effect
        glow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        
        for i in range(8):
            offset = i * 3
            glow_draw.text((x_pos, y_pos), title, font=font, fill=style['glow'])
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
        
        # Composite glow
        result = Image.alpha_composite(image.convert('RGBA'), glow_layer)
        
        # Add stroke
        draw = ImageDraw.Draw(result)
        stroke_width = max(2, font_size // 30)
        for ox in range(-stroke_width, stroke_width+1):
            for oy in range(-stroke_width, stroke_width+1):
                if ox*ox + oy*oy <= stroke_width*stroke_width:
                    draw.text((x_pos+ox, y_pos+oy), title, font=font, fill=(0, 0, 0, 255))
        
        # Main text
        draw.text((x_pos, y_pos), title, font=font, fill=style['color'])
        
        return result.convert('RGB')


class StyleEnhancedFlux:
    """FLUX text generation without PIL overlay"""
    
    def __init__(self, shared_generator=None):
        if shared_generator:
            self.generator = shared_generator
        else:
            from src.visual_generator_flux import VisualGeneratorFlux
            self.generator = VisualGeneratorFlux()
    
    def generate_poster(self, keywords, title, genre='action', seed=None, style_preset='cinematic', poster_type='movie'):
        """Generate with FLUX text generation (no PIL overlay)"""
        
        # Poster type templates
        poster_types = {
            'movie': 'cinematic movie poster',
            'advertise': 'professional advertising poster, commercial design',
            'event': 'event poster, promotional design, eye-catching',
            'education': 'educational poster, informative design, clear layout',
            'social': 'social awareness poster, impactful message, modern design',
            'music': 'music concert poster, energetic design, bold typography',
            'sports': 'sports event poster, dynamic action, athletic design'
        }
        
        # Style presets
        presets = {
            'cinematic': 'dramatic lighting, high contrast, depth of field',
            'minimalist': 'clean composition, negative space, bold colors, modern design',
            'vintage': 'retro style, grain texture, classic typography aesthetic',
            'neon': 'vibrant neon colors, cyberpunk aesthetic, glowing elements',
            'dark': 'dark moody atmosphere, dramatic shadows, noir style',
            'bright': 'vibrant colors, high energy, cheerful atmosphere',
            'professional': 'clean professional design, corporate style, polished'
        }
        
        # Genre/category-specific text styles
        text_styles = {
            'action': 'bold red metallic title text',
            'horror': 'dark blood-red dripping horror title text',
            'scifi': 'glowing cyan futuristic neon title text',
            'romance': 'elegant pink script title text',
            'comedy': 'playful yellow bouncy title text',
            'fantasy': 'golden magical ornate title text',
            'thriller': 'sharp white angular title text with dramatic shadow',
            'drama': 'classic white serif title text',
            'business': 'professional bold sans-serif title text',
            'education': 'clear readable bold title text',
            'event': 'eye-catching bold colorful title text'
        }
        
        poster_template = poster_types.get(poster_type, poster_types['movie'])
        style_suffix = presets.get(style_preset, presets['cinematic'])
        text_style = text_styles.get(genre, 'bold professional title text')
        
        # FLUX prompt with text generation
        full_prompt = f"{poster_template}, {keywords}, {style_suffix}, with {text_style} displaying '{title}' at bottom, professional poster design"
        
        # Generate with FLUX
        result = self.generator.pipe(
            full_prompt,
            width=720,
            height=1280,
            num_inference_steps=4,
            guidance_scale=0.0,
            generator=torch.Generator().manual_seed(seed) if seed else None
        ).images[0]
        
        # Post-process for quality
        result = self._enhance_composition(result)
        
        return result
    
    def _enhance_composition(self, image):
        """Apply composition enhancements"""
        # Add subtle vignette
        w, h = image.size
        vignette = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vignette)
        
        # Radial gradient vignette
        for i in range(min(w, h) // 4):
            alpha = int(80 * (i / (min(w, h) // 4)))
            draw.rectangle([i, i, w-i, h-i], outline=(0, 0, 0, alpha))
        
        vignette = vignette.filter(ImageFilter.GaussianBlur(50))
        
        # Composite
        result = Image.alpha_composite(image.convert('RGBA'), vignette)
        
        # Slight contrast boost
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.15)
        
        return result.convert('RGB')
