# Style Improvements - Natural Movie Poster Look

## Problem
Generated posters had artificial SD colors and didn't match real movie poster aesthetics.

## Solutions Implemented

### 1. Stronger LoRA Training
**File:** `src/train_lora.py`
- **Epochs:** 10 → 20 (more training for stronger style transfer)
- **Learning Rate:** 1e-5 → 5e-5 (faster adaptation to poster style)

### 2. More Trainable Layers
**File:** `src/lora_trainer.py`
- Added **conv_in** and **conv_out** layers (controls color/texture)
- Kept **attn1** (self-attention for style)
- Kept **attn2** (cross-attention for content)
- Result: ~5-10% trainable parameters (was ~2-5%)

### 3. Simplified Training Prompts
**File:** `src/lora_trainer.py`
- Before: `"professional movie poster, dramatic composition, cinematic lighting, [genres]"`
- After: `"movie poster, [genres]"`
- Reason: Let the model learn style from images, not from SD keywords

### 4. Simplified Generation Prompts
**File:** `src/pipeline.py`
- Before: `"cinematic poster art, [mood], [themes], original concept, creative interpretation"`
- After: `"movie poster, [keywords], [themes]"`
- Reason: Rely on LoRA's learned style instead of generic SD descriptors

### 5. Film-Like Color Grading
**File:** `src/refiner.py`
- **Desaturate:** 0.9x (reduce oversaturation)
- **Contrast:** 1.15x (add depth)
- **Color balance:** Reduce blue 5%, boost red 2% (warm tint)
- Result: More natural, film-like colors

### 6. Better Negative Prompts
**File:** `src/visual_generator.py`
- Added: `"oversaturated, neon colors, artificial colors, digital art, 3d render"`
- Removed generic terms
- Result: Actively prevents SD's artificial color palette

## How to Apply

### Option 1: Retrain from Scratch
```bash
# Delete old model
rm -rf models/poster_lora/*

# Retrain with new settings
python src/train_lora.py

# Generate with improved model
python run_pipeline.py "your keywords" --lora
```

### Option 2: Quick Test (No Retraining)
The color grading and prompt improvements work immediately:
```bash
python run_pipeline.py "your keywords" --lora
```

## Expected Results

### Before
- Oversaturated colors
- Digital/artificial look
- Generic SD aesthetic
- Neon-like tones

### After
- Natural color palette
- Film-like grading
- Movie poster aesthetic
- Warm, cinematic tones

## Technical Details

### Training Changes
```python
# More epochs for stronger style
epochs=20  # was 10

# Higher learning rate for faster adaptation
lr=5e-5  # was 1e-5

# More layers trained (color + style + content)
trainable = ["attn1", "attn2", "conv_in", "conv_out"]  # was just "attn2"
```

### Color Grading Formula
```python
# Desaturate
color *= 0.9

# Color balance (warm tint)
red_channel *= 1.02
blue_channel *= 0.95

# Contrast
contrast *= 1.15
```

## Troubleshooting

**Issue:** Still looks artificial after retraining  
**Solution:** Increase epochs to 30 or learning rate to 1e-4

**Issue:** Colors too desaturated  
**Solution:** Change `enhance(0.9)` to `enhance(0.95)` in refiner.py

**Issue:** Too warm/orange  
**Solution:** Reduce red boost from 1.02 to 1.01 in refiner.py

**Issue:** Not enough poster style  
**Solution:** Collect more training data (100+ posters) and retrain

## Quick Comparison

| Aspect | Before | After |
|--------|--------|-------|
| Training Epochs | 10 | 20 |
| Learning Rate | 1e-5 | 5e-5 |
| Trainable Layers | attn2 only | attn1+attn2+conv |
| Saturation | 1.15x | 0.9x |
| Color Balance | None | Warm tint |
| Prompt Style | SD keywords | Simple natural |

## Next Steps

1. **Retrain model** with new settings
2. **Test generation** with simple prompts
3. **Compare** old vs new outputs
4. **Fine-tune** color grading if needed
