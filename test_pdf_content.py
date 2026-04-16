from openjarvis.tools.pdf_generate import PDFGenerateTool
tool = PDFGenerateTool()
res = tool.execute(content="Test content", title="Test Title")
print(res)
