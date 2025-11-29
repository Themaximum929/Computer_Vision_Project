"""Smart Template Selection - Level 2 Enhancement"""
import random
import glob
import json

class SmartTemplateSelector:
    """Select templates based on content analysis"""
    
    GENRE_PREFERENCES = {
        'movie': [1, 3, 5, 7],      # Cinematic layouts
        'music': [2, 4, 6],          # Bold designs
        'event': [1, 2, 8],          # Promotional
        'sports': [3, 5, 7],         # Dynamic
    }
    
    def select(self, keywords, genre='movie'):
        """Select best template for keywords"""
        templates = glob.glob("templates/template*_layers.json")
        
        if not templates:
            return None
        
        # Filter by genre preference
        preferred = self.GENRE_PREFERENCES.get(genre, [1, 2, 3])
        filtered = [t for t in templates if any(f"template{n}_" in t for n in preferred)]
        
        if not filtered:
            filtered = templates
        
        # Random selection from filtered
        selected = random.choice(filtered)
        
        with open(selected) as f:
            template = json.load(f)
        
        # Randomize text alignment
        if 'fonts' not in template:
            template['fonts'] = {}
        
        align = random.choice(['left', 'center', 'right'])
        template['fonts']['title'] = template['fonts'].get('title', {})
        template['fonts']['title']['align'] = align
        
        return template
