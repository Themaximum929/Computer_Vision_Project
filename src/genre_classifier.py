"""Genre classification from keywords"""
import re

class GenreClassifier:
    def __init__(self):
        self.genre_keywords = {
            "action": ["action", "battle", "fight", "war", "combat", "explosion", "chase", "hero", "warrior"],
            "scifi": ["space", "sci-fi", "science fiction", "alien", "robot", "future", "cyberpunk", "tech", "galaxy", "star"],
            "fantasy": ["fantasy", "magic", "dragon", "wizard", "medieval", "kingdom", "quest", "mythical", "epic"],
            "horror": ["horror", "scary", "dark", "haunted", "ghost", "zombie", "monster", "terror", "nightmare"],
            "romance": ["romance", "love", "romantic", "couple", "heart", "passion", "wedding", "kiss"],
            "comedy": ["comedy", "funny", "humor", "laugh", "silly", "fun", "joke", "happy"],
            "drama": ["drama", "emotional", "serious", "intense", "powerful", "tragic", "life"],
            "thriller": ["thriller", "suspense", "mystery", "detective", "crime", "noir", "investigation"]
        }
    
    def classify(self, keywords):
        """Classify genre from keywords"""
        keywords_lower = keywords.lower()
        
        # Count matches for each genre
        scores = {}
        for genre, genre_words in self.genre_keywords.items():
            score = sum(1 for word in genre_words if word in keywords_lower)
            if score > 0:
                scores[genre] = score
        
        # Return genre with highest score, or "general" if no match
        if scores:
            return max(scores, key=scores.get)
        return "general"
