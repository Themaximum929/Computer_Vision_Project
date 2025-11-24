"""Main Key2Poster Pipeline"""
from src.concept_expander import ConceptExpander
from src.visual_generator import VisualGenerator
from src.visual_generator_flux import VisualGeneratorFlux
from src.evaluator import PosterEvaluator
from src.refiner import QualityRefiner
from src.super_resolution import SuperResolution
from src.text_remover import TextRemover
from src.aggressive_text_remover import AggressiveTextRemover
from src.enhanced_text_overlay import EnhancedTextOverlay
try:
    from src.diffusion_text_overlay import DiffusionTextOverlay
    MODERN_TEXT_AVAILABLE = True
except:
    MODERN_TEXT_AVAILABLE = False
from src.poster_composer import PosterComposer
from src.genre_classifier import GenreClassifier
from PIL import Image, ImageEnhance
from pathlib import Path
import time
import os

class Key2PosterPipeline:
    def __init__(self, lora_path=None, use_lora=False, remove_text=True, aggressive_text_removal=False, 
                 super_resolution=True, add_title=False, baseline_style=False, genre_lora=False, 
                 use_template=False, template_path=None, use_flux=False, flux_model="black-forest-labs/FLUX.1-schnell",
                 modern_text=False):
        print("Initializing Key2Poster Pipeline...")
        print("Multi-Agent System (7 Agents):")
        print("  Agent 1: Concept Expander (Sentiment Analysis + Thematic Expansion)")
        print(f"  Agent 2: Genre Classifier ({'Enabled' if genre_lora else 'Disabled'})")
        model_type = 'FLUX' if use_flux else ('Baseline' if baseline_style else 'Genre-LoRA' if genre_lora else 'LoRA' if use_lora else 'Standard')
        print(f"  Agent 3: Visual Designer ({model_type})")
        print(f"  Agent 4: Text Remover ({'Aggressive' if aggressive_text_removal else 'Standard'} Mode)")
        print(f"  Agent 5: Quality Enhancer (Denoise + {'Super-Res' if super_resolution else 'Standard'})")
        print(f"  Agent 6: Text Overlay ({'Enabled' if add_title else 'Disabled'})")
        print("  Agent 7: Quality Evaluator (Aesthetic + Resolution Validation)")
        self.expander = ConceptExpander()
        self.genre_classifier = GenreClassifier() if genre_lora else None
        
        # Store settings for genre-based LoRA loading
        self.genre_lora = genre_lora
        self.baseline_style = baseline_style
        self.use_lora = use_lora
        self.lora_path = lora_path
        self.use_flux = use_flux
        self.flux_model = flux_model
        
        # Generator will be created per-generation if genre_lora is enabled (but not for FLUX)
        if not genre_lora or use_flux:
            if use_flux:
                self.generator = VisualGeneratorFlux(model_id=flux_model)
            elif baseline_style:
                self.generator = VisualGenerator(lora_path=None, use_lora=False)
            else:
                self.generator = VisualGenerator(lora_path=lora_path, use_lora=use_lora)
        else:
            self.generator = None
        
        if remove_text:
            self.text_remover = AggressiveTextRemover() if aggressive_text_removal else TextRemover()
        else:
            self.text_remover = None
        self.refiner = QualityRefiner()
        self.super_res = SuperResolution() if super_resolution else None
        self.modern_text = False  # Disable for now - FLUX text generation unreliable
        if add_title:
            self.text_overlay = EnhancedTextOverlay()
        else:
            self.text_overlay = None
        self.poster_composer = PosterComposer() if use_template else None
        self.use_template = use_template
        self.template_path = template_path
        self.evaluator = PosterEvaluator()
        self.remove_text = remove_text
        self.aggressive_text_removal = aggressive_text_removal
        self.super_resolution = super_resolution
        self.add_title = add_title
    
    def generate_poster(self, keywords, output_path="outputs/poster.png", seed=None, evaluate=True):
        """End-to-end poster generation"""
        # Validate input: 2-5 keywords
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            raise ValueError(f"Input must contain 2-5 keywords. Got {len(keyword_list)} keywords.")
        
        start_time = time.time()
        
        # Step 1: Expand concepts
        print(f"\n[1/3] Expanding concepts for: '{keywords}'")
        brief = self.expander.expand(keywords)
        print(f"  Sentiment: {brief['sentiment']} (confidence: {brief['confidence']:.2f})")
        print(f"  Mood: {brief['mood']}")
        print(f"  Enhanced prompt: {brief['prompt']}")
        
        # Step 2: Classify genre and load appropriate LoRA
        if self.genre_lora and self.genre_classifier:
            genre = self.genre_classifier.classify(keywords)
            self._current_genre = genre  # Store for text styling
            print(f"\n[2/7] Detected genre: {genre}")
            
            # Load genre-specific LoRA (only if not using FLUX and generator not already loaded)
            if self.use_flux:
                print(f"  Using FLUX (LoRA not supported)")
                # Don't reload FLUX if already loaded
                if self.generator is None:
                    self.generator = VisualGeneratorFlux(model_id=self.flux_model)
                else:
                    print(f"  Reusing existing FLUX generator")
            else:
                genre_lora_path = f"models/lora_{genre}"
                if os.path.exists(genre_lora_path):
                    print(f"  Loading {genre} LoRA...")
                    self.generator = VisualGenerator(lora_path=genre_lora_path, use_lora=True)
                else:
                    print(f"  {genre} LoRA not found, using baseline")
                    self.generator = VisualGenerator(lora_path=None, use_lora=False)
        
        # Step 3: Generate visual
        print(f"\n[3/7] Generating poster...")
        if self.use_lora or self.genre_lora:
            poster_prompt = f"movie poster art, {brief['themes']}, visual composition, no text"
        else:
            poster_prompt = f"{brief['prompt']}, no text, no words, no letters"
        
        image = self.generator.generate(poster_prompt, seed=seed)
        
        # Step 4: Remove text (skip if disabled)
        if self.remove_text and self.text_remover:
            print(f"\n[4/7] Removing artificial text...")
            if self.aggressive_text_removal:
                image, text_found = self.text_remover.remove_text(image, iterations=3)
            else:
                image, text_found = self.text_remover.remove_text(image)
            if text_found:
                print("  [OK] Text detected and removed")
            else:
                print("  [OK] No text detected")
        else:
            print(f"\n[4/7] Text removal disabled - skipped")
        
        # Step 5: Enhance and refine quality (conditional)
        if self.super_resolution and self.super_res:
            print(f"\n[5/7] Enhancing with super-resolution...")
            image = self.super_res.enhance_details(image)
            image = self.refiner.enhance(image)
        else:
            print(f"\n[5/7] Basic enhancement (super-res disabled)...")
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
        
        # Step 5.5: Compose with template (if enabled)
        if self.use_template and self.poster_composer:
            print(f"\n[5.5/7] Composing with poster template...")
            if self.template_path:
                image = self.poster_composer.compose_poster(self.template_path, image)
            else:
                image = self.poster_composer.compose_with_simple_layout(image)
            print(f"  ✓ Poster composed with template layout")
        
        # Step 6: Add aesthetic text overlay (skip if disabled)
        if self.add_title and self.text_overlay and not self.use_template:
            print(f"\n[6/7] Adding aesthetic text overlay...")
            # Use genre for styling if available
            if hasattr(self, '_current_genre'):
                genre = self._current_genre
            else:
                genre = "cinematic"
            
            if self.modern_text:
                # Modern diffusion-based text - use PIL as fallback (FLUX text generation not reliable)
                print(f"  Using enhanced PIL text rendering...")
                from src.enhanced_text_overlay import EnhancedTextOverlay
                temp_overlay = EnhancedTextOverlay()
                taglines = {
                    "action": "Prepare for action",
                    "horror": "Fear the unknown",
                    "scifi": "The future awaits",
                    "romance": "A love story",
                    "comedy": "Laugh out loud",
                    "fantasy": "Enter the realm",
                    "thriller": "On the edge",
                    "drama": "A powerful story"
                }
                tagline = taglines.get(genre, "An epic adventure")
                image = temp_overlay.add_poster_text(image, keywords, genre, tagline, None)
                print(f"  ✓ Title: {keywords.upper()} (Enhanced PIL)")
            else:
                # Traditional PIL text
                taglines = {
                    "action": "Prepare for action",
                    "horror": "Fear the unknown",
                    "scifi": "The future awaits",
                    "romance": "A love story",
                    "comedy": "Laugh out loud",
                    "fantasy": "Enter the realm",
                    "thriller": "On the edge",
                    "drama": "A powerful story"
                }
                tagline = taglines.get(genre, "An epic adventure")
                
                image = self.text_overlay.add_poster_text(
                    image=image,
                    title=keywords,
                    genre=genre,
                    tagline=tagline,
                    credits=None
                )
                print(f"  ✓ Title: {keywords.upper()}")
                print(f"  ✓ Genre: {genre}")
                print(f"  ✓ Tagline: {tagline}")
        else:
            print(f"\n[6/7] Text overlay disabled - skipped")
        
        # Step 7: Save output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        
        # Step 8: Evaluate
        metrics = None
        if evaluate:
            print(f"\n[7/7] Evaluating quality...")
            metrics = self.evaluator.evaluate(output_path)
            print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
            print(f"  Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
        
        elapsed = time.time() - start_time
        print(f"\n✅ Poster saved to {output_path} ({elapsed:.1f}s)")
        
        return image, brief, metrics
    
    def _get_text_prompt(self, title, genre):
        """Generate FLUX prompt for text overlay"""
        styles = {
            'action': 'bold red metallic title text, strong typography',
            'horror': 'dark blood-red dripping title text, horror typography',
            'scifi': 'glowing cyan futuristic title text, neon effect',
            'romance': 'elegant pink script title text, soft',
            'comedy': 'playful yellow bouncy title text, energetic',
            'fantasy': 'golden magical title text, ornate',
            'thriller': 'sharp white angular title text, dramatic shadow',
            'drama': 'classic white serif title text, professional'
        }
        style = styles.get(genre, 'cinematic title text')
        return f"movie poster with {style} displaying '{title}', professional poster design"
    
    def batch_generate(self, keywords_list, output_dir="outputs/batch", seed=42):
        """Generate multiple posters"""
        results = []
        for i, keywords in enumerate(keywords_list):
            output_path = f"{output_dir}/poster_{i}.png"
            image, brief, metrics = self.generate_poster(keywords, output_path, seed=seed+i)
            results.append({"keywords": keywords, "brief": brief, "metrics": metrics, "path": output_path})
        return results

if __name__ == "__main__":
    # Test baseline
    pipeline = Key2PosterPipeline(use_lora=False)
    pipeline.generate_poster("space exploration adventure")
