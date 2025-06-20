#!/usr/bin/env python
# vim: set et ts=8 sts=4 sw=4 ai:

import os
import tempfile
import json
import csv
import re
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

try:
    from flask import current_app
except ImportError:
    # Fallback for when Flask is not available during imports
    current_app = None


class FileParser:
    """File parser that converts various document formats to markdown using docling."""
    
    def __init__(self):
        if DOCLING_AVAILABLE:
            self.converter = DocumentConverter()
        else:
            self.converter = None
        
        self.supported_extensions = {
            # Text formats
            '.txt', '.text',
            '.md', '.markdown',
            '.csv',
            '.json',
            # Microsoft Office formats
            '.docx', '.doc',
            '.xlsx', '.xls',
            '.pptx', '.ppt',
            # PDF
            '.pdf',
            # Web formats
            '.html', '.htm'
        }
    
    def is_supported(self, filename):
        """Check if the file format is supported."""
        ext = Path(filename).suffix.lower()
        return ext in self.supported_extensions
    
    def parse_file(self, file_path, filename, page_path=None):
        """
        Parse a file and convert it to markdown content.
        
        Args:
            file_path (str): Path to the file to parse
            filename (str): Original filename
            page_path (str): Path for the page where images should be saved
            
        Returns:
            str: Markdown content
        """
        ext = Path(filename).suffix.lower()
        
        try:
            if ext in ['.txt', '.text']:
                return self._parse_text_file(file_path)
            elif ext in ['.md', '.markdown']:
                return self._parse_markdown_file(file_path)
            elif ext == '.csv':
                return self._parse_csv_file(file_path)
            elif ext == '.json':
                return self._parse_json_file(file_path)
            else:
                # Use docling for other formats (PDF, DOCX, XLSX, PPTX, etc.)
                return self._parse_with_docling(file_path, filename, page_path)
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error parsing file {filename}: {str(e)}")
            return f"# Error parsing file: {filename}\n\nError: {str(e)}\n\nPlease try uploading the file manually."
    
    def _parse_text_file(self, file_path):
        """Parse plain text files."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Wrap in code block if it looks like code or has special formatting
        if self._looks_like_code(content):
            return f"```\n{content}\n```"
        else:
            return content
    
    def _parse_markdown_file(self, file_path):
        """Parse markdown files."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _parse_csv_file(self, file_path):
        """Parse CSV files and convert to markdown table."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to detect the dialect
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                
                reader = csv.reader(f, dialect)
                rows = list(reader)
            
            if not rows:
                return "# CSV File\n\nEmpty CSV file."
            
            # Create markdown table
            markdown = "# CSV Data\n\n"
            
            # Header row
            if rows:
                header = rows[0]
                markdown += "| " + " | ".join(header) + " |\n"
                markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"
                
                # Data rows
                for row in rows[1:]:
                    # Pad row to match header length
                    while len(row) < len(header):
                        row.append("")
                    markdown += "| " + " | ".join(row[:len(header)]) + " |\n"
            
            return markdown
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error parsing CSV: {str(e)}")
            return f"# CSV File\n\nError parsing CSV: {str(e)}"
    
    def _parse_json_file(self, file_path):
        """Parse JSON files and convert to formatted text."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            # Pretty print JSON with markdown formatting
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            return f"# JSON Data\n\n```json\n{formatted_json}\n```"
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error parsing JSON: {str(e)}")
            return f"# JSON File\n\nError parsing JSON: {str(e)}"
    
    def _parse_with_docling(self, file_path, filename, page_path=None):
        """Parse files using docling and handle embedded images."""
        if not DOCLING_AVAILABLE or not self.converter:
            return f"# Document\n\nDocling is not available. Please install docling to parse this file type."
        
        try:
            result = self.converter.convert(file_path)
            markdown_content = result.document.export_to_markdown()
            
            # Process images if page_path is provided
            if page_path and hasattr(result, 'images') and result.images:
                markdown_content = self._process_embedded_images(
                    markdown_content, result.images, page_path, filename
                )
            
            # Add a header if the content doesn't start with one
            if not markdown_content.strip().startswith('#'):
                filename = Path(file_path).name
                markdown_content = f"# {filename}\n\n{markdown_content}"
            
            return markdown_content
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error parsing with docling: {str(e)}")
            return f"# Document\n\nError parsing document: {str(e)}"
    
    def _process_embedded_images(self, markdown_content, images, page_path, original_filename):
        """
        Process embedded images from the document and save them to the page's attachment directory.
        
        Args:
            markdown_content (str): The markdown content with image references
            images (list): List of image objects from docling
            page_path (str): The page path where images should be saved
            original_filename (str): Original document filename
            
        Returns:
            str: Updated markdown content with correct image paths
        """
        if not images:
            return markdown_content
        
        # Create page attachment directory
        page_dir = Path(page_path)
        page_dir.mkdir(parents=True, exist_ok=True)
        
        # Track image replacements
        image_replacements = {}
        
        for i, image in enumerate(images):
            try:
                # Generate unique filename for the image
                image_ext = self._get_image_extension(image)
                image_filename = f"{Path(original_filename).stem}_image_{i+1}{image_ext}"
                
                # Save image to page directory
                image_path = page_dir / image_filename
                with open(image_path, 'wb') as f:
                    f.write(image.data)
                
                # Create the correct path for markdown
                markdown_image_path = f"./{image_filename}"
                image_replacements[f"image_{i+1}"] = markdown_image_path
                
                if current_app:
                    current_app.logger.info(f"Saved embedded image: {image_filename}")
                    
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Error saving embedded image: {str(e)}")
        
        # Replace image references in markdown content
        # Look for patterns like ![image](image_1) or ![image](image_1.png)
        for old_ref, new_path in image_replacements.items():
            # Replace various image reference patterns
            patterns = [
                rf'!\[([^\]]*)\]\({old_ref}\)',  # ![alt](image_1)
                rf'!\[([^\]]*)\]\({old_ref}\.[a-zA-Z]+\)',  # ![alt](image_1.png)
                rf'!\[([^\]]*)\]\({old_ref}\s*\)',  # ![alt](image_1 )
            ]
            
            for pattern in patterns:
                markdown_content = re.sub(
                    pattern,
                    rf'![\1]({new_path})',
                    markdown_content
                )
        
        return markdown_content
    
    def _get_image_extension(self, image):
        """Get the appropriate file extension for an image based on its format."""
        # Try to determine format from image object
        if hasattr(image, 'format') and image.format:
            return f".{image.format.lower()}"
        elif hasattr(image, 'mime_type') and image.mime_type:
            mime_to_ext = {
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/tiff': '.tiff',
                'image/webp': '.webp'
            }
            return mime_to_ext.get(image.mime_type, '.png')
        else:
            # Default to PNG if we can't determine the format
            return '.png'
    
    def _looks_like_code(self, content):
        """Heuristic to determine if content looks like code."""
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', 'from ',
            '#include', 'public class', 'private ', 'protected ',
            '<?php', '<?xml', '<!DOCTYPE', '<html', '<script',
            'SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ',
            'console.log', 'print(', 'printf('
        ]
        
        lines = content.split('\n')
        code_like_lines = 0
        
        for line in lines[:10]:  # Check first 10 lines
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in code_indicators):
                code_like_lines += 1
            # Check for common code patterns
            if line.strip().endswith((';', '{', '}', ':', '=>')):
                code_like_lines += 1
        
        return code_like_lines > len(lines) * 0.3  # If >30% of lines look like code


def parse_uploaded_file(uploaded_file, filename, page_path=None):
    """
    Convenience function to parse an uploaded file.
    
    Args:
        uploaded_file: Flask uploaded file object
        filename (str): Original filename
        page_path (str): Path for the page where images should be saved
        
    Returns:
        str: Markdown content or None if parsing failed
    """
    parser = FileParser()
    
    if not parser.is_supported(filename):
        return None
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
        uploaded_file.save(tmp_file.name)
        
        try:
            markdown_content = parser.parse_file(tmp_file.name, filename, page_path)
            return markdown_content
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file.name)
            except:
                pass
    
    return None