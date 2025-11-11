"""Main Key2Poster Pipeline"""
from src.concept_expander import ConceptExpander
from src.visual_generator import VisualGenerator
from src.evaluator import PosterEvaluator
from src.refiner import QualityRefiner
from src.text_remover import TextRemover
from src.aggressive_text_remover import AggressiveTextRemover
from pathlib import Path
import time

class Key2PosterPipeline:
    def __init__(self, lora_path=None, use_lora=False, remove_text=True, aggressive_text_removal=False):
        print("Initializing Key2Poster Pipeline...")
        print("Multi-Agent System (5 Agents):")
        print("  Agent 1: Concept Expander (Sentiment Analysis + Thematic Expansion)")
        print("  Agent 2: Visual Designer (Stable Diffusion + LoRA Fine-tuning)")
        print(f"  Agent 3: Text Remover ({'Aggressive' if aggressive_text_removal else 'Standard'} Mode)")
        print("  Agent 4: Quality Refiner (Post-processing Enhancement)")
        print("  Agent 5: Quality Evaluator (Aesthetic + Resolution Validation)")
        self.expander = ConceptExpander()
        self.generator = VisualGenerator(lora_path=lora_path, use_lora=use_lora)
        if remove_text:
            self.text_remover = AggressiveTextRemover() if aggressive_text_removal else TextRemover()
        else:
            self.text_remover = None
        self.refiner = QualityRefiner()
        self.evaluator = PosterEvaluator()
        self.use_lora = use_lora
        self.remove_text = remove_text
        self.aggressive_text_removal = aggressive_text_removal
    
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
            # Simple prompt - let LoRA handle the style
            poster_prompt = f"movie poster, {brief['keywords']}, {brief['themes']}"
        else:
            # Use expanded prompt for baseline
            poster_prompt = brief['prompt']
        
        image = self.generator.generate(poster_prompt, seed=seed)
        
        # Step 3: Remove text
        if self.remove_text:
            print(f"\n[3/5] Removing artificial text...")
            image, text_found = self.text_remover.remove_text(image)
            if text_found:
                print("  ✓ Text detected and removed")
            else:
                print("  ✓ No text detected")
        
        # Step 4: Refine quality
        print(f"\n[4/5] Refining image quality...")
        image = self.refiner.refine(image)
        
        # Step 4: Save output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        
        # Step 5: Evaluate
        metrics = None
        if evaluate:
            print(f"\n[5/5] Evaluating quality...")
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
        print(f"Agent 4 (Quality Refiner): Text-Free Image → Enhanced Image")
        print(f"Agent 5 (Quality Evaluator): Enhanced Image → Quality Metrics")
        
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
