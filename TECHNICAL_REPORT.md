# Key2Poster: Technical Report

## Executive Summary

Key2Poster is an AI-powered poster generation system that transforms 2-5 keywords into professional 720x1280 posters using state-of-the-art generative models. The system integrates three distinct layout generation approaches: template-based, LayoutGAN, and PosterO (CVPR 2025), providing users with flexibility between speed, quality, and editability.

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          KEY2POSTER SYSTEM                                   │
│                                                                              │
│  ┌────────────┐         ┌──────────────────────────────────┐               │
│  │   INPUT    │         │      PROCESSING PIPELINE         │               │
│  │            │         │                                  │               │
│  │ Keywords   │────────▶│  1. Concept Expansion (LLM)     │               │
│  │  (2-5)     │         │     • Prompt enhancement         │               │
│  │            │         │     • Title/caption generation   │               │
│  │ Poster     │         │     • Style/sentiment analysis   │               │
│  │  Type      │         │                                  │               │
│  │            │         │  2. Layout Generation            │               │
│  │ Style      │         │     ┌──────────────────────────┐ │               │
│  │  Preset    │         │     │ Mode Selection:          │ │               │
│  │            │         │     │                          │ │               │
│  │ Seed       │         │     │ ┌────────────────────┐  │ │               │
│  └────────────┘         │     │ │ A. Template Mode   │  │ │               │
│                         │     │ │  • JSON templates  │  │ │               │
│                         │     │ │  • 6 layout types  │  │ │               │
│                         │     │ │  • Fast (~10-15s)  │  │ │               │
│                         │     │ └────────────────────┘  │ │               │
│                         │     │                          │ │               │
│                         │     │ ┌────────────────────┐  │ │               │
│                         │     │ │ B. LayoutGAN Mode  │  │ │               │
│                         │     │ │  • Auto-generated  │  │ │               │
│                         │     │ │  • Adaptive layout │  │ │               │
│                         │     │ │  • Medium (~20-30s)│  │ │               │
│                         │     │ └────────────────────┘  │ │               │
│                         │     │                          │ │               │
│                         │     │ ┌────────────────────┐  │ │               │
│                         │     │ │ C. PosterO Mode    │  │ │               │
│                         │     │ │  • CNN detection   │  │ │               │
│                         │     │ │  • LLM generation  │  │ │               │
│                         │     │ │  • Slow (~30-40s)  │  │ │               │
│                         │     │ └────────────────────┘  │ │               │
│                         │     └──────────────────────────┘ │               │
│                         │                                  │               │
│                         │  3. Image Generation (FLUX.1)    │               │
│                         │     • 4-step schnell inference   │               │
│                         │     • Sequential CPU offload     │               │
│                         │     • Dimension validation (÷8)  │               │
│                         │     • ~23GB VRAM requirement     │               │
│                         │                                  │               │
│                         │  4. Text Rendering               │               │
│                         │     • Dynamic font sizing        │               │
│                         │     • Contrast-based coloring    │               │
│                         │     • Smooth anti-aliasing       │               │
│                         │     • Text wrapping              │               │
│                         │                                  │               │
│                         │  5. Post-Processing              │               │
│                         │     • Resolution standardization │               │
│                         │     • Quality evaluation         │               │
│                         │     • Metadata generation        │               │
│                         └──────────────────────────────────┘               │
│                                        │                                    │
│                                        ▼                                    │
│                         ┌──────────────────────────────┐                   │
│                         │         OUTPUT               │                   │
│                         │                              │                   │
│                         │  • 720x1280 Poster (PNG)     │                   │
│                         │  • Layout SVG (optional)     │                   │
│                         │  • Generation metadata       │                   │
│                         │  • Quality metrics           │                   │
│                         └──────────────────────────────┘                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Detailed Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPONENT INTERACTION FLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

    USER INPUT                 CONCEPT EXPANDER              LAYOUT ENGINE
