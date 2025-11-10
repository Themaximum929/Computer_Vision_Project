# Key2Poster Usage Guide

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Demo (Baseline)
```bash
python demo.py
```

## Full Workflow

### Step 1: Collect Training Data
```bash
python src/collect_data.py
```
This scrapes ~25 movie posters from IMDB to `data/posters/`

### Step 2: Train LoRA (Optional but Recommended)
```bash
python src/train_lora.py
```
Fine-tunes Stable Diffusion on collected posters (~10 epochs)

### Step 3: Run Experiments
```bash
python src/experiment.py
```
Generates comparison between baseline and LoRA models

## Individual Components

### Concept Expander
```python
from src.concept_expander import ConceptExpander

expander = ConceptExpander()
brief = expander.expand("space exploration")
print(brief['prompt'])
```

### Visual Generator
```python
from src.visual_generator import VisualGenerator

# Baseline
generator = VisualGenerator(use_lora=False)
image = generator.generate("cinematic poster")

# With LoRA
generator = VisualGenerator(lora_path="models/poster_lora", use_lora=True)
image = generator.generate("cinematic poster")
```

### Full Pipeline
```python
from src.pipeline import Key2PosterPipeline

# Baseline
pipeline = Key2PosterPipeline(use_lora=False)
image, brief, metrics = pipeline.generate_poster("dark fantasy warrior")

# With LoRA
pipeline = Key2PosterPipeline(lora_path="models/poster_lora", use_lora=True)
image, brief, metrics = pipeline.generate_poster("dark fantasy warrior")
```

## Project Structure
```
Key2Poster/
├── src/
│   ├── concept_expander.py   # Agent 1: Semantic expansion
│   ├── visual_generator.py   # Agent 2: Image generation
│   ├── evaluator.py          # Agent 3: Quality assessment
│   ├── scraper.py            # Data collection
│   ├── lora_trainer.py       # LoRA fine-tuning
│   ├── pipeline.py           # Main pipeline
│   ├── experiment.py         # Baseline vs LoRA comparison
│   ├── collect_data.py       # Data collection script
│   └── train_lora.py         # Training script
├── data/posters/             # Training data
├── models/poster_lora/       # Trained LoRA weights
├── outputs/                  # Generated posters
├── demo.py                   # Quick demo
└── requirements.txt
```

## Expected Results

### Level 2 (70-80 points)
- ✅ Working baseline SD implementation
- ✅ LoRA fine-tuning on custom dataset
- ✅ Controlled comparison experiments
- ✅ Quantitative evaluation metrics

### Level 3 (80-90 points)
- ✅ Multi-agent architecture
- ✅ Semantic expansion beyond basic prompts
- ✅ Comprehensive evaluation framework
- ✅ Ablation studies

## Troubleshooting

### Out of Memory
- Reduce batch_size in training
- Use CPU instead of GPU (slower but works)
- Reduce image resolution

### Slow Generation
- Reduce num_inference_steps (default: 30)
- Use smaller resolution (512x512 instead of 512x768)

### No Training Data
- Run `python src/collect_data.py` first
- Or manually add poster images to `data/posters/`
