# Data Directory

This directory contains training data for LoRA model training.

## Structure

```
data/
├── posters/              # Raw scraped posters (with text)
├── posters_clean/        # Preprocessed posters (text removed)
├── posters_by_genre/     # Organized by genre
│   ├── action/
│   ├── comedy/
│   ├── fantasy/
│   ├── horror/
│   ├── romance/
│   └── scifi/
└── posters_lora/         # Final training set
```

## Data NOT Included

**Training data is NOT included in the repository due to:**
- Large size (~2GB+)
- Copyright considerations
- Not required for running the app

## Collecting Your Own Data

### Option 1: Scrape from IMDB
```bash
python src/collect_data.py
```

This will:
1. Scrape movie posters from IMDB
2. Download with genre labels
3. Save to `data/posters/`

### Option 2: Use Your Own Images
Place poster images in `data/posters/` with naming format:
```
{genre}_{title}_{id}.jpg
```

Example: `action_dark_knight_tt0468569.jpg`

## Preprocessing

Remove text from posters before training:
```bash
python preprocess_training_data.py
```

Output: `data/posters_clean/`

## Data Requirements

- **Minimum:** 50 images per genre
- **Recommended:** 100+ images per genre
- **Format:** JPG or PNG
- **Resolution:** 512x768 or higher
- **Quality:** High-quality movie posters

## Training Without Data

You can use the app without training data if you have pre-trained LoRA models.
