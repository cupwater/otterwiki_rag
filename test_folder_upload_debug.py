#!/usr/bin/env python3
"""
调试文件夹上传功能的脚本
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

def create_test_folder():
    """创建测试文件夹结构"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件夹结构
        test_structure = {
            "file1.md": "# 文件1\n\n这是第一个文件的内容。",
            "file2.md": "# 文件2\n\n这是第二个文件的内容。",
            "file3.md": "# 文件3\n\n这是第三个文件的内容。",
        }
        
        # 创建文件和目录
        for file_path, content in test_structure.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 创建测试文件: {file_path}")
        
        return temp_dir

def test_folder_processor_debug():
    """调试文件夹处理器"""
    print("\n=== 调试文件夹处理器 ===")
    
    # 创建处理器
    processor = FolderProcessor()
    print(f"✓ 文件夹处理器创建成功")
    
    # 模拟FileStorage对象
    class MockFileStorage:
        def __init__(self, filename, content):
            self.filename = filename
            self.content = content
        
        def save(self, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.content)
    
    # 创建模拟文件列表 - 模拟三个文件
    mock_files = []
    test_files = [
        ("file1.md", "# 文件1\n\n这是第一个文件的内容。"),
        ("file2.md", "# 文件2\n\n这是第二个文件的内容。"),
        ("file3.md", "# 文件3\n\n这是第三个文件的内容。"),
    ]
    
    for filename, content in test_files:
        mock_files.append(MockFileStorage(filename, content))
    
    print(f"✓ 创建了 {len(mock_files)} 个模拟文件")
    
    # 测试文件夹处理
    with tempfile.TemporaryDirectory() as output_dir:
        try:
            print(f"\n--- 开始处理文件夹 ---")
            success, message, created_pages = processor.process_folder_upload(
                mock_files, output_dir, "test_folder"
            )
            
            print(f"处理结果: {success}")
            print(f"消息: {message}")
            print(f"创建的页面数量: {len(created_pages)}")
            
            if success and created_pages:
                print("\n--- 创建的页面详情 ---")
                for file_path, page_info in created_pages.items():
                    print(f"文件路径: {file_path}")
                    print(f"页面名称: {page_info['page_name']}")
                    print(f"完整页面名称: {page_info['full_page_name']}")
                    print(f"页面目录: {page_info['page_dir']}")
                    print(f"内容长度: {len(page_info['content'])} 字符")
                    print(f"内容预览: {page_info['content'][:100]}...")
                    print("---")
            else:
                print("✗ 没有创建任何页面")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_file_parsing():
    """测试文件解析"""
    print("\n=== 测试文件解析 ===")
    
    try:
        from otterwiki.file_parser import FileParser
        parser = FileParser()
        
        # 创建测试文件
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.md")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("# 测试文件\n\n这是测试内容。")
            
            # 测试解析
            content = parser.parse_file(test_file, "test.md", temp_dir)
            print(f"✓ 文件解析成功，内容长度: {len(content)}")
            print(f"内容预览: {content[:100]}...")
            
    except Exception as e:
        print(f"✗ 文件解析测试失败: {e}")
        return False
    
    return True

def test_page_creation_simulation():
    """模拟页面创建过程"""
    print("\n=== 模拟页面创建过程 ===")
    
    try:
        from otterwiki.folder_processor import FolderProcessor
        processor = FolderProcessor()
        
        # 模拟FileStorage对象
        class MockFileStorage:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
            
            def save(self, path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.content)
        
        # 创建三个测试文件
        mock_files = [
            MockFileStorage("file1.md", "# 文件1\n\n这是第一个文件的内容。"),
            MockFileStorage("file2.md", "# 文件2\n\n这是第二个文件的内容。"),
            MockFileStorage("file3.md", "# 文件3\n\n这是第三个文件的内容。"),
        ]
        
        with tempfile.TemporaryDirectory() as output_dir:
            # 第一步：处理文件夹
            success, message, created_pages = processor.process_folder_upload(
                mock_files, output_dir, "test_folder"
            )
            
            print(f"文件夹处理结果: {success}")
            print(f"创建的页面数量: {len(created_pages)}")
            
            if success and created_pages:
                # 第二步：模拟页面创建（类似views.py中的逻辑）
                created_count = 0
                for file_path, page_info in created_pages.items():
                    try:
                        full_page_name = page_info['full_page_name']
                        content = page_info['content']
                        
                        print(f"正在创建页面: {full_page_name}")
                        print(f"内容长度: {len(content)} 字符")
                        
                        # 模拟保存到文件系统
                        page_file = os.path.join(output_dir, f"{full_page_name}.md")
                        os.makedirs(os.path.dirname(page_file), exist_ok=True)
                        with open(page_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        created_count += 1
                        print(f"✓ 成功创建页面: {full_page_name}")
                        
                    except Exception as e:
                        print(f"✗ 创建页面失败 {file_path}: {str(e)}")
                
                print(f"\n总结: 成功创建了 {created_count} 个页面")
                
                # 检查实际创建的文件
                print("\n--- 检查实际创建的文件 ---")
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, output_dir)
                            print(f"找到文件: {rel_path}")
                
            else:
                print("✗ 文件夹处理失败或没有创建页面")
                
    except Exception as e:
        print(f"✗ 页面创建模拟失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("开始调试文件夹上传功能...")
    
    success = True
    success &= test_folder_processor_debug()
    success &= test_file_parsing()
    success &= test_page_creation_simulation()
    
    if success:
        print("\n🎉 所有测试完成！")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1) 