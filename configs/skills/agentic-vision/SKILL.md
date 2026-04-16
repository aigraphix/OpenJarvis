---
name: agentic-vision
description: AI-powered image analysis with zoom, annotation, and code-driven understanding
---

# Agentic Vision Skill

## Overview

Enables AI-powered image analysis through active investigation. Instead of
looking at an image once and guessing, Agentic Vision treats vision as a
**dynamic process** - analyzing, manipulating, and re-examining images through
code execution to build deeper understanding.

## How It Works: Think → Act → Observe

1. **Think**: Analyze the user's question and the image, formulate a multi-step
   plan
2. **Act**: Write and execute Python code to manipulate or analyze the image
   (crop, zoom, annotate, calculate)
3. **Observe**: Review the modified image and refine understanding before giving
   a final answer

## Capabilities

### Zoom & Inspection

- Automatically crop and zoom into fine details (serial numbers, small text,
  fine print)
- Focus on specific regions of high-resolution images
- Progressive refinement of visual understanding

### Image Annotation

- Draw bounding boxes around detected objects
- Add labels and markers directly on images
- Visual proof for counting and identification tasks

### Visual Math & Data Extraction

- Parse complex tables and charts
- Perform actual calculations instead of estimating
- Generate proper matplotlib visualizations from data

### Object Analysis

- Count objects with visual verification
- Compare visual elements systematically
- Spatial relationship understanding

## Use Cases

**Counting with Confidence**

> "How many people are in this photo?" The model draws bounding boxes around
> each person, eliminating miscounts.

**Detail Extraction**

> "What's the serial number on this device?" Crops and zooms to the label area
> for clear reading.

**Chart Analysis**

> "What are the exact values in this bar chart?" Extracts data points and can
> recreate the chart with matplotlib.

**Document Processing**

> "Summarize this document with the tables" Parses tables into structured data
> for accurate extraction.

## Code Execution Tools

The skill has access to:

- **PIL/Pillow** - Image manipulation and annotation
- **NumPy** - Numerical operations and array processing
- **Matplotlib** - Visualization and chart creation
- **OpenCV** (when available) - Advanced computer vision

## Example Workflow

```
User: "Count the red cars in this parking lot image"

Think: I need to identify and count red vehicles. I'll use code to:
  1. Detect car-shaped objects
  2. Filter by red color
  3. Draw bounding boxes for verification

Act: [Executes Python code to analyze image]
  - Uses color filtering for red hues
  - Identifies car-shaped regions
  - Draws numbered boxes around each

Observe: [Reviews annotated image]
  - Confirms 7 red cars identified
  - Verifies no false positives/negatives

Response: "I found 7 red cars in the parking lot" + annotated image
```

## Why It's Better

Traditional AI vision can hallucinate or guess when details are unclear. Agentic
Vision provides:

- **Verifiable Results** - Code produces deterministic outputs
- **Visual Proof** - Annotated images show exactly what was detected
- **Iterative Refinement** - Can zoom in and re-examine if needed
- **Accurate Calculations** - Math through code, not estimation

## Integration Notes

- Works with any uploaded image format (JPEG, PNG, WebP, etc.)
- Maximum recommended image size: 20MB
- For best results with fine details, use high-resolution images
- Code execution adds 2-5 seconds to response time

## Activation

This skill is triggered when:

- User asks to analyze, count, or measure things in an image
- User uploads an image with a question about its contents
- User asks to annotate or mark up an image
- User needs to extract data from charts, tables, or documents
