#!/usr/bin/env python3
"""
基于颜色匹配的棋子识别器
适合棋子颜色与棋盘有明显差异的场景
"""

import cv2
import numpy as np
import pyautogui
import mss
import chess
from pathlib import Path
import pickle


class ColorBasedRecognizer:
    """基于颜色匹配的识别器"""

    def __init__(self):
        self.screen_capturer = mss.mss()
        self.board_region = None
        self.square_size = None

        # 颜色统计（从第一次识别中学习）
        self.empty_square_color = None
        self.piece_color_range = None

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"✓ 棋盘区域设置完成")

    def capture_square(self, rank, file):
        """捕获单个格子"""
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        square_w, square_h = self.square_size
        y = (7 - rank) * square_h
        x = file * square_w

        return board_img[y:y + square_h, x:x + square_w]

    def analyze_color_histogram(self, img):
        """
        分析颜色直方图
        """
        # 转换为HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 计算直方图
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])

        # 归一化
        h_hist = h_hist.flatten() / np.sum(h_hist)
        s_hist = s_hist.flatten() / np.sum(s_hist)
        v_hist = v_hist.flatten() / np.sum(v_hist)

        return {
            'h': h_hist,
            's': s_hist,
            'v': v_hist
        }

    def histogram_distance(self, hist1, hist2):
        """
        计算直方图距离（使用巴氏距离）
        """
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)

    def detect_piece_by_color(self, square_img):
        """
        使用颜色直方图检测棋子
        """
        # 如果没有学习过空格子颜色，返回默认结果
        if self.empty_square_color is None:
            # 使用简单的阈值检测
            gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            center = gray[h//3:2*h//3, w//3:2*w//3]
            return np.std(center) > 5

        # 计算当前格子的直方图
        current_hist = self.analyze_color_histogram(square_img)
        empty_hist = self.empty_square_color

        # 计算距离
        h_dist = self.histogram_distance(current_hist['h'], empty_hist['h'])
        s_dist = self.histogram_distance(current_hist['s'], empty_hist['s'])
        v_dist = self.histogram_distance(current_hist['v'], empty_hist['v'])

        # 综合距离
        total_dist = (h_dist + s_dist + v_dist) / 3

        # 如果距离大，说明颜色差异大，有棋子
        return total_dist > 0.3

    def learn_empty_squares(self, board_img):
        """
        学习空格子的颜色特征
        """
        print("\n📚 学习空格子颜色特征...")

        # 假设初始位置的一些格子是空的
        # 或者让用户选择一个空格子

        # 简单策略：计算所有格子的平均颜色
        # 然后使用中位数作为空格子颜色

        all_hists = []

        square_w, square_h = self.square_size

        for rank in range(8):
            for file in range(8):
                y = (7 - rank) * square_h
                x = file * square_w

                square = board_img[y:y + square_h, x:x + square_w]

                # 获取中心区域
                h, w = square.shape
                center = square[h//4:3*h//4, w//4:3*w//4]

                hist = self.analyze_color_histogram(center)
                all_hists.append(hist)

        # 计算中位数直方图
        if all_hists:
            # 简化：使用第一个格子的直方图作为参考
            # 实际应用中应该使用更复杂的方法
            self.empty_square_color = all_hists[0]

            print("✓ 空格子颜色特征已学习")
        else:
            print("⚠️  无法学习空格子颜色")

    def scan_board_with_learning(self):
        """
        带学习的棋盘扫描
        """
        print("\n" + "=" * 70)
        print("  🎨 基于颜色匹配的识别器")
        print("=" * 70)

        # 先捕获整个棋盘
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        # 学习空格子
        self.learn_empty_squares(board_img)

        # 扫描棋盘
        board = chess.Board()
        board.clear()

        detected_count = 0

        for rank in range(8):
            for file in range(8):
                square_idx = rank * 8 + file
                square_name = chess.SQUARE_NAMES[square_idx]

                square_img = self.capture_square(rank, file)

                # 检测是否有棋子
                has_piece = self.detect_piece_by_color(square_img)

                if has_piece:
                    detected_count += 1

                    # 识别颜色
                    gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
                    h, w = gray.shape
                    center = gray[h//4:3*h//4, w//4:3*w//4]

                    is_white = np.mean(center) > 128
                    piece = 'P' if is_white else 'p'

                    piece_obj = chess.Piece.from_symbol(piece)
                    board.set_piece_at(square_idx, piece_obj)

                    print(f"  ✓ {square_name}: {'白棋' if is_white else '黑棋'}")
                else:
                    print(f"  ✗ {square_name}: 空")

        print(f"\n📊 检测到 {detected_count} 个棋子")
        print(f"   识别率: {detected_count/64*100:.1f}%")

        return board

    def save_calibration(self, filepath="calibration_color.pkl"):
        """保存校准数据"""
        calibration_data = {
            "board_region": self.board_region,
            "square_size": self.square_size,
            "empty_square_color": self.empty_square_color
        }
        with open(filepath, 'wb') as f:
            pickle.dump(calibration_data, f)
        print(f"✓ 校准数据已保存: {filepath}")


def main():
    """主程序"""
    print("=" * 70)
    print("  🎨 基于颜色匹配的棋子识别器")
    print("  适合棋子颜色与棋盘有明显差异的场景")
    print("=" * 70)

    recognizer = ColorBasedRecognizer()

    # 检查校准
    calib_file = Path(__file__).parent / "calibration_color.pkl"
    if calib_file.exists():
        with open(calib_file, 'rb') as f:
            data = pickle.load(f)
        recognizer.board_region = data["board_region"]
        recognizer.square_size = data["square_size"]
        recognizer.empty_square_color = data["empty_square_color"]
        print(f"\n✓ 已加载校准数据")
    else:
        print("\n=== 棋盘校准 ===")
        print("1. 点击棋盘左上角...")
        input("按Enter后点击左上角，然后按Enter继续...")

        x1, y1 = pyautogui.position()
        print(f"  左上角: ({x1}, {y1})")

        print("2. 点击棋盘右下角...")
        input("按Enter后点击右下角，然后按Enter继续...")

        x2, y2 = pyautogui.position()
        print(f"  右下角: ({x2}, {y2})")

        recognizer.set_board_region(x1, y1, x2, y2)
        recognizer.save_calibration()

    # 扫描棋盘
    board = recognizer.scan_board_with_learning()

    # 显示结果
    print("\n" + "=" * 70)
    print("  ♟️  识别的棋盘")
    print("=" * 70)
    print(board)

    # 保存FEN
    fen = board.fen()
    print(f"\n📋 FEN字符串:")
    print(fen)

    fen_file = Path(__file__).parent / "recognized_fen_color.txt"
    with open(fen_file, 'w') as f:
        f.write(fen)
    print(f"✓ FEN已保存: {fen_file}")

    print("\n" + "=" * 70)
    print("  完成！")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
