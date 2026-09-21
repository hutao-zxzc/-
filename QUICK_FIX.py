#!/usr/bin/env python3
"""
快速修复棋子识别问题
"""

import cv2
import numpy as np
import pyautogui
import mss
import chess
from pathlib import Path
import sys


class QuickFixBot:
    """快速修复版本 - 使用宽松的识别阈值"""

    def __init__(self):
        self.screen_capturer = mss.mss()
        self.board_region = None
        self.square_size = None

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"✓ 棋盘区域设置完成: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"✓ 格子大小: {self.square_size}")

    def capture_square(self, rank, file):
        """捕获单个格子"""
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        square_w, square_h = self.square_size
        y = (7 - rank) * square_h
        x = file * square_w

        return board_img[y:y + square_h, x:x + square_w]

    def recognize_piece_v2(self, square_img):
        """
        改进的识别方法 - 使用宽松的阈值
        """
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 获取多个区域（更灵活）
        regions = {
            'center': gray[h//3:2*h//3, w//3:2*w//3],  # 中心1/3
            'whole': gray[h//4:3*h//4, w//4:3*w//4],   # 中心1/2
        }

        # 多种检测方法
        detection_scores = []

        for region_name, region in regions.items():
            mean_val = np.mean(region)
            std_dev = np.std(region)

            # 检测1：标准差（宽松阈值）
            score1 = 1 if std_dev > 8 else 0  # 从30降到8

            # 检测2：亮度范围（更宽松）
            min_val = np.min(region)
            max_val = np.max(region)
            score2 = 1 if (max_val - min_val) > 15 else 0  # 从25降到15

            # 检测3：边缘检测（更敏感）
            edges = cv2.Canny(region, 30, 80)  # 降低阈值
            edge_pixels = np.sum(edges > 0)
            edge_ratio = edge_pixels / region.size
            score3 = 1 if edge_ratio > 0.02 else 0  # 从0.05降到0.02

            detection_scores.append(score1 + score2 + score3)

        # 综合判断（至少2种方法检测到棋子）
        total_score = sum(detection_scores)
        has_piece = total_score >= 4  # 6分中至少4分

        if not has_piece:
            return None

        # 识别颜色
        center_mean = np.mean(regions['center'])
        is_white_piece = center_mean > 128

        # 识别棋子类型（简化版，但更准确）
        # 使用轮廓分析
        edges = cv2.Canny(regions['whole'], 50, 120)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            # 有棋子但没检测到轮廓，可能是兵
            return 'P' if is_white_piece else 'p'

        # 获取最大轮廓
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)
        perimeter = cv2.arcLength(max_contour, True)

        # 计算特征
        area_ratio = area / regions['whole'].size
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

        # 改进的分类逻辑
        if area_ratio > 0.4:
            # 大面积：可能是后或王
            if circularity > 0.6:
                return 'Q' if is_white_piece else 'q'
            else:
                return 'K' if is_white_piece else 'k'
        elif area_ratio > 0.25:
            # 中等面积：可能是车或象
            if circularity < 0.4:
                return 'R' if is_white_piece else 'r'
            else:
                return 'B' if is_white_piece else 'b'
        else:
            # 小面积：可能是马或兵
            if circularity > 0.5:
                return 'P' if is_white_piece else 'p'
            else:
                return 'N' if is_white_piece else 'n'

    def scan_board(self):
        """扫描整个棋盘"""
        print("\n=== 开始扫描棋盘 ===")

        board = chess.Board()
        board.clear()

        recognized_count = 0
        empty_count = 0

        for rank in range(8):
            for file in range(8):
                square_idx = rank * 8 + file
                square_name = chess.SQUARE_NAMES[square_idx]

                square_img = self.capture_square(rank, file)
                piece = self.recognize_piece_v2(square_img)

                if piece:
                    piece_obj = chess.Piece.from_symbol(piece)
                    board.set_piece_at(square_idx, piece_obj)
                    print(f"  ✓ {square_name}: {piece}")
                    recognized_count += 1
                else:
                    empty_count += 1
                    if empty_count <= 3:  # 只显示前3个空格子
                        print(f"  ✗ {square_name}: 空")

        print(f"\n识别结果: {recognized_count} 个棋子, {empty_count} 个空格子")
        print("\n当前棋局:")
        print(board)

        return board

    def save_calibration(self, filepath="calibration_v2.pkl"):
        """保存校准数据"""
        import pickle
        calibration_data = {
            "board_region": self.board_region,
            "square_size": self.square_size
        }
        with open(filepath, 'wb') as f:
            pickle.dump(calibration_data, f)
        print(f"✓ 校准数据已保存: {filepath}")


def main():
    """主程序"""
    print("=" * 70)
    print("  快速修复 - 棋子识别改进版")
    print("=" * 70)
    print("\n改进点:")
    print("  1. ✓ 降低识别阈值，更容易检测到棋子")
    print("  2. ✓ 使用多种检测方法，提高准确率")
    print("  3. ✓ 改进棋子分类逻辑")
    print("  4. ✓ 保存校准数据，下次使用")
    print("=" * 70)

    bot = QuickFixBot()

    # 检查是否有保存的校准
    calib_file = Path(__file__).parent / "calibration_v2.pkl"
    if calib_file.exists():
        import pickle
        with open(calib_file, 'rb') as f:
            data = pickle.load(f)
        bot.board_region = data["board_region"]
        bot.square_size = data["square_size"]
        print(f"\n✓ 已加载校准数据: {calib_file}")
    else:
        print("\n=== 棋盘校准 ===")
        print("1. 请点击棋盘左上角...")
        input("按Enter后点击左上角，然后按Enter继续...")

        x1, y1 = pyautogui.position()
        print(f"  左上角: ({x1}, {y1})")

        print("2. 请点击棋盘右下角...")
        input("按Enter后点击右下角，然后按Enter继续...")

        x2, y2 = pyautogui.position()
        print(f"  右下角: ({x2}, {y2})")

        bot.set_board_region(x1, y1, x2, y2)
        bot.save_calibration()

    # 测试识别
    print("\n=== 测试识别 ===")
    try:
        board = bot.scan_board()

        print("\n=== 识别结果验证 ===")
        print(f"棋子总数: {len(list(board.piece_map().keys()))}")

        # 保存识别结果
        output_file = Path(__file__).parent / "recognized_fen.txt"
        with open(output_file, 'w') as f:
            f.write(board.fen())
        print(f"\n✓ FEN字符串已保存: {output_file}")
        print(f"  FEN: {board.fen()}")

    except Exception as e:
        print(f"\n❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 70)
    print("  完成！")
    print("=" * 70)
    print("\n提示:")
    print("  1. 如果识别还不准确，请检查:")
    print("     - 棋盘是否完全可见")
    print("     - 光线是否充足")
    print("     - 棋子样式是否清晰")
    print("  2. 仍然识别不准？建议使用FEN手动输入模式")
    print("  3. 或者训练一个神经网络模型（需要大量标注数据）")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
