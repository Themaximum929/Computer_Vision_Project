# Using FLUX with Key2Poster Pipeline

## Quick Start

### Basic FLUX Generation
```bash
python run_pipeline.py "cyberpunk neon city" --use-flux
```

### FLUX with All Features
```bash
python run_pipeline.py "space adventure" --use-flux --add-title --aggressive-text-removal
```

### FLUX with Genre Detection
```bash
python run_pipeline.py "dark horror mansion" --use-flux --genre-lora --add-title
```

Note: Genre detection works, but LoRA weights won't be applied when using FLUX (FLUX doesn't support LoRA yet).

---

## Command Options

| Option | Description |
|--------|-------------|
| `--use-flux` | Use FLUX.1 instead of Stable Diffusion v1.5 |
| `--flux-model` | Specify FLUX model (default: FLUX.1-schnell) |
| `--add-title` | Add styled title overlay |
| `--genre-lora` | Auto-detect genre for text styling |
| `--aggressive-text-removal` | 3-pass text removal |
| `--seed 42` | Reproducible generation |

---

## Examples

### Fast Generation (FLUX.1-schnell)
```bash
python run_pipeline.py "epic battle scene" --use-flux
```

### High Quality (FLUX.1-dev)
```bash
python run_pipeline.py "romantic sunset" --use-flux --flux-model black-forest-labs/FLUX.1-dev
```

### Complete Pipeline
```bash
python run_pipeline.py "horror mansion" \
  --use-flux \
  --add-title \
  --aggressive-text-removal \
  --seed 42 \
  --output outputs/horror_poster.png
```

---

## Comparison

### SD v1.5 (Default)
```bash
python run_pipeline.py "space adventure" --genre-lora --add-title
```
- Speed: ~15s
- Quality: Good
- LoRA: ✅ Supported

### FLUX.1 (New)
```bash
python run_pipeline.py "space adventure" --use-flux --add-title
```
- Speed: ~8s
- Quality: Better
- LoRA: ❌ Not supported

---

## Authentication

FLUX.1 requires HuggingFace authentication:

```bash
pip install huggingface_hub
huggingface-cli login
```

Then accept license at: https://huggingface.co/black-forest-labs/FLUX.1-schnell

---

## Troubleshooting

### "Access to model is restricted"
→ Run `huggingface-cli login` and accept model license

### Out of Memory
→ FLUX requires 8GB+ VRAM (vs 4GB for SD v1.5)

### Slow Generation
→ Use FLUX.1-schnell (4 steps) instead of FLUX.1-dev (20+ steps)
