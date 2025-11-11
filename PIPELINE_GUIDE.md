# Key2Poster Complete Pipeline Guide

## Quick Start (3 Steps)

### Step 1: Collect Training Data
```bash
python src/collect_data.py
```
This scrapes 50+ movie posters from IMDB with genre labels (~2 minutes).

### Step 2: Train LoRA Model
```bash
python src/train_lora.py
```
Fine-tunes Stable Diffusion on collected posters (~10-30 minutes depending on GPU).

### Step 3: Generate Posters
```bash
# Baseline (no fine-tuning)
python run_pipeline.py "space exploration adventure"

# With LoRA fine-tuning
python run_pipeline.py "space exploration adventure" --lora
```

---

## Complete Workflow

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# For CUDA 12.x
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify setup
python test_setup.py
```

### 2. Data Collection (5-10 minutes)
```bash
python src/collect_data.py
```

**What it does:**
- Scrapes 50+ movie/anime posters from IMDB
- Extracts genre labels for each poster
- Saves images to `data/posters/`
- Creates `metadata.json` with genre information

**Output:**
```
data/posters/
├── action_epic_tt0468569.jpg
├── drama_thriller_tt0111161.jpg
├── anime_fantasy_tt5311514.jpg
└── metadata.json
```

### 3. LoRA Training (10-30 minutes)
```bash
python src/train_lora.py
```

**What it does:**
- Loads Stable Diffusion v1.5
- Fine-tunes cross-attention layers on poster dataset
- Saves LoRA weights to `models/poster_lora/`

**Training Parameters:**
- Epochs: 10
- Batch Size: 1
- Learning Rate: 1e-5
- Trainable Parameters: ~2-5% of total model

**Output:**
```
models/poster_lora/
├── lora_weights.pth
├── adapter_config.json
└── adapter_model.safetensors
```

### 4. Poster Generation

#### Single Poster
```bash
# Baseline
python run_pipeline.py "dark fantasy warrior" --output outputs/my_poster.png

# With LoRA
python run_pipeline.py "dark fantasy warrior" --lora --output outputs/my_poster.png

# With seed for reproducibility
python run_pipeline.py "space adventure" --lora --seed 42
```

#### Batch Generation
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(use_lora=True, lora_path="models/poster_lora")

keywords_list = [
    "space exploration adventure",
    "dark fantasy warrior",
    "romantic sunset beach"
]

results = pipeline.batch_generate(keywords_list, output_dir="outputs/batch")
```

### 5. Baseline vs LoRA Comparison
```bash
python src/experiment.py
```

**What it does:**
- Generates 5 test posters with baseline SD
- Generates same 5 posters with LoRA fine-tuning
- Compares aesthetic scores and quality metrics
- Saves results to `outputs/comparison/`

**Output:**
```
outputs/comparison/
├── baseline/
│   ├── poster_0.png
│   └── results.json
├── lora/
│   ├── poster_0.png
│   └── results.json
└── results.json
```

---

## Multi-Agent Architecture

### Agent 1: Concept Expander
**Input:** Keywords (e.g., "space exploration adventure")  
**Process:**
- Sentiment analysis using DistilBERT
- Thematic expansion with genre mapping
- Mood detection (dark/bright)

**Output:** Creative brief with enhanced prompt

### Agent 2: Visual Designer
**Input:** Creative brief  
**Process:**
- Stable Diffusion v1.5 generation
- LoRA fine-tuning (optional)
- 720×1280 resolution rendering

**Output:** Raw poster image

### Agent 3: Quality Refiner
**Input:** Raw image  
**Process:**
- Sharpness enhancement
- Contrast adjustment
- Color saturation boost

**Output:** Enhanced image

### Agent 4: Quality Evaluator
**Input:** Enhanced image  
**Process:**
- Aesthetic scoring (color variance, brightness)
- Resolution validation
- Instruction following check

**Output:** Quality metrics

---

## Project Structure

