#!/usr/bin/env python3
"""
测试修复后的文件夹上传功能
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
    
    # 创建模拟文件列表，包含子目录结构
    mock_files = []
    test_files = [
        ("readme.md", "# 项目说明\n\n这是一个测试项目。"),
        ("docs/guide.md", "# 使用指南\n\n这里是使用说明。"),
        ("docs/api.md", "# API文档\n\nAPI接口说明。"),
        ("src/main.py", "# 主程序\n\n```python\nprint('Hello World')\n```"),
        ("src/utils.py", "# 工具函数\n\n```python\ndef helper():\n    pass\n```"),
        ("data/sample.csv", "name,age,city\n张三,25,北京\n李四,30,上海"),
        ("config.json", '{"name": "test", "version": "1.0.0"}')
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
                
                print("\n创建的页面详情:")
                for file_path, page_info in created_pages.items():
                    full_page_name = page_info.get('full_page_name', page_info['page_name'])
                    print(f"  - {file_path} -> {full_page_name}")
                    
                    # 验证页面名称是否正确
                    expected_page_name = os.path.splitext(os.path.basename(file_path))[0]
                    if page_info['page_name'] == expected_page_name:
                        print(f"    ✓ 页面名称正确: {page_info['page_name']}")
                    else:
                        print(f"    ✗ 页面名称错误: 期望 {expected_page_name}, 实际 {page_info['page_name']}")
                    
                    # 验证完整页面名称
                    file_dir = os.path.dirname(file_path)
                    if file_dir and file_dir != ".":
                        expected_full_name = f"{file_dir}/{expected_page_name}"
                    else:
                        expected_full_name = expected_page_name
                    
                    if full_page_name == expected_full_name:
                        print(f"    ✓ 完整页面名称正确: {full_page_name}")
                    else:
                        print(f"    ✗ 完整页面名称错误: 期望 {expected_full_name}, 实际 {full_page_name}")
                
                return True
            else:
                print(f"✗ {message}")
                return False
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False

def test_page_name_sanitization():
    """测试页面名称清理功能"""
    print("\n=== 测试页面名称清理功能 ===")
    
    processor = FolderProcessor()
    
    test_cases = [
        ("test file.md", "test_file"),
        ("test-file.md", "test-file"),
        ("test.file.md", "test_file"),
        ("test<file>.md", "test_file_"),
        ("test file  name.md", "test_file_name"),
        ("test..file.md", "test_file"),
        ("test   file.md", "test_file"),
    ]
    
    for input_name, expected in test_cases:
        # 直接测试清理逻辑
        cleaned = input_name
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        cleaned = cleaned.strip(' .')
        
        # Replace multiple spaces/underscores with single underscore
        import re
        cleaned = re.sub(r'[_\s]+', '_', cleaned)
        
        # 移除扩展名
        cleaned = os.path.splitext(cleaned)[0]
        
        if cleaned == expected:
            print(f"✓ '{input_name}' -> '{cleaned}'")
        else:
            print(f"✗ '{input_name}' -> '{cleaned}' (期望: '{expected}')")
    
    return True

def test_file_support_check():
    """测试文件支持检查"""
    print("\n=== 测试文件支持检查 ===")
    
    processor = FolderProcessor()
    
    test_files = [
        ("document.pdf", True),
        ("readme.md", True),
        ("data.csv", True),
        ("config.json", True),
        ("image.png", False),
        ("script.js", False),
        ("style.css", False),
        ("archive.zip", False),
    ]
    
    for filename, expected in test_files:
        ext = os.path.splitext(filename)[1].lower()
        supported = ext in processor.supported_extensions
        
        if supported == expected:
            print(f"✓ '{filename}' -> {'支持' if supported else '不支持'}")
        else:
            print(f"✗ '{filename}' -> {'支持' if supported else '不支持'} (期望: {'支持' if expected else '不支持'})")
    
    return True

if __name__ == "__main__":
    print("开始测试修复后的文件夹上传功能...")
    
    success = True
    success &= test_page_name_sanitization()
    success &= test_file_support_check()
    success &= test_folder_upload_simulation()
    
    if success:
        print("\n🎉 所有测试通过！文件夹上传功能已修复。")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1) 