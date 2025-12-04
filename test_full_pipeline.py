"""Test full pipeline: FLUX + PosterO + Text"""
from src.pipeline_postero import Key2PosterPipelineWithPosterO
import os

HF_TOKEN = os.getenv("HF_TOKEN", "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")

def test_full_pipeline():
    """Test complete pipeline with PosterO"""
    print("Testing Full Pipeline: FLUX + PosterO + LLM Text")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = Key2PosterPipelineWithPosterO(
        hf_token=HF_TOKEN,
        use_flux=True,
        poster_type="movie",
        style_preset="cinematic"
    )
    
    # Generate poster
    keywords = "cyberpunk neon city"
    poster, brief, metrics = pipeline.generate_poster(
        keywords=keywords,
        output_path="outputs/postero_full_test.png",
        category="movie-poster",
        seed=42
    )
    
    print("\n" + "=" * 60)
    print("✓ Pipeline Complete!")
    print(f"  Title: {brief['story title']}")
    print(f"  Layout: {len(brief['layout']['labels'])} elements")
    print(f"  Output: outputs/postero_full_test.png")

if __name__ == "__main__":
    test_full_pipeline()
