"""Test Title Generator"""
from src.title_generator import TitleGenerator

def test_title_generation():
    """Test simple title generation"""
    print("\n" + "="*60)
    print("TESTING TITLE GENERATOR")
    print("="*60)
    
    gen = TitleGenerator()
    
    test_cases = [
        ("cyberpunk neon city", "scifi", "Cyberpunk"),
        ("dark horror mansion", "horror", "Dark"),
        ("space exploration adventure", "scifi", "Space"),
        ("romantic sunset beach", "romance", "Romantic"),
        ("epic fantasy warrior", "fantasy", "Epic"),
        ("action packed thriller", "action", "Action"),
    ]
    
    print("\n[Test] Generating simple titles from keywords\n")
    
    for keywords, genre, expected_type in test_cases:
        title = gen.generate(keywords, genre)
        print(f"Keywords: '{keywords}'")
        print(f"Genre: {genre}")
        print(f"Generated Title: '{title}'")
        print(f"Length: {len(title)} chars")
        
        # Validate
        assert len(title) <= 10, f"Title too long: {title}"
        assert title.isalpha(), f"Title should be single word: {title}"
        
        print("✓ Valid\n")
    
    print("="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    
    print("\nTitle Generation Rules:")
    print("1. Extract first meaningful word (≤7 chars)")
    print("2. Skip articles (the, a, an)")
    print("3. Capitalize first letter")
    print("4. Fallback to genre-specific titles")
    
    print("\nGenre-Specific Fallbacks:")
    for genre in ["action", "horror", "scifi", "romance", "comedy", "fantasy"]:
        title = gen.generate("", genre)
        print(f"  {genre.capitalize()}: {title}")

if __name__ == "__main__":
    try:
        test_title_generation()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
