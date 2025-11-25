"""Concept Expander Agent - Enhances keywords with semantic meaning"""
from transformers import pipeline

class ConceptExpander:
    def __init__(self):
        try:
            self.sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        except:
            self.sentiment = None
    
    def expand(self, keywords):
        """Expand keywords into creative brief"""
        # Sentiment analysis
        if self.sentiment:
            sentiment = self.sentiment(keywords)[0]
            mood = "dark, moody, dramatic" if sentiment['label'] == 'NEGATIVE' else "bright, vibrant, uplifting"
            confidence = sentiment['score']
        else:
            mood = "cinematic, atmospheric"
            confidence = 0.5
        
        # Thematic keywords expansion with genre mapping
        theme_map = {
            "space": "cosmic, stars, nebula, vast",
            "fantasy": "magical, mystical, epic",
            "warrior": "heroic, battle-worn, powerful",
            "romance": "emotional, intimate, tender",
            "horror": "eerie, suspenseful, haunting",
            "adventure": "dynamic, exciting, journey",
            "action": "intense, explosive, dramatic",
            "drama": "emotional, powerful, compelling",
            "comedy": "lighthearted, fun, colorful",
            "thriller": "suspenseful, tense, gripping",
            "sci-fi": "futuristic, technological, otherworldly",
            "anime": "stylized, vibrant, expressive"
        }
        
        expanded_themes = []
        keywords_lower = keywords.lower()
        for key, themes in theme_map.items():
            if key in keywords_lower:
                expanded_themes.append(themes)
        
        theme_str = ", ".join(expanded_themes) if expanded_themes else "dramatic"
        
        brief = {
            "keywords": keywords,
            "sentiment": sentiment['label'] if self.sentiment else "NEUTRAL",
            "confidence": confidence,
            "mood": mood,
            "themes": theme_str,
            "prompt": f"{keywords}, {mood}, {theme_str}, movie poster style, professional, high quality, detailed"
        }
        return brief
