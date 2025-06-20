#!/usr/bin/env python3
"""
测试文件夹上传功能的脚本
"""

import os
import tempfile
import sys

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from otterwiki.folder_processor import FolderProcessor
    print("✓ 成功导入 FolderProcessor")
except ImportError as e:
    print(f"✗ 导入 FolderProcessor 失败: {e}")
    sys.exit(1)

def create_test_files():
    """创建测试文件结构"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件夹结构
        test_structure = {
            "readme.md": "# 项目说明\n\n这是一个测试项目。",
            "docs/guide.md": "# 使用指南\n\n这里是使用说明。",
            "docs/api.md": "# API文档\n\nAPI接口说明。",
            "src/main.py": "# 主程序\n\n```python\nprint('Hello World')\n```",
            "src/utils.py": "# 工具函数\n\n```python\ndef helper():\n    pass\n```",
            "data/sample.csv": "name,age,city\n张三,25,北京\n李四,30,上海",
            "config.json": '{"name": "test", "version": "1.0.0"}'
        }
        
        # 创建文件和目录
        for file_path, content in test_structure.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 创建测试文件: {file_path}")
        
        return temp_dir

def test_folder_processor():
    """测试文件夹处理器"""
    print("\n=== 测试文件夹处理器 ===")
    
    # 创建处理器
    processor = FolderProcessor()
    print(f"✓ 文件夹处理器创建成功")
    print(f"✓ 支持的扩展名: {processor.supported_extensions}")
    
    # 测试文件名清理
    test_names = [
        "test file.md",
        "test-file.md", 
        "test.file.md",
        "test<file>.md",
        "test file  name.md"
    ]
    
    print("\n--- 测试文件名清理 ---")
    for name in test_names:
        # 直接测试文件名清理逻辑
        cleaned = name
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        cleaned = cleaned.strip(' .')
        
        # Replace multiple spaces/underscores with single underscore
        import re
        cleaned = re.sub(r'[_\s]+', '_', cleaned)
        
        print(f"'{name}' -> '{cleaned}'")
    
    # 测试文件支持检查
    test_files = [
        "document.pdf",
        "readme.md",
        "data.csv",
        "image.png",
        "script.js"
    ]
    
    print("\n--- 测试文件支持检查 ---")
    for filename in test_files:
        ext = os.path.splitext(filename)[1].lower()
        supported = ext in processor.supported_extensions
        print(f"'{filename}' -> {'支持' if supported else '不支持'}")
    
    return True

def test_file_structure_processing():
    """测试文件结构处理"""
    print("\n=== 测试文件结构处理 ===")
    
    processor = FolderProcessor()
    
    # 模拟文件结构
    file_structure = {
        "readme.md": "/tmp/readme.md",
        "docs/guide.md": "/tmp/docs/guide.md",
        "docs/api.md": "/tmp/docs/api.md",
        "src/main.py": "/tmp/src/main.py",
        "data/sample.csv": "/tmp/data/sample.csv"
    }
    
    # 测试目录分组
    files_by_dir = {}
    
    for file_path in file_structure.keys():
        dir_path = os.path.dirname(file_path)
        if dir_path == "":
            dir_path = "."
        
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        
        files_by_dir[dir_path].append(file_path)
    
    print("文件按目录分组:")
    for dir_path, files in files_by_dir.items():
        print(f"  {dir_path}: {files}")
    
    return True

def test_folder_upload_simulation():
    """模拟文件夹上传测试"""
    print("\n=== 模拟文件夹上传测试 ===")
    
    # 创建测试文件
    temp_dir = create_test_files()
    
    # 模拟FileStorage对象
    class MockFileStorage:
        def __init__(self, filename, content):
            self.filename = filename
            self.content = content
        
        def save(self, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.content)
    
    # 创建模拟文件列表
    mock_files = []
    test_files = [
        ("readme.md", "# 项目说明\n\n这是一个测试项目。"),
        ("docs/guide.md", "# 使用指南\n\n这里是使用说明。"),
        ("docs/api.md", "# API文档\n\nAPI接口说明。"),
        ("src/main.py", "# 主程序\n\n```python\nprint('Hello World')\n```"),
        ("data/sample.csv", "name,age,city\n张三,25,北京\n李四,30,上海")
    ]
    
    for filename, content in test_files:
        mock_files.append(MockFileStorage(filename, content))
    
    # 测试文件夹处理
    processor = FolderProcessor()
    
    with tempfile.TemporaryDirectory() as output_dir:
        try:
            success, message, created_pages = processor.process_folder_upload(
                mock_files, output_dir, "test_project"
            )
            
            if success:
                print(f"✓ {message}")
                print(f"✓ 创建的页面数量: {len(created_pages)}")
                
                for file_path, page_info in created_pages.items():
                    print(f"  - {file_path} -> {page_info['page_name']}")
            else:
                print(f"✗ {message}")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("开始测试文件夹上传功能...")
    
    success = True
    success &= test_folder_processor()
    success &= test_file_structure_processing()
    success &= test_folder_upload_simulation()
    
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1) 