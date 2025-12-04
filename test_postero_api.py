"""Test PosterO with HuggingFace API (no local GPU needed)"""
from src.postero_generalized_api import PosterOGeneralizedAPI
import os

# Get HuggingFace token from environment or set it here
HF_TOKEN = os.getenv("HF_TOKEN", "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")

def test_api():
    """Test API-based generation"""
    print("Testing PosterO with HuggingFace API...")
    print(f"Token: {HF_TOKEN[:10]}..." if len(HF_TOKEN) > 10 else "⚠️  Set HF_TOKEN!")
    
    generator = PosterOGeneralizedAPI(
        hf_token=HF_TOKEN,
        dataset_root="/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
    )
    
    print("\nGenerating layout for movie-poster...")
    layout = generator.generate_layout(
        category="movie-poster",
        num_elements=3,
        sample_size=5
    )
    
    print(f"\n✓ Generated layout:")
    print(f"  Canvas: {layout['canvas_size']}")
    print(f"  Elements: {len(layout['bboxes'])}")
    print(f"  Labels: {layout['labels']}")
    print(f"  SVG preview:\n{layout['svg'][:300]}...")

if __name__ == "__main__":
    if HF_TOKEN == "hf_YOUR_TOKEN_HERE":
        print("⚠️  Set your HuggingFace token!")
        print("\nGet token from: https://huggingface.co/settings/tokens")
        print("\nThen either:")
        print("  export HF_TOKEN='hf_...'")
        print("  or edit this file and set HF_TOKEN")
    else:
        test_api()
