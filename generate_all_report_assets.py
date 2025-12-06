"""
Master Script: Generate All Report Assets
Runs evaluation, creates charts, and generates diagrams
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"✗ {description} failed")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return False
    
    return True

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     LAYOUT & COMPOSITION REPORT ASSET GENERATOR              ║
║     Generates all charts, diagrams, and evaluation data      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create output directory
    os.makedirs("outputs/evaluation", exist_ok=True)
    
    # Step 1: Generate demo evaluation data
    print("\n[Step 1/3] Generating evaluation data...")
    if not run_command("python demo_evaluation.py", "Demo Evaluation Data Generation"):
        print("\n⚠ Warning: Demo data generation failed. Continuing anyway...")
    
    # Step 2: Generate evaluation charts
    print("\n[Step 2/3] Generating evaluation charts...")
    if not run_command("python visualize_evaluation.py", "Evaluation Charts Generation"):
        print("\n⚠ Warning: Chart generation failed. Check if demo_evaluation.py ran successfully.")
    
    # Step 3: Generate layout diagrams
    print("\n[Step 3/3] Generating layout diagrams...")
    if not run_command("python generate_layout_diagrams.py", "Layout Diagrams Generation"):
        print("\n⚠ Warning: Diagram generation failed.")
    
    # Summary
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    
    # Check what was generated
    expected_files = [
        "outputs/evaluation/metrics_comparison.json",
        "outputs/evaluation/performance_comparison.json",
        "outputs/evaluation/evaluation_charts.png",
        "outputs/evaluation/architecture_diagram.png",
        "outputs/evaluation/layout_patterns.png",
        "outputs/evaluation/pipeline_flow.png",
        "outputs/evaluation/constraint_diagram.png"
    ]
    
    print("\nGenerated Files:")
    for file in expected_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✓ {file} ({size:,} bytes)")
        else:
            print(f"  ✗ {file} (missing)")
    
    # Instructions
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review generated assets in outputs/evaluation/

2. For your report, use:
   - REPORT_LAYOUT_SECTION.md (main content)
   - evaluation_charts.png (comparative results)
   - architecture_diagram.png (system overview)
   - layout_patterns.png (template visualization)
   - pipeline_flow.png (PosterO pipeline)
   - constraint_diagram.png (design principles)

3. Copy REPORT_LAYOUT_SECTION.md to your report:
   cat REPORT_LAYOUT_SECTION.md >> YOUR_REPORT.md

4. Include images in your report:
   ![Evaluation](outputs/evaluation/evaluation_charts.png)
   ![Architecture](outputs/evaluation/architecture_diagram.png)

5. For full evaluation with actual posters (requires GPU):
   python run_comparative_evaluation.py
   python visualize_evaluation.py
    """)
    
    print("="*60)
    print("✓ All assets generated successfully!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        sys.exit(1)
