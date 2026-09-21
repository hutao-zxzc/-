#!/usr/bin/env python3
"""
鼠标点击测试脚本
验证pyautogui是否正常工作
"""

import pyautogui
import time

def test_mouse():
    """测试鼠标移动和点击"""
    print("=" * 60)
    print("  鼠标控制测试")
    print("=" * 60)

    # 获取当前屏幕大小
    screen_width, screen_height = pyautogui.size()
    print(f"\n屏幕大小: {screen_width} x {screen_height}")

    # 获取当前鼠标位置
    current = pyautogui.position()
    print(f"当前鼠标位置: ({current.x}, {current.y})")

    print("\n将执行以下测试:")
    print("1. 移动鼠标到屏幕中心")
    print("2. 移动鼠标到四个角落")
    print("3. 测试点击")
    print("\n准备开始...")
    input("按Enter开始测试 (请确保鼠标不会干扰): ")

    # 测试1：移动到屏幕中心
    print("\n[测试1] 移动到屏幕中心...")
    center_x = screen_width // 2
    center_y = screen_height // 2
    pyautogui.moveTo(center_x, center_y, duration=1.0)
    time.sleep(1)
    print(f"  鼠标已移动到 ({center_x}, {center_y})")

    # 测试2：移动到四个角落
    print("\n[测试2] 移动到四个角落...")

    corners = [
        ("左上角", 100, 100),
        ("右上角", screen_width - 100, 100),
        ("左下角", 100, screen_height - 100),
        ("右下角", screen_width - 100, screen_height - 100),
    ]

    for name, x, y in corners:
        print(f"  移动到 {name}: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.5)

    # 返回中心
    print("\n  返回屏幕中心...")
    pyautogui.moveTo(center_x, center_y, duration=0.5)
    time.sleep(0.5)

    # 测试3：点击测试
    print("\n[测试3] 点击测试...")
    print("  将执行3次点击，请观察鼠标")

    for i in range(3):
        print(f"    点击 {i+1}/3...")
        pyautogui.click(center_x, center_y, button='left')
        time.sleep(1)

    print("  ✅ 点击测试完成")

    # 测试4：拖拽测试
    print("\n[测试4] 拖拽测试...")
    print("  将从中心拖拽到右下角...")

    pyautogui.moveTo(center_x, center_y, duration=0.5)
    time.sleep(0.3)
    pyautogui.mouseDown(button='left')
    time.sleep(0.3)
    pyautogui.moveTo(screen_width - 100, screen_height - 100, duration=1.0)
    time.sleep(0.3)
    pyautogui.mouseUp(button='left')
    print("  ✅ 拖拽测试完成")

    # 测试5：安全测试
    print("\n[测试5] FAILSAFE功能...")
    print("  如果鼠标移动到屏幕角落，程序会停止")
    print("  这是安全功能，防止失控")

    print("\n" + "=" * 60)
    print("  所有测试完成！")
    print("=" * 60)

    # 返回初始位置
    print(f"\n返回初始位置: ({current.x}, {current.y})")
    pyautogui.moveTo(current.x, current.y, duration=1.0)

def print_tips():
    """打印使用提示"""
    print("\n" + "=" * 60)
    print("  使用提示")
    print("=" * 60)
    print("""
1. 如果鼠标没有移动：
   - 检查是否有防病毒软件阻止
   - 尝试以管理员身份运行
   - 检查pyautogui版本

2. 如果移动不准确：
   - 可能是屏幕缩放问题
   - 调整DPI缩放设置
   - 在Windows显示设置中禁用缩放

3. 如果点击不生效：
   - 可能是时机问题
   - 增加延迟时间
   - 确保窗口在前台

4. 常见问题解决：
   - 更新pyautogui: pip install --upgrade pyautogui
   - 禁用FAILSAFE: pyautogui.FAILSAFE = False
   - 使用更长的duration: moveTo(x, y, duration=1.0)
""")

if __name__ == "__main__":
    try:
        test_mouse()
        print_tips()

        input("\n按Enter退出...")
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()
