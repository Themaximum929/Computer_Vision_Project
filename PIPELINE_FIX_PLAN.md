# Movie Poster Pipeline - Step by Step Fix

## Current Status
- ✅ Movie posters scraped (160 images with genres)
- ❌ Text removal not working well
- ❌ Text overlay too simple

## The Plan

### Phase 1: Skip Text Removal (Use Negative Prompt)
**Why:** Text removal fails 60-70% of time
**Solution:** Train on raw posters, use strong negative prompt

```bash
# Step 1: Train on raw posters (with text)
python train_by_genre.py --data-dir data/posters --epochs 20

# The negative prompt in visual_generator.py will prevent text generation
```

---

### Phase 2: Fix Text Overlay (Smart Positioning)
**Current:** Simple bottom-center placement
**Goal:** Analyze image, find best position, professional styling

**Test:**
```bash
python run_pipeline.py "space adventure" --genre-lora --add-title
```

---

### Phase 3: Test Each Component

#### Test 1: Basic Generation (No LoRA)
```bash
python run_pipeline.py "epic battle" --baseline-style
```
**Expected:** Clean image, no text

#### Test 2: With LoRA
```bash
python train_by_genre.py --data-dir data/posters --min-images 15
python run_pipeline.py "action hero" --genre-lora
```
**Expected:** Genre-styled image, no text

#### Test 3: With Text Overlay
```bash
python run_pipeline.py "space adventure" --genre-lora --add-title
```
**Expected:** Image + professionally placed text

---

## Current Issues to Fix

### Issue 1: train_by_genre.py expects metadata.json
**Location:** `data/posters/metadata.json`
**Status:** Should exist from scraping
**Fix:** Verify file exists

### Issue 2: Smart text overlay not working
**File:** `src/smart_text_overlay.py`
**Status:** Created but needs testing
**Fix:** Test and debug

### Issue 3: Pipeline imports
**File:** `src/pipeline.py`
**Status:** May have wrong imports
**Fix:** Verify all imports work

---

## Step-by-Step Execution

### Step 1: Verify Data
```bash
# Check if metadata exists
dir data\posters\metadata.json

# Check image count
dir data\posters\*.jpg | find /c ".jpg"
```

### Step 2: Train LoRA
```bash
python train_by_genre.py --data-dir data/posters --min-images 15 --epochs 10
```

### Step 3: Test Generation
```bash
# Test 1: Baseline
python run_pipeline.py "epic battle" --baseline-style

# Test 2: With LoRA
python run_pipeline.py "action hero" --genre-lora

# Test 3: With text
python run_pipeline.py "space adventure" --genre-lora --add-title
```

---

## Expected Results

### After Training:
```
models/
├── lora_action/
├── lora_drama/
├── lora_horror/
├── lora_scifi/
└── ...
```

### After Generation:
```
outputs/
└── poster.png  (720x1280, professional quality)
```

---

## Next Steps

1. ✅ Archive product poster files
2. ⏳ Verify movie poster data
3. ⏳ Train genre LoRAs
4. ⏳ Test generation pipeline
5. ⏳ Fix text overlay issues
6. ⏳ Final testing

---

## Commands Summary

```bash
# 1. Verify data
dir data\posters\metadata.json

# 2. Train (10 min on GPU)
python train_by_genre.py --data-dir data/posters --epochs 10

# 3. Generate
python run_pipeline.py "space adventure" --genre-lora --add-title

# 4. Web interface
python app_simple.py
```
