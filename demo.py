"""Quick demo of Key2Poster system"""
from src.pipeline import Key2PosterPipeline

def main():
    print("="*60)
    print("KEY2POSTER: Creative Poster Generator")
    print("="*60)
    
    # Initialize pipeline (baseline mode)
    pipeline = Key2PosterPipeline(use_lora=False)
    
    # Test keywords
    test_cases = [
        "space exploration adventure",
        "dark fantasy warrior",
        "romantic sunset beach"
    ]
    
    print(f"\nGenerating {len(test_cases)} posters...\n")
    
    for i, keywords in enumerate(test_cases):
        output_path = f"outputs/demo/poster_{i}.png"
        image, brief, metrics = pipeline.generate_poster(keywords, output_path)
        print("\n" + "-"*60 + "\n")
    
    print("="*60)
    print("Demo complete! Check outputs/demo/ for results")
    print("="*60)

if __name__ == "__main__":
    main()