┌──────────────┐           ┌──────────────────┐         ┌─────────────────┐
│              │           │                  │         │                 │
│  Keywords    │──────────▶│  POE API (LLM)   │────────▶│  Template/      │
│  Poster Type │           │  • Claude Sonnet │         │  LayoutGAN/     │
│  Style       │           │  • GPT-4         │         │  PosterO        │
│  Seed        │           │                  │         │                 │
│              │           │  Outputs:        │         │  Outputs:       │
└──────────────┘           │  • Description   │         │  • Bounding     │
                           │  • Title         │         │    boxes        │
                           │  • 3 Captions    │         │  • Layout SVG   │
                           │  • Sentiment     │         │  • Element IDs  │
                           └──────────────────┘         └─────────────────┘
                                    │                            │
                                    │                            │
                                    ▼                            ▼
                           ┌──────────────────┐         ┌─────────────────┐
                           │                  │         │                 │
                           │  FLUX.1 Model    │◀────────│  Dimension      │
                           │  • Schnell       │         │  Calculator     │
                           │  • 4 steps       │         │  • Round to ÷8  │
                           │  • FP16          │         │  • Validate     │
                           │                  │         │                 │
                           │  Outputs:        │         └─────────────────┘
                           │  • Base image    │
                           │  • Latents       │
                           └──────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │                  │
                           │  Text Renderer   │
                           │  • Font loader   │
                           │  • Color picker  │
                           │  • Outline draw  │
                           │                  │
                           │  Outputs:        │
                           │  • Final poster  │
                           └──────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │                  │
                           │  Post-Processor  │
                           │  • Resize 720x   │
                           │    1280          │
                           │  • Quality eval  │
                           │  • Save metadata │
                           │                  │
                           └──────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │   FINAL OUTPUT   │
                           │   720x1280 PNG   │
                           └──────────────────┘
