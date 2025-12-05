#!/usr/bin/env python3
"""
简洁测试：验证简化后的 navigate_to_page_xplore 函数
只显示函数返回的完整信息，无多余调试输出
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# 添加父目录到路径以导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config
from browser_utils import launch_persistent_browser
from xplore_actions import search_xplore, navigate_to_page_xplore, search_extract_xplore

def test_simple_navigation():
    """测试简化后的导航功能"""
    print("=== 测试简化后的 navigate_to_page_xplore 函数 ===\n")
    
    with sync_playwright() as p:
        context = None
        try:
            context, page = launch_persistent_browser(p)
            
            # 导航到 IEEE Xplore
            print("1. 连接到 IEEE Xplore...")
            page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            # 搜索测试关键词
            search_query = "opf flow machine learning"
            print(f"2. 搜索: '{search_query}'")
            search_xplore(page, search_query)
            
            # 等待结果
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except:
                print("  警告：等待页面加载超时")
            time.sleep(5)
            
            # 先提取第1页信息作为基准
            print("\n" + "="*80)
            print("基准：第1页信息")
            print("="*80)
            page1_info = search_extract_xplore(page, start_index=1, end_index=3)
            print(page1_info)
            
            print("\n" + "="*80)
            print("测试用例 1: 导航到第2页（正常情况）")
            print("="*80)
            nav_result = navigate_to_page_xplore(page, 2)
            print(f"导航结果: {nav_result}")
            
            # 提取第2页信息
            page2_info = search_extract_xplore(page, start_index=1, end_index=3)
            print("\n第2页信息：")
            print("-"*80)
            print(page2_info)
            print("-"*80)
            
            print("\n" + "="*80)
            print("测试用例 2: 导航到第3页（正常情况）")
            print("="*80)
            nav_result = navigate_to_page_xplore(page, 3)
            print(f"导航结果: {nav_result}")
            
            # 提取第3页信息
            page3_info = search_extract_xplore(page, start_index=1, end_index=3)
            print("\n第3页信息：")
            print("-"*80)
            print(page3_info)
            print("-"*80)
            
            print("\n" + "="*80)
            print("测试用例 3: 导航回第1页（正常情况）")
            print("="*80)
            nav_result = navigate_to_page_xplore(page, 1)
            print(f"导航结果: {nav_result}")
            
            # 提取第1页信息
            page1_info_again = search_extract_xplore(page, start_index=1, end_index=3)
            print("\n第1页信息：")
            print("-"*80)
            print(page1_info_again)
            print("-"*80)
            
            print("\n" + "="*80)
            print("测试用例 4: 页码为0（不合法情况）")
            print("="*80)
            nav_result = navigate_to_page_xplore(page, 0)
            print(f"导航结果: {nav_result}")
            
            # 检查是否在第1页
            current_page_info = search_extract_xplore(page, start_index=1, end_index=3)
            print("\n当前页面信息：")
            print("-"*80)
            print(current_page_info)
            print("-"*80)
            
            print("\n" + "="*80)
            print("测试用例 5: 页码为100（越界情况）")
            print("="*80)
            nav_result = navigate_to_page_xplore(page, 100)
            print(f"导航结果: {nav_result}")
            
            # 检查是否在第1页
            current_page_info = search_extract_xplore(page, start_index=1, end_index=3)
            print("\n当前页面信息：")
            print("-"*80)
            print(current_page_info)
            print("-"*80)
            
            print("\n" + "="*80)
            print("测试用例 6: 页码为-1（不合法情况）")
            print("="*80)
            nav_result = navigate_to_page_xplore(page, -1)
            print(f"导航结果: {nav_result}")
            
            # 检查是否在第1页
            current_page_info = search_extract_xplore(page, start_index=1, end_index=3)
            print("\n当前页面信息：")
            print("-"*80)
            print(current_page_info)
            print("-"*80)
            
            print("\n=== 所有测试完成 ===")
            
        finally:
            if context:
                input("\n按 Enter 键关闭浏览器...")
                context.close()

if __name__ == "__main__":
    test_simple_navigation()