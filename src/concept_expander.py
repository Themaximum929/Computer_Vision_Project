"""Concept Expander Agent - Enhances keywords with semantic meaning"""
import openai
import os
import json
from dotenv import load_dotenv
load_dotenv()
POE_API_KEY = os.getenv("POE_API_KEY")

class ConceptExpander:
    def __init__(self, model="GPT-4o-mini"):
        self.base_url = "https://api.poe.com/v1"
        assert POE_API_KEY is not None, "POE_API_KEY is not set in the .env file"
        self.client = openai.OpenAI(api_key=POE_API_KEY, base_url=self.base_url)
        self.model = model
        self.valid_poster_types = ["movie", "book", "event", "product", "music", "game", "theater", "conference", "festival"]
        self.poster_type_guidance = {
            "movie": "cinematic, dramatic, film-like composition with strong visual storytelling",
            "book": "literary, evocative, cover art style with symbolic or narrative elements",
            "event": "dynamic, engaging, promotional style with clear focal points",
            "product": "clean, professional, commercial style emphasizing the product",
            "music": "atmospheric, mood-driven, album art style with artistic expression",
            "game": "action-oriented, immersive, game art style with dynamic elements",
            "theater": "theatrical, dramatic, stage-inspired composition with bold visuals",
            "conference": "professional, modern, corporate style with clear hierarchy",
            "festival": "vibrant, energetic, celebratory style with festive atmosphere"
        }
    
    def expand(self, prompt, poster_type="movie", paint_style="digital watercolor", img_size=(720, 1072), temperature=1.2):
        """Expand keywords into creative brief
        
        Args:
            prompt: The keywords or prompt to expand
            poster_type: Type of poster (movie, book, event, product, music, game, theater, conference, festival)
            paint_style: Painting style to append to description
            img_size: Image dimensions as (width, height) tuple
            temperature: Temperature for LLM generation
        """
        # Validate poster type
        poster_type = poster_type.lower()
        assert poster_type in self.valid_poster_types, f"Invalid poster type. Must be one of: {self.valid_poster_types}"
        
        width, height = img_size
        
        poster_type_description = self.poster_type_guidance.get(
            poster_type, 
            "visually compelling, well-composed poster style appropriate for the content"
        )
        
        system_prompt = f"""
        You are an imaginative image designer who transforms a short list of 3-5 keywords into a vivid, {poster_type} poster image description.
        You are an expert visual concept designer specializing in {poster_type} poster design.
        Your task is to generate a vivid, natural-language description of an image concept based on given keywords, tailored for a {poster_type} poster.
        
        **Poster Type:** {poster_type}
        **Style Guidance:** The description should reflect {poster_type_description}.
        **Painting Style:** {paint_style}
        
        **Image Specifications:**
        - Image dimensions: {width} x {height} pixels (width x height)
        - Aspect ratio: approximately {width/height:.2f}:1 (portrait orientation)
        
        **Rules:**
        The total word count must not exceed 45 words.
        Focus on composition, atmosphere, lighting, and tone — use {poster_type}-appropriate visual detail rather than lists.
        The description must be coherent, evocative, and suitable for visual art generation.
        Do not include artist names, camera specs, or formatting.
        Every output should read like a concise art direction sentence, not a paragraph.
        Adapt the visual style and tone to match {poster_type} poster conventions while maintaining creativity.
        
        **CRITICAL: Painting Style Requirement:**
        You MUST append the painting style "{paint_style}" at the END of the description. The painting style should be naturally integrated as the final element of the description, such as "..., rendered in {paint_style} style" or "..., {paint_style} style" or similar phrasing that flows naturally.
        
        **CRITICAL: Spatial Positioning Requirements:**
        You MUST explicitly describe the spatial position and layout of visual elements in the image. Use clear positional language such as:
        - "in the upper left/right corner", "at the top center", "in the foreground/background"
        - "centered", "positioned on the left/right side", "occupying the lower third"
        - "in the middle ground", "at the horizon line", "along the bottom edge"
        - Specify relative positions: "above", "below", "to the left/right of", "behind", "in front of"
        - Use directional terms: "top", "bottom", "center", "left", "right", "upper", "lower"
        The description should allow someone to understand WHERE each major visual element is located within the {width}x{height} frame.
        
        The output should be in json format.
        The json format should be like this:
        {{
            "description": "The description of the image concept, all should be visualizable elements with explicit spatial positioning, styled appropriately for a {poster_type} poster, ending with the painting style '{paint_style}'",
            "story title": "The title of the story",
            "captions": [
                "The first caption of the image",
                "The second caption of the image",
                ...
            ]
        }}
        **Example:**
        [INPUT] Keywords: Dancing, forest, spirits, warm
        [Painting Style: digital watercolor]

        [OUTPUT]
            {{
                "description": "In the upper third, ethereal crystal forest at sunrise with glowing mist wrapping luminous trees. Soft pastel light radiating warmth from the center. Ghostly spirits dancing faintly through the haze in the middle ground, positioned slightly to the right, rendered in digital watercolor style.",
                "story title": "The Dance of the Spirits",
                "captions": [
                    "Comming soon",
                    "Warm story of love",
                    "A story of love and loss",
                ]
            }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            response = response.choices[0].message.content
            response = json.loads(response)
        except Exception as e:
            print(f"Error: {e}")
            return None
        return response