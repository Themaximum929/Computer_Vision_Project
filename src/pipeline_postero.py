"""Pipeline with PosterO API Integration"""
from src.pipeline import Key2PosterPipeline
from src.postero_generalized_api import PosterOGeneralizedAPI
from PIL import Image, ImageDraw, ImageFont
import os

class Key2PosterPipelineWithPosterO(Key2PosterPipeline):
    """Extended pipeline with PosterO layout generation"""
    
    def __init__(self, hf_token, **kwargs):
        super().__init__(**kwargs)
        self.postero_api = PosterOGeneralizedAPI(
            hf_token=hf_token,
            dataset_root="/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
        )
    
    def generate_poster(self, keywords, output_path=None, seed=None, category="movie-poster"):
        """Generate poster with PosterO layout"""
        import time
        from pathlib import Path
        
        if output_path is None:
            output_path = f"outputs/poster_{int(time.time())}.png"
        
        start_time = time.time()
        
        # Step 1: Expand concepts
        print(f"\n[1/4] Expanding concepts: '{keywords}'")
        brief = self.expander.expand(keywords, poster_type=self.poster_type, paint_style=self.style_preset)
        print(f"  Title: {brief['story title']}")
        
        # Step 2: Generate FLUX image (full size first)
        print(f"\n[2/4] Generating FLUX image...")
        poster_prompt = f"{brief['description']}, no text, no words"
        flux_image = self.generator.generate(poster_prompt, width=512, height=768, seed=seed)
        
        # Step 3: Generate PosterO layout
        print(f"\n[3/4] Generating layout with PosterO API...")
        layout = self.postero_api.generate_layout(
            category=category,
            num_elements=3,
            sample_size=5
        )
        print(f"  Generated {len(layout['labels'])} elements: {layout['labels']}")
        
        # Step 4: Compose poster with layout
        print(f"\n[4/4] Composing final poster...")
        canvas_size = tuple(layout['canvas_size']) if isinstance(layout['canvas_size'], list) else layout['canvas_size']
        # Ensure valid canvas size
        if canvas_size[0] <= 0 or canvas_size[1] <= 0:
            canvas_size = (512, 768)
            print(f"  ⚠ Invalid canvas size, using default {canvas_size}")
        poster = Image.new('RGB', canvas_size, 'white')
        
        # Find image region in layout
        image_regions = [(i, bbox) for i, (bbox, label) in enumerate(zip(layout['bboxes'], layout['labels'])) 
                        if label == 'U' or 'underlay' in label.lower()]
        
        if image_regions:
            _, img_bbox = image_regions[0]
            # Clamp bbox to canvas
            x1 = max(0, min(img_bbox[0], canvas_size[0]))
            y1 = max(0, min(img_bbox[1], canvas_size[1]))
            x2 = max(0, min(img_bbox[2], canvas_size[0]))
            y2 = max(0, min(img_bbox[3], canvas_size[1]))
            
            img_w = x2 - x1
            img_h = y2 - y1
            
            if img_w > 0 and img_h > 0:
                flux_resized = flux_image.resize((img_w, img_h))
                poster.paste(flux_resized, (x1, y1))
                print(f"  ✓ Placed image at [{x1}, {y1}, {x2}, {y2}]")
            else:
                print(f"  ⚠ Invalid image region, using full canvas")
                flux_resized = flux_image.resize(canvas_size)
                poster.paste(flux_resized, (0, 0))
        
        # Add text from LLM to text regions
        draw = ImageDraw.Draw(poster)
        title = brief['story title']
        captions = brief.get('captions', [])
        
        text_regions = [(i, bbox, label) for i, (bbox, label) in enumerate(zip(layout['bboxes'], layout['labels'])) 
                       if 'T-' in label or 'text' in label.lower()]
        
        for idx, (_, bbox, label) in enumerate(text_regions):
            text = title if idx == 0 else (captions[idx-1] if idx-1 < len(captions) else "")
            if not text:
                continue
            
            # Clamp bbox to canvas
            x1 = max(0, min(bbox[0], canvas_size[0]))
            y1 = max(0, min(bbox[1], canvas_size[1]))
            x2 = max(0, min(bbox[2], canvas_size[0]))
            y2 = max(0, min(bbox[3], canvas_size[1]))
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            try:
                font = ImageFont.truetype("fonts/Graduate-Regular.ttf", 32)
            except:
                font = ImageFont.load_default()
            
            # Center text in bbox
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            x = x1 + (x2 - x1 - text_w) // 2
            y = y1 + (y2 - y1 - text_h) // 2
            
            draw.text((x, y), text, font=font, fill='black')
            print(f"  ✓ Added text '{text[:20]}...' at [{x1}, {y1}, {x2}, {y2}]")
        
        # Save - convert to RGB to avoid PIL issues
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        poster = poster.convert('RGB')
        poster.save(output_path, 'PNG')
        
        elapsed = time.time() - start_time
        print(f"\n✅ Poster saved to {output_path} ({elapsed:.1f}s)")
        
        brief['layout'] = layout
        brief['flux_image'] = flux_image
        
        return poster, brief, None
