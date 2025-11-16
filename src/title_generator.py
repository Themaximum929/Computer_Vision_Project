"""AI Title Generator using mini LLM"""
import random

class TitleGenerator:
    """Generate single-word movie titles using LLM or fallback"""
    
    def __init__(self, use_llm=True):
        self.use_llm = use_llm
        self.llm = None
        
        if use_llm:
            try:
                # Try to use transformers with small model
                from transformers import pipeline
                self.llm = pipeline("text-generation", model="distilgpt2", max_length=10)
                print("✓ Using DistilGPT2 for title generation")
            except:
                print("⚠ LLM not available, using fallback")
                self.use_llm = False
        
        # Fallback titles
        self.fallback_titles = {
            'action': ['VENGEANCE', 'FURY', 'STRIKE', 'IMPACT', 'ASSAULT'],
            'horror': ['NIGHTMARE', 'TERROR', 'DARKNESS', 'HAUNTED', 'EVIL'],
            'scifi': ['NEXUS', 'QUANTUM', 'VOID', 'GENESIS', 'HORIZON'],
            'romance': ['FOREVER', 'DESTINY', 'PASSION', 'BELOVED', 'HEARTS'],
            'comedy': ['CHAOS', 'MADNESS', 'MAYHEM', 'TROUBLE', 'WILD'],
            'fantasy': ['LEGEND', 'REALM', 'MAGIC', 'QUEST', 'KINGDOM'],
            'thriller': ['HUNTED', 'TRAPPED', 'ESCAPE', 'DANGER', 'PURSUIT'],
            'drama': ['TRUTH', 'LEGACY', 'JOURNEY', 'HOPE', 'REDEMPTION']
        }
    
    def generate(self, keywords, genre='action'):
        """Generate single-word title"""
        if self.use_llm and self.llm:
            return self._generate_with_llm(keywords, genre)
        else:
            return self._generate_fallback(genre)
    
    def _generate_with_llm(self, keywords, genre):
        """Generate using LLM"""
        try:
            # Better prompt with explicit constraints
            prompt = f"Generate exactly ONE powerful {genre} movie title word (like VENGEANCE, FURY, NEXUS). Word:"
            result = self.llm(prompt, max_new_tokens=3, num_return_sequences=1, do_sample=True, temperature=0.9)
            
            # Extract first word from generated text
            generated = result[0]['generated_text'].replace(prompt, '').strip()
            words = generated.split()
            
            # Expanded meaningless words list
            meaningless = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'but', 
                          'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been',
                          'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                          'it', 'its', 'he', 'she', 'they', 'we', 'you', 'i', 'me', 'my', 'your'}
            
            for word in words:
                title = word.upper().strip('.,!?;:"\'')
                # Validate: 4-12 chars, alphabetic, not meaningless, starts with capital letter concept
                if 4 <= len(title) <= 12 and title.isalpha() and title.lower() not in meaningless:
                    return title
        except:
            pass
        
        # Fallback if LLM fails
        return self._generate_fallback(genre)
    
    def _generate_fallback(self, genre):
        """Fallback to predefined titles"""
        titles = self.fallback_titles.get(genre, self.fallback_titles['action'])
        return random.choice(titles)
