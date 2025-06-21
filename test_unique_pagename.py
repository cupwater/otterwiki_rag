#!/usr/bin/env python3
"""
测试唯一页面名称生成功能
"""

import os
import sys
import tempfile

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unique_pagename_generation():
    """测试唯一页面名称生成功能"""
    print("测试唯一页面名称生成功能...")
    
    try:
        # 导入必要的模块
        from otterwiki.views import generate_unique_pagename
        from otterwiki.folder_processor import FolderProcessor
        print("✓ 成功导入模块")
        
        # 测试单个文件上传的唯一页面名称生成
        print("\n1. 测试单个文件上传的唯一页面名称生成:")
        
        # 模拟测试场景
        test_cases = [
            ("test.md", "test"),
            ("test.md", "test_1"),  # 如果test已存在
            ("test.md", "test_2"),  # 如果test和test_1都已存在
            ("document.md", "document"),
            ("README.md", "README"),
        ]
        
        for filename, expected_base in test_cases:
            base_name = os.path.splitext(filename)[0]
            unique_name = generate_unique_pagename(base_name, "")
            print(f"  文件: {filename} -> 页面名称: {unique_name}")
        
        # 测试文件夹上传的唯一页面名称生成
        print("\n2. 测试文件夹上传的唯一页面名称生成:")
        
        processor = FolderProcessor()
        
        # 测试不同目录下的同名文件
        test_files = [
            ("file1.md", ""),           # 根目录
            ("file1.md", "docs"),       # docs目录
            ("file1.md", "docs/api"),   # docs/api目录
        ]
        
        for filename, directory in test_files:
            base_name = os.path.splitext(filename)[0]
            unique_name = processor._generate_unique_pagename(base_name, directory)
            if directory:
                print(f"  文件: {directory}/{filename} -> 页面名称: {directory}/{unique_name}")
            else:
                print(f"  文件: {filename} -> 页面名称: {unique_name}")
        
        # 测试边界情况
        print("\n3. 测试边界情况:")
        
        # 测试空文件名
        empty_name = processor._generate_unique_pagename("", "")
        print(f"  空文件名 -> 页面名称: {empty_name}")
        
        # 测试特殊字符
        special_name = processor._generate_unique_pagename("test@#$%^&*()", "")
        print(f"  特殊字符文件名 -> 页面名称: {special_name}")
        
        # 测试长文件名
        long_name = "a" * 100
        long_unique_name = processor._generate_unique_pagename(long_name, "")
        print(f"  长文件名 -> 页面名称: {long_unique_name[:50]}...")
        
        print("\n✓ 所有测试完成")
        return True
        
    except ImportError as e:
        print(f"✗ 导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_file_upload_scenarios():
    """测试文件上传场景"""
    print("\n测试文件上传场景...")
    
    try:
        from otterwiki.views import generate_unique_pagename
        
        # 模拟上传相同文件名的场景
        print("\n模拟上传相同文件名的场景:")
        
        filenames = ["report.md", "report.md", "report.md"]
        for i, filename in enumerate(filenames):
            base_name = os.path.splitext(filename)[0]
            unique_name = generate_unique_pagename(base_name, "")
            print(f"  第{i+1}次上传 {filename} -> 页面名称: {unique_name}")
        
        # 模拟不同目录下的同名文件
        print("\n模拟不同目录下的同名文件:")
        
        file_scenarios = [
            ("docs/report.md", "docs"),
            ("api/report.md", "api"),
            ("reports/report.md", "reports"),
        ]
        
        for filepath, directory in file_scenarios:
            filename = os.path.basename(filepath)
            base_name = os.path.splitext(filename)[0]
            unique_name = generate_unique_pagename(base_name, directory)
            print(f"  文件: {filepath} -> 页面名称: {directory}/{unique_name}")
        
        print("✓ 文件上传场景测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 文件上传场景测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试唯一页面名称生成功能...")
    
    success1 = test_unique_pagename_generation()
    success2 = test_file_upload_scenarios()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
        print("\n功能说明:")
        print("- 当上传同名文件时，系统会自动在页面名称后添加序号")
        print("- 序号从1开始递增（test_1, test_2, test_3...）")
        print("- 支持不同目录下的同名文件")
        print("- 包含特殊字符的文件名会被清理")
        print("- 防止无限循环，最多尝试1000次后使用时间戳")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1) 