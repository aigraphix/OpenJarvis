# Dolphin Document Intelligence Skill 🐬🧠

## Overview

The **Dolphin-Scale Document Engine** provides high-fidelity document parsing,
knowledge extraction, and automatic growth of the user's personal knowledge
base. All parsed data flows to Supabase for persistent storage.

## Primary Capabilities

1. **Document Parsing**: Analyze documents (PDF, DOCX, images, markdown) to
   extract:
   - Tables (`table`)
   - Sections/Headers (`section`)
   - Figures/Images (`figure`)
   - Code blocks (`code`)
   - Paragraphs (`paragraph`)

2. **Knowledge Extraction**: Transform parsed content into searchable knowledge:
   - Summarize documents
   - Extract key facts
   - Identify entities and relationships
   - Tag and categorize content

3. **Supabase Integration**: All data persists to cloud:
   - `nexus_documents` → File metadata and storage paths
   - `nexus_knowledge` → Extracted knowledge entries
   - `nexus_lessons` → Learned patterns and facts
   - `nexus-files` bucket → Raw file storage

## Data Flow Pipeline

```
User Upload → nexus-files bucket → nexus_documents record
     ↓
Dolphin Parser → Extract elements → nexus_knowledge entries
     ↓
AI Summarization → Key facts → nexus_lessons
     ↓
Vector Embeddings (future) → Semantic search
```

## Target Tables by Content Type

| File Type     | Bucket Folder | Primary Table   | Knowledge Type |
| ------------- | ------------- | --------------- | -------------- |
| Images        | images/       | nexus_documents | figure         |
| PDFs          | documents/    | nexus_documents | document       |
| Audio         | audio/        | nexus_documents | transcript     |
| Text/MD       | documents/    | nexus_documents | text           |
| Conversations | -             | nexus_messages  | conversation   |

## Usage

### Parse a document:

```bash
python3 skills/advanced-intelligence/scripts/task_advanced_parse.py --run --input <file_path>
```

### From agents:

When a user uploads a file via chat:

1. Upload to `nexus-files` bucket (via nexus-upload edge function)
2. Create `nexus_documents` record
3. Call Dolphin parser to extract elements
4. Store extracted knowledge in `nexus_knowledge`
5. Generate summary as `nexus_lesson` entry

## Knowledge Growth Protocol

When agents learn from documents:

1. **Extract**: Parse document structure and content
2. **Summarize**: Create concise knowledge summary
3. **Tag**: Apply relevant categories and tags
4. **Store**: Persist to `nexus_knowledge` with source reference
5. **Index**: (Future) Generate embeddings for semantic search

## Strategic Constraints

- **Privacy-First**: No PHI sent to external APIs without anonymization
- **User-Scoped**: All knowledge is isolated per user_id
- **Source Tracking**: All knowledge links back to source document

## Tech Stack

- **Parsing**: Beautiful Soup 4, Markdown-Extra, PyPDF2
- **Rendering**: python-docx, reportlab (PDF generation)
- **Storage**: Supabase Storage + PostgreSQL
- **Knowledge Base**: nexus_knowledge, nexus_lessons tables
