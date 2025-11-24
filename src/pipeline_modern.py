"""Modern Key2Poster Pipeline with Diffusion-Based Text Rendering"""
from src.concept_expander import ConceptExpander
from src.visual_generator import VisualGenerator
from src.visual_generator_flux import VisualGeneratorFlux
from src.evaluator import PosterEvaluator
from src.refiner import QualityRefiner
from src.super_resolution import SuperResolution
from src.aggressive_text_remover import AggressiveTextRemover
from src.diffusion_text_overlay import DiffusionTextOverlay, HybridTextOverlay
from src.genre_classifier import GenreClassifier
from PIL import Image, ImageEnhance
from pathlib import Path
import time
import os

class ModernKey2PosterPipeline:
    """Pipeline with modern diffusion-based text rendering"""
    
    def __init__(self, use_flux=True, flux_model="black-forest-labs/FLUX.1-schnell",
                 text_method='diffusion', genre_lora=False, super_resolution=True):
        print("Initializing Modern Key2Poster Pipeline...")
        print("🎨 Modern Text Rendering: ENABLED")
        print(f"  Text Method: {text_method.upper()}")
        print(f"  Model: {flux_model}")
        
        self.expander = ConceptExpander()
        self.genre_classifier = GenreClassifier() if genre_lora else None
        self.genre_lora = genre_lora
        self.use_flux = use_flux
        self.text_method = text_method
        
        # Visual generator
        if use_flux:
            self.generator = VisualGeneratorFlux(model_id=flux_model)
        else:
            self.generator = VisualGenerator(lora_path=None, use_lora=False)
        
        # Modern text overlay
        if text_method == 'diffusion':
            print("  Loading FLUX text renderer...")
            self.text_overlay = DiffusionTextOverlay(model_id=flux_model)
        elif text_method == 'hybrid':
            print("  Loading hybrid text renderer...")
            self.text_overlay = HybridTextOverlay()
        else:  # fallback
            from src.enhanced_text_overlay import EnhancedTextOverlay
            self.text_overlay = EnhancedTextOverlay()
        
        self.text_remover = AggressiveTextRemover()
        self.refiner = QualityRefiner()
        self.super_res = SuperResolution() if super_resolution else None
        self.evaluator = PosterEvaluator()
    
    def generate_poster(self, keywords, output_path="outputs/poster.png", seed=None):
        """Generate poster with modern text rendering"""
        start_time = time.time()
        
        # Validate input
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            raise ValueError(f"Input must contain 2-5 keywords. Got {len(keyword_list)} keywords.")
        
        # Step 1: Expand concepts
        print(f"\n[1/5] Expanding concepts: '{keywords}'")
        brief = self.expander.expand(keywords)
        print(f"  Sentiment: {brief['sentiment']} ({brief['confidence']:.2f})")
        print(f"  Mood: {brief['mood']}")
        
        # Step 2: Classify genre
        genre = 'action'
        if self.genre_lora and self.genre_classifier:
            genre = self.genre_classifier.classify(keywords)
            print(f"\n[2/5] Detected genre: {genre}")
        
        # Step 3: Generate base poster (without text)
        print(f"\n[3/5] Generating base poster...")
        poster_prompt = f"movie poster art, {brief['themes']}, visual composition, no text, no words"
        image = self.generator.generate(poster_prompt, seed=seed)
        
        # Remove any generated text
        print(f"\n[4/5] Cleaning image...")
        image, _ = self.text_remover.remove_text(image, iterations=2)
        
        # Enhance quality
        if self.super_res:
            image = self.super_res.enhance_details(image)
        image = self.refiner.enhance(image)
        
        # Step 5: Add text using modern method
        print(f"\n[5/5] Adding text with {self.text_method} method...")
        
        if self.text_method == 'diffusion':
            # Generate text directly with FLUX
            image = self.text_overlay.add_text_via_generation(image, keywords, genre, seed)
            print(f"  ✓ Text generated with FLUX diffusion")
        elif self.text_method == 'hybrid':
            # Smart hybrid approach
            image = self.text_overlay.add_text(image, keywords, genre, method='auto')
            print(f"  ✓ Text added with hybrid method")
        else:
            # Fallback to PIL
            image = self.text_overlay.add_poster_text(image, keywords, genre)
            print(f"  ✓ Text added with PIL")
        
        # Save
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        
        # Evaluate
        metrics = self.evaluator.evaluate(output_path)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Poster saved: {output_path} ({elapsed:.1f}s)")
        print(f"   Aesthetic: {metrics['aesthetic']['overall']:.3f}")
        print(f"   Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
        
        return image, brief, metrics


if __name__ == "__main__":
    # Test modern pipeline
    pipeline = ModernKey2PosterPipeline(text_method='diffusion')
    pipeline.generate_poster("cyberpunk neon city", seed=42)
