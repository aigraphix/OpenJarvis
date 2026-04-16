# NEXUS-ADIS Skill 🧠📄

## Advanced Data Intelligence System

**Version**: 3.0\
**Status**: Production\
**MCP Server**: `adis`

---

## Overview

**NEXUS-ADIS** (Advanced Data Intelligence System) is Nexus's unified document
parsing and knowledge extraction engine. It provides high-fidelity document
parsing, intelligent knowledge extraction, and automatic growth of the user's
personal knowledge base.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NEXUS-ADIS v3.0                          │
│                (Unified Parser Engine)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   DOCLING   │  │   NATIVE    │  │   FUTURE    │
│   Backend   │  │   Parsers   │  │   Plugins   │
│             │  │             │  │             │
│ • PDF (adv) │  │ • Markdown  │  │ • Medical   │
│ • DOCX      │  │ • JSON/YAML │  │ • Legal     │
│ • PPTX      │  │ • CSV/TSV   │  │ • Financial │
│ • Audio/ASR │  │ • Plain text│  │             │
│ • OCR       │  │ • Images    │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Primary Capabilities

1. **Document Parsing**: Analyze documents to extract structured elements:
   - Tables (`table`)
   - Sections/Headers (`section`)
   - Figures/Images (`figure`)
   - Code blocks (`code`)
   - Paragraphs (`paragraph`)
   - Formulas (`formula`)

2. **Multi-Format Support**:
   - PDF (with layout detection, OCR, tables)
   - DOCX, PPTX, XLSX
   - Markdown, HTML
   - Images (PNG, JPEG, TIFF)
   - Audio (WAV, MP3) via ASR
   - JSON, YAML, CSV

3. **Knowledge Extraction**: Transform parsed content into searchable knowledge:
   - Summarize documents
   - Extract key facts
   - Identify entities and relationships
   - Tag and categorize content

4. **Supabase Integration**: All data persists to cloud:
   - `nexus_documents` → File metadata and storage paths
   - `nexus_knowledge` → Extracted knowledge entries
   - `nexus_lessons` → Learned patterns and facts
   - `nexus-files` bucket → Raw file storage

## Data Flow Pipeline

```
User Upload → nexus-files bucket → nexus_documents record
     ↓
ADIS Parser → Extract elements → nexus_knowledge entries
     ↓
AI Summarization → Key facts → nexus_lessons
     ↓
Vector Embeddings (future) → Semantic search
```

## Usage

### CLI Parse

```bash
python3 skills/nexus-adis/scripts/adis_parse.py --input <file_path>
```

### From Agents

When a user uploads a file via chat:

1. Upload to `nexus-files` bucket (via nexus-upload edge function)
2. Create `nexus_documents` record
3. Call ADIS parser to extract elements
4. Store extracted knowledge in `nexus_knowledge`
5. Generate summary as `nexus_lesson` entry

### MCP Server

The ADIS MCP server provides document parsing tools to any MCP-compatible
client:

```json
{
    "mcpServers": {
        "adis": {
            "command": "uvx",
            "args": ["--from=docling-mcp", "docling-mcp-server"]
        }
    }
}
```

## Backends

### Docling Backend (Primary)

Used for complex documents requiring advanced parsing:

- PDF with layout detection
- Table structure extraction
- OCR for scanned documents
- Audio transcription (ASR)
- Formula recognition

**Install**: `pip install docling`

### Native Backend (Fallback)

Used for simple formats or when Docling is unavailable:

- Markdown → BeautifulSoup
- JSON/YAML → stdlib
- CSV → pandas
- Text → direct read
- Images → basic metadata

**Always available** - no extra dependencies.

## Strategic Constraints

- **Privacy-First**: No PHI sent to external APIs without anonymization
- **User-Scoped**: All knowledge is isolated per user_id
- **Source Tracking**: All knowledge links back to source document
- **Graceful Degradation**: Falls back to native if Docling unavailable

## Tech Stack

- **Advanced Parsing**: Docling (IBM)
- **Native Parsing**: Beautiful Soup 4, Markdown-Extra, PyPDF
- **Storage**: Supabase Storage + PostgreSQL
- **Knowledge Base**: nexus_knowledge, nexus_lessons tables
- **MCP**: docling-mcp server

## Migration Notes

This skill replaces the legacy "Dolphin Document Intelligence" system.
Historical references to "Dolphin" have been marked as "dolphin-legacy".

---

_NEXUS-ADIS v3.0 - Advanced Data Intelligence System_
