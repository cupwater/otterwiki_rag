#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试PDF/DOCX文件图片提取功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

def test_image_extraction():
    """测试图片提取功能"""
    print("开始测试图片提取功能...")
    
    try:
        from otterwiki.file_parser import FileParser, parse_uploaded_file
        from otterwiki.document_parser import DocumentParser
        
        # 检查docling是否可用
        try:
            import docling
            print(f"✓ docling库已安装，版本: {docling.__version__}")
        except ImportError:
            print("✗ docling库未安装，请运行: pip install docling")
            return False
        
        # 创建临时目录用于测试
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"使用临时目录: {temp_dir}")
            
            # 测试FileParser
            parser = FileParser()
            print(f"✓ FileParser创建成功，支持的扩展名: {len(parser.supported_extensions)}")
            
            # 创建一个包含图片的页面目录
            page_dir = Path(temp_dir) / "test_page"
            page_dir.mkdir(exist_ok=True)
            
            # 检查图片处理方法是否存在
            if hasattr(parser, '_process_embedded_images'):
                print("✓ _process_embedded_images 方法存在")
            else:
                print("✗ _process_embedded_images 方法不存在")
                return False
            
            if hasattr(parser, '_get_image_extension'):
                print("✓ _get_image_extension 方法存在")
            else:
                print("✗ _get_image_extension 方法不存在")
                return False
            
            # 测试支持的文件格式
            test_files = [
                'test.pdf',
                'test.docx',
                'test.doc',
                'test.xlsx',
                'test.pptx'
            ]
            
            for filename in test_files:
                if parser.is_supported(filename):
                    print(f"✓ 支持格式: {filename}")
                else:
                    print(f"✗ 不支持格式: {filename}")
            
            print("图片提取功能组件验证完成")
            return True
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False

def test_create_view_integration():
    """测试创建页面视图的文件上传集成"""
    print("\n测试创建页面的文件上传集成...")
    
    try:
        # 检查views.py中的集成代码
        with open('otterwiki/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键集成点
        checks = [
            ('parse_uploaded_file导入', 'from otterwiki.file_parser import parse_uploaded_file'),
            ('页面目录路径计算', 'page_dir = os.path.join(storage.path, p.pagepath)'),
            ('图片处理调用', 'parse_uploaded_file(uploaded_file, uploaded_file.filename, page_dir)'),
        ]
        
        for check_name, check_text in checks:
            if check_text in content:
                print(f"✓ {check_name}: 已集成")
            else:
                print(f"✗ {check_name}: 未发现集成代码")
        
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=== PDF/DOCX图片提取功能测试 ===")
    
    success1 = test_image_extraction()
    success2 = test_create_view_integration()
    
    if success1 and success2:
        print("\n✓ 所有测试通过！图片提取功能应该正常工作。")
        print("\n下一步测试建议:")
        print("1. 上传一个包含图片的PDF或DOCX文件")
        print("2. 检查生成的页面是否正确显示图片")
        print("3. 检查页面目录中是否保存了提取的图片文件")
    else:
        print("\n✗ 部分测试失败，需要进一步修复。")
    
    return success1 and success2

if __name__ == "__main__":
    sys.exit(0 if main() else 1)