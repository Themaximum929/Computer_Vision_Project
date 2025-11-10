"""Main Key2Poster Pipeline"""
from src.concept_expander import ConceptExpander
from src.visual_generator import VisualGenerator
from src.evaluator import PosterEvaluator
from pathlib import Path
import time

class Key2PosterPipeline:
    def __init__(self, lora_path=None, use_lora=False):
        print("Initializing Key2Poster Pipeline...")
        self.expander = ConceptExpander()
        self.generator = VisualGenerator(lora_path=lora_path, use_lora=use_lora)
        self.evaluator = PosterEvaluator()
        self.use_lora = use_lora
    
    def generate_poster(self, keywords, output_path="outputs/poster.png", seed=None, evaluate=True):
        """End-to-end poster generation"""
        start_time = time.time()
        
        # Step 1: Expand concepts
        print(f"\n[1/3] Expanding concepts for: '{keywords}'")
        brief = self.expander.expand(keywords)
        print(f"  Sentiment: {brief['sentiment']} (confidence: {brief['confidence']:.2f})")
        print(f"  Mood: {brief['mood']}")
        print(f"  Enhanced prompt: {brief['prompt']}")
        
        # Step 2: Generate visual
        print(f"\n[2/3] Generating poster {'with LoRA' if self.use_lora else 'with baseline SD'}...")
        image = self.generator.generate(brief['prompt'], seed=seed)
        
        # Step 3: Save output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        
        # Step 4: Evaluate
        metrics = None
        if evaluate:
            print(f"\n[3/3] Evaluating quality...")
            metrics = self.evaluator.evaluate(output_path)
            print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
            print(f"  Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
        
        elapsed = time.time() - start_time
        print(f"\n✓ Poster saved to {output_path} ({elapsed:.1f}s)")
        
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
