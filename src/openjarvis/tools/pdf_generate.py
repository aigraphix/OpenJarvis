"""PDF generation tool — create PDF files from text content or a topic."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

@ToolRegistry.register("pdf_generate")
class PDFGenerateTool(BaseTool):
    """Generate a PDF file from text content or a topic and render it in the canvas."""

    tool_id = "pdf_generate"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="pdf_generate",
            description=(
                "Generate a standard, text-heavy PDF document. You can provide either: (a) a 'topic' and an optional 'title', and the tool will write the content automatically, "
                "or (b) a 'title' and full 'content' text. This tool creates a real PDF file and opens it in the UI Canvas for preview. "
                "IMPORTANT: Do NOT use this tool for posters, visual art, or highly aesthetic design layouts. For posters and art, ALWAYS use the 'canvas_design' tool immediately without doing a web search first."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the PDF document. If omitted, one will be generated from the topic.",
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic/subject for the PDF. When provided, the tool will auto-generate comprehensive content about this topic. Use this when you don't have the content written yet.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full text content for the PDF. If provided, this is used directly instead of auto-generating from topic.",
                    },
                    "is_presentation": {
                        "type": "boolean",
                        "description": "Set to true if the user requests a 'slide deck' or 'presentation'. This will render a landscape-oriented slide-deck PDF instead of a standard document.",
                    },
                },
                "required": [],
            },
            category="media",
            required_capabilities=[],
        )

    def _generate_content_from_topic(self, topic: str, title: str) -> str:
        """Use the LLM engine to generate content about a topic."""
        import re

        # Extract word count constraint from topic string
        # Matches: "20 words max", "50 words or less", "under 30 words", "no more than 25 words"
        wc_match = re.search(
            r"(?:(\d+)\s*words?\s*(?:or\s*less|max(?:imum)?|limit))|(?:(?:under|fewer\s+than|no\s+more\s+than|at\s+most|up\s+to)\s+(\d+)\s*words?)",
            topic, re.IGNORECASE,
        )
        word_limit: int | None = None
        if wc_match:
            word_limit = int(wc_match.group(1) or wc_match.group(2))

        try:
            from openjarvis.core.config import load_config
            from openjarvis.engine.ollama import OllamaEngine
            from openjarvis.core.types import Message, Role

            config = load_config()
            model = config.intelligence.default_model
            engine_name = config.intelligence.default_engine
            
            if engine_name == "ollama":
                from openjarvis.engine.ollama import OllamaEngine
                engine = OllamaEngine()
            else:
                from openjarvis.engine.cloud import CloudEngine
                engine = CloudEngine()

            constraint_msg = ""
            if word_limit:
                constraint_msg = (
                    f"\n\nCRITICAL CONSTRAINT: Your ENTIRE response must be {word_limit} words or fewer. "
                    f"Count carefully. Do NOT exceed {word_limit} words under any circumstances. "
                    "Be concise and direct."
                )

            messages = [
                Message(role=Role.SYSTEM, content=(
                    "You are a professional document writer. Write well-structured content for a PDF document. "
                    "Use clear paragraphs with proper formatting. Do NOT use markdown headers (# ## etc), "
                    "bullet points, or asterisks — write flowing prose paragraphs only. "
                    "Match the requested length precisely — if asked for a short piece, write a short piece."
                    f"{constraint_msg}"
                )),
                Message(role=Role.USER, content=(
                    f"Write a professional document titled '{title}' about: {topic}"
                    + (f"\nRemember: maximum {word_limit} words total." if word_limit else "")
                )),
            ]

            # Adapt max_tokens to the request: short requests don't need 800 tokens
            gen_max_tokens = min(word_limit * 3, 200) if word_limit else 800

            result = engine.generate(messages, model=model, temperature=0.7, max_tokens=gen_max_tokens)
            content = result.get("content", "")
            if content:
                # Strip any think tags
                content = re.sub(r'<think>[\s\S]*?</think>\s*', '', content, flags=re.IGNORECASE)
                content = re.sub(r'^[\s\S]*?</think>\s*', '', content, flags=re.IGNORECASE)
                # Strip any markdown-style headers that slipped through
                content = re.sub(r'^#{1,6}\s+.*$', '', content, flags=re.MULTILINE)
                content = content.strip()

                # Hard-enforce word count limit as final safety net
                if word_limit:
                    words = content.split()
                    if len(words) > word_limit:
                        content = " ".join(words[:word_limit])
                        # Ensure it ends with proper punctuation
                        if not content.endswith(('.', '!', '?')):
                            content += "."

                return content
        except Exception as exc:
            return f"Content about {topic}. (Auto-generation encountered an error: {exc})"

        return f"A comprehensive overview of {topic}."

    def execute(self, **params: Any) -> ToolResult:
        title = params.get("title", "")
        content = params.get("content", "")
        topic = params.get("topic", "")
        is_pres = params.get("is_presentation", False)

        # If no content but has topic, auto-generate
        if not content and topic:
            if not title:
                title = topic.title() if len(topic) < 60 else topic[:57] + "..."
            
            # Explicitly instruct the model to write slide content if it's a presentation
            if is_pres and "slide" not in topic.lower():
                topic = f"{topic} (Format as a slide deck presentation, 3-5 slides, use bullet points)"
                
            content = self._generate_content_from_topic(topic, title)
        elif not content and not topic:
            return ToolResult(
                tool_name="pdf_generate",
                content="Please provide either a 'topic' or 'content' for the PDF.",
                success=False,
            )
        
        if not title:
            title = "Document"

        try:
            from fpdf import FPDF
        except ImportError:
            return ToolResult(
                tool_name="pdf_generate",
                content=(
                    "fpdf2 package not installed."
                    " Install with: uv pip install fpdf2"
                ),
                success=False,
            )

        try:
            import re
            
            orientation = "L" if is_pres else "portrait"
            pdf = FPDF(orientation=orientation)
            pdf.set_auto_page_break(auto=True, margin=15)
            
            safe_content = content.encode('latin-1', errors='replace').decode('latin-1')
            
            if is_pres:
                pdf.set_margins(left=20, top=20, right=20)
                slides = re.split(r'\n\s*\n', safe_content.strip())
                
                # Title slide
                pdf.add_page(orientation="L")
                pdf.set_font("Helvetica", "B", 32)
                pdf.cell(0, 50, "", new_x="LMARGIN", new_y="NEXT") # Spacer
                pdf.multi_cell(0, 15, title, align="C")
                pdf.set_font("Helvetica", "", 18)
                pdf.cell(0, 10, "", new_x="LMARGIN", new_y="NEXT")
                pdf.multi_cell(0, 10, "Presentation Deck", align="C")
                
                # Content slides
                for slide_text in slides:
                    if not slide_text.strip():
                        continue
                    if title.lower() in slide_text.lower() and len(slide_text) < len(title) + 20:
                        continue
                    
                    pdf.add_page(orientation="L")
                    lines = slide_text.split('\n')
                    
                    if len(lines) > 0 and (lines[0].startswith('Slide') or lines[0].startswith('#') or len(lines[0]) < 60):
                        pdf.set_font("Helvetica", "B", 24)
                        header = lines[0].strip('# *:_-')
                        pdf.cell(0, 15, header, new_x="LMARGIN", new_y="NEXT")
                        pdf.cell(0, 5, "", new_x="LMARGIN", new_y="NEXT") # Spacer
                        lines = lines[1:]
                    
                    pdf.set_font("Helvetica", "", 18)
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith('*') or line.startswith('-'):
                            pdf.multi_cell(0, 12, "• " + line.lstrip('*- '))
                        else:
                            pdf.multi_cell(0, 12, line)
                        pdf.cell(0, 4, "", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.add_page()
                # --- Title ---
                pdf.set_font("Helvetica", "B", size=16)
                pdf.cell(190, 10, txt=title, align='C', new_x="LMARGIN", new_y="NEXT")
                pdf.ln(8)
                # --- Body ---
                pdf.set_font("Helvetica", size=11)
                pdf.multi_cell(190, 6, txt=safe_content)

            # Save to public frontend folder
            frontend_dir = Path("/Users/danny/Desktop/OpenJarvis/frontend/public/generated")
            frontend_dir.mkdir(parents=True, exist_ok=True)

            safe_title = "".join([c if c.isalnum() else "_" for c in title])
            file_path = frontend_dir / f"{safe_title}.pdf"

            pdf.output(str(file_path))
            
            public_url = f"/generated/{safe_title}.pdf"

            return ToolResult(
                tool_name="pdf_generate",
                content=f"PDF generated successfully. The document '{title}' has been created and is ready for preview.\n[RENDER_CANVAS:pdf:{public_url}]\n\nSYSTEM NOTE TO ASSISTANT: You have successfully created the PDF using this tool. Do NOT apologize or claim that you are a text-based AI. Simply tell the user that the PDF is ready in the canvas.",
                success=True,
                metadata={
                    "file_path": str(file_path),
                    "url": public_url
                },
            )
        except Exception as exc:
            return ToolResult(
                tool_name="pdf_generate",
                content=f"PDF generation error: {exc}",
                success=False,
            )

__all__ = ["PDFGenerateTool"]
