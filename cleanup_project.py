"""Clean up project - Remove guide files and outdated files"""
import os
from pathlib import Path

# Files to DELETE
DELETE_FILES = [
    # Guide files
    "AESTHETIC_TEXT_SUMMARY.md",
    "CINEMATIC_TEXT_OVERLAY_GUIDE.txt",
    "ENHANCED_LORA_TRAINING.md",
    "ENHANCEMENT_QUICKSTART.md",
    "ENHANCEMENTS.md",
    "FINDINGS.md",
    "FLUX_USAGE.md",
    "FONT_SELECTION_GUIDE.txt",
    "IMPLEMENTATION_SUMMARY.md",
    "INTEGRATION_TEST_GUIDE.txt",
    "MODERN_TEXT_RENDERING.md",
    "PIPELINE_FIX_PLAN.md",
    "POSTERCRAFT_TEXT_GUIDE.md",
    "PREPROCESSING_GUIDE.md",
    "PROFESSIONAL_TEXT_OVERLAY_GUIDE.md",
    "PROJECT_COMPARISON.md",
    "QUICK_IMPLEMENTATION.md",
    "QUICK_REFERENCE.md",
    "QUICK_START_UNIFIED.md",
    "SETUP_GUIDE.md",
    "SMART_TEXT_OVERLAY.md",
    "SOLUTION_TEXT_PROBLEM.md",
    "TEXT_REMOVAL_ANALYSIS.md",
    "TEXT_RENDERING_GUIDE.txt",
    "TITLE_GENERATION.md",
    "UNIFIED_PIPELINE.md",
    "WORKFLOW.md",
    
    # Outdated test files
    "test_aesthetic_text.py",
    "test_baseline_with_text.py",
    "test_cinematic_overlay.py",
    "test_enhancements.py",
    "test_full_pipeline.py",
    "test_hybrid_removal.py",
    "test_modern_text.py",
    "test_ocr_text_removal.py",
    "test_pipeline_step_by_step.py",
    "test_pipeline.py",
    "test_poster_enhancement.py",
    "test_poster_integration.py",
    "test_professional_overlay.py",
    "test_repair.py",
    "test_template_composition.py",
    "test_text_bounds_fix.py",
    "test_text_comparison.py",
    "test_text_simple.py",
    "test_text_styles.py",
    "test_text_truncation_fix.py",
    "test_title_generator.py",
    "test_unified.py",
    "test_upscale_text_removal.py",
    
    # Outdated app files
    "app_enhanced.py",
    "app_text_overlay.py",
    "app.py",
    
    # Outdated comparison files
    "compare_all_methods.py",
    "compare_differences.py",
    "compare_text_removal_methods.py",
    "demo_modern_text.py",
    
    # Outdated pipeline files
    "run_pipeline.py",
    
    # Outdated preprocessing
    "preprocess_for_lora.py",
    "preprocess_with_ocr.py",
    
    # Outdated training
    "train_by_genre.py",
    "train_simple.py",
    
    # Outdated src files
    "src/aesthetic_text_overlay.py",
    "src/color_extractor.py",
    "src/color_palette_extractor.py",
    "src/composition_engine.py",
    "src/diffusion_text_overlay.py",
    "src/enhanced_lora_trainer.py",
    "src/enhanced_text_overlay.py",
    "src/hybrid_text_remover.py",
    "src/modern_text_overlay.py",
    "src/pipeline_modern.py",
    "src/poster_composer.py",
    "src/poster_text_styles.py",
    "src/postercraft_pipeline.py",
    "src/product_scraper.py",
    "src/product_text_styles.py",
    "src/professional_text_overlay.py",
    "src/template_engine.py",
    "src/template_manager.py",
    "src/title_generator.py",
    "src/unified_pipeline.py",
]

# Files to KEEP (essential)
KEEP_FILES = [
    "README.md",
    "FLUX_ENHANCEMENTS.md",
    "requirements.txt",
    ".gitignore",
    ".gitattributes",
    "clear_gpu.py",
    
    # Essential apps
    "app_simple.py",
    "app_unified.py",
    
    # Essential pipelines
    "run_pipeline_flux.py",
    
    # Essential preprocessing
    "preprocess_training_data.py",
    
    # Essential tests
    "test_flux.py",
    "test_flux_text_generation.py",
    "test_flux_enhanced.py",
    "test_flux_text_generation_enhanced.py",
    
    # Essential src files (pipeline, training, flux, text removal)
    "src/__init__.py",
    "src/pipeline.py",
    "src/concept_expander.py",
    "src/genre_classifier.py",
    "src/visual_generator.py",
    "src/visual_generator_flux.py",
    "src/text_remover.py",
    "src/aggressive_text_remover.py",
    "src/refiner.py",
    "src/super_resolution.py",
    "src/evaluator.py",
    "src/flux_text_inpainting.py",
    "src/enhanced_flux_text.py",
    "src/lora_trainer.py",
    "src/train_lora.py",
    "src/collect_data.py",
    "src/scraper.py",
]

def cleanup():
    base_dir = Path(__file__).parent
    deleted = []
    errors = []
    
    print("="*60)
    print("PROJECT CLEANUP")
    print("="*60)
    
    for file_path in DELETE_FILES:
        full_path = base_dir / file_path
        if full_path.exists():
            try:
                os.remove(full_path)
                deleted.append(file_path)
                print(f"[OK] Deleted: {file_path}")
            except Exception as e:
                errors.append((file_path, str(e)))
                print(f"[ERROR] Error deleting {file_path}: {e}")
        else:
            print(f"[SKIP] Not found: {file_path}")
    
    print("\n" + "="*60)
    print(f"SUMMARY: Deleted {len(deleted)} files")
    if errors:
        print(f"Errors: {len(errors)}")
        for file, err in errors:
            print(f"  - {file}: {err}")
    print("="*60)
    
    print("\nKept essential files:")
    for file in KEEP_FILES[:10]:
        print(f"  [KEEP] {file}")
    print(f"  ... and {len(KEEP_FILES)-10} more")

if __name__ == "__main__":
    cleanup()
