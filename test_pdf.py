from openjarvis.tools.pdf_generate import PDFGenerateTool
import asyncio
tool = PDFGenerateTool()
res = tool.execute(topic="iphone17promax, 20 words max")
print(res)
