"""Unified Pipeline - Best of All Three Projects"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from pathlib import Path
import time

class UnifiedPosterPipeline:
    """
    Combines best practices from:
    - PosterCraft: Clean 5-step flow
    - poster-generator-ai: Template system
    - digitalmovieposter: Text styling
    - Key2Poster: Genre-specific LoRA
    """
    
    def __init__(self, use_lora=True, genre_detection=True):
        self.use_lora = use_lora
        self.genre_detection = genre_detection
        self._load_components()
    
    def _load_components(self):
        """Load all pipeline components"""
        from src.concept_expander import ConceptExpander
        from src.genre_classifier import GenreClassifier
        from src.visual_generator import VisualGenerator
        from src.color_palette_extractor import ColorPaletteExtractor
        from src.composition_engine import CompositionEngine
        from src.template_manager import TemplateManager
        
        self.expander = ConceptExpander()
        self.classifier = GenreClassifier() if self.genre_detection else None
        self.generator = None  # Loaded per-genre
        self.color_extractor = ColorPaletteExtractor()
        self.composition = CompositionEngine()
        self.templates = TemplateManager()
    
    def generate(self, keywords, template="minimal", add_effects=True, seed=None):
        """
        Complete unified flow:
        1. Concept Analysis (sentiment + genre)
        2. Image Generation (with genre-specific LoRA)
        3. Color Extraction (palette analysis)
        4. Background Processing (vignette + enhancement)
        5. Text Composition (smart placement + styling)
        """
        start = time.time()
        print(f"\n{'='*60}")
        print(f"🎬 UNIFIED POSTER PIPELINE")
        print(f"{'='*60}")
        print(f"Keywords: {keywords}")
        
        # STEP 1: Concept Analysis
        print(f"\n[1/5] 🧠 Analyzing Concept...")
        brief = self.expander.expand(keywords)
        genre = self.classifier.classify(keywords) if self.classifier else "general"
        
        print(f"  • Sentiment: {brief['sentiment']} ({brief['confidence']:.2f})")
        print(f"  • Mood: {brief['mood']}")
        print(f"  • Genre: {genre}")
        
        # STEP 2: Image Generation
        print(f"\n[2/5] 🎨 Generating Image...")
        image = self._generate_with_lora(brief, genre, seed)
        print(f"  • Generated: {image.size}")
        
        # STEP 3: Color Analysis
        print(f"\n[3/5] 🎨 Analyzing Colors...")
        palette = self.color_extractor.extract_palette(image, n_colors=5)
        mood = self.color_extractor.analyze_mood_from_colors()
        accent = self.color_extractor.get_accent_color()
        
        print(f"  • Palette: {palette[:3]}")
        print(f"  • Mood: {mood}")
        print(f"  • Accent: {accent}")
        
        # STEP 4: Background Processing
        print(f"\n[4/5] ✨ Processing Background...")
        if add_effects:
            image = self.composition.add_vignette(image, strength=0.3)
            image = self._enhance_quality(image)
            print(f"  • Vignette applied")
            print(f"  • Quality enhanced")
        
        # STEP 5: Text Composition
        print(f"\n[5/5] 📝 Composing Text...")
        safe_zones = self.composition.detect_safe_zones(image)
        best_zone = safe_zones[0] if safe_zones else None
        
        image = self.templates.apply_template(image, template, keywords)
        image = self._add_smart_text(image, keywords, genre, accent, best_zone)
        
        print(f"  • Template: {template}")
        print(f"  • Text zone: {best_zone['position'] if best_zone else 'default'}")
        
        elapsed = time.time() - start
        print(f"\n✅ Complete in {elapsed:.1f}s")
        
        return {
            "image": image,
            "brief": brief,
            "genre": genre,
            "palette": palette,
            "mood": mood,
            "time": elapsed
        }
    
    def _generate_with_lora(self, brief, genre, seed):
        """Generate image with genre-specific LoRA"""
        from src.visual_generator import VisualGenerator
        import os
        
        if self.use_lora:
            lora_path = f"models/lora_{genre}"
            if os.path.exists(lora_path):
                self.generator = VisualGenerator(lora_path=lora_path, use_lora=True)
            else:
                self.generator = VisualGenerator(lora_path=None, use_lora=False)
        else:
            self.generator = VisualGenerator(lora_path=None, use_lora=False)
        
        prompt = f"movie poster art, {brief['themes']}, cinematic composition, no text"
        return self.generator.generate(prompt, seed=seed)
    
    def _enhance_quality(self, image):
        """Enhance image quality"""
        # Sharpen
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        # Contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)
        
        # Brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def _add_smart_text(self, image, text, genre, accent_color, safe_zone):
        """Add text with PosterCraft-style aesthetic design"""
        from src.aesthetic_text_overlay import AestheticTextOverlay
        
        overlay = AestheticTextOverlay()
        
        # Use full poster text with tagline
        taglines = {
            "action": "Prepare for action",
            "horror": "Fear the unknown",
            "scifi": "The future awaits",
            "romance": "A love story",
            "comedy": "Laugh out loud",
            "fantasy": "Enter the realm",
        }
        
        tagline = taglines.get(genre, "An epic adventure")
        
        return overlay.add_poster_text(
            image=image,
            title=text,
            genre=genre,
            tagline=tagline,
            credits=None
        )
    
    def save(self, result, output_path):
        """Save result with metadata"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result["image"].save(output_path, quality=95)
        
        # Save metadata
        meta_path = Path(output_path).with_suffix('.json')
        import json
        metadata = {k: v for k, v in result.items() if k != "image"}
        metadata["palette"] = [str(c) for c in metadata["palette"]]
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n💾 Saved:")
        print(f"  • Image: {output_path}")
        print(f"  • Metadata: {meta_path}")
