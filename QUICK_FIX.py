"""
Chess Bot - 国际象棋机器人
修复版：解决自动识别和坐标计算问题
"""

import cv2
import numpy as np
import pyautogui
import chess
import chess.engine
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from datetime import datetime
import sys

# 修复1: 使用正确的mss导入
try:
    import mss

    MSS_CLASS = mss.MSS  # 使用新的类名
except:
    MSS_CLASS = None


class ChessBot:
    def __init__(self):
        # 修复2: 初始化时添加错误处理和默认值
        self.screen_capturer = None
        if MSS_CLASS:
            try:
                self.screen_capturer = MSS_CLASS()
            except Exception as e:
                print(f"初始化屏幕捕获失败: {e}")

        self.board_region = None
        self.is_running = False
        self.engine = None
        self.board = chess.Board()
        self.square_size = 0
        self.debug_mode = True  # 调试模式

    def capture_screen(self, region=None):
        """截取屏幕区域"""
        try:
            if region:
                # 修复3: 确保区域参数有效
                region = self.validate_region(region)
                if not region:
                    return None

                screenshot = pyautogui.screenshot(region=(
                    region['left'],
                    region['top'],
                    region['width'],
                    region['height']
                ))
            else:
                screenshot = pyautogui.screenshot()

            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def validate_region(self, region):
        """修复4: 验证并修正区域坐标"""
        if not region:
            return None

        try:
            left = int(region.get('left', 0))
            top = int(region.get('top', 0))
            width = int(region.get('width', 0))
            height = int(region.get('height', 0))

            # 确保宽度和高度为正数
            if width < 0:
                left = left + width
                width = abs(width)
            if height < 0:
                top = top + height
                height = abs(height)

            # 确保最小尺寸
            width = max(width, 100)
            height = max(height, 100)

            return {
                'left': left,
                'top': top,
                'width': width,
                'height': height
            }
        except Exception as e:
            print(f"区域验证失败: {e}")
            return None

    def detect_board(self, image=None):
        """修复5: 改进棋盘检测逻辑"""
        if image is None:
            image = self.capture_screen()

        if image is None:
            return None

        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 使用边缘检测
            edges = cv2.Canny(gray, 50, 150)

            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 寻找最大的矩形（假设是棋盘）
            best_rect = None
            best_area = 0

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h

                # 检查是否是正方形（棋盘应该是正方形）
                if area > best_area and w > 200 and h > 200:
                    aspect_ratio = w / float(h)
                    if 0.8 <= aspect_ratio <= 1.2:  # 接近正方形
                        best_area = area
                        best_rect = (x, y, w, h)

            if best_rect:
                x, y, w, h = best_rect
                self.board_region = {
                    'left': x,
                    'top': y,
                    'width': w,
                    'height': h
                }
                self.square_size = w // 8
                return self.board_region

        except Exception as e:
            print(f"棋盘检测失败: {e}")

        return None

    def manual_select_board(self):
        """手动选择棋盘区域"""
        print("\n请手动选择棋盘区域...")
        print("将鼠标移到棋盘左上角，按 Enter 确认")
        input()
        x1, y1 = pyautogui.position()

        print("将鼠标移到棋盘右下角，按 Enter 确认")
        input()
        x2, y2 = pyautogui.position()

        # 修复6: 确保坐标顺序正确
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        self.board_region = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        self.square_size = width // 8

        print(f"已选择区域: {self.board_region}")
        return self.board_region

    def get_square_position(self, square_name):
        """获取棋格在屏幕上的位置"""
        if not self.board_region:
            return None

        # 转换棋格名称到坐标 (如 'e2' -> (4, 1))
        file = ord(square_name[0]) - ord('a')
        rank = int(square_name[1]) - 1

        # 修复7: 处理棋盘方向（假设白方在下方）
        x = self.board_region['left'] + file * self.square_size + self.square_size // 2
        y = self.board_region['top'] + (7 - rank) * self.square_size + self.square_size // 2

        return (x, y)

    def make_move(self, move_uci):
        """执行移动"""
        try:
            move = chess.Move.from_uci(move_uci)
            from_square = chess.square_name(move.from_square)
            to_square = chess.square_name(move.to_square)

            from_pos = self.get_square_position(from_square)
            to_pos = self.get_square_position(to_square)

            if from_pos and to_pos:
                # 点击起始位置
                pyautogui.click(from_pos[0], from_pos[1])
                time.sleep(0.1)

                # 点击目标位置
                pyautogui.click(to_pos[0], to_pos[1])
                time.sleep(0.1)

                return True
        except Exception as e:
            print(f"执行移动失败: {e}")

        return False

    def analyze_position(self, fen=None):
        """分析当前局面"""
        if self.engine:
            try:
                if fen:
                    board = chess.Board(fen)
                else:
                    board = self.board

                result = self.engine.analyse(board, chess.engine.Limit(time=0.1))
                return result
            except Exception as e:
                print(f"分析失败: {e}")

        return None

    def get_best_move(self, fen=None):
        """获取最佳移动"""
        if self.engine:
            try:
                if fen:
                    board = chess.Board(fen)
                else:
                    board = self.board

                result = self.engine.play(board, chess.engine.Limit(time=0.5))
                return result.move
            except Exception as e:
                print(f"获取最佳移动失败: {e}")

        return None

    def save_config(self, filename='chess_bot_config.json'):
        """保存配置"""
        config = {
            'board_region': self.board_region,
            'square_size': self.square_size
        }
        try:
            with open(filename, 'w') as f:
                json.dump(config, f)
            print(f"配置已保存到 {filename}")
        except Exception as e:
            print(f"保存配置失败: {e}")

    def load_config(self, filename='chess_bot_config.json'):
        """加载配置"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    config = json.load(f)
                self.board_region = config.get('board_region')
                self.square_size = config.get('square_size', 0)
                print(f"配置已从 {filename} 加载")
                return True
        except Exception as e:
            print(f"加载配置失败: {e}")

        return False

    def run(self):
        """主运行循环"""
        print("=== 国际象棋机器人启动 ===\n")

        # 尝试加载配置
        if not self.load_config():
            print("未找到配置文件，需要重新识别棋盘\n")

        # 选择模式
        print("请选择模式:")
        print("1. 自动识别屏幕棋盘（默认）")
        print("2. 手动框选棋盘区域")

        try:
            mode = input("\n请选择 (1/2, 默认1): ").strip() or "1"

            if mode == "1":
                print("\n=== 识别棋盘 ===")
                print("正在识别屏幕棋盘...")

                # 给用户时间切换到棋盘窗口
                print("请在3秒内切换到棋盘窗口...")
                time.sleep(3)

                region = self.detect_board()
                if region:
                    print(f"识别成功: {region}")
                else:
                    print("自动识别失败，切换到手动输入模式...")
                    self.manual_select_board()

            elif mode == "2":
                self.manual_select_board()
            else:
                print("无效选择")
                return

        except KeyboardInterrupt:
            print("\n操作已取消")
            return
        except Exception as e:
            print(f"错误: {e}")
            return

        # 保存配置
        self.save_config()

        print("\n=== 准备就绪 ===")
        print(f"棋盘区域: {self.board_region}")
        print(f"格子大小: {self.square_size}")
        print("\n按 Ctrl+C 停止")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n机器人已停止")


def main():
    """主函数"""
    bot = ChessBot()
    bot.run()


if __name__ == "__main__":
    main()
