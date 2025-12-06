# Layout and Composition Documentation

## 📚 Document Overview

This directory contains comprehensive documentation for the Layout and Composition system of the Key2Poster project. The documentation is organized into multiple files for different audiences and purposes.

## 🗂️ Document Structure

```
Layout Documentation
├── REPORT_LAYOUT_SECTION.md          ⭐ Main report section (use this for your report)
├── LAYOUT_COMPOSITION_REPORT.md      📖 Full technical report
├── LAYOUT_SUMMARY.md                 📋 Executive summary
├── LAYOUT_QUICK_REFERENCE.md         🎯 Quick reference card
├── EVALUATION_GUIDE.md               📊 Evaluation system guide
└── LAYOUT_DOCS_README.md             📚 This file
```

## 📄 Document Descriptions

### 1. REPORT_LAYOUT_SECTION.md ⭐ **[USE THIS FOR YOUR REPORT]**
**Purpose**: Polished section ready for direct inclusion in your technical report  
**Audience**: Academic reviewers, instructors  
**Length**: ~2,500 words  
**Contains**:
- Overview and motivation
- Technical implementation of all 3 methods
- Comparative evaluation with results table
- Visualization charts
- Conclusion and references

**When to use**: Copy this directly into your report document

---

### 2. LAYOUT_COMPOSITION_REPORT.md
**Purpose**: Comprehensive technical documentation  
**Audience**: Developers, researchers  
**Length**: ~3,500 words  
**Contains**:
- Detailed architecture diagrams
- Implementation code snippets
- Design principles explanation
- Performance analysis
- Future improvements

**When to use**: Deep dive into technical details, development reference

---

### 3. LAYOUT_SUMMARY.md
**Purpose**: Executive summary for quick understanding  
**Audience**: Project managers, stakeholders  
**Length**: ~1,500 words  
**Contains**:
- High-level comparison table
- Evolution timeline
- Key innovations
- Recommendations by use case

**When to use**: Presentations, project overviews, quick briefings

---

### 4. LAYOUT_QUICK_REFERENCE.md
**Purpose**: Cheat sheet for developers  
**Audience**: Developers using the system  
**Length**: ~800 words  
**Contains**:
- Code snippets for each mode
- Visual layout patterns
- Decision tree
- Common issues and solutions

**When to use**: Daily development, troubleshooting, quick lookup

---

### 5. EVALUATION_GUIDE.md
**Purpose**: Instructions for running evaluations  
**Audience**: Researchers, QA testers  
**Length**: ~1,200 words  
**Contains**:
- Metric definitions
- Evaluation scripts usage
- Expected results
- Customization guide

**When to use**: Running comparative evaluations, adding new metrics

---

## 🚀 Quick Start

### For Report Writing
```bash
# Copy the main section to your report
cat REPORT_LAYOUT_SECTION.md >> YOUR_REPORT.md
```

### For Development
```bash
# Quick reference while coding
less LAYOUT_QUICK_REFERENCE.md
```

### For Evaluation
```bash
# Run evaluation and generate charts
python demo_evaluation.py
python visualize_evaluation.py
# Then see EVALUATION_GUIDE.md for interpretation
```

## 📊 Evaluation System

### Quick Demo (2 minutes, no GPU)
```bash
python demo_evaluation.py
python visualize_evaluation.py
```

### Full Evaluation (30 minutes, requires GPU)
```bash
python run_comparative_evaluation.py
python visualize_evaluation.py
```

### Output Files
```
outputs/evaluation/
├── metrics_comparison.json          # Raw metrics data
├── performance_comparison.json      # Timing and memory
├── evaluation_charts.png            # 6-panel visualization
├── template_*.png                   # Generated posters
├── layoutgan_*.png
└── postero_*.png
```

## 🎯 Key Results Summary

| Method | Quality | Speed | Best For |
|--------|---------|-------|----------|
| **Template** | 0.75 | 10s ⚡⚡⚡ | Batch production |
| **LayoutGAN** | 0.78 | 19s ⚡⚡ | Varied content |
| **PosterO** | 0.84 | 28s ⚡ | Premium quality |

