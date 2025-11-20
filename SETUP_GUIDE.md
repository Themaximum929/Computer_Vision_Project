# Setup Guide for Colleagues

## ⚠️ Important: What's NOT in GitHub

The `.gitignore` currently excludes these **ESSENTIAL** directories:

```
data/          # Training data (posters)
models/        # LoRA weights
outputs/       # Generated results
*.jpg, *.png   # All images
*.pth          # Model weights
*.safetensors  # Model weights
```

## 🚨 Critical Files Needed to Run

### 1. **LoRA Models** (Required for genre-specific generation)
Location: `models/lora_{genre}/`

You need these trained LoRA models:
- `models/lora_action/lora_weights.pth`
- `models/lora_comedy/lora_weights.pth`
- `models/lora_fantasy/lora_weights.pth`
- `models/lora_horror/lora_weights.pth`
- `models/lora_romance/lora_weights.pth`
- `models/lora_scifi/lora_weights.pth`
- `models/lora_general/lora_weights.pth`

**Without these:** The app will fall back to baseline Stable Diffusion (no genre-specific styling).

### 2. **Fonts** (Required for text overlay)
Location: `fonts/cinematic/`

✅ **GOOD NEWS:** Fonts are NOT ignored and should be in the repo!

### 3. **Training Data** (Optional - only needed for retraining)
Location: `data/posters/` and `data/posters_clean/`

**Without these:** You can't retrain LoRA models, but you can still generate posters.

---

## 📦 Setup Instructions for Colleagues

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd Computer_Vision_Project
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create Required Directories
```bash
mkdir outputs
mkdir models
mkdir data
```

### Step 4: Get LoRA Models (Choose One Option)

#### Option A: Download from Shared Drive
Ask the project owner for the `models/` folder containing trained LoRA weights.

```bash
# Copy the models folder to project root
# models/
#   ├── lora_action/
#   ├── lora_comedy/
#   ├── lora_fantasy/
#   ├── lora_horror/
#   ├── lora_romance/
#   └── lora_scifi/
```

#### Option B: Train Your Own (Requires Training Data)
```bash
# 1. Get training data (posters)
python src/collect_data.py

# 2. Preprocess (remove text)
python preprocess_training_data.py

# 3. Train LoRA models by genre
python train_by_genre.py
```

### Step 5: Verify Setup
```bash
# Quick verification
python -c "from src.genre_classifier import GenreClassifier; print('✓ Imports work')"
python -c "import os; print('✓ Models exist' if os.path.exists('models/lora_action') else '✗ Models missing')"
```

---

## 🚀 Running the Application

### Option 1: Web Interface (Recommended)
```bash
python app_unified.py
```
Open: **http://localhost:7860**

### Option 2: Command Line
```bash
# With genre-specific LoRA
python run_pipeline.py "space exploration adventure" --genre-lora --add-title

# Without LoRA (baseline)
python run_pipeline.py "space exploration adventure" --add-title
```

---

## 🧪 Testing

### Test 1: Text Styling
```bash
python test_text_styles.py
```

### Test 2: OCR Text Removal
```bash
python test_text_removal.py
```

### Test 3: Full Pipeline
```bash
python test_unified.py
```

---

## 📁 What Should Be in GitHub

### ✅ Files That SHOULD Be Committed:
- All `.py` files in `src/`
- All app files (`app_*.py`)
- `requirements.txt`
- `README.md` and all `.md` documentation
- `fonts/` directory with font files
- `.gitignore`

### ❌ Files That Should NOT Be Committed:
- `data/` - Training images (too large)
- `models/` - LoRA weights (too large, ~500MB each)
- `outputs/` - Generated posters (temporary)
- `__pycache__/` - Python cache
- `*.jpg`, `*.png` - Images
- `*.pth`, `*.safetensors` - Model weights

---

## 🔧 Recommended .gitignore Update

Your current `.gitignore` is **TOO AGGRESSIVE**. Consider this update:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Data (large files)
data/posters/
data/posters_clean/
data/posters_lora/
data/products/

# Models (large files)
models/lora_*/
models/movie_lora/
models/poster_lora/*.pth
models/poster_lora/*.safetensors

# Outputs (temporary)
outputs/

# Images (except examples)
*.jpg
*.png
!poster_templates/*.jpg
!fonts/**/*

# Model weights
*.pth
*.safetensors

# Jupyter
.ipynb_checkpoints/
```

This allows:
- ✅ Template images in `poster_templates/`
- ✅ Font files in `fonts/`
- ❌ Training data and generated outputs
- ❌ Large model weights

---

## 📤 Sharing Models with Colleagues

### Option 1: Cloud Storage (Recommended)
Upload `models/` folder to:
- Google Drive
- Dropbox
- AWS S3
- OneDrive

Share the link in your README.

### Option 2: Git LFS (For GitHub)
```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "models/**/*.pth"
git lfs track "models/**/*.safetensors"

# Commit
git add .gitattributes
git add models/
git commit -m "Add LoRA models via LFS"
git push
```

**Note:** GitHub LFS has storage limits (1GB free).

---

## 🎯 Minimal Working Setup

For colleagues to run the app **without training**:

### Required:
1. ✅ Source code (`src/`, `app_*.py`)
2. ✅ Dependencies (`requirements.txt`)
3. ✅ Fonts (`fonts/cinematic/`)
4. ⚠️ LoRA models (`models/lora_*/`) - **Share separately**

### Optional:
- Training data (`data/`) - Only for retraining
- Outputs (`outputs/`) - Will be generated

---

## 📝 Add to README.md

Add this section to your README:

```markdown
## Setup for New Users

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (recommended)
- 8GB+ RAM

### Installation
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Download LoRA models from [LINK] and extract to `models/`
4. Run: `python app_unified.py`

### Without LoRA Models
The app will work without LoRA models but will use baseline Stable Diffusion (no genre-specific styling).
```

---

## ✅ Verification Checklist

Before sharing with colleagues, verify:

- [ ] `requirements.txt` is up to date
- [ ] `README.md` has setup instructions
- [ ] `fonts/` directory is in repo
- [ ] LoRA models are shared via cloud storage
- [ ] `.gitignore` doesn't block essential files
- [ ] Sample outputs are documented
- [ ] Test scripts work without training data

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "LoRA model not found"
App will fall back to baseline. Download models from shared drive.

### "Font not found"
Verify `fonts/cinematic/` exists in repo.

### CUDA out of memory
Reduce batch size or use CPU mode (slower).