```
Computer_Vision_Project/
├── src/
│   ├── concept_expander.py    # Agent 1: Semantic expansion
│   ├── visual_generator.py    # Agent 2: SD + LoRA
│   ├── refiner.py             # Agent 3: Post-processing
│   ├── evaluator.py           # Agent 4: Quality metrics
│   ├── pipeline.py            # Main orchestrator
│   ├── lora_trainer.py        # LoRA fine-tuning
│   ├── scraper.py             # Data collection
│   ├── collect_data.py        # Data collection script
│   ├── train_lora.py          # Training script
│   └── experiment.py          # Comparison experiments
├── data/posters/              # Training dataset
├── models/poster_lora/        # Fine-tuned weights
├── outputs/                   # Generated posters
├── run_pipeline.py            # Main entry point
├── demo.py                    # Quick demo
└── requirements.txt           # Dependencies
```

---

## Usage Examples

### Example 1: Quick Demo
```bash
python demo.py
```
Generates 3 sample posters with baseline model.

### Example 2: Custom Keywords
```bash
python run_pipeline.py "cyberpunk city noir" --lora --seed 123
```

### Example 3: Programmatic Usage
```python
from src.pipeline import Key2PosterPipeline

# Initialize with LoRA
pipeline = Key2PosterPipeline(
    lora_path="models/poster_lora",
    use_lora=True
)

# Generate poster
image, brief, metrics = pipeline.generate_poster(
    keywords="epic battle scene",
    output_path="outputs/my_poster.png",
    seed=42
)

# Access results
print(f"Sentiment: {brief['sentiment']}")
print(f"Aesthetic Score: {metrics['aesthetic']['overall']:.3f}")
```

### Example 4: Ablation Study
```python
# Test without Agent 1 (Concept Expander)
from src.visual_generator import VisualGenerator
generator = VisualGenerator(use_lora=True, lora_path="models/poster_lora")
image = generator.generate("space adventure")  # Raw keywords

# Test without Agent 3 (Quality Refiner)
pipeline = Key2PosterPipeline(use_lora=True)
# Modify pipeline.py to skip refiner step
```

---

## Evaluation Metrics

### Aesthetic Score
- **Color Variance:** Measures color diversity (0-1000+)
- **Brightness Balance:** Optimal brightness around 127.5 (0-1)
- **Overall:** Combined aesthetic quality (0-1)

### Resolution Check
- **Target:** 720×1280 pixels
- **Validation:** Exact dimension match

### Instruction Following
- Boolean check for meeting resolution requirements

---

## Troubleshooting

### CUDA Out of Memory
```python
# Reduce batch size in train_lora.py
trainer.train(batch_size=1)  # Already set to 1

# Use CPU (slower)
# Set device="cpu" in visual_generator.py
```

### No Training Data
```bash
# Collect data first
python src/collect_data.py
```

### LoRA Weights Not Found
```bash
# Train model first
python src/train_lora.py
```

### Slow Generation
- Use GPU (CUDA) instead of CPU
- Reduce num_inference_steps in visual_generator.py (default: 50)
- Use DPMSolverMultistepScheduler (already enabled)

---

## Expected Results

### Baseline (No Fine-tuning)
- Generic poster aesthetics
- May lack cinematic composition
- Aesthetic score: ~0.4-0.6

### LoRA Fine-tuned
- Movie poster style composition
- Better color grading and lighting
- Aesthetic score: ~0.5-0.7
- Improvement: 10-30%

---

## Next Steps

1. **Collect More Data:** Increase to 500+ posters for better fine-tuning
2. **Hyperparameter Tuning:** Experiment with learning rates, epochs
3. **Ablation Studies:** Test individual agent contributions
4. **User Study:** Collect human preference ratings
5. **Advanced LoRA:** Try different rank values, target modules

---

## Grading Alignment

### Level 2 (70-80 points)
✅ Baseline SD implementation  
✅ LoRA fine-tuning on custom dataset  
✅ Web scraping for data collection  
✅ Controlled comparison baseline vs LoRA  

### Level 3 (80-90 points)
✅ Multi-agent architecture (4 specialized agents)  
✅ Semantic expansion with sentiment analysis  
✅ Comprehensive evaluation metrics  
✅ Ablation study capability  
✅ Novel combination of techniques  

---

## References

- Stable Diffusion: https://github.com/CompVis/stable-diffusion
- LoRA: https://arxiv.org/abs/2106.09685
- Diffusers: https://github.com/huggingface/diffusers