**Winner by Category**:
- 🏆 Quality: PosterO (+13% vs Template)
- 🏆 Speed: Template (3× faster than PosterO)
- 🏆 Balance: LayoutGAN (middle ground)

## 📈 Visualization

All documents reference the same evaluation charts:

![Evaluation Charts](outputs/evaluation/evaluation_charts.png)

Generate charts with:
```bash
python visualize_evaluation.py
```

## 🔗 Related Files

### Source Code
```
src/
├── template_generator.py         # Template Mode implementation
├── clg_lo_layout.py             # LayoutGAN Mode (CLG-LO)
├── pipeline_postero.py          # PosterO Mode
├── comparative_evaluator.py     # Evaluation metrics
├── text_layout.py               # Collision resolution
└── color_contrast.py            # Contrast adjustment
```

### Evaluation Scripts
```
run_comparative_evaluation.py     # Full evaluation
demo_evaluation.py                # Quick demo
visualize_evaluation.py           # Chart generation
```

### Main Documentation
```
README.md                         # Project overview
TECHNICAL_REPORT.md              # Full technical report
PIPELINE_CHANGES.md              # Pipeline evolution
```

## 🎓 Academic Context

This work builds upon:
- **PosterO** (CVPR 2025): Content-aware AI layout
- **LayoutGAN** (CVPR 2019): Generative layout design
- **FLUX.1** (2024): High-quality image generation

Our contributions:
1. **CLG-LO**: Constrained Latent Optimization for LayoutGAN
2. **Three-tier architecture**: Speed-quality trade-off system
3. **Comparative evaluation**: Quantitative metrics for layout quality
4. **POE API integration**: Cloud-based LLM for layout generation

## 📝 Citation

If using this work, please cite:

```bibtex
@misc{key2poster_layout,
  title={Three-Tier Layout Architecture for AI Poster Generation},
  author={Your Name},
  year={2024},
  note={Template vs LayoutGAN vs PosterO comparative study}
}
```

## 🤝 Contributing

To add new documentation:

1. **New metric**: Edit `src/comparative_evaluator.py`
2. **New visualization**: Edit `visualize_evaluation.py`
3. **New layout pattern**: Edit `src/template_generator.py`
4. **Update docs**: Maintain consistency across all 5 documents

## 📧 Support

For questions about:
- **Report writing**: See REPORT_LAYOUT_SECTION.md
- **Technical details**: See LAYOUT_COMPOSITION_REPORT.md
- **Quick usage**: See LAYOUT_QUICK_REFERENCE.md
- **Evaluation**: See EVALUATION_GUIDE.md

## ✅ Checklist for Report Submission

- [ ] Copy REPORT_LAYOUT_SECTION.md to your report
- [ ] Run evaluation: `python demo_evaluation.py`
- [ ] Generate charts: `python visualize_evaluation.py`
- [ ] Include evaluation_charts.png in report
- [ ] Verify all metrics in results table
- [ ] Add references section
- [ ] Proofread for consistency

## 🎨 Visual Assets

All documents reference these visual elements:

1. **Architecture Diagram**: Three-tier system overview
2. **Flow Diagrams**: Pipeline flows for each method
3. **Layout Patterns**: 6 template types visualization
4. **Evaluation Charts**: 6-panel comparative analysis
5. **Constraint Diagrams**: Rule of thirds, golden ratio

Generate all visuals with:
```bash
python visualize_evaluation.py  # Generates evaluation_charts.png
```

## 🔄 Update Workflow

When updating the layout system:

1. **Code changes**: Update source files
2. **Run evaluation**: `python run_comparative_evaluation.py`
3. **Update metrics**: Verify results in JSON files
4. **Update docs**: Maintain consistency across all 5 documents
5. **Regenerate charts**: `python visualize_evaluation.py`
6. **Commit all**: Code + docs + charts

---

**Last Updated**: 2024  
**Version**: 4.0 (PosterO Integration)  
**Status**: Production Ready ✅
