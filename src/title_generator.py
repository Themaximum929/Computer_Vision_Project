"""Generate Simple Movie Titles from Keywords"""

class TitleGenerator:
    """Generate concise 1-word movie titles from prompts"""
    
    def __init__(self):
        self.genre_patterns = {
            "action": ["strike", "fury", "impact", "blaze", "storm", "rage"],
            "horror": ["dread", "terror", "shadows", "haunted", "cursed", "nightmare"],
            "scifi": ["nexus", "quantum", "void", "genesis", "eclipse", "horizon"],
            "romance": ["beloved", "forever", "destiny", "passion", "hearts", "embrace"],
            "comedy": ["chaos", "madness", "mayhem", "laughs", "hijinks", "antics"],
            "fantasy": ["legend", "realm", "quest", "magic", "prophecy", "kingdom"],
            "thriller": ["hunted", "trapped", "vanished", "secrets", "lies", "betrayal"],
            "drama": ["truth", "legacy", "journey", "redemption", "sacrifice", "hope"]
        }
    
    def generate(self, keywords, genre="cinematic"):
        """Generate simple title from keywords (max 7 chars, 1 word)"""
        words = keywords.lower().split()
        
        # Try to extract key noun/adjective
        key_words = []
        for word in words:
            if len(word) <= 7 and word not in ["the", "a", "an", "of", "in", "on", "at"]:
                key_words.append(word)
        
        # Use first suitable word
        if key_words:
            return key_words[0].capitalize()
        
        # Fallback to genre-specific title
        import random
        if genre in self.genre_patterns:
            return random.choice(self.genre_patterns[genre]).capitalize()
        
        # Ultimate fallback
        return words[0].capitalize() if words else "Untitled"
