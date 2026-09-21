#!/usr/bin/env python3
"""
棋子识别调试工具
帮助诊断为什么识别不到棋子
"""

import cv2
import numpy as np
import pyautogui
import mss
from pathlib import Path
import sys


class PieceRecognitionDebugger:
    """棋子识别调试器"""

    def __init__(self):
        """初始化调试器"""
        self.screen_capturer = mss.mss()
        self.board_region = None
        self.square_size = None

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"棋盘区域: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"格子大小: {self.square_size}")

    def capture_square(self, rank, file):
        """
        捕获单个格子

        Args:
            rank: 0-7, 从下到上
            file: 0-7, 从左到右

        Returns:
            格子图像
        """
        if not self.board_region:
            raise ValueError("请先设置棋盘区域")

        # 捕获棋盘
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        # 提取单个格子
        square_w, square_h = self.square_size

        y = (7 - rank) * square_h
        x = file * square_w

        square = board_img[y:y + square_h, x:x + square_w]

        return square

    def analyze_square(self, square_img, rank, file):
        """
        分析单个格子

        Args:
            square_img: 格子图像
            rank: 行号
            file: 列号
        """
        print(f"\n格子 ({rank}, {file}) - {chess.SQUARE_NAMES[rank * 8 + file]}")
        print("=" * 50)

        # 基本信息
        print(f"图像尺寸: {square_img.shape}")

        # 转换为灰度图
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

        # 获取中心区域
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]

        # 统计信息
        mean_val = np.mean(center_region)
        std_dev = np.std(center_region)

        print(f"中心区域均值: {mean_val:.2f}")
        print(f"中心区域标准差: {std_dev:.2f}")

        # 阈值分割
        _, binary = cv2.threshold(center_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        white_pixels = np.sum(binary == 255)
        black_pixels = np.sum(binary == 0)
        total = white_pixels + black_pixels

        print(f"白色像素: {white_pixels} ({white_pixels/total*100:.1f}%)")
        print(f"黑色像素: {black_pixels} ({black_pixels/total*100:.1f}%)")

        # 检测棋子（使用宽松的阈值）
        # 方法1：标准差
        has_piece_std = std_dev > 10
        print(f"\n方法1 (标准差): {'✓ 有棋子' if has_piece_std else '✗ 无棋子'}")

        # 方法2：像素比例
        has_piece_pixels = (black_pixels / total) > 0.05
        print(f"方法2 (像素比例): {'✓ 有棋子' if has_piece_pixels else '✗ 无棋子'}")

        # 方法3：边缘检测
        edges = cv2.Canny(center_region, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        has_piece_edges = len(contours) > 0
        print(f"方法3 (边缘检测): {'✓ 有棋子' if has_piece_edges else '✗ 无棋子'}")

        # 综合判断
        has_piece = has_piece_std or has_piece_pixels or has_piece_edges
        print(f"\n综合判断: {'✓ 有棋子' if has_piece else '✗ 无棋子'}")

        # 识别棋子类型
        if has_piece:
            is_white_piece = mean_val > 128
            if has_piece_edges and len(contours) > 0:
                max_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_contour)
                perimeter = cv2.arcLength(max_contour, True)

                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                else:
                    circularity = 0

                print(f"\n轮廓面积: {area:.2f}")
                print(f"轮廓周长: {perimeter:.2f}")
                print(f"圆形度: {circularity:.3f}")

                if circularity > 0.6:
                    piece_guess = "后/兵" if area > center_region.size * 0.3 else "兵"
                elif circularity < 0.3:
                    piece_guess = "车/象"
                else:
                    piece_guess = "马"

                color_guess = "白棋" if is_white_piece else "黑棋"
                print(f"棋子猜测: {color_guess} {piece_guess}")
            else:
                color_guess = "白棋" if is_white_piece else "黑棋"
                print(f"\n棋子猜测: {color_guess} 兵（简化识别）")

        print("=" * 50)

    def test_specific_squares(self, square_names):
        """
        测试特定的格子

        Args:
            square_names: 格子名称列表，如 ['e2', 'e4', 'd4']
        """
        print("\n" + "=" * 70)
        print("  测试指定格子")
        print("=" * 70)

        for square_name in square_names:
            # 解析格子名称
            try:
                square = chess.parse_square(square_name)
                rank = chess.square_rank(square)  # 0-7
                file = chess.square_file(square)  # 0-7
            except ValueError:
                print(f"\n⚠️  无效的格子名称: {square_name}")
                continue

            # 捕获格子
            square_img = self.capture_square(rank, file)

            # 分析格子
            self.analyze_square(square_img, rank, file)

            # 保存格子图像
            output_dir = Path(__file__).parent / "debug_squares"
            output_dir.mkdir(exist_ok=True)

            output_path = output_dir / f"{square_name}.png"
            cv2.imwrite(str(output_path), square_img)
            print(f"格子图像已保存: {output_path}")

    def test_all_squares(self):
        """测试所有格子"""
        print("\n" + "=" * 70)
        print("  测试所有格子（这可能需要一些时间）")
        print("=" * 70)

        output_dir = Path(__file__).parent / "debug_squares"
        output_dir.mkdir(exist_ok=True)

        for rank in range(8):
            for file in range(8):
                square_name = chess.SQUARE_NAMES[rank * 8 + file]

                # 捕获格子
                square_img = self.capture_square(rank, file)

                # 分析格子（简化版）
                gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
                h, w = gray.shape
                center_region = gray[h//4:3*h//4, w//4:3*w//4]
                std_dev = np.std(center_region)
                mean_val = np.mean(center_region)

                has_piece = std_dev > 10

                # 保存结果
                if has_piece:
                    color_guess = "白棋" if mean_val > 128 else "黑棋"
                    print(f"{square_name}: ✓ {color_guess}")
                else:
                    print(f"{square_name}: ✗ 空")

                # 保存格子图像
                output_path = output_dir / f"{square_name}.png"
                cv2.imwrite(str(output_path), square_img)

        print(f"\n所有格子图像已保存到: {output_dir}")
        print("请检查这些图像，看看识别是否正确")


def main():
    """主函数"""
    import chess

    print("=" * 70)
    print("  棋子识别调试工具")
    print("=" * 70)

    debugger = PieceRecognitionDebugger()

    # 设置棋盘区域
    print("\n请设置棋盘区域:")
    print("1. 点击棋盘左上角")

    input("按Enter继续...")
    x1, y1 = pyautogui.position()

    print("2. 点击棋盘右下角")
    input("按Enter继续...")
    x2, y2 = pyautogui.position()

    debugger.set_board_region(x1, y1, x2, y2)

    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 测试指定格子（推荐）")
    print("2. 测试所有格子")
    print("3. 测试中心区域（e4, d4, e5, d5）")

    choice = input("\n请输入选择 (1/2/3): ").strip()

    try:
        if choice == '1':
            print("\n请输入要测试的格子名称（用空格分隔）:")
            print("例如: e2 e4 d4 e5")

            squares_input = input("格子名称: ").strip()
            square_names = squares_input.split()

            debugger.test_specific_squares(square_names)

        elif choice == '2':
            confirm = input("\n⚠️  这将测试所有64个格子并保存图像，是否继续? (y/n): ").strip().lower()
            if confirm == 'y':
                debugger.test_all_squares()
            else:
                print("已取消")

        elif choice == '3':
            debugger.test_specific_squares(['e4', 'd4', 'e5', 'd5'])

        else:
            print("无效选择")

        print("\n" + "=" * 70)
        print("  测试完成")
        print("=" * 70)
        print("\n提示:")
        print("  1. 查看保存的格子图像")
        print("  2. 检查识别是否准确")
        print("  3. 如果识别不准确，调整棋盘位置或改善光线条件")
        print("  4. 如果经常识别不到棋子，使用FEN输入模式")

    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已中断")