```

### 1.3 Core Components

#### 1.2.1 Concept Expander
- **Purpose**: Enhance user keywords into detailed prompts
- **Technology**: LLM-based (GPT/Claude via POE API)
- **Input**: 2-5 keywords
- **Output**: 
  - Enhanced description
  - Story title
  - 3 captions
  - Sentiment analysis
  - Thematic tags

#### 1.2.2 Visual Generator (FLUX.1)
- **Model**: FLUX.1-schnell
- **Parameters**: ~12B
- **VRAM**: ~23GB
- **Speed**: 4 inference steps
- **Features**:
  - Sequential CPU offload for memory efficiency
  - Automatic dimension rounding (÷8 requirement)
  - High-quality image synthesis

#### 1.2.3 Layout Generators

**A. Template Mode**
- Pre-designed JSON templates
- 6 layout types: split, grid, hero, sidebar, asymmetric, minimal
- Fast generation (~10-15s)
- Full editability

**B. LayoutGAN Mode**
- Auto-generated layouts
- Content-adaptive positioning
- Medium speed (~20-30s)
- Limited editability

**C. PosterO Mode (CVPR 2025)**
- Two-stage process:
  - Part 1: Design intent detection (CNN-based)
  - Part 2: LLM-based layout generation
- Content-aware positioning
- Highest quality (~30-40s)
- No manual editing needed

## 2. Technical Implementation

### 2.1 Pipeline Flow

#### Template Mode Pipeline

```python
def generate_poster(keywords, poster_type, style_preset, seed):
    # 1. Prompt Enhancement
    brief = concept_expander.expand(keywords, poster_type, style_preset)
    
    # 2. Template Selection
    template = select_or_generate_template(poster_type)
    
    # 3. Extract Image Region
    img_bbox = template['layers']['Image']['bbox']
    w, h = img_bbox[2] - img_bbox[0], img_bbox[3] - img_bbox[1]
    
    # 4. Round to ÷8 for FLUX
    w_flux = (w // 8) * 8
    h_flux = (h // 8) * 8
    
    # 5. Generate Image
    image = flux_generator.generate(
        prompt=brief['description'],
        width=w_flux,
        height=h_flux,
        num_inference_steps=4
    )
    
    # 6. Resize to exact template size
    if (w, h) != (w_flux, h_flux):
        image = image.resize((w, h), LANCZOS)
    
    # 7. Compose with template
    poster = compose_template(image, template, brief)
    
    # 8. Add text overlay
    poster = add_text(poster, brief['title'], brief['captions'])
    
    # 9. Standardize to 720x1280
    poster = poster.resize((720, 1280), LANCZOS)
    
    return poster
```

#### PosterO Mode Pipeline

```python
def generate_poster_postero(keywords, poster_type, style_preset, seed):
    # 1. Prompt Enhancement
    brief = concept_expander.expand(keywords, poster_type, style_preset)
    
    # 2. Generate FLUX Background
    image = flux_generator.generate(
        prompt=brief['description'],
        width=512,
        height=768,
        num_inference_steps=4
    )
    image = image.resize((513, 750), LANCZOS)
    
    # 3. PosterO Part 1: Design Intent Detection
    model = load_design_intent_model()
    heatmap = model(image)
    available_areas = extract_high_confidence_regions(heatmap)
    
    # 4. PosterO Part 2: LLM Layout Generation
    svg_layout = llm_generate_layout(
        available_areas=available_areas,
        elements=['text_1', 'text_2', 'text_3', 'logo_1', 'underlay_1']
    )
    
    # 5. Extract Text Bounding Boxes
    text_boxes = parse_svg_text_elements(svg_layout)
    
    # 6. Upscale to 720x1280
    image = image.resize((720, 1280), LANCZOS)
    text_boxes = scale_bboxes(text_boxes, 720/513, 1280/750)
    
    # 7. Render Text with Dynamic Sizing
    poster = render_text_dynamic(
        image=image,
        text_boxes=text_boxes,
        title=brief['title'],
        captions=brief['captions']
    )
    
    return poster
```

### 2.2 Key Algorithms

#### 2.2.1 Dynamic Font Sizing

```python
def fit_text_to_bbox(text, bbox, draw, font_path):
    x1, y1, x2, y2 = bbox
    box_w, box_h = x2 - x1, y2 - y1
    
    # Dynamic max size based on box height
    max_size = min(int(box_h * 0.6), 120)
    min_size = max(int(box_h * 0.15), 20)
    
    # Binary search for optimal size
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size)
        bbox_text = draw.textbbox((0, 0), text, font=font)
        text_w = bbox_text[2] - bbox_text[0]
        text_h = bbox_text[3] - bbox_text[1]
        
        if text_w <= box_w * 0.95 and text_h <= box_h * 0.85:
            return font, text
    
    # Fallback: text wrapping
    return wrap_text(text, box_w, min_size, font_path)
```

#### 2.2.2 Contrast-Based Color Selection

```python
def get_contrasting_color(image, bbox):
    x1, y1, x2, y2 = bbox
    region = image.crop((x1, y1, x2, y2))
    
    # Calculate average brightness
    stat = ImageStat.Stat(region)
    avg_brightness = sum(stat.mean) / 3
    
    # Select color palette based on brightness
    if avg_brightness < 100:  # Dark background
        colors = [(255,255,255), (255,220,100), (100,200,255)]
    elif avg_brightness < 160:  # Medium
        colors = [(255,255,255), (255,200,50), (50,255,200)]
    else:  # Light background
        colors = [(20,20,20), (80,40,120), (120,40,40)]
    
    return random.choice(colors)
```

#### 2.2.3 Smooth Text Rendering

```python
def render_text_with_outline(draw, text, pos, font, color, outline_color):
    x, y = pos
    outline_width = max(2, int(font.size / 20))
    
    # Circular outline for smoothness
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx*dx + dy*dy <= outline_width*outline_width:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    
    # Main text
    draw.text((x, y), text, font=font, fill=color)
```

### 2.3 PosterO Integration

#### Part 1: Design Intent Detection

```python
class DesignIntentDetector:
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.model.eval()
    
    def detect(self, image):
        # Resize to model input size
        img = image.resize((513, 750))
        img_tensor = torch.from_numpy(np.array(img))
        img_tensor = img_tensor.permute(2, 0, 1).float() / 255.0
        
        # Forward pass
        with torch.no_grad():
            heatmap = self.model(img_tensor.unsqueeze(0))
        
        # Extract high-confidence regions
        heatmap_np = heatmap[0, 0].cpu().numpy()
        regions = self.extract_regions(heatmap_np, threshold=0.2)
        
        return regions
    
    def extract_regions(self, heatmap, threshold):
        # Grid-based detection (3x2 cells)
        h, w = heatmap.shape
        grid_h, grid_w = 3, 2
        cell_h, cell_w = h // grid_h, w // grid_w
        
        regions = []
        for row in range(grid_h):
            for col in range(grid_w):
                y1, y2 = row * cell_h, (row + 1) * cell_h
                x1, x2 = col * cell_w, (col + 1) * cell_w
                
                region = heatmap[y1:y2, x1:x2]
                if region.mean() > threshold:
                    regions.append((x1, y1, x2, y2))
        
        return regions
```

#### Part 2: LLM Layout Generation

```python
def generate_layout_llm(available_areas, elements):
    areas_str = ", ".join([f"({x1},{y1},{x2},{y2})" 
                           for x1,y1,x2,y2 in available_areas])
    
    prompt = f"""Generate SVG poster layout.

Canvas: 513x750
Available areas: {areas_str}
Elements: {', '.join(elements)}

Rules:
1. Use <rect> tags
2. Place elements within available areas
3. No overlapping
4. Valid coordinates

Output complete SVG:"""
    
    # Call LLM via POE API
    response = llm.generate(prompt, temperature=0.7, max_tokens=800)
    svg = response.text
    
    return svg
```

## 3. Performance Optimization

### 3.1 Memory Management

**FLUX.1 Sequential CPU Offload**
```python
pipe.enable_sequential_cpu_offload()
```
- Reduces VRAM usage by ~40%
- Moves model components to CPU when not in use
- Slight speed trade-off for memory efficiency

### 3.2 Dimension Validation

**FLUX Requirement**: All dimensions must be divisible by 8

```python
def round_to_8(value):
    return (value // 8) * 8

# Template generator
img_w = round_to_8(w - 2 * margin)
img_h = round_to_8(h - margin - 250)
```

### 3.3 Caching Strategy

- Model weights cached after first load
- Font files loaded once per session
- Template JSON parsed and cached

## 4. Quality Metrics

### 4.1 Aesthetic Scoring

Uses pre-trained aesthetic predictor:
- Score range: 0-10
- Average scores: 2.2-2.4 (typical for AI-generated)
- Factors: composition, color harmony, visual balance

### 4.2 Resolution Validation

- Input: 2-5 keywords
- Intermediate: Variable (template-dependent)
- Output: 720x1280 (standardized)
- Quality: LANCZOS resampling for upscaling

## 5. User Interface

### 5.1 Unified App (app_unified.py)

**Features**:
- Mode selection (Template/LayoutGAN/PosterO)
- Keyword input with validation
- Poster type and style dropdowns
- Seed control for reproducibility
- Interactive text editing (Template mode)
- Real-time preview

**Text Editing Controls**:
- Title: text, size (20-120), color (8 options), X/Y position (0-100%)
- Caption: text, size (15-80), color (8 options), X/Y position (0-100%)
- Update button for live preview

### 5.2 Specialized Apps

- **app_editable.py**: Full Adobe-like editing with layers
- **app.py**: PosterO-focused interface
- **app_clg_lo.py**: LayoutGAN-specific features

## 6. Comparison of Modes

| Feature | Template | LayoutGAN | PosterO |
|---------|----------|-----------|---------|
| **Speed** | ⚡⚡⚡ Fast (10-15s) | ⚡⚡ Medium (20-30s) | ⚡ Slow (30-40s) |
| **Quality** | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Great | ⭐⭐⭐⭐⭐ Best |
| **Editability** | ✅ Full | ⚠️ Limited | ❌ None |
| **Consistency** | High | Medium | Variable |
| **Customization** | High | Medium | Low |
| **Learning Curve** | Low | Medium | Low |

## 7. Limitations and Future Work

### 7.1 Current Limitations

1. **GPU Requirement**: FLUX.1 requires CUDA GPU
2. **VRAM**: Minimum 16GB recommended
3. **Font Support**: Limited to included fonts
4. **Language**: English only
5. **Batch Processing**: Sequential only

### 7.2 Future Enhancements

1. **Multi-GPU Support**: Parallel generation
2. **Cloud Deployment**: Web-based service
3. **Font Library**: Expanded font collection
4. **Multi-Language**: I18n support
5. **Real-Time Preview**: Live editing feedback
6. **Style Transfer**: Custom style training
7. **Video Posters**: Animated poster generation

## 8. Conclusion

Key2Poster successfully integrates three state-of-the-art approaches to poster generation, providing users with flexibility between speed, quality, and editability. The system demonstrates:

- **Robustness**: Handles diverse inputs and poster types
- **Quality**: Produces professional 720x1280 posters
- **Usability**: Intuitive interfaces for all skill levels
- **Extensibility**: Modular architecture for future enhancements

The integration of FLUX.1 for image generation and PosterO for layout provides a powerful combination that advances the state-of-the-art in automated poster design.

## 9. References

1. FLUX.1-schnell: Black Forest Labs, 2024
2. PosterO: Content-aware Poster Layout Generation, CVPR 2025
3. LayoutGAN: Generating Graphic Layouts with Generative Adversarial Networks
4. Stable Diffusion: High-Resolution Image Synthesis with Latent Diffusion Models

## Appendix A: System Requirements

**Minimum**:
- GPU: NVIDIA RTX 3060 (12GB VRAM)
- RAM: 16GB
- Storage: 50GB
- Python: 3.10+

**Recommended**:
- GPU: NVIDIA RTX 3090/4090 (24GB VRAM)
- RAM: 32GB
- Storage: 100GB SSD
- Python: 3.10+

## Appendix B: API Documentation

See individual module docstrings for detailed API documentation:
- `src/pipeline.py`
- `src/pipeline_postero.py`
- `src/visual_generator_flux.py`
- `add_text_to_poster.py`

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Authors**: Key2Poster Development Team
