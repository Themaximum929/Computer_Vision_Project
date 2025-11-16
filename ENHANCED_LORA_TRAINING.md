# Enhanced LoRA Training Guide - Artifact Prevention

## Overview
This enhanced LoRA training system prevents text artifacts through:
1. Clean text-free datasets
2. Conservative training parameters
3. Two-stage training approach
4. Rich style-focused captions

---

## Stage 1: Background & Mood Training

### Data Preparation
```bash
# 1. Collect posters
python src/collect_data.py

# 2. Remove ALL text aggressively
python preprocess_training_data.py --iterations 5

# 3. Verify no text remains
# Manually inspect data/posters_clean/
```

### Training Parameters (Conservative)
- **Rank**: 4-8 (low rank prevents overfitting)
- **Learning Rate**: 1e-5 (very low to prevent artifacts)
- **Dropout**: 0.05-0.1 (regularization)
- **Epochs**: 15 (stage 1)
- **Gradient Clipping**: 0.5 (conservative)

### Caption Format
```
movie poster style, {genre} genre, {style descriptors}, 
professional photography, no text, clean background
```

**Example Captions:**
- "movie poster style, action genre, dynamic cinematic composition, intense dramatic lighting, bold color palette, no text"
- "movie poster style, horror genre, dark moody atmosphere, ominous lighting, desaturated colors, no text"

### Training Command
```bash
python src/enhanced_lora_trainer.py \
  --data-dir data/posters_clean \
  --genre action \
  --stage 1 \
  --rank 4 \
  --lr 1e-5 \
  --dropout 0.08
```

---

## Stage 2: Optional Text Overlay (Advanced)

**Note**: Only proceed if Stage 1 produces clean results.

### Synthetic Text Overlay
- Generate clean backgrounds from Stage 1
- Add synthetic text using PIL/ImageDraw
- Train on text placement (NOT text generation)

---

## Artifact Prevention Checklist

### ✅ Dataset Quality
- [ ] All text removed from training images
- [ ] No watermarks or logos
- [ ] Clean backgrounds verified
- [ ] Minimum 50 images per genre

### ✅ Training Parameters
- [ ] Rank ≤ 8
- [ ] Learning rate ≤ 1e-5
- [ ] Dropout 0.05-0.1
- [ ] Conservative gradient clipping

### ✅ Caption Quality
- [ ] No text content in captions
- [ ] Focus on style/atmosphere/mood
- [ ] Genre-specific descriptors
- [ ] Consistent format

### ✅ Evaluation
- [ ] Test generation every 5 epochs
- [ ] Check for text artifacts
- [ ] Verify style consistency
- [ ] Compare with baseline

---

## Troubleshooting

### Problem: Text artifacts appear
**Solution**: 
- Reduce learning rate to 5e-6
- Reduce rank to 4
- Increase dropout to 0.1
- Re-clean dataset

### Problem: Overfitting
**Solution**:
- Reduce epochs
- Increase dropout
- Add more training data

### Problem: Style not captured
**Solution**:
- Increase rank to 8
- Increase epochs to 20
- Improve caption quality

---

## Best Practices

1. **Start Conservative**: Use rank=4, lr=1e-5
2. **Evaluate Often**: Check every 5 epochs
3. **Clean Data**: Spend time on preprocessing
4. **Rich Captions**: Focus on style, not content
5. **Gradual Tuning**: Adjust one parameter at a time

---

## Expected Results

**Good LoRA**:
- Clean backgrounds
- Genre-appropriate style
- No text artifacts
- Consistent quality

**Bad LoRA**:
- Broken text fragments
- Watermark-like artifacts
- Inconsistent style
- Overfitted to specific images

---

## Commands Summary

```bash
# Full workflow
python src/collect_data.py
python preprocess_training_data.py --iterations 5
python src/enhanced_lora_trainer.py --genre action --stage 1
python run_pipeline.py "epic battle" --genre-lora --add-title
```
