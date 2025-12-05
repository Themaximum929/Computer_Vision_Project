"""Enhanced Key2Poster Pipeline with PosterO Integration"""
import sys
import os
import subprocess
import time
import random
import glob
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re

sys.path.insert(0, 'src')
from src.concept_expander import ConceptExpander
from src.visual_generator_flux import VisualGeneratorFlux
from src.evaluator import PosterEvaluator


class Key2PosterPosterO:
    """
    Enhanced Key2Poster Pipeline with PosterO Layout Generation
    
    Pipeline Steps:
    1. Prompt Engineering (ConceptExpander)
    2. FLUX Image Generation
    3. PosterO Layout Generation (Part 1 + Part 2)
    4. Text Formatting & Rendering
    5. Quality Evaluation
    """
    
    def __init__(self, flux_model="black-forest-labs/FLUX.1-schnell", 
                 poster_type='movie', style_preset='cinematic',
                 font_path="fonts/Graduate-Regular.ttf"):
        # Select one random font for entire session
        font_files = glob.glob("fonts/*.ttf") + glob.glob("fonts/*.otf")
        self.shared_font = random.choice(font_files) if font_files else font_path
        print("="*60)
        print("Key2Poster + PosterO Pipeline (CVPR 2025)")
        print("="*60)
        print("Pipeline Steps:")
        print("  1. Prompt Engineering (LLM-based)")
        print("  2. FLUX Image Generation")
        print("  3. PosterO Layout Detection + Generation")
        print("  4. Text Formatting & Rendering")
        print("  5. Quality Evaluation")
        print("="*60)
        
        self.expander = ConceptExpander()
        self.generator = VisualGeneratorFlux(model_id=flux_model)
        self.evaluator = PosterEvaluator()
        self.poster_type = poster_type
        self.style_preset = style_preset
        self.font_path = self.shared_font
        print(f"  Selected font: {self.shared_font}")
    
    def _run_postero_layout(self, image_path):
        """Run PosterO layout generation (Part 1 + Part 2)"""
        print("\n[3/5] PosterO Layout Generation")
        print("  Running Part 1 (Design Intent Detection)...")
        print("  Running Part 2 (LLM Layout Generation)...")
        
        # Run combine_simple.py
        result = subprocess.run(
            ["python", "combine_simple.py", image_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            print(f"  ⚠ PosterO failed: {result.stderr}")
            return None
        
        # Read generated SVG
        if os.path.exists("combined_output.svg"):
            with open("combined_output.svg", 'r') as f:
                svg_content = f.read()
            print("  ✓ Layout generated successfully")
            return svg_content
        else:
            print("  ⚠ No SVG output found")
            return None
    
    def _extract_text_bboxes(self, svg_content):
        """Extract text element bounding boxes from PosterO SVG"""
        svg_clean = svg_content.replace('```svg', '').replace('```', '').strip()
        
        # Pattern 1: Match comments like <!-- Text 1 --> or <!-- text_1: --> followed by <rect>
        comment_pattern = re.compile(
            r'<!--\s*[Tt]ext[_ ]?(\d+)[^>]*?-->\s*'
            r'<rect[^>]*?x="([^"]+)"[^>]*?y="([^"]+)"[^>]*?width="([^"]+)"[^>]*?height="([^"]+)"',
            re.DOTALL | re.IGNORECASE
        )
        
        # Pattern 2: Match <rect id="text_N" ...>
        id_pattern = re.compile(
            r'<rect[^>]*?id="(text_\d+)"[^>]*?'
            r'x="([^"]+)"[^>]*?y="([^"]+)"[^>]*?'
            r'width="([^"]+)"[^>]*?height="([^"]+)"',
            re.DOTALL
        )
        
        text_boxes = []
        
        # Try comment pattern first
        for match in comment_pattern.finditer(svg_clean):
            elem_id = match.group(1)
            x = int(float(match.group(2)))
            y = int(float(match.group(3)))
            w = int(float(match.group(4)))
            h = int(float(match.group(5)))
            text_boxes.append({'id': elem_id, 'bbox': (x, y, x+w, y+h)})
        
        # Try id pattern if no results
        if not text_boxes:
            for match in id_pattern.finditer(svg_clean):
                elem_id = match.group(1)
                x = int(float(match.group(2)))
                y = int(float(match.group(3)))
                w = int(float(match.group(4)))
                h = int(float(match.group(5)))
                text_boxes.append({'id': elem_id, 'bbox': (x, y, x+w, y+h)})
        
        # Sort by area (largest first for title)
        text_boxes.sort(key=lambda b: (b['bbox'][2]-b['bbox'][0])*(b['bbox'][3]-b['bbox'][1]), reverse=True)
        
        return text_boxes
    
    def _fit_text_to_bbox(self, text, bbox, draw, max_font_size=120, min_font_size=20):
        """Find optimal font size to fit text in bbox"""
        x1, y1, x2, y2 = bbox
        box_w, box_h = x2 - x1, y2 - y1
        
        # Dynamic max font size based on box height
        dynamic_max = min(int(box_h * 0.6), max_font_size)
        dynamic_min = max(int(box_h * 0.15), min_font_size)
        
        # Use shared font for entire poster
        font_path = self.font_path
        
        for size in range(dynamic_max, dynamic_min - 1, -2):
            try:
                font = ImageFont.truetype(font_path, size)
            except:
                font = ImageFont.load_default()
                return font, text
            
            bbox_text = draw.textbbox((0, 0), text, font=font)
            text_w = bbox_text[2] - bbox_text[0]
            text_h = bbox_text[3] - bbox_text[1]
            
            if text_w <= box_w * 0.9 and text_h <= box_h * 0.8:
                return font, text
        
        # Text wrapping if doesn't fit
        font = ImageFont.truetype(font_path, dynamic_min)
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox_text = draw.textbbox((0, 0), test_line, font=font)
            if bbox_text[2] - bbox_text[0] <= box_w * 0.9:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return font, '\n'.join(lines)
    
    def _get_contrasting_color(self, image, bbox):
        """Get contrasting and varied text color based on background."""
        from PIL import ImageStat
        x1, y1, x2, y2 = bbox
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(image.width, x2), min(image.height, y2)
        
        if x2 <= x1 or y2 <= y1:
            return (255, 255, 255)
        
        region = image.crop((x1, y1, x2, y2))
        stat = ImageStat.Stat(region)
        avg_brightness = sum(stat.mean) / 3
        
        # Generate varied colors with good contrast
        if avg_brightness < 100:
            colors = [(255, 255, 255), (255, 220, 100), (100, 200, 255), (255, 150, 150)]
        elif avg_brightness < 160:
            colors = [(255, 255, 255), (255, 200, 50), (50, 255, 200), (255, 100, 100)]
        else:
            colors = [(20, 20, 20), (80, 40, 120), (120, 40, 40), (40, 80, 120)]
        
        return random.choice(colors)
    
    def _render_text(self, image, text_boxes, title, captions):
        """Render title and captions on poster"""
        print("\n[4/5] Text Formatting & Rendering")
        
        if not text_boxes:
            print("  ⚠ No text boxes found, skipping text")
            return image
        
        img = image.convert('RGBA')
        draw = ImageDraw.Draw(img)
        
        # Add title to largest text box
        if title and len(text_boxes) > 0:
            title_box = text_boxes[0]['bbox']
            font, fitted_text = self._fit_text_to_bbox(title, title_box, draw, max_font_size=80)
            
            # Get contrasting color
            text_color = self._get_contrasting_color(img, title_box)
            outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
            
            # Center text in bbox
            x1, y1, x2, y2 = title_box
            bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
            text_w = bbox_text[2] - bbox_text[0]
            text_h = bbox_text[3] - bbox_text[1]
            
            text_x = x1 + (x2 - x1 - text_w) // 2
            text_y = y1 + (y2 - y1 - text_h) // 2
            
            # Draw with smooth outline
            outline_width = max(2, int(font.size / 20))
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx*dx + dy*dy <= outline_width*outline_width:
                        draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
            draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
            
            print(f"  ✓ Title: '{title}' (color: {text_color})")
        
        # Add captions to remaining text boxes
        for i, caption in enumerate(captions):
            if i + 1 >= len(text_boxes):
                break
            
            caption_box = text_boxes[i + 1]['bbox']
            font, fitted_text = self._fit_text_to_bbox(caption, caption_box, draw, max_font_size=40)
            
            # Get contrasting color
            text_color = self._get_contrasting_color(img, caption_box)
            outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
            
            # Center text
            x1, y1, x2, y2 = caption_box
            bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
            text_w = bbox_text[2] - bbox_text[0]
            text_h = bbox_text[3] - bbox_text[1]
            
            text_x = x1 + (x2 - x1 - text_w) // 2
            text_y = y1 + (y2 - y1 - text_h) // 2
            
            # Draw with smooth outline
            outline_width = max(2, int(font.size / 25))
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx*dx + dy*dy <= outline_width*outline_width:
                        draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
            draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
            
            print(f"  ✓ Caption {i+1}: '{caption}' (color: {text_color})")
        
        return img.convert('RGB')
    
    def generate_poster(self, keywords, output_path=None, seed=None):
        """
        End-to-end poster generation with PosterO
        
        Args:
            keywords: 2-5 keywords for poster generation
            output_path: Where to save final poster
            seed: Random seed for reproducibility
        
        Returns:
            image: Final poster image
            brief: Generation metadata
            metrics: Quality metrics
        """
        # Validate input
        keyword_list = [k.strip() for k in keywords.split() if k.strip()]
        if len(keyword_list) < 2 or len(keyword_list) > 5:
            raise ValueError(f"Input must contain 2-5 keywords. Got {len(keyword_list)} keywords.")
        
        if output_path is None:
            output_path = f"outputs/poster_{int(time.time())}.png"
        
        start_time = time.time()
        
        print("\n" + "="*60)
        print(f"Generating poster for: '{keywords}'")
        print("="*60)
        
        # Step 1: Prompt Engineering
        print("\n[1/5] Prompt Engineering")
        brief = self.expander.expand(keywords, poster_type=self.poster_type, paint_style=self.style_preset)
        print(f"  Title: {brief['story title']}")
        print(f"  Description: {brief['description'][:80]}...")
        print(f"  Captions: {brief['captions']}")
        
        # Step 2: FLUX Image Generation
        print("\n[2/5] FLUX Image Generation")
        print(f"  Generating 513x750 image...")
        
        prompt = f"{brief['description']}, no text, no words, no letters"
        image = self.generator.generate(
            prompt=prompt,
            width=512,
            height=768,
            num_inference_steps=4,
            seed=seed
        )
        
        # Resize to PosterO size
        image = image.resize((513, 750), Image.LANCZOS)
        
        # Save temp image for PosterO
        temp_image_path = f"temp_flux_{int(time.time())}.png"
        image.save(temp_image_path)
        print(f"  ✓ Image generated")
        
        # Step 3: PosterO Layout Generation
        svg_content = self._run_postero_layout(temp_image_path)
        
        if svg_content:
            # Extract text bboxes
            text_boxes = self._extract_text_bboxes(svg_content)
            print(f"  ✓ Found {len(text_boxes)} text regions")
            
            # Upscale image to final resolution first
            image = image.resize((720, 1280), Image.LANCZOS)
            
            # Scale text boxes to final resolution
            scale_x = 720 / 513
            scale_y = 1280 / 750
            text_boxes_scaled = [{
                'id': box['id'],
                'bbox': (
                    int(box['bbox'][0] * scale_x),
                    int(box['bbox'][1] * scale_y),
                    int(box['bbox'][2] * scale_x),
                    int(box['bbox'][3] * scale_y)
                )
            } for box in text_boxes]
            
            # Step 4: Text Rendering
            title = brief['story title']
            captions = brief['captions']
            final_image = self._render_text(image, text_boxes_scaled, title, captions)
        else:
            print("  ⚠ Using image without layout")
            final_image = image.resize((720, 1280), Image.LANCZOS)
        
        # Step 5: Quality Evaluation
        print("\n[5/5] Quality Evaluation")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final_image.save(output_path, quality=95)
        
        metrics = self.evaluator.evaluate(output_path)
        print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
        print(f"  Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
        
        # Cleanup
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists("combined_output.svg"):
            os.rename("combined_output.svg", output_path.replace('.png', '_layout.svg'))
        if os.path.exists("combined_visualization.png"):
            os.rename("combined_visualization.png", output_path.replace('.png', '_visualization.png'))
        
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print(f"✅ Poster saved to {output_path} ({elapsed:.1f}s)")
        print("="*60)
        
        return final_image, brief, metrics


if __name__ == "__main__":
    # Test pipeline
    pipeline = Key2PosterPosterO(poster_type="movie", style_preset="cinematic")
    pipeline.generate_poster("cyberpunk neon city", output_path="outputs/test_postero.png", seed=42)
