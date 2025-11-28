"""
CLIP Score Evaluator for Poster Generation
Author: LLC (Liu Lichao)
Purpose: Evaluate the semantic similarity between text prompts and generated poster images
"""

import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from typing import Union, Dict, List, Tuple
import os


class CLIPEvaluatorLLC:
    """
    CLIP-based evaluator for measuring text-image semantic similarity.
    
    This module compares Original Prompts and Enhanced Prompts against generated
    poster images to evaluate the effectiveness of prompt enhancement.
    
    Features:
    - Automatic device detection (CUDA > MPS > CPU)
    - Support for both file paths and PIL Image objects
    - Batch evaluation support
    - Detailed comparison reports
    """
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize the CLIP evaluator.
        
        Args:
            model_name: Hugging Face model identifier for CLIP model
                       Default: "openai/clip-vit-base-patch32" (150MB, fast)
                       Alternative: "openai/clip-vit-large-patch14" (larger, more accurate)
        """
        print("Initializing CLIP Evaluator LLC...")
        
        # Detect and set device
        self.device = self._get_device()
        print(f"Using device: {self.device}")
        
        # Load CLIP model and processor
        print(f"Loading CLIP model: {model_name}")
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
        # Move model to device
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        print("✓ CLIP Evaluator initialized successfully!\n")
    
    def _get_device(self) -> str:
        """
        Automatically detect the best available device.
        
        Priority: CUDA (NVIDIA GPU) > MPS (Apple Silicon) > CPU
        
        Returns:
            Device string: "cuda", "mps", or "cpu"
        """
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def _load_image(self, image: Union[str, Image.Image]) -> Image.Image:
        """
        Load image from file path or use PIL Image directly.
        
        Args:
            image: File path (str) or PIL Image object
            
        Returns:
            PIL Image object in RGB mode
        """
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image file not found: {image}")
            return Image.open(image).convert("RGB")
        elif isinstance(image, Image.Image):
            return image.convert("RGB")
        else:
            raise TypeError(f"Image must be a file path or PIL Image, got {type(image)}")
    
    def calculate_clip_score(
        self, 
        image: Union[str, Image.Image], 
        text_prompt: str
    ) -> float:
        """
        Calculate CLIP score between an image and a text prompt.
        
        The score represents semantic similarity, ranging from 0 to 100.
        Higher scores indicate better alignment between text and image.
        
        Args:
            image: Image file path or PIL Image object
            text_prompt: Text description to compare with the image
            
        Returns:
            CLIP score (float): Similarity score between 0 and 100
            
        Example:
            >>> evaluator = CLIPEvaluatorLLC()
            >>> score = evaluator.calculate_clip_score("poster.jpg", "hamburger and pizza")
            >>> print(f"CLIP Score: {score:.2f}")
        """
        # Load and preprocess image
        pil_image = self._load_image(image)
        
        # Prepare inputs
        inputs = self.processor(
            text=[text_prompt],
            images=pil_image,
            return_tensors="pt",
            padding=True
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Calculate similarity
        with torch.no_grad():
            outputs = self.model(**inputs)
            
            # Get similarity score (logits_per_image)
            # Shape: [1, 1], represents similarity between the image and text

            image_embeds = outputs.image_embeds
            text_embeds = outputs.text_embeds
            
            # Normalize embeddings
            image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)
            text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
            
            # Calculate cosine similarity
            similarity = (image_embeds @ text_embeds.T).squeeze()
            
            # Convert to score (scale to 0-100)
            clip_score = similarity.item() * 100
        
        return clip_score
    
    def compare_prompts(
        self,
        image: Union[str, Image.Image],
        original_prompt: str,
        enhanced_prompt: str
    ) -> Dict[str, float]:
        """
        Compare Original Prompt and Enhanced Prompt against the same image.
        
        This is the core function for evaluating prompt enhancement effectiveness.
        
        Args:
            image: Generated poster image (file path or PIL Image)
            original_prompt: Original keywords (e.g., "hamburger and pizza")
            enhanced_prompt: LLM-enhanced detailed description
            
        Returns:
            Dictionary containing:
                - original_score: CLIP score for original prompt
                - enhanced_score: CLIP score for enhanced prompt
                - improvement: Difference (enhanced - original)
                - improvement_percentage: Percentage improvement
                
        Example:
            >>> result = evaluator.compare_prompts(
            ...     "poster.jpg",
            ...     "hamburger and pizza",
            ...     "A vibrant digital watercolor scene of a cozy diner table..."
            ... )
            >>> print(f"Original: {result['original_score']:.2f}")
            >>> print(f"Enhanced: {result['enhanced_score']:.2f}")
            >>> print(f"Improvement: {result['improvement']:.2f}")
        """
        print("Calculating CLIP scores...")
        
        # Calculate scores
        original_score = self.calculate_clip_score(image, original_prompt)
        enhanced_score = self.calculate_clip_score(image, enhanced_prompt)
        
        # Calculate improvement
        improvement = enhanced_score - original_score
        improvement_percentage = (improvement / original_score * 100) if original_score > 0 else 0
        
        result = {
            'original_score': original_score,
            'enhanced_score': enhanced_score,
            'improvement': improvement,
            'improvement_percentage': improvement_percentage
        }
        
        # Print results
        print("\n" + "="*60)
        print("CLIP SCORE COMPARISON RESULTS")
        print("="*60)
        print(f"Original Prompt:  {original_prompt[:50]}...")
        print(f"  → CLIP Score: {original_score:.2f}")
        print(f"\nEnhanced Prompt:  {enhanced_prompt[:50]}...")
        print(f"  → CLIP Score: {enhanced_score:.2f}")
        print(f"\nImprovement: {improvement:+.2f} ({improvement_percentage:+.1f}%)")
        print("="*60 + "\n")
        
        return result
    
    def batch_evaluate(
        self,
        image_prompt_pairs: List[Tuple[Union[str, Image.Image], str, str]]
    ) -> List[Dict[str, float]]:
        """
        Evaluate multiple image-prompt pairs in batch.
        
        Args:
            image_prompt_pairs: List of tuples, each containing:
                (image, original_prompt, enhanced_prompt)
                
        Returns:
            List of comparison results (one dict per pair)
            
        Example:
            >>> pairs = [
            ...     ("poster1.jpg", "hamburger", "A juicy hamburger..."),
            ...     ("poster2.jpg", "pizza", "A delicious pizza...")
            ... ]
            >>> results = evaluator.batch_evaluate(pairs)
        """
        results = []
        total = len(image_prompt_pairs)
        
        print(f"\n{'='*60}")
        print(f"BATCH EVALUATION: {total} image-prompt pairs")
        print(f"{'='*60}\n")
        
        for idx, (image, original, enhanced) in enumerate(image_prompt_pairs, 1):
            print(f"[{idx}/{total}] Evaluating pair {idx}...")
            result = self.compare_prompts(image, original, enhanced)
            results.append(result)
        
        # Summary statistics
        avg_original = np.mean([r['original_score'] for r in results])
        avg_enhanced = np.mean([r['enhanced_score'] for r in results])
        avg_improvement = np.mean([r['improvement'] for r in results])
        
        print(f"\n{'='*60}")
        print("BATCH EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"Average Original Score:  {avg_original:.2f}")
        print(f"Average Enhanced Score:  {avg_enhanced:.2f}")
        print(f"Average Improvement:     {avg_improvement:+.2f}")
        print(f"{'='*60}\n")
        
        return results


# Convenience function for quick evaluation
def evaluate_poster(
    image_path: str,
    original_prompt: str,
    enhanced_prompt: str
) -> Dict[str, float]:
    """
    Quick evaluation function without needing to instantiate the class.
    
    Args:
        image_path: Path to the poster image
        original_prompt: Original keywords
        enhanced_prompt: Enhanced description
        
    Returns:
        Comparison results dictionary
        
    Example:
        >>> from src.clip_evaluator_LLC import evaluate_poster
        >>> result = evaluate_poster(
        ...     "output/poster.jpg",
        ...     "hamburger and pizza",
        ...     "A vibrant digital watercolor scene..."
        ... )
    """
    evaluator = CLIPEvaluatorLLC()
    return evaluator.compare_prompts(image_path, original_prompt, enhanced_prompt)


if __name__ == "__main__":
    # Demo usage
    print("\n" + "="*60)
    print("CLIP Evaluator LLC - Demo")
    print("="*60 + "\n")
    
    print("This is a demo of the CLIP Evaluator module.")
    print("To use it, you need:")
    print("  1. A poster image (generated by FLUX.1)")
    print("  2. The original prompt (keywords)")
    print("  3. The enhanced prompt (from ConceptExpander)")
    print("\nExample usage:")
    print("-" * 60)
    print("""
from src.clip_evaluator_LLC import CLIPEvaluatorLLC

# Initialize evaluator
evaluator = CLIPEvaluatorLLC()

# Evaluate a single poster
result = evaluator.compare_prompts(
    image="output/poster.jpg",
    original_prompt="hamburger and pizza",
    enhanced_prompt="A vibrant digital watercolor scene of a cozy diner table, "
                   "steam rising from a juicy hamburger beside a bubbling cheese pizza..."
)

# Access results
print(f"Original Score: {result['original_score']:.2f}")
print(f"Enhanced Score: {result['enhanced_score']:.2f}")
print(f"Improvement: {result['improvement']:.2f}")
    """)
    print("-" * 60)
