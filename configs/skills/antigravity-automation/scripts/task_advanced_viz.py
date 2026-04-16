#!/usr/bin/env python3
"""task_advanced_viz.py

Autonomous Team Task: High-Fidelity Data Visualization

Collaborators:
- Architect: Antigravity (Data Design & SVG Generation)
- Worker: Nexus (Execution & Resource Management)

Purpose:
- Certify the inclusion of 'Advanced' visualization capabilities.
- Generate a Trend performance chart (Matplotlib/Seaborn).
- Generate a System Icon (SVG Direct Generation).
"""

from __future__ import annotations

import argparse
import time
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import svgwrite
from PIL import Image, ImageDraw, ImageFont

from lib import AutomationAgentTask

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_BASE = REPO_ROOT / "reports" / "artifacts"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Data Visualization: Advanced Mastery",
        description="Generating high-fidelity charts and SVG icons."
    )

    if not args.run:
        print("[VizMaster] Prepared mode. Use --run.")
        return 0

    task.start()

    ts = time.strftime("%Y-%m-%d-%H-%M-%S")
    out_dir = OUT_BASE / f"advanced-viz-{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Performance Trend (Matplotlib/Seaborn)
        def gen_chart():
            dates = pd.date_range(start="2026-01-20", periods=7, freq='D')
            data = {
                "Date": dates,
                "Success Rate": [90, 92, 88, 95, 98, 96, 99],
                "Throughput": [80, 82, 79, 81, 85, 83, 85]
            }
            df = pd.DataFrame(data)
            
            sns.set_theme(style="whitegrid")
            plt.figure(figsize=(10, 6))
            
            sns.lineplot(data=df, x="Date", y="Success Rate", marker="o", label="Success Rate")
            sns.lineplot(data=df, x="Date", y="Throughput", marker="s", label="Throughput")
            
            plt.title("System Performance Trend (Last 7 Days)", fontsize=14, fontweight='bold')
            plt.ylabel("Metric Value")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = out_dir / "performance_trend.png"
            plt.savefig(chart_path, dpi=300)
            plt.close()
            return str(chart_path)

        task.step("Generate Performance Trend Chart (Seaborn)", gen_chart)

        # 2. System Icon (SVG Direct Generation)
        def gen_svg():
            svg_path = out_dir / "system_cross.svg"
            dwg = svgwrite.Drawing(str(svg_path), profile='tiny', size=(100, 100))
            
            # Draw a cross icon
            dwg.add(dwg.rect(insert=(40, 10), size=(20, 80), fill='#3B82F6', rx=5, ry=5))
            dwg.add(dwg.rect(insert=(10, 40), size=(80, 20), fill='#3B82F6', rx=5, ry=5))
            
            dwg.save()
            return str(svg_path)

        task.step("Generate Clinical SVG Icon (svgwrite)", gen_svg)

        # 3. Image Manipulation (Pillow)
        def gen_composite():
            img_path = out_dir / "viz_card.png"
            # Create a simple background
            img = Image.new('RGB', (800, 400), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Simple design
            draw.rectangle([0, 0, 800, 60], fill=(37, 99, 235))
            draw.text((20, 20), "ADVANCED DATA SUMMARY", fill=(255, 255, 255))
            
            # Draw a placeholder for where the chart would go in a real composite
            draw.rectangle([50, 80, 750, 350], outline=(200, 200, 200), width=2)
            draw.text((350, 200), "[Chart Area]", fill=(150, 150, 150))
            
            img.save(img_path)
            return str(img_path)

        task.step("Generate Composite Visual Card (Pillow)", gen_composite)

        task.finish(success=True, final_result={
            "artifacts_dir": str(out_dir),
            "status": "Vivid Presence Enabled"
        })
        
        print(f"\n[VizMaster Success] Visualization artifacts: {out_dir}")
        return 0

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise

if __name__ == "__main__":
    main()
