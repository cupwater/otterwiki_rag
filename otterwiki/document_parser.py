#!/usr/bin/env python
# vim: set et ts=8 sts=4 sw=4 ai:

"""
Document parser module for converting various document formats to Markdown using docling.
"""

import os
import json
import csv
import io
import tempfile
from typing import Tuple
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    docling_available = True
except ImportError:
    DocumentConverter = None
    docling_available = False


class DocumentParser:
    """Parser for converting various document formats to Markdown."""
    
    def __init__(self):
        if docling_available and DocumentConverter:
            self.converter = DocumentConverter()
        else:
            self.converter = None
    
    def parse_file(self, file_content: bytes, filename: str) -> Tuple[str, bool]:
        """
        Parse a file and convert it to Markdown format.
        
        Args:
            file_content: The binary content of the file
            filename: The original filename (used to determine format)
            
        Returns:
            A tuple of (markdown_content, success)
        """
        if not filename:
            return "Error: No filename provided", False
            
        file_ext = Path(filename).suffix.lower()
        
        try:
            # Handle text-based formats directly
            if file_ext == '.md':
                return self._parse_markdown(file_content)
            elif file_ext == '.txt':
                return self._parse_text(file_content)
            elif file_ext == '.csv':
                return self._parse_csv(file_content)
            elif file_ext == '.json':
                return self._parse_json(file_content)
            
            # Handle binary formats using docling
            elif file_ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt']:
                return self._parse_with_docling(file_content, filename)
            
            else:
                return f"Error: Unsupported file format '{file_ext}'", False
                
        except Exception as e:
            return f"Error parsing file: {str(e)}", False
    
    def _parse_markdown(self, file_content: bytes) -> Tuple[str, bool]:
        """Parse Markdown files."""
        try:
            content = file_content.decode('utf-8')
            return content, True
        except UnicodeDecodeError:
            return "Error: Unable to decode Markdown file as UTF-8", False
    
    def _parse_text(self, file_content: bytes) -> Tuple[str, bool]:
        """Parse plain text files."""
        try:
            content = file_content.decode('utf-8')
            # Wrap in code block to preserve formatting
            return f"```\n{content}\n```", True
        except UnicodeDecodeError:
            return "Error: Unable to decode text file as UTF-8", False
    
    def _parse_csv(self, file_content: bytes) -> Tuple[str, bool]:
        """Parse CSV files and convert to Markdown table."""
        try:
            content = file_content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            
            if not rows:
                return "Empty CSV file", True
            
            # Create Markdown table
            markdown_lines = []
            
            # Header row
            if rows:
                header = rows[0]
                markdown_lines.append("| " + " | ".join(header) + " |")
                markdown_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
                
                # Data rows
                for row in rows[1:]:
                    # Pad row to match header length
                    padded_row = row + [""] * (len(header) - len(row))
                    markdown_lines.append("| " + " | ".join(padded_row[:len(header)]) + " |")
            
            return "\n".join(markdown_lines), True
            
        except UnicodeDecodeError:
            return "Error: Unable to decode CSV file as UTF-8", False
        except Exception as e:
            return f"Error parsing CSV: {str(e)}", False
    
    def _parse_json(self, file_content: bytes) -> Tuple[str, bool]:
        """Parse JSON files and convert to formatted Markdown."""
        try:
            content = file_content.decode('utf-8')
            data = json.loads(content)
            
            # Pretty format JSON in a code block
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            return f"```json\n{formatted_json}\n```", True
            
        except UnicodeDecodeError:
            return "Error: Unable to decode JSON file as UTF-8", False
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON format - {str(e)}", False
        except Exception as e:
            return f"Error parsing JSON: {str(e)}", False
    
    def _parse_with_docling(self, file_content: bytes, filename: str) -> Tuple[str, bool]:
        """Parse binary documents using docling."""
        if not docling_available:
            return "Error: docling library is not available. Please install it: pip install docling", False
        
        if not self.converter:
            return "Error: docling converter not initialized", False
        
        try:
            # Create a temporary file since docling works with file paths
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                
                try:
                    # Convert document using docling
                    result = self.converter.convert(temp_file.name)
                    markdown_content = result.document.export_to_markdown()
                    
                    return markdown_content, True
                    
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file.name)
                    except OSError:
                        pass
                        
        except Exception as e:
            return f"Error converting document with docling: {str(e)}", False


def parse_uploaded_file(file_storage) -> Tuple[str, bool]:
    """
    Convenience function to parse an uploaded file.
    
    Args:
        file_storage: Flask FileStorage object
        
    Returns:
        A tuple of (markdown_content, success)
    """
    if not file_storage or not file_storage.filename:
        return "Error: No file provided", False
    
    try:
        file_content = file_storage.read()
        parser = DocumentParser()
        return parser.parse_file(file_content, file_storage.filename)
    except Exception as e:
        return f"Error reading uploaded file: {str(e)}", False