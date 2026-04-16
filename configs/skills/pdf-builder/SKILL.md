---
name: ai-pdf-builder
description: Generate professional PDFs from Markdown using Pandoc and LaTeX. Creates whitepapers, term sheets, memos, agreements, SAFEs, NDAs, and more. Use when someone wants to create a professional PDF document from text or markdown content.
version: 1.0.0
author: Next Frontier
metadata:
  nexus:
    requires:
      bins: []
    optional:
      bins:
        - pandoc
        - pdflatex
---

# AI PDF Builder

Generate professional PDFs from Markdown. Perfect for:

- Whitepapers & Litepapers
- Term Sheets
- SAFEs & NDAs
- Memos & Reports
- Legal Agreements

## Requirements

**Option A: Local Generation (Free, Unlimited)**

```bash
# macOS
brew install pandoc
brew install --cask basictex
sudo tlmgr install collection-fontsrecommended fancyhdr titlesec enumitem xcolor booktabs longtable geometry hyperref graphicx setspace array multirow

# Linux
sudo apt-get install pandoc texlive-full
```

**Option B: Cloud API (Coming Soon)** No install required. Get API key at
ai-pdf-builder.com

## Usage

### Generate via Automation Agent (Preferred)

```bash
python3 runner.py ../pdf-builder/scripts/task_pdf_gen.py --run --type termsheet --input ../pdf-builder/samples/termsheet.md --title "SAFE Term Sheet"
```

### Check System

```bash
python3 runner.py ../pdf-builder/scripts/task_pdf_gen.py --run --input none
```

### Generate via Code

```typescript
import {
  generateSAFE,
  generateTermsheet,
  generateWhitepaper,
} from "ai-pdf-builder";

// Whitepaper
const result = await generateWhitepaper(
  "# My Whitepaper\n\nContent here...",
  { title: "Project Name", author: "Your Name", version: "v1.0" },
);

if (result.success) {
  fs.writeFileSync("whitepaper.pdf", result.buffer);
}

// Term Sheet
const termsheet = await generateTermsheet(
  "# Series Seed Term Sheet\n\n## Investment Amount\n\n$500,000...",
  { title: "Series Seed", subtitle: "Your Company Inc." },
);

// SAFE
const safe = await generateSAFE(
  "# Simple Agreement for Future Equity\n\n...",
  { title: "SAFE Agreement", subtitle: "Your Company Inc." },
);
```

## Document Types

| Type         | Function               | Best For                   |
| ------------ | ---------------------- | -------------------------- |
| `whitepaper` | `generateWhitepaper()` | Technical docs, litepapers |
| `memo`       | `generateMemo()`       | Executive summaries        |
| `agreement`  | `generateAgreement()`  | Legal contracts            |
| `termsheet`  | `generateTermsheet()`  | Investment terms           |
| `safe`       | `generateSAFE()`       | SAFE agreements            |
| `nda`        | `generateNDA()`        | Non-disclosure agreements  |
| `report`     | `generateReport()`     | Business reports           |
| `proposal`   | `generateProposal()`   | Business proposals         |

## Custom Branding

```typescript
const result = await generateWhitepaper(content, metadata, {
  customColors: {
    primary: "#E85D04", // Signal Orange
    secondary: "#14B8A6", // Coordinate Teal
    accent: "#0D0D0D", // Frontier Dark
  },
  fontSize: 11,
  margin: "1in",
  paperSize: "letter",
});
```

## Agent Instructions

When a user asks to generate a PDF:

1. **Check what type of document they need** (whitepaper, term sheet, memo,
   etc.)
2. **Get the content** - either from their message or a file they reference
3. **Ask for metadata** if not provided (title, author, company name)
4. **Check if Pandoc is installed**: `which pandoc`
5. **If Pandoc missing**, provide install instructions or suggest cloud API
6. **Generate the PDF** using the appropriate function
7. **Send the PDF file** to the user

### Example Interaction

```
User: "Generate a term sheet PDF for a $500k SAFE at $5M cap for Strykr AI"

Agent: I'll create that term sheet for you.

[Generates PDF with:
- Title: Series Seed Term Sheet
- Company: Strykr AI Inc.
- Investment: $500,000 SAFE
- Valuation Cap: $5,000,000
- Standard SAFE terms]

Here's your term sheet PDF: [sends file]
```

## Links

- npm: https://www.npmjs.com/package/ai-pdf-builder
- GitHub: https://github.com/NextFrontierBuilds/ai-pdf-builder
- Issues: https://github.com/NextFrontierBuilds/ai-pdf-builder/issues
