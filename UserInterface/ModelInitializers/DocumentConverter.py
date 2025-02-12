import os
import tempfile
from pdf2markdown import convert_pdf_to_markdown

class DocumentConverter:
    @staticmethod
    def pdf_to_markdown(pdf_path):
        """
        Convert PDF directly to Markdown using pdf2markdown
        """
        try:
            # Convert PDF to markdown
            markdown_content = convert_pdf_to_markdown(pdf_path)
            return markdown_content
            
        except Exception as e:
            raise Exception(f"PDF to Markdown conversion failed: {str(e)}")
