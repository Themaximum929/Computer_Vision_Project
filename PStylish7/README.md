# PStylish7 Guideline

## Introduction
PStylish7 is a dataset designed to facilitate the few-shot learning research in the field of **generalized content-aware layout generation**.
- Statistics: It contains 152 few-shot learning samples and 100 test images.
- Generalized in what?
    - Diverse purposes: It contains posters covering 7 purposes, including cultural education, merchandising display, public advocacy, public safety, social-media interaction, entertainment marketing, and artwork exhibition.
    - Diverse entities: It contains layout elements covering 8 types, including logo (L), underlay (U), embellishment (E), and text (T-G, general), along with four text variants (T-V, vertical; T-R, rotated; T-S, ellipse; T-C, complex curve).
    
## File Structure
```
└── PStylish7
    ├── chinese-poem
    │   ├── predm_zs
    │   │   ├── features
    │   │   ├── design_intent_bbox_test.pt
    │   │   └── design_intent_bbox_train.pt
    │   ├── test.csv
    │   └── train.csv
    ├── food-menu
    │   └── ... (as above)
    ├── kind-animals
    │   └── ... (as above)
    ├── london-subway
    │   └── ... (as above)
    ├── motivational-quote
    │   └── ... (as above)
    ├── movie-poster
    │   └── ... (as above)
    └── travel-vintage
        └── ... (as above)
```

## Category
| Name (Same as in manuscript) | Directory | Description |
| --- |
| Poem | chinese-poem | For cultural education |
| Menu | food-menu | For merchandising display |
| Animal | kind-animals | For public advocacy |
| Metro | london-subway | For public safety |
| Instagram | motivational-quote | For social-media interaction |
| Movie | movie-poster | For entertainment marketing |
| Paint | travel-vintage | For artwork exhibition |