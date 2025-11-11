# Key2Poster Workflow Diagram

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     KEY2POSTER PIPELINE                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA PREPARATION                                       │
└─────────────────────────────────────────────────────────────────┘

    [IMDB Website]
          │
          │ Web Scraping
          ▼
    ┌──────────────┐
    │   Scraper    │ ──► Extract posters + genres
    │   Agent      │
    └──────────────┘
          │
          ▼
    [data/posters/]
    - 50+ movie posters
    - Genre metadata
    - 512×768 resolution


┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: MODEL TRAINING                                         │
└─────────────────────────────────────────────────────────────────┘

    [Stable Diffusion v1.5]
          │
          │ Load Base Model
          ▼
    ┌──────────────┐
    │ LoRA Trainer │ ──► Fine-tune cross-attention
    │              │     - Epochs: 10
    └──────────────┘     - LR: 1e-5
          │              - Batch: 1
          │
          ▼
    [models/poster_lora/]
    - lora_weights.pth
    - adapter_config.json


┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: POSTER GENERATION (Multi-Agent System)                 │
└─────────────────────────────────────────────────────────────────┘

    [User Input: "space exploration adventure"]
          │
          ▼
    ┌──────────────────────────────────────────────────────────┐
    │ AGENT 1: Concept Expander                                │
    │ ─────────────────────────                                │
    │ • Sentiment Analysis (DistilBERT)                        │
    │ • Thematic Expansion (Genre Mapping)                     │
    │ • Mood Detection (Dark/Bright)                           │
    └──────────────────────────────────────────────────────────┘
          │
          │ Creative Brief
          │ {sentiment, mood, themes, enhanced_prompt}
          ▼
    ┌──────────────────────────────────────────────────────────┐
    │ AGENT 2: Visual Designer                                 │
    │ ────────────────────────                                 │
    │ • Stable Diffusion v1.5                                  │
    │ • LoRA Fine-tuning (Optional)                            │
    │ • DPM Solver Scheduler                                   │
    │ • 720×1280 Resolution                                    │
    └──────────────────────────────────────────────────────────┘
          │
          │ Raw Poster Image
          ▼
    ┌──────────────────────────────────────────────────────────┐
    │ AGENT 3: Quality Refiner                                 │
    │ ────────────────────────                                 │
    │ • Sharpness Enhancement (1.2x)                           │
    │ • Contrast Adjustment (1.1x)                             │
    │ • Color Saturation (1.15x)                               │
    └──────────────────────────────────────────────────────────┘
          │
          │ Enhanced Image
          ▼
    ┌──────────────────────────────────────────────────────────┐
    │ AGENT 4: Quality Evaluator                               │
    │ ──────────────────────────                               │
    │ • Aesthetic Score (Color + Brightness)                   │
    │ • Resolution Check (720×1280)                            │
    │ • Instruction Following Validation                       │
    └──────────────────────────────────────────────────────────┘
          │
          │ Quality Metrics
          ▼
    [outputs/poster.png]
    + Evaluation Report


┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: EVALUATION & COMPARISON                                │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐         ┌─────────────────┐
    │ Baseline Model  │         │  LoRA Model     │
    │ (SD v1.5)       │         │  (Fine-tuned)   │
    └─────────────────┘         └─────────────────┘
            │                           │
            │ Generate 5 posters        │ Generate 5 posters
            ▼                           ▼
    [baseline/poster_*.png]     [lora/poster_*.png]
            │                           │
            └───────────┬───────────────┘
                        │
                        ▼
                ┌───────────────┐
                │  Comparison   │
                │  Metrics      │
                └───────────────┘
                        │
                        ▼
            [results.json]
            - Aesthetic scores
            - Resolution checks
            - Time comparisons
            - Improvement %


┌─────────────────────────────────────────────────────────────────┐
│ AGENT COMMUNICATION PROTOCOL                                    │
└─────────────────────────────────────────────────────────────────┘

Agent 1 → Agent 2:
    {
        "keywords": "space exploration adventure",
        "sentiment": "POSITIVE",
        "confidence": 0.95,
        "mood": "bright, vibrant, uplifting",
        "themes": "cosmic, stars, nebula, vast, dynamic, exciting",
        "prompt": "space exploration adventure, bright, vibrant..."
    }

Agent 2 → Agent 3:
    PIL.Image (720×1280 RGB)

Agent 3 → Agent 4:
    PIL.Image (720×1280 RGB, enhanced)

