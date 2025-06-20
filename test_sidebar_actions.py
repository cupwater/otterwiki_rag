#!/usr/bin/env python3
"""
测试侧边栏删除和重命名功能
"""

import requests

def test_sidebar_actions():
    """测试侧边栏删除和重命名功能"""
    
    # 配置
    base_url = "http://localhost:5000"
    
    print("测试侧边栏删除和重命名功能")
    print("=" * 50)
    
    # 1. 测试访问首页，检查侧边栏是否包含删除和重命名按钮
    print("1. 测试首页侧边栏...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            content = response.text
            if "重命名页面" in content and "删除页面" in content:
                print("   ✓ 侧边栏包含删除和重命名按钮")
            else:
                print("   ✗ 侧边栏未找到删除和重命名按钮")
        else:
            print(f"   ✗ 访问首页失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    # 2. 测试访问具体页面，检查侧边栏功能
    print("\n2. 测试具体页面侧边栏...")
    test_page = "test_page"
    try:
        response = requests.get(f"{base_url}/{test_page}")
        if response.status_code == 200:
            content = response.text
            if "重命名页面" in content and "删除页面" in content:
                print("   ✓ 页面侧边栏包含删除和重命名按钮")
            else:
                print("   ✗ 页面侧边栏未找到删除和重命名按钮")
        else:
            print(f"   ✗ 访问测试页面失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
    
    # 3. 测试删除和重命名链接是否正确
    print("\n3. 测试链接URL...")
    try:
        # 测试重命名链接
        rename_url = f"{base_url}/{test_page}/rename"
        response = requests.get(rename_url)
        if response.status_code in [200, 403]:  # 200成功或403权限不足都是正常的
            print("   ✓ 重命名链接可访问")
        else:
            print(f"   ✗ 重命名链接访问失败: {response.status_code}")
        
        # 测试删除链接
        delete_url = f"{base_url}/{test_page}/delete"
        response = requests.get(delete_url)
        if response.status_code in [200, 403]:  # 200成功或403权限不足都是正常的
            print("   ✓ 删除链接可访问")
        else:
            print(f"   ✗ 删除链接访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ 链接测试失败: {e}")
    
    print("\n测试完成！")
    print("\n注意事项:")
    print("- 删除和重命名功能需要WRITE权限")
    print("- 首页(Home)不会显示删除和重命名按钮")
    print("- 删除按钮使用红色样式(text-danger)突出显示")

if __name__ == "__main__":
    test_sidebar_actions() 