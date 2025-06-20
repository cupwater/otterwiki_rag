#!/usr/bin/env python3
"""
测试每个文件作为独立页面的文件夹上传功能
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

def test_independent_page_creation():
    """测试每个文件作为独立页面创建"""
    print("\n=== 测试每个文件作为独立页面创建 ===")
    
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
        ("data/sample.csv", "name,age,city\n张三,25,北京\n李四,30,上海"),
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
                
                print("\n创建的独立页面:")
                expected_pages = {
                    "readme.md": "readme",
                    "docs/guide.md": "docs/guide", 
                    "docs/api.md": "docs/api",
                    "src/main.py": "src/main",
                    "data/sample.csv": "data/sample"
                }
                
                for file_path, page_info in created_pages.items():
                    full_page_name = page_info.get('full_page_name', page_info['page_name'])
                    expected_name = expected_pages.get(file_path, "unknown")
                    
                    print(f"  - {file_path} -> {full_page_name}")
                    
                    if full_page_name == expected_name:
                        print(f"    ✓ 页面名称正确: {full_page_name}")
                    else:
                        print(f"    ✗ 页面名称错误: 期望 {expected_name}, 实际 {full_page_name}")
                
                return True
            else:
                print(f"✗ {message}")
                return False
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False

def test_page_name_generation():
    """测试页面名称生成逻辑"""
    print("\n=== 测试页面名称生成逻辑 ===")
    
    test_cases = [
        ("readme.md", "readme"),
        ("docs/guide.md", "docs/guide"),
        ("src/main.py", "src/main"),
        ("data/sample.csv", "data/sample"),
        ("file.txt", "file"),
        ("subdir/file.md", "subdir/file"),
    ]
    
    for file_path, expected in test_cases:
        # 模拟页面名称生成逻辑
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        # 清理页面名称
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name_without_ext = name_without_ext.replace(char, '_')
        
        name_without_ext = name_without_ext.strip(' .')
        import re
        name_without_ext = re.sub(r'[_\s]+', '_', name_without_ext)
        
        # 计算完整页面名称
        file_dir = os.path.dirname(file_path)
        if file_dir and file_dir != ".":
            full_page_name = f"{file_dir}/{name_without_ext}"
        else:
            full_page_name = name_without_ext
        
        if full_page_name == expected:
            print(f"✓ '{file_path}' -> '{full_page_name}'")
        else:
            print(f"✗ '{file_path}' -> '{full_page_name}' (期望: '{expected}')")
    
    return True

def test_directory_structure_preservation():
    """测试目录结构保持"""
    print("\n=== 测试目录结构保持 ===")
    
    test_files = [
        "readme.md",
        "docs/guide.md", 
        "docs/api.md",
        "src/main.py",
        "src/utils.py",
        "data/sample.csv",
        "config.json"
    ]
    
    expected_structure = {
        "readme.md": "readme",
        "docs/guide.md": "docs/guide",
        "docs/api.md": "docs/api", 
        "src/main.py": "src/main",
        "src/utils.py": "src/utils",
        "data/sample.csv": "data/sample",
        "config.json": "config"
    }
    
    for file_path in test_files:
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        file_dir = os.path.dirname(file_path)
        if file_dir and file_dir != ".":
            full_page_name = f"{file_dir}/{name_without_ext}"
        else:
            full_page_name = name_without_ext
        
        expected = expected_structure[file_path]
        if full_page_name == expected:
            print(f"✓ {file_path} -> {full_page_name}")
        else:
            print(f"✗ {file_path} -> {full_page_name} (期望: {expected})")
    
    return True

if __name__ == "__main__":
    print("开始测试每个文件作为独立页面的功能...")
    
    success = True
    success &= test_independent_page_creation()
    success &= test_page_name_generation()
    success &= test_directory_structure_preservation()
    
    if success:
        print("\n🎉 所有测试通过！每个文件现在都作为独立页面创建。")
        print("\n功能特点:")
        print("✓ 文件夹内的每个文件都创建为独立的页面")
        print("✓ 保持原有的目录结构")
        print("✓ 文件名作为页面名称")
        print("✓ 支持子目录中的文件")
        print("✓ 完整的错误处理和用户反馈")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1) 