Agent 4 → Output:
    {
        "aesthetic": {
            "color_variance": 2500.5,
            "brightness_balance": 0.85,
            "overall": 0.65
        },
        "resolution": {
            "width": 720,
            "height": 1280,
            "meets_target": true
        },
        "instruction_following": true
    }


┌─────────────────────────────────────────────────────────────────┐
│ USAGE PATTERNS                                                  │
└─────────────────────────────────────────────────────────────────┘

Pattern 1: Quick Generation
    python run_pipeline.py "keywords" --lora

Pattern 2: Batch Processing
    python -c "from src.pipeline import Key2PosterPipeline; \
               pipeline = Key2PosterPipeline(use_lora=True); \
               pipeline.batch_generate(['k1', 'k2', 'k3'])"

Pattern 3: Comparison Study
    python src/experiment.py

Pattern 4: Full Pipeline
    python run_full_pipeline.py --test-mode


┌─────────────────────────────────────────────────────────────────┐
│ FILE STRUCTURE                                                  │
└─────────────────────────────────────────────────────────────────┘

Computer_Vision_Project/
│
├── src/                          # Core modules
│   ├── concept_expander.py       # Agent 1
│   ├── visual_generator.py       # Agent 2
│   ├── refiner.py                # Agent 3
│   ├── evaluator.py              # Agent 4
│   ├── pipeline.py               # Orchestrator
│   ├── lora_trainer.py           # Training
│   ├── scraper.py                # Data collection
│   ├── collect_data.py           # Collection script
│   ├── train_lora.py             # Training script
│   └── experiment.py             # Experiments
│
├── data/                         # Training data
│   └── posters/
│       ├── *.jpg                 # Poster images
│       └── metadata.json         # Genre labels
│
├── models/                       # Trained models
│   └── poster_lora/
│       ├── lora_weights.pth      # Fine-tuned weights
│       └── adapter_config.json   # Config
│
├── outputs/                      # Generated posters
│   ├── baseline/                 # Baseline results
│   ├── lora/                     # LoRA results
│   └── comparison/               # Comparison study
│
├── run_pipeline.py               # Main entry point
├── run_full_pipeline.py          # Complete automation
├── test_pipeline.py              # Test suite
├── demo.py                       # Quick demo
│
└── docs/
    ├── PIPELINE_GUIDE.md         # Full documentation
    ├── QUICKSTART_PIPELINE.md    # Quick start
    └── WORKFLOW.md               # This file


┌─────────────────────────────────────────────────────────────────┐
│ TECHNICAL SPECIFICATIONS                                        │
└─────────────────────────────────────────────────────────────────┘

Base Model:
    - Stable Diffusion v1.5 (runwayml/stable-diffusion-v1-5)
    - 860M parameters
    - 512×512 native resolution (upscaled to 720×1280)

LoRA Configuration:
    - Target: Cross-attention layers (attn2)
    - Trainable: ~2-5% of total parameters
    - Rank: 4 (implicit)
    - Learning Rate: 1e-5
    - Optimizer: AdamW

Training Dataset:
    - Size: 50+ movie/anime posters
    - Resolution: 512×768 (training), 720×1280 (inference)
    - Genres: Action, Drama, Horror, Sci-Fi, Romance, Comedy, Fantasy, Anime
    - Source: IMDB

Generation Parameters:
    - Inference Steps: 50
    - Guidance Scale: 7.5
    - Scheduler: DPMSolverMultistepScheduler
    - Negative Prompt: Anti-text, anti-distortion

Evaluation Metrics:
    - Aesthetic Score: 0-1 (color variance + brightness)
    - Resolution: 720×1280 validation
    - Instruction Following: Boolean check


┌─────────────────────────────────────────────────────────────────┐
│ PERFORMANCE BENCHMARKS                                          │
└─────────────────────────────────────────────────────────────────┘

Data Collection:
    - Time: ~2 minutes for 50 posters
    - Success Rate: ~90% (network dependent)

Training:
    - GPU (RTX 3090): ~10-15 minutes
    - GPU (RTX 2060): ~20-30 minutes
    - CPU: Not recommended (hours)

Generation:
    - GPU: ~10-15 seconds per poster
    - CPU: ~2-3 minutes per poster

Quality Improvement:
    - Baseline Aesthetic: 0.4-0.6
    - LoRA Aesthetic: 0.5-0.7
    - Average Improvement: 10-30%
```
