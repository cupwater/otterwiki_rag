# OtterWiki File Upload Feature

## Overview

This feature enables users to upload various types of files when creating new wiki pages. The system automatically parses the uploaded files and converts them into markdown format for immediate use as page content.

## Supported File Formats

### Text Files
- **Markdown** (.md, .markdown) - Direct import
- **Plain Text** (.txt) - Automatic formatting
- **CSV** (.csv) - Converted to markdown tables
- **JSON** (.json) - Formatted code blocks

### Document Files  
- **Microsoft Word** (.docx, .doc) - Parsed with docling
- **Microsoft Excel** (.xlsx, .xls) - Table extraction
- **Microsoft PowerPoint** (.pptx, .ppt) - Content extraction
- **PDF** (.pdf) - Full text and layout extraction

## How It Works

1. **Upload**: Select a file when creating a new page
2. **Parse**: System automatically detects file type and parses content
3. **Convert**: Content is converted to markdown format
4. **Create**: Page is created with the parsed content

## Benefits

- **Time Saving**: No need to manually copy and paste content
- **Format Consistency**: All content is standardized as markdown
- **Error Handling**: Graceful fallback for unsupported formats
- **User Friendly**: Simple upload interface

## Technical Details

- Uses the **docling** library for advanced document parsing
- Supports OCR for scanned documents  
- Maintains document structure and formatting
- Handles tables, images, and complex layouts