"""Concept Expander Agent - Enhances keywords with semantic meaning"""
import openai
import os
import json
from dotenv import load_dotenv
load_dotenv()
POE_API_KEY = os.getenv("POE_API_KEY")

class ConceptExpander:
    def __init__(self, model="GPT-5-Chat"):
        self.base_url = "https://api.poe.com/v1"
        assert POE_API_KEY is not None, "POE_API_KEY is not set in the .env file"
        self.client = openai.OpenAI(api_key=POE_API_KEY, base_url=self.base_url)
        self.model = model
        self.system_prompt = """
        You are an imaginative image designer who transforms a short list of 3-5 keywords into a vivid, cinematic image description.
        You are an expert visual concept designer.
        Your task is to generate a vivid, natural-language description of an image concept based on given keywords.
        **Rules:**
        The description must contain exactly one painting style (e.g., “oil painting,” “digital watercolor,” “Impressionist,” “surrealist,” “cyberpunk matte painting,” etc.).
        The total word count must not exceed 45 words.
        Focus on composition, atmosphere, lighting, and tone — use cinematic or painterly detail rather than lists.
        The description must be coherent, evocative, and suitable for visual art generation.
        Do not include artist names, camera specs, or formatting.
        Every output should read like a concise art direction sentence, not a paragraph.
        The output should be in json format.
        The json format should be like this:
        {
            "description": "The description of the image concept",
            "story title": "The title of the story",
            "captions": [
                "The first caption of the image",
                "The second caption of the image",
                "The third caption of the image",
                ...
            ]
        }
        **Example:**
        [INPUT] Keywords: Dancing, forest, spirits, warm

        [OUTPUT]
            {
                "description": "Ethereal crystal forest at sunrise, glowing mist wrapping luminous trees, soft pastel light radiating warmth, ghostly spirits dancing faintly through the haze.painted in delicate digital watercolor style.",
                "story title": "The Dance of the Spirits",
                "captions": [
                    "Comming soon",
                    "Warm story of love",
                    "A story of love and loss",
                ]
            }
        """
    
    def expand(self, keywords, temperature=1.2):
        """Expand keywords into creative brief"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": keywords}
                ],
                temperature=temperature
            )
            response = response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            return None
        return response