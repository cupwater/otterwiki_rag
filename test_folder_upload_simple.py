#!/usr/bin/env python3
"""
简单的文件夹上传功能测试
"""

import os
import tempfile
import sys

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_folder_processor():
    """测试文件夹处理器"""
    try:
        from otterwiki.folder_processor import FolderProcessor
        print("✓ 成功导入 FolderProcessor")
        
        # 创建处理器
        processor = FolderProcessor()
        print(f"✓ 文件夹处理器创建成功")
        print(f"✓ 支持的扩展名数量: {len(processor.supported_extensions)}")
        
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
        
        print(f"✓ 创建了 {len(mock_files)} 个模拟文件")
        
        # 测试文件夹处理
        with tempfile.TemporaryDirectory() as output_dir:
            success, message, created_pages = processor.process_folder_upload(
                mock_files, output_dir, "test_folder"
            )
            
            print(f"处理结果: {success}")
            print(f"消息: {message}")
            print(f"创建的页面数量: {len(created_pages)}")
            
            if success and created_pages:
                print("\n创建的页面:")
                for file_path, page_info in created_pages.items():
                    print(f"  - {file_path} -> {page_info['full_page_name']}")
                
                # 验证是否创建了3个页面
                if len(created_pages) == 3:
                    print("✓ 成功创建了3个页面，测试通过！")
                    return True
                else:
                    print(f"✗ 期望创建3个页面，实际创建了{len(created_pages)}个页面")
                    return False
            else:
                print("✗ 没有创建任何页面")
                return False
                
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试文件夹上传功能...")
    
    if test_folder_processor():
        print("\n🎉 测试通过！")
    else:
        print("\n❌ 测试失败")
        sys.exit(1) 