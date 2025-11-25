# Key2Poster Project Structure

Clean, organized structure with essential files only.

## Core Files

### Documentation
- `README.md` - Main project documentation
- `FLUX_ENHANCEMENTS.md` - FLUX text generation enhancements
- `requirements.txt` - Python dependencies

### Applications
- `app_simple.py` - Simple Gradio UI
- `app_unified.py` - Full-featured Gradio UI (recommended)

### Pipeline Scripts
- `run_pipeline_flux.py` - CLI for FLUX generation
- `preprocess_training_data.py` - Text removal preprocessing

### Testing
- `test_flux.py` - Basic FLUX tests
- `test_flux_text_generation.py` - FLUX text generation tests
- `test_flux_enhanced.py` - Enhanced FLUX tests
- `test_flux_text_generation_enhanced.py` - Full comparison tests

### Utilities
- `clear_gpu.py` - GPU memory cleanup
- `cleanup_project.py` - Project cleanup script

## Source Code (`src/`)

### Core Pipeline
- `pipeline.py` - Main orchestrator (7 agents)
- `concept_expander.py` - Agent 1: Sentiment analysis
- `genre_classifier.py` - Agent 2: Genre detection
- `visual_generator.py` - Agent 3: SD 1.5 generator
- `visual_generator_flux.py` - Agent 3: FLUX generator
- `text_remover.py` - Agent 4: Basic text removal
- `aggressive_text_remover.py` - Agent 4: Advanced text removal
- `refiner.py` - Agent 5: Quality enhancement
- `super_resolution.py` - Agent 5: Super-resolution
- `evaluator.py` - Agent 7: Quality evaluation

### FLUX Text Generation
- `flux_text_inpainting.py` - FLUX text overlay
- `enhanced_flux_text.py` - Enhanced FLUX with artifact removal

### Training & Data
- `lora_trainer.py` - LoRA training module
- `train_lora.py` - LoRA training script
- `collect_data.py` - Data collection
- `scraper.py` - Web scraping utilities

## Data Structure

```
data/
├── posters/              # Original scraped posters
├── posters_clean/        # Text-removed posters
├── posters_by_genre/     # Genre-organized posters
└── posters_lora/         # LoRA training data
```

## Models

```
models/
├── lora_action/          # Action genre LoRA
├── lora_comedy/          # Comedy genre LoRA
├── lora_fantasy/         # Fantasy genre LoRA
├── lora_horror/          # Horror genre LoRA
├── lora_romance/         # Romance genre LoRA
├── lora_general/         # General LoRA
└── poster_lora/          # Main poster LoRA
```

## Fonts

```
fonts/cinematic/          # 25+ cinematic fonts
```

## Outputs

```
outputs/
├── flux_enhanced_comparison/  # Enhanced FLUX tests
├── flux_text_test/            # FLUX text tests
└── [various test outputs]
```

## Quick Start

### 1. Generate Poster (Web UI)
```bash
python app_unified.py
```

### 2. Generate Poster (CLI)
```bash
python run_pipeline_flux.py "cyberpunk city" --enhanced-flux --style neon
```

### 3. Train LoRA
```bash
python preprocess_training_data.py
python src/train_lora.py --data-dir data/posters_clean
```

### 4. Test Enhancements
```bash
python test_flux_text_generation_enhanced.py
```

## Workflow

1. **Data Collection** → `src/collect_data.py`
2. **Preprocessing** → `preprocess_training_data.py`
3. **Training** → `src/train_lora.py`
4. **Generation** → `app_unified.py` or `run_pipeline_flux.py`

## Key Features

- 7-agent multi-agent system
- Genre-specific LoRA models
- FLUX text generation with artifact removal
- 5 style presets (cinematic, minimalist, neon, dark, vintage)
- 8 genre text styles
- Aggressive text removal
- Super-resolution enhancement
- Quality evaluation

## Removed Files

Cleaned up 81+ outdated files:
- 26 guide/documentation files
- 24 outdated test files
- 3 outdated app files
- 14 outdated src files
- Various comparison and demo files

## Essential Dependencies

- PyTorch
- Diffusers (FLUX, Stable Diffusion)
- Transformers (OCR, text models)
- Gradio (Web UI)
- PIL/Pillow (Image processing)
- See `requirements.txt` for full list
