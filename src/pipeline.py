"""Main Key2Poster Pipeline"""
from src.concept_expander import ConceptExpander
from src.visual_generator import VisualGenerator
from src.no_text_generator import NoTextGenerator
from src.evaluator import PosterEvaluator
from src.refiner import QualityRefiner
from src.super_resolution import SuperResolution
from src.text_remover import TextRemover
from src.aggressive_text_remover import AggressiveTextRemover
from src.text_overlay import TextOverlay
from pathlib import Path
import time

class Key2PosterPipeline:
    def __init__(self, lora_path=None, use_lora=False, remove_text=True, aggressive_text_removal=False, 
                 no_text_mode=False, super_resolution=True, add_title=False, baseline_style=False):
        print("Initializing Key2Poster Pipeline...")
        print("Multi-Agent System (6 Agents):")
        print("  Agent 1: Concept Expander (Sentiment Analysis + Thematic Expansion)")
        print(f"  Agent 2: Visual Designer ({'Baseline Style' if baseline_style else 'LoRA Style' if use_lora else 'Standard'})")
        print(f"  Agent 3: Text Remover ({'Aggressive' if aggressive_text_removal else 'Standard'} Mode)")
        print(f"  Agent 4: Quality Enhancer (Denoise + {'Super-Res' if super_resolution else 'Standard'})")
        print(f"  Agent 5: Text Overlay ({'Enabled' if add_title else 'Disabled'})")
        print("  Agent 6: Quality Evaluator (Aesthetic + Resolution Validation)")
        self.expander = ConceptExpander()
        
        # Use baseline style (no LoRA) if requested
        if baseline_style:
            self.generator = VisualGenerator(lora_path=None, use_lora=False)
        elif no_text_mode:
            self.generator = NoTextGenerator(lora_path=lora_path, use_lora=use_lora)
        else:
            self.generator = VisualGenerator(lora_path=lora_path, use_lora=use_lora)
        
        if remove_text:
            self.text_remover = AggressiveTextRemover() if aggressive_text_removal else TextRemover()
        else:
            self.text_remover = None
        self.refiner = QualityRefiner()
        self.super_res = SuperResolution() if super_resolution else None
        self.text_overlay = TextOverlay() if add_title else None
        self.evaluator = PosterEvaluator()
        self.use_lora = use_lora
        self.remove_text = remove_text
        self.aggressive_text_removal = aggressive_text_removal
        self.no_text_mode = no_text_mode
        self.super_resolution = super_resolution
        self.add_title = add_title
        self.baseline_style = baseline_style
    
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
        
        # Step 2: Generate visual with poster-specific prompt
        print(f"\n[2/3] Generating poster {'with LoRA' if self.use_lora else 'with baseline SD'}...")
        if self.use_lora:
            # Simple prompt WITHOUT text-triggering words
            poster_prompt = f"movie poster art, {brief['themes']}, visual composition, no text"
        else:
            # Use expanded prompt for baseline
            poster_prompt = f"{brief['prompt']}, no text, no words, no letters"
        
        image = self.generator.generate(poster_prompt, seed=seed)
        
        # Step 3: Remove text (skip if disabled)
        if self.remove_text and self.text_remover:
            print(f"\n[3/5] Removing artificial text...")
            if self.aggressive_text_removal:
                image, text_found = self.text_remover.remove_text(image, iterations=3)
            else:
                image, text_found = self.text_remover.remove_text(image)
            if text_found:
                print("  ✓ Text detected and removed")
            else:
                print("  ✓ No text detected")
        else:
            print(f"\n[3/5] Text removal disabled - skipped")
        
        # Step 4: Enhance and refine quality (conditional)
        if self.super_resolution and self.super_res:
            print(f"\n[4/6] Enhancing with super-resolution...")
            image = self.super_res.enhance_details(image)
            image = self.refiner.enhance(image)
        else:
            print(f"\n[4/6] Basic enhancement (super-res disabled)...")
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
        
        # Step 5: Add title overlay (skip if disabled)
        if self.add_title and self.text_overlay:
            print(f"\n[5/6] Adding styled title...")
            image = self.text_overlay.add_title(image, keywords, style="cinematic")
        else:
            print(f"\n[5/6] Title overlay disabled - skipped")
        
        # Step 6: Save output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        
        # Step 7: Evaluate
        metrics = None
        if evaluate:
            print(f"\n[6/6] Evaluating quality...")
            metrics = self.evaluator.evaluate(output_path)
            print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
            print(f"  Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
            print(f"  Meets 720×1280 requirement: {metrics['instruction_following']}")
        
        elapsed = time.time() - start_time
        print(f"\n✓ Poster saved to {output_path} ({elapsed:.1f}s)")
        print(f"\n=== AGENT WORKFLOW SUMMARY ===")
        print(f"Agent 1 (Concept Expander): Keywords → Creative Brief")
        print(f"Agent 2 (Visual Designer): Brief → Raw Image")
        print(f"Agent 3 (Text Remover): Raw Image → Text-Free Image")
        print(f"Agent 4 (Quality Enhancer): Text-Free Image → Smooth Sharp Image")
        print(f"Agent 5 (Text Overlay): Image → Image + Styled Title")
        print(f"Agent 6 (Quality Evaluator): Final Image → Quality Metrics")
        
        return image, brief, metrics
    
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
