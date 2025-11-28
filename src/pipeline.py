"""Main Key2Poster Pipeline"""
from src.concept_expander import ConceptExpander
from src.visual_generator import VisualGenerator
from src.visual_generator_flux import VisualGeneratorFlux
from src.evaluator import PosterEvaluator
from src.refiner import QualityRefiner
from src.super_resolution import SuperResolution
from src.text_remover import TextRemover
from src.aggressive_text_remover import AggressiveTextRemover
from src.color_contrast import get_average_color, adjust_text_color
from src.text_layout import resolve_text_positions, calculate_text_bbox
try:
    from src.enhanced_flux_text import EnhancedFluxText, StyleEnhancedFlux
    ENHANCED_FLUX_AVAILABLE = True
except:
    ENHANCED_FLUX_AVAILABLE = False
from src.genre_classifier import GenreClassifier
from PIL import Image, ImageEnhance
from pathlib import Path
import time
import os

class Key2PosterPipeline:
    def __init__(self, lora_path=None, use_lora=False, remove_text=True, aggressive_text_removal=False, 
                 super_resolution=True, add_title=False, baseline_style=False, genre_lora=False, 
                 use_template=False, template_path=None, use_flux=False, flux_model="black-forest-labs/FLUX.1-schnell",
                 modern_text=False, enhanced_flux=False, style_preset='cinematic', poster_type='movie'):
        print("Initializing Key2Poster Pipeline...")
        print("Multi-Agent System (7 Agents):")
        print("  Agent 1: Concept Expander (Sentiment Analysis + Thematic Expansion)")
        print(f"  Agent 2: Genre Classifier ({'Enabled' if genre_lora else 'Disabled'})")
        model_type = 'FLUX' if use_flux else ('Baseline' if baseline_style else 'Genre-LoRA' if genre_lora else 'LoRA' if use_lora else 'Standard')
        print(f"  Agent 3: Visual Designer ({model_type})")
        print(f"  Agent 4: Text Remover ({'Aggressive' if aggressive_text_removal else 'Standard'} Mode)")
        print(f"  Agent 5: Quality Enhancer (Denoise + {'Super-Res' if super_resolution else 'Standard'})")
        print(f"  Agent 6: Text Overlay ({'Enabled' if add_title else 'Disabled'})")
        print("  Agent 7: Quality Evaluator (Aesthetic + Resolution Validation)")
        self.expander = ConceptExpander()
        self.genre_classifier = GenreClassifier() if genre_lora else None
        
        # Store settings for genre-based LoRA loading
        self.genre_lora = genre_lora
        self.baseline_style = baseline_style
        self.use_lora = use_lora
        self.lora_path = lora_path
        self.use_flux = use_flux
        self.flux_model = flux_model
        self.enhanced_flux = enhanced_flux
        self.style_preset = style_preset
        self.poster_type = poster_type
        
        # Use FLUX with text generation if requested
        if use_flux:
            self.generator = VisualGeneratorFlux(model_id=flux_model)
            if add_title and ENHANCED_FLUX_AVAILABLE:
                self.flux_text_gen = StyleEnhancedFlux(shared_generator=self.generator)
            else:
                self.flux_text_gen = None
        elif not genre_lora:
            if baseline_style:
                self.generator = VisualGenerator(lora_path=None, use_lora=False)
            else:
                self.generator = VisualGenerator(lora_path=lora_path, use_lora=use_lora)
        else:
            self.generator = None
        
        if remove_text:
            self.text_remover = AggressiveTextRemover() if aggressive_text_removal else TextRemover()
        else:
            self.text_remover = None
        self.refiner = QualityRefiner()
        self.super_res = SuperResolution() if super_resolution else None
        self.text_overlay = None  # Text overlay handled by enhanced_flux_text
        self.use_template = use_template
        self.template_path = template_path
        self.evaluator = PosterEvaluator()
        self.remove_text = remove_text
        self.aggressive_text_removal = aggressive_text_removal
        self.super_resolution = super_resolution
        self.add_title = add_title
    
    def generate_poster(self, keywords, output_path=None, seed=None, evaluate=True, template=None):
        """End-to-end poster generation with template support"""
        # Validate input: 2-5 keywords
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            raise ValueError(f"Input must contain 2-5 keywords. Got {len(keyword_list)} keywords.")
        
        # Set default output path if None
        if output_path is None:
            output_path = f"outputs/poster_{int(time.time())}.png"
        
        start_time = time.time()
        
        # Step 1: Select random template
        import glob
        import json
        import random
        
        if template is None:
            template_files = glob.glob("templates/template*_layers.json")
            if template_files:
                template_file = random.choice(template_files)
                with open(template_file) as f:
                    template = json.load(f)
                print(f"\n[1/5] Selected template: {template_file}")
            else:
                template = {"size": [720, 1080], "layers": []}
                print(f"\n[1/5] No template found, using default")
        
        # Get image layer dimensions from template
        img_layer = next((l for l in template['layers'] if 'image' in l['name'].lower()), None)
        if img_layer:
            img_bbox = img_layer['bbox']
            image_size = (img_bbox[2] - img_bbox[0], img_bbox[3] - img_bbox[1])
        else:
            image_size = (512, 512)
        print(f"  Image region size: {image_size}")
        
        # Step 2: Expand concepts (TODO: Enhancement by teammates)
        print(f"\n[2/5] Expanding concepts for: '{keywords}'")
        brief = self.expander.expand(keywords, poster_type=self.poster_type, paint_style=self.style_preset, img_size=image_size)
        print(f"Advanced prompt enhancement")
        print(f"  Description: {brief['description']}")
        print(f"  Story title: {brief['story title']}")
        print(f"  Captions: {brief['captions']}")
        
        # Step 3: Classify genre and load appropriate LoRA
        if self.genre_lora and self.genre_classifier:
            genre = self.genre_classifier.classify(keywords)
            self._current_genre = genre  # Store for text styling
            print(f"\n[3/5] Detected genre: {genre}")
            
            # Load genre-specific LoRA (only if not using FLUX and generator not already loaded)
            if self.use_flux:
                print(f"  Using FLUX (LoRA not supported)")
                # Don't reload FLUX if already loaded
                if self.generator is None:
                    self.generator = VisualGeneratorFlux(model_id=self.flux_model)
                else:
                    print(f"  Reusing existing FLUX generator")
            else:
                genre_lora_path = f"models/lora_{genre}"
                if os.path.exists(genre_lora_path):
                    print(f"  Loading {genre} LoRA...")
                    self.generator = VisualGenerator(lora_path=genre_lora_path, use_lora=True)
                else:
                    print(f"  {genre} LoRA not found, using baseline")
                    self.generator = VisualGenerator(lora_path=None, use_lora=False)
        
        # Step 4: Generate visual with FLUX (pass image size)
        print(f"\n[4/5] Generating image with FLUX...")
        print(f"  Target size: {image_size}")
        
        if self.use_lora or self.genre_lora:
            poster_prompt = f"movie poster art, {brief['description']}, visual composition, no text"
        else:
            poster_prompt = f"{brief['description']}, no text, no words, no letters"
        
        # Generate image at template size
        flux_image = self.generator.generate(poster_prompt, seed=seed, width=image_size[0], height=image_size[1])
        print(f"  ✓ Generated at {image_size}")
        
        # Store FLUX image in brief for canvas editing
        brief['flux_image'] = flux_image
        
        # Step 5: Merge with template and add LLM-processed text
        print(f"\n[5/5] Composing final poster...")
        
        # Create poster from template
        from PIL import ImageDraw, ImageFont
        
        poster_size = tuple(template['size'])
        bg_color_hex = template.get('background_color', '#faefcf')
        if bg_color_hex.startswith('#'):
            hex_color = bg_color_hex.lstrip('#')
            bg_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            bg_rgb = (250, 239, 207)
        poster = Image.new('RGB', poster_size, bg_rgb)
        
        # Paste generated image into template
        if img_layer:
            img_bbox = img_layer['bbox']
            poster.paste(flux_image, (img_bbox[0], img_bbox[1]))
            print(f"  ✓ Placed image at {img_bbox}")
        
        # Add LLM-processed text (support multiple text layers)
        text_layers = [l for l in template['layers'] if 'text' in l['name'].lower() or 'title' in l['name'].lower() or 'caption' in l['name'].lower()]
        print(f"  Found {len(text_layers)} text layers: {[l['name'] for l in text_layers]}")
        
        # Get title and captions from LLM
        llm_title = brief.get('title', ' '.join(keyword_list[:3]).title())
        llm_captions = brief.get('captions', [])
        
        # Prepare text elements for collision detection
        text_elements = []
        text_data = []
        
        for idx, text_layer in enumerate(text_layers):
            print(f"  Processing layer {idx}: {text_layer['name']}")
            text_bbox = text_layer['bbox']
            layer_type = text_layer.get('type', 'title')
            
            # Determine text content from LLM output
            layer_name_lower = text_layer['name'].lower()
            if 'title' in layer_name_lower or idx == 0:
                title = llm_title
                print(f"    Title text (from LLM): {title}")
            elif 'caption' in layer_name_lower:
                # Extract caption number (e.g., caption1 -> 0, caption2 -> 1)
                import re
                caption_num = re.findall(r'\d+', layer_name_lower)
                if caption_num:
                    caption_idx = int(caption_num[0]) - 1
                    if 0 <= caption_idx < len(llm_captions):
                        title = llm_captions[caption_idx]
                        print(f"    Caption{caption_idx+1} text (from LLM): {title}")
                    else:
                        title = llm_captions[0] if llm_captions else "COMING SOON"
                        print(f"    Caption fallback: {title}")
                else:
                    title = llm_captions[0] if llm_captions else "COMING SOON"
                    print(f"    Caption default: {title}")
            else:
                title = llm_captions[idx-1] if idx-1 < len(llm_captions) else "SUBTITLE"
                print(f"    Default text: {title}")
            
            # Character spacing for Caption1
            if text_layer.get('spacing') == 'character':
                # Add space between each character, and double space between words
                spaced_chars = []
                for char in title:
                    if char == ' ':
                        spaced_chars.append('  ')  # Double space for word separation
                    else:
                        spaced_chars.append(char + ' ')  # Single space after each character
                title = ''.join(spaced_chars).strip()
                print(f"    After character spacing: {title}")
            
            draw = ImageDraw.Draw(poster)
            
            # Get font for this layer
            fonts_config = template.get('fonts', {})
            layer_name_lower = text_layer['name'].lower()
            
            # Get title alignment for caption inheritance
            title_font_info = fonts_config.get('title', template.get('font', {}))
            title_align = title_font_info.get('align', 'center')
            
            if 'caption2' in layer_name_lower:
                font_info = fonts_config.get('caption2', {})
                # Inherit title alignment if caption is center-aligned
                if font_info.get('align', 'center') == 'center' and title_align == 'center':
                    font_info['align'] = 'center'
                print(f"    Using caption2 font config: {font_info}")
            elif 'caption1' in layer_name_lower or 'caption' in layer_name_lower:
                font_info = fonts_config.get('caption', {})
                # Inherit title alignment if caption is center-aligned
                if font_info.get('align', 'center') == 'center' and title_align == 'center':
                    font_info['align'] = 'center'
                print(f"    Using caption font config: {font_info}")
            else:
                font_info = title_font_info
                print(f"    Using title font config: {font_info}")
            
            font_family = font_info.get('family', 'Graduate-Regular.ttf')
            font_size = font_info.get('size', 37)
            font_color = font_info.get('color', '#043bb4')
            font_align = font_info.get('align', 'center')
            
            try:
                font = ImageFont.truetype(f"fonts/{font_family}", font_size)
            except:
                font = ImageFont.load_default()
            
            if font_color.startswith('#'):
                hex_color = font_color.lstrip('#')
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                rgb_color = (4, 59, 180)
            
            # Auto-adjust text color for contrast
            print(f"    Original text color: {rgb_color}")
            bg_avg_color = get_average_color(poster, text_bbox)
            rgb_color = adjust_text_color(bg_avg_color, rgb_color)
            print(f"    Final text color: {rgb_color}")
            
            # Text wrapping
            max_width = text_bbox[2] - text_bbox[0]
            words = title.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            if current_line:
                lines.append(' '.join(current_line))
            
            # Calculate actual text bbox
            actual_bbox = calculate_text_bbox(text_bbox, lines, font, draw)
            priority = 1 if 'title' in text_layer['name'].lower() else 0
            
            text_elements.append({
                'bbox': actual_bbox,
                'name': text_layer['name'],
                'priority': priority
            })
            
            text_data.append({
                'lines': lines,
                'font': font,
                'rgb_color': rgb_color,
                'font_align': font_align,
                'original_bbox': text_bbox,
                'title': title,
                'font_family': font_family,
                'font_size': font_size,
                'font_color': font_color
            })
        
        # Resolve collisions
        print(f"  Checking text layout collisions...")
        adjusted_elements = resolve_text_positions(text_elements, poster_size, img_bbox if img_layer else None)
        
        # Render text with adjusted positions
        poster_center_x = poster_size[0] // 2
        
        for idx, elem in enumerate(adjusted_elements):
            data = text_data[idx]
            adjusted_bbox = elem['bbox']
            lines = data['lines']
            font = data['font']
            rgb_color = data['rgb_color']
            font_align = data['font_align']
            original_bbox = data['original_bbox']
            
            text_y = adjusted_bbox[1]
            
            if font_align == 'left':
                draw.multiline_text((adjusted_bbox[0], text_y), '\n'.join(lines), font=font, fill=rgb_color, align='left')
            elif font_align == 'right':
                y_offset = text_y
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_width = bbox[2] - bbox[0]
                    text_x = adjusted_bbox[2] - line_width
                    draw.text((text_x, y_offset), line, font=font, fill=rgb_color)
                    y_offset += bbox[3] - bbox[1] + 5
            else:
                # Center align relative to poster center
                y_offset = text_y
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_width = bbox[2] - bbox[0]
                    text_x = poster_center_x - (line_width // 2)
                    draw.text((text_x, y_offset), line, font=font, fill=rgb_color)
                    y_offset += bbox[3] - bbox[1] + 5
            
            print(f"  ✓ Added {elem['name']}: '{data['title']}' at {adjusted_bbox}")
        
        # Use composed poster as final image
        image = poster
        
        # Save and evaluate
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        
        metrics = None
        if evaluate:
            print(f"\nEvaluating quality...")
            metrics = self.evaluator.evaluate(output_path)
            print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
            print(f"  Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
        
        elapsed = time.time() - start_time
        print(f"\n✅ Poster saved to {output_path} ({elapsed:.1f}s)")
        
        # Store rendered text info for editing
        brief['template'] = template
        brief['rendered_texts'] = []
        for idx, elem in enumerate(adjusted_elements):
            data = text_data[idx]
            bbox = elem['bbox']
            align = data['font_align']
            
            # Store reference point based on alignment
            if align == 'center':
                ref_x = poster_center_x
            elif align == 'right':
                ref_x = bbox[2]
            else:
                ref_x = bbox[0]
            
            brief['rendered_texts'].append({
                'text': '\n'.join(data['lines']),
                'bbox': bbox,
                'ref_x': ref_x,
                'color': '#{:02x}{:02x}{:02x}'.format(*data['rgb_color']),
                'size': data['font_size'],
                'family': data['font_family'],
                'align': align
            })
        
        return image, brief, metrics
    

    
    def batch_generate(self, keywords_list, output_dir="outputs/batch", seed=42):
        """Generate multiple posters"""
        results = []
        for i, keywords in enumerate(keywords_list):
            output_path = f"{output_dir}/poster_{i}.png"
            image, brief, metrics = self.generate_poster(keywords, output_path, seed=seed+i)
            results.append({"keywords": keywords, "brief": brief, "metrics": metrics, "path": output_path})
        return results

if __name__ == "__main__":
    # Test baseline
    pipeline = Key2PosterPipeline(use_lora=False, remove_text=False, super_resolution=False, add_title=False, use_flux=True, poster_type="movie", style_preset="digital watercolor")
    pipeline.generate_poster("space exploration adventure")
