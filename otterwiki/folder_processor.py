#!/usr/bin/env python
# vim: set et ts=8 sts=4 sw=4 ai:

"""
Folder processor module for handling folder uploads and recursive file processing.
"""

import os
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from flask import current_app
except ImportError:
    # Fallback for when Flask is not available during imports
    current_app = None

from .file_parser import FileParser


class FolderProcessor:
    """Processor for handling folder uploads and recursive file processing."""
    
    def __init__(self):
        self.file_parser = FileParser()
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
    
    def process_folder_upload(self, folder_files, base_page_path: str, 
                            folder_name: str) -> Tuple[bool, str, Dict]:
        """
        Process a folder upload and create pages for all files.
        
        Args:
            folder_files: List of FileStorage objects from the folder upload
            base_page_path: Base path for the wiki pages
            folder_name: Name of the folder being uploaded
            
        Returns:
            Tuple of (success, message, created_pages_info)
        """
        try:
            # Create temporary directory to extract files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract files to temporary directory
                file_structure = self._extract_folder_files(folder_files, temp_dir)
                
                # Process the folder structure
                created_pages = self._process_folder_structure(
                    file_structure, temp_dir, base_page_path, folder_name
                )
                
                return True, f"成功处理文件夹 '{folder_name}'，创建了 {len(created_pages)} 个页面", created_pages
                
        except Exception as e:
            error_msg = f"处理文件夹时出错: {str(e)}"
            if current_app:
                current_app.logger.error(error_msg)
            return False, error_msg, {}
    
    def _extract_folder_files(self, folder_files, temp_dir: str) -> Dict[str, str]:
        """
        Extract uploaded folder files to temporary directory.
        
        Args:
            folder_files: List of FileStorage objects
            temp_dir: Temporary directory path
            
        Returns:
            Dictionary mapping file paths to temporary file paths
        """
        file_structure = {}
        
        for file_storage in folder_files:
            if not file_storage.filename:
                continue
                
            # Get the relative path from the folder
            relative_path = file_storage.filename
            
            # Create the full path in temp directory
            temp_file_path = os.path.join(temp_dir, relative_path)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            # Save the file
            file_storage.save(temp_file_path)
            file_structure[relative_path] = temp_file_path
            
            if current_app:
                current_app.logger.info(f"提取文件: {relative_path}")
        
        return file_structure
    
    def _process_folder_structure(self, file_structure: Dict[str, str], temp_dir: str, 
                                base_page_path: str, folder_name: str) -> Dict:
        """
        Process the folder structure and create wiki pages.
        
        Args:
            file_structure: Dictionary mapping file paths to temporary file paths
            temp_dir: Temporary directory path
            base_page_path: Base path for the wiki pages
            folder_name: Name of the folder being uploaded
            
        Returns:
            Dictionary with information about created pages
        """
        created_pages = {}
        
        # 遍历所有文件，将每个文件作为独立的页面
        for file_path, temp_file_path in file_structure.items():
            page_info = self._create_page_from_file(
                file_path, temp_file_path, base_page_path
            )
            if page_info:
                created_pages[file_path] = page_info
        
        return created_pages
    
    def _group_files_by_directory(self, file_structure: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Group files by their directory structure.
        
        Args:
            file_structure: Dictionary mapping file paths to temporary file paths
            
        Returns:
            Dictionary mapping directory paths to lists of file paths
        """
        files_by_dir = {}
        
        for file_path in file_structure.keys():
            dir_path = os.path.dirname(file_path)
            if dir_path == "":
                dir_path = "."
            
            if dir_path not in files_by_dir:
                files_by_dir[dir_path] = []
            
            files_by_dir[dir_path].append(file_path)
        
        return files_by_dir
    
    def _create_page_from_file(self, file_path: str, temp_file_path: str, 
                             base_page_path: str):
        """
        Create a wiki page from a file.
        
        Args:
            file_path: Relative path of the file in the folder
            temp_file_path: Temporary file path
            base_page_path: Base path for the wiki pages
            
        Returns:
            Dictionary with page information or None if failed
        """
        try:
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Skip files that don't have supported extensions
            if not self._is_supported_file(filename):
                if current_app:
                    current_app.logger.info(f"跳过不支持的文件: {file_path}")
                return None
            
            # Create page name from filename
            page_name = self._sanitize_page_name(name_without_ext)
            if not page_name:
                page_name = "untitled"
            
            # 计算页面目录路径
            # 如果文件在子目录中，保持目录结构
            file_dir = os.path.dirname(file_path)
            if file_dir and file_dir != ".":
                # 文件在子目录中，创建对应的页面目录
                page_dir_path = os.path.join(base_page_path, file_dir)
                # 页面名称包含目录路径
                full_page_name = f"{file_dir}/{page_name}"
            else:
                # 文件在根目录
                page_dir_path = base_page_path
                full_page_name = page_name
            
            # Parse the file content
            markdown_content = self.file_parser.parse_file(temp_file_path, filename, page_dir_path)
            
            if not markdown_content:
                if current_app:
                    current_app.logger.warning(f"无法解析文件: {file_path}")
                return None
            
            # Create the page
            page_info = {
                'page_name': page_name,
                'full_page_name': full_page_name,
                'file_path': file_path,
                'content': markdown_content,
                'page_dir': page_dir_path
            }
            
            if current_app:
                current_app.logger.info(f"创建页面: {full_page_name} (来自 {file_path})")
            
            return page_info
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"创建页面失败 {file_path}: {str(e)}")
            return None
    
    def _is_supported_file(self, filename: str) -> bool:
        """
        Check if a file is supported for processing.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if the file is supported, False otherwise
        """
        ext = Path(filename).suffix.lower()
        return ext in self.supported_extensions
    
    def _sanitize_page_name(self, name: str) -> str:
        """
        Sanitize a page name for use in the wiki.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized page name
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        name = name.strip(' .')
        
        # Replace multiple spaces/underscores with single underscore
        name = re.sub(r'[_\s]+', '_', name)
        
        return name


def process_folder_upload(folder_files, base_page_path: str, 
                         folder_name: str) -> Tuple[bool, str, Dict]:
    """
    Convenience function to process a folder upload.
    
    Args:
        folder_files: List of FileStorage objects from the folder upload
        base_page_path: Base path for the wiki pages
        folder_name: Name of the folder being uploaded
        
    Returns:
        Tuple of (success, message, created_pages_info)
    """
    processor = FolderProcessor()
    return processor.process_folder_upload(folder_files, base_page_path, folder_name) 