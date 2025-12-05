"""Key2Poster Pipeline with PosterO Underlay Support"""
import sys
import os
import subprocess
import time
import random
import glob
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline
import torch

sys.path.insert(0, 'src')
from src.concept_expander import ConceptExpander
from src.visual_generator_flux import VisualGeneratorFlux
from src.evaluator import PosterEvaluator


class Key2PosterUnderlayMode:
    """
    PosterO Underlay Mode Pipeline:
    1. FLUX background image
    2. SD-generated underlay images
    3. Text overlay
    """
    
    def __init__(self, flux_model="black-forest-labs/FLUX.1-schnell",
                 sd_model="runwayml/stable-diffusion-v1-5",
                 poster_type='movie', style_preset='cinematic'):
        print("="*60)
        print("Key2Poster + PosterO Underlay Mode")
        print("="*60)
        print("Pipeline:")
        print("  1. FLUX Background Generation")
        print("  2. PosterO Layout Detection")
        print("  3. SD Underlay Image Generation")
        print("  4. Text Overlay")
        print("  5. Quality Evaluation")
        print("="*60)
        
        self.expander = ConceptExpander()
        self.flux_generator = VisualGeneratorFlux(model_id=flux_model)
        self.evaluator = PosterEvaluator()
        self.poster_type = poster_type
        self.style_preset = style_preset
        
        # Load lightweight SD for underlay
        print("Loading SD for underlay generation...")
        self.sd_pipe = StableDiffusionPipeline.from_pretrained(
            sd_model,
            torch_dtype=torch.float16,
            safety_checker=None
        )
        self.sd_pipe.to("cuda")
        self.sd_pipe.enable_attention_slicing()
        print("✓ SD loaded")
        
        # Select font
        font_files = glob.glob("fonts/*.ttf") + glob.glob("fonts/*.otf")
        self.shared_font = random.choice(font_files) if font_files else "fonts/Graduate-Regular.ttf"
        print(f"  Selected font: {self.shared_font}")
    
    def _run_postero_layout(self, image_path):
        """Run PosterO layout generation"""
        print("\n[2/5] PosterO Layout Generation")
        result = subprocess.run(
            ["python", "combine_simple.py", image_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            return None
        
        if os.path.exists("combined_output.svg"):
            with open("combined_output.svg", 'r') as f:
                return f.read()
        return None
    
    def _extract_underlay_bboxes(self, svg_content):
        """Extract underlay element bboxes from SVG"""
        svg_clean = svg_content.replace('```svg', '').replace('```', '').strip()
        
        pattern = re.compile(
            r'<!--\s*[Uu]nderlay[_ ]?(\d+)[^>]*?-->\s*'
            r'<rect[^>]*?x="([^"]+)"[^>]*?y="([^"]+)"[^>]*?width="([^"]+)"[^>]*?height="([^"]+)"',
            re.DOTALL | re.IGNORECASE
        )
        
        underlays = []
        for match in pattern.finditer(svg_clean):
            x = int(float(match.group(2)))
            y = int(float(match.group(3)))
            w = int(float(match.group(4)))
            h = int(float(match.group(5)))
            underlays.append({'bbox': (x, y, x+w, y+h)})
        
        return underlays
    
    def _extract_text_bboxes(self, svg_content):
        """Extract text element bboxes"""
        svg_clean = svg_content.replace('```svg', '').replace('```', '').strip()
        
        pattern = re.compile(
            r'<!--\s*[Tt]ext[_ ]?(\d+)[^>]*?-->\s*'
            r'<rect[^>]*?x="([^"]+)"[^>]*?y="([^"]+)"[^>]*?width="([^"]+)"[^>]*?height="([^"]+)"',
            re.DOTALL | re.IGNORECASE
        )
        
        text_boxes = []
        for match in pattern.finditer(svg_clean):
            x = int(float(match.group(2)))
            y = int(float(match.group(3)))
            w = int(float(match.group(4)))
            h = int(float(match.group(5)))
            text_boxes.append({'id': match.group(1), 'bbox': (x, y, x+w, y+h)})
        
        text_boxes.sort(key=lambda b: (b['bbox'][2]-b['bbox'][0])*(b['bbox'][3]-b['bbox'][1]), reverse=True)
        return text_boxes
    
    def _generate_underlay_image(self, prompt, width, height, seed):
        """Generate underlay image with SD"""
        with torch.no_grad():
            result = self.sd_pipe(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=20,
                guidance_scale=7.5,
                generator=torch.Generator("cuda").manual_seed(seed) if seed else None
            )
        return result.images[0]
    
    def _render_text(self, image, text_boxes, title, captions):
        """Render text with dynamic sizing"""
        from PIL import ImageStat
        
        img = image.convert('RGBA')
        draw = ImageDraw.Draw(img)
        
        def get_contrasting_color(bbox):
            x1, y1, x2, y2 = bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img.width, x2), min(img.height, y2)
            if x2 <= x1 or y2 <= y1:
                return (255, 255, 255)
            region = img.crop((x1, y1, x2, y2))
            stat = ImageStat.Stat(region)
            avg_brightness = sum(stat.mean) / 3
            if avg_brightness < 100:
                colors = [(255, 255, 255), (255, 220, 100), (100, 200, 255)]
            elif avg_brightness < 160:
                colors = [(255, 255, 255), (255, 200, 50), (50, 255, 200)]
            else:
                colors = [(20, 20, 20), (80, 40, 120), (120, 40, 40)]
            return random.choice(colors)
        
        def fit_text(text, bbox):
            x1, y1, x2, y2 = bbox
            box_w, box_h = x2 - x1, y2 - y1
            dynamic_max = min(int(box_h * 0.6), 120)
            dynamic_min = max(int(box_h * 0.15), 20)
            
            for size in range(dynamic_max, dynamic_min - 1, -2):
                try:
                    font = ImageFont.truetype(self.shared_font, size)
                    bbox_text = draw.textbbox((0, 0), text, font=font)
                    if bbox_text[2] - bbox_text[0] <= box_w * 0.95 and bbox_text[3] - bbox_text[1] <= box_h * 0.85:
                        return font, text
                except:
                    pass
            return ImageFont.truetype(self.shared_font, dynamic_min), text
        
        # Title
        if title and len(text_boxes) > 0:
            title_box = text_boxes[0]['bbox']
            font, fitted_text = fit_text(title, title_box)
            text_color = get_contrasting_color(title_box)
            outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
            
            x1, y1, x2, y2 = title_box
            bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
            text_w, text_h = bbox_text[2] - bbox_text[0], bbox_text[3] - bbox_text[1]
            text_x = x1 + (x2 - x1 - text_w) // 2
            text_y = y1 + (y2 - y1 - text_h) // 2
            
            outline_width = max(2, int(font.size / 20))
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx*dx + dy*dy <= outline_width*outline_width:
                        draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
            draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
            print(f"  ✓ Title: '{title}'")
        
        # Captions
        for i, caption in enumerate(captions):
            if i + 1 >= len(text_boxes):
                break
            caption_box = text_boxes[i + 1]['bbox']
            font, fitted_text = fit_text(caption, caption_box)
            text_color = get_contrasting_color(caption_box)
            outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
            
            x1, y1, x2, y2 = caption_box
            bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
            text_w, text_h = bbox_text[2] - bbox_text[0], bbox_text[3] - bbox_text[1]
            text_x = x1 + (x2 - x1 - text_w) // 2
            text_y = y1 + (y2 - y1 - text_h) // 2
            
            outline_width = max(2, int(font.size / 25))
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx*dx + dy*dy <= outline_width*outline_width:
                        draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
            draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
            print(f"  ✓ Caption {i+1}: '{caption}'")
        
        return img.convert('RGB')
    
    def generate_poster(self, keywords, output_path=None, seed=None):
        """Generate poster with underlay mode"""
        if output_path is None:
            output_path = f"outputs/poster_underlay_{int(time.time())}.png"
        
        start_time = time.time()
        
        print("\n" + "="*60)
        print(f"Generating poster: '{keywords}'")
        print("="*60)
        
        # Step 1: FLUX Background
        print("\n[1/5] FLUX Background Generation")
        brief = self.expander.expand(keywords, poster_type=self.poster_type, paint_style=self.style_preset)
        print(f"  Title: {brief['story title']}")
        
        prompt = f"{brief['description']}, no text, no words"
        bg_image = self.flux_generator.generate(prompt, width=512, height=768, num_inference_steps=4, seed=seed)
        bg_image = bg_image.resize((513, 750), Image.LANCZOS)
        
        temp_path = f"temp_bg_{int(time.time())}.png"
        bg_image.save(temp_path)
        print("  ✓ Background generated")
        
        # Step 2: PosterO Layout
        svg_content = self._run_postero_layout(temp_path)
        if not svg_content:
            print("  ⚠ Layout failed, using background only")
            bg_image = bg_image.resize((720, 1280), Image.LANCZOS)
            bg_image.save(output_path)
            return bg_image, brief, None
        
        underlays = self._extract_underlay_bboxes(svg_content)
        text_boxes = self._extract_text_bboxes(svg_content)
        print(f"  ✓ Found {len(underlays)} underlays, {len(text_boxes)} text regions")
        
        # Step 3: Generate Underlay Images
        print("\n[3/5] SD Underlay Generation")
        bg_image = bg_image.resize((720, 1280), Image.LANCZOS)
        
        for i, underlay in enumerate(underlays):
            x1, y1, x2, y2 = underlay['bbox']
            # Scale to 720x1280
            x1 = int(x1 * 720 / 513)
            x2 = int(x2 * 720 / 513)
            y1 = int(y1 * 1280 / 750)
            y2 = int(y2 * 1280 / 750)
            
            w, h = x2 - x1, y2 - y1
            if w < 64 or h < 64:
                continue
            
            # Round to nearest multiple of 8 for SD
            w = (w // 8) * 8
            h = (h // 8) * 8
            
            # Generate underlay image
            underlay_prompt = f"{brief['description']}, decorative element, abstract"
            print(f"  Generating underlay {i+1}: {w}x{h}")
            underlay_img = self._generate_underlay_image(underlay_prompt, w, h, seed + i + 100 if seed else None)
            
            # Resize to exact bbox size if needed
            if underlay_img.size != (x2 - x1, y2 - y1):
                underlay_img = underlay_img.resize((x2 - x1, y2 - y1), Image.LANCZOS)
            
            # Paste with transparency
            underlay_img = underlay_img.convert('RGBA')
            alpha = Image.new('L', underlay_img.size, int(255 * 0.7))
            underlay_img.putalpha(alpha)
            bg_image.paste(underlay_img, (x1, y1), underlay_img)
            print(f"  ✓ Underlay {i+1} added")
        
        # Step 4: Text Overlay
        print("\n[4/5] Text Overlay")
        # Scale text boxes
        text_boxes_scaled = [{
            'id': box['id'],
            'bbox': (
                int(box['bbox'][0] * 720 / 513),
                int(box['bbox'][1] * 1280 / 750),
                int(box['bbox'][2] * 720 / 513),
                int(box['bbox'][3] * 1280 / 750)
            )
        } for box in text_boxes]
        
        final_image = self._render_text(bg_image, text_boxes_scaled, brief['story title'], brief['captions'])
        
        # Step 5: Save
        print("\n[5/5] Quality Evaluation")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final_image.save(output_path, quality=95)
        
        metrics = self.evaluator.evaluate(output_path)
        print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists("combined_output.svg"):
            os.rename("combined_output.svg", output_path.replace('.png', '_layout.svg'))
        
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print(f"✅ Poster saved to {output_path} ({elapsed:.1f}s)")
        print("="*60)
        
        return final_image, brief, metrics


if __name__ == "__main__":
    pipeline = Key2PosterUnderlayMode(poster_type="movie", style_preset="cinematic")
    pipeline.generate_poster("cyberpunk neon city", output_path="outputs/test_underlay.png", seed=42)
