import re

content = """I cannot create a physical PDF file, but I can give you the text content, which you can easily copy and paste into a document editor (like Google Docs or Word) and save as a PDF.

Here is the text, under 20 words:

**iPhone 17 Pro Max: Unmatched power. Revolutionary AI camera. Stunning titanium design. Experience the future of mobile.**"""

cleaned = re.sub(
    r'[^.!?\n]*(?:cannot|can\'t|unable|sorry|apologize|text-based|limitations)[^.!?\n]*[.!?]\s*',
    '', content, flags=re.IGNORECASE,
).strip()
print("CLEANED:")
print(cleaned)
