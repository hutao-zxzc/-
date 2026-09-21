#!/usr/bin/env python3
"""
棋盘校准工具
可视化辅助工具，帮助用户精确校准棋盘区域
"""

import cv2
import numpy as np
import mss
import pyautogui
from typing import Tuple, Optional
import pickle
from pathlib import Path


class CalibrationTool:
    """棋盘校准工具"""

    def __init__(self):
        self.screen_capturer = mss.mss()
        self.calibration_points = []  # 存储校准点 [tl, tr, bl, br]

    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        return pyautogui.size()

    def capture_screen(self) -> np.ndarray:
        """捕获整个屏幕"""
        monitor = self.screen_capturer.monitors[0]
        screenshot = self.screen_capturer.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def draw_calibration_ui(self, img: np.ndarray) -> np.ndarray:
        """
        绘制校准UI

        Args:
            img: 屏幕图像

        Returns:
            带UI的图像
        """
        display = img.copy()
        h, w = img.shape[:2]

        # 绘制网格线（辅助定位）
        for i in range(1, 10):
            x = w // 10 * i
            cv2.line(display, (x, 0), (x, h), (50, 50, 50), 1)
            y = h // 10 * i
            cv2.line(display, (0, y), (w, y), (50, 50, 50), 1)

        # 绘制已选择的点
        for i, point in enumerate(self.calibration_points):
            color = (0, 255, 0)
            cv2.circle(display, point, 10, color, -1)
            cv2.putText(display, f"P{i+1}", point, cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (255, 255, 255), 2)

        # 如果有4个点，绘制矩形
        if len(self.calibration_points) == 4:
            tl, tr, bl, br = self.calibration_points

            # 计算棋盘边界
            x1 = min(tl[0], bl[0])
            x2 = max(tr[0], br[0])
            y1 = min(tl[1], tr[1])
            y2 = max(bl[1], br[1])

            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 绘制9x9网格线
            for i in range(9):
                x = x1 + (x2 - x1) // 8 * i
                cv2.line(display, (x, y1), (x, y2), (0, 255, 0), 1)
                y = y1 + (y2 - y1) // 8 * i
                cv2.line(display, (x1, y), (x2, y), (0, 255, 0), 1)

        # 绘制说明文字
        text = f"已选择 {len(self.calibration_points)}/4 个点"
        cv2.putText(display, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (0, 255, 0), 2)

        instructions = [
            "操作说明:",
            "- 鼠标左键: 添加校准点",
            "- 鼠标右键: 清除所有点",
            "- 按 ESC: 退出并保存",
            "- 按 R: 重置所有点",
            "- 按 SPACE: 完成校准",
        ]

        for i, line in enumerate(instructions):
            cv2.putText(display, line, (20, 80 + i * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return display

    def run_interactive_calibration(self):
        """运行交互式校准"""
        print("=== 棋盘校准工具 ===")
        print("请按照提示操作...")

        cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Calibration', cv2.WND_PROP_FULLSCREEN,
                             cv2.WINDOW_FULLSCREEN)

        while True:
            # 捕获屏幕
            screen_img = self.capture_screen()

            # 绘制UI
            display = self.draw_calibration_ui(screen_img)

            # 显示图像
            cv2.imshow('Calibration', display)

            # 获取鼠标位置
            mouse_pos = pyautogui.position()

            # 设置鼠标回调
            cv2.setMouseCallback('Calibration', self._mouse_callback, mouse_pos)

            key = cv2.waitKey(1) & 0xFF

            # 键盘事件处理
            if key == 27:  # ESC
                if len(self.calibration_points) == 4:
                    print("校准完成，保存数据...")
                    break
                else:
                    print("需要选择4个点才能完成校准")
            elif key == ord('r'):
                self.calibration_points = []
                print("已重置所有校准点")
            elif key == 32:  # SPACE
                if len(self.calibration_points) == 4:
                    print("校准完成，保存数据...")
                    break
                else:
                    print(f"当前已选择 {len(self.calibration_points)} 个点，需要4个")

        cv2.destroyAllWindows()

    def _mouse_callback(self, event, x, y, flags, param):
        """鼠标回调函数"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.calibration_points) < 4:
                self.calibration_points.append((x, y))
                print(f"添加校准点 P{len(self.calibration_points)}: ({x}, {y})")
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.calibration_points = []
            print("已清除所有校准点")

    def get_board_region(self) -> Optional[dict]:
        """
        获取棋盘区域

        Returns:
            棋盘区域字典
        """
        if len(self.calibration_points) != 4:
            return None

        tl, tr, bl, br = self.calibration_points

        # 计算棋盘边界
        x1 = min(tl[0], bl[0])
        x2 = max(tr[0], br[0])
        y1 = min(tl[1], tr[1])
        y2 = max(bl[1], br[1])

        return {
            "top": y1,
            "left": x1,
            "width": x2 - x1,
            "height": y2 - y1
        }

    def save_calibration(self, filepath: str):
        """
        保存校准数据

        Args:
            filepath: 保存路径
        """
        board_region = self.get_board_region()

        # 计算棋盘大小和格子大小
        board_width = board_region["width"]
        board_height = board_region["height"]
        square_w = board_width // 8
        square_h = board_height // 8

        calibration_data = {
            "calibration_points": self.calibration_points,
            "board_region": board_region,
            "board_size": (board_width, board_height),
            "square_size": (square_w, square_h)
        }

        with open(filepath, 'wb') as f:
            pickle.dump(calibration_data, f)
        print(f"校准数据已保存到: {filepath}")
        print(f"棋盘大小: {board_width}x{board_height}, 格子大小: {square_w}x{square_h}")

    def load_calibration(self, filepath: str):
        """
        加载校准数据

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'rb') as f:
                calibration_data = pickle.load(f)

            self.calibration_points = calibration_data["calibration_points"]
            board_region = calibration_data["board_region"]
            print(f"校准数据已加载: {filepath}")
            print(f"棋盘区域: {board_region}")
            return board_region
        except FileNotFoundError:
            print(f"文件不存在: {filepath}")
            return None
        except Exception as e:
            print(f"加载校准数据失败: {e}")
            return None

    def preview_board(self, board_region: dict, save_path: str = "board_preview.png"):
        """
        预览棋盘区域

        Args:
            board_region: 棋盘区域
            save_path: 保存路径
        """
        screenshot = self.screen_capturer.grab(board_region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 绘制网格线
        h, w = img.shape[:2]
        for i in range(9):
            x = w // 8 * i
            cv2.line(img, (x, 0), (x, h), (0, 255, 0), 1)
            y = h // 8 * i
            cv2.line(img, (0, y), (w, y), (0, 255, 0), 1)

        # 保存图像
        cv2.imwrite(save_path, img)
        print(f"棋盘预览已保存: {save_path}")

        # 显示预览
        cv2.imshow('Board Preview', img)
        cv2.waitKey(3000)  # 显示3秒
        cv2.destroyAllWindows()


def main():
    """主程序"""
    print("=== 棋盘校准工具 ===\n")

    tool = CalibrationTool()
    calib_file = Path(__file__).parent / "calibration.pkl"

    # 检查是否已有校准数据
    if calib_file.exists():
        print("发现已有校准数据")
        print("1. 加载已有校准数据")
        print("2. 重新校准")
        choice = input("请选择 (1/2): ").strip()

        if choice == "1":
            board_region = tool.load_calibration(str(calib_file))
            if board_region:
                tool.preview_board(board_region)
            return

    # 运行交互式校准
    tool.run_interactive_calibration()

    # 获取棋盘区域
    board_region = tool.get_board_region()

    if board_region:
        print(f"\n棋盘区域: {board_region}")

        # 保存校准数据
        tool.save_calibration(str(calib_file))

        # 预览棋盘
        tool.preview_board(board_region)

        print("\n校准完成！现在可以使用 chess_bot.py 进行对弈了。")
    else:
        print("校准失败，请重试")


if __name__ == "__main__":
    main()
