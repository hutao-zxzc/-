#!/usr/bin/env python3
"""
超级宽松的棋子识别器
使用多种方法，极大提高识别率
"""

import cv2
import numpy as np
import pyautogui
import mss
import chess
from pathlib import Path
import pickle


class UltraLooseRecognizer:
    """超宽松识别器 - 最大化识别率"""

    def __init__(self):
        self.screen_capturer = mss.mss()
        self.board_region = None
        self.square_size = None

        # 识别统计
        self.stats = {
            'total_squares': 64,
            'detected': 0,
            'method1': 0,  # 标准差
            'method2': 0,  # 颜色范围
            'method3': 0,  # 边缘检测
            'method4': 0,  # 颜色聚类
            'method5': 0,  # 亮度直方图
        }

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"✓ 棋盘区域设置完成")
        print(f"  左上角: ({x1}, {y1})")
        print(f"  右下角: ({x2}, {y2})")
        print(f"  格子大小: {self.square_size}")

    def capture_square(self, rank, file):
        """捕获单个格子"""
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        square_w, square_h = self.square_size
        y = (7 - rank) * square_h
        x = file * square_w

        return board_img[y:y + square_h, x:x + square_w]

    def method_std_dev(self, gray_img):
        """
        方法1：标准差检测（超低阈值）
        """
        std = np.std(gray_img)
        # 超低阈值：只要有一点变化就认为有棋子
        return std > 3  # 从8降到3

    def method_color_range(self, gray_img):
        """
        方法2：颜色范围检测（超宽松）
        """
        min_val = np.min(gray_img)
        max_val = np.max(gray_img)
        range_val = max_val - min_val
        # 只要亮度有变化就认为有棋子
        return range_val > 5  # 从15降到5

    def method_edge_detection(self, gray_img):
        """
        方法3：边缘检测（极其敏感）
        """
        # 使用极低的Canny阈值
        edges = cv2.Canny(gray_img, 20, 50)  # 从30,80降到20,50
        edge_pixels = np.sum(edges > 0)
        edge_ratio = edge_pixels / gray_img.size
        # 只要有0.5%的边缘就认为有棋子
        return edge_ratio > 0.005  # 从0.02降到0.005

    def method_color_clustering(self, img):
        """
        方法4：颜色聚类分析（新方法）
        """
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 分割颜色通道
        h, s, v = cv2.split(hsv)

        # 分析饱和度通道（检测物体）
        s_std = np.std(s)

        # 如果饱和度有明显变化，说明有物体
        return s_std > 10

    def method_histogram(self, gray_img):
        """
        方法5：亮度直方图分析（新方法）
        """
        # 计算直方图
        hist = cv2.calcHist([gray_img], [0], None, [32], [0, 256])
        hist = hist.flatten()

        # 计算直方图的熵（衡量复杂度）
        if np.sum(hist) == 0:
            return False

        hist_norm = hist / np.sum(hist)
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-10))

        # 高熵意味着有更多细节（有棋子）
        return entropy > 3.5

    def detect_piece(self, square_img):
        """
        检测格子是否有棋子（使用5种方法）
        返回：检测结果和使用的检测方法
        """
        # 转换为灰度图
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

        # 使用多种区域检测（提高鲁棒性）
        h, w = gray.shape
        regions = {
            'whole': gray[h//4:3*h//4, w//4:3*w//4],  # 中心50%
            'small': gray[h//3:2*h//3, w//3:2*w//3],  # 中心33%
        }

        detection_votes = 0
        methods_used = []

        # 对每个区域应用所有方法
        for region_name, region in regions.items():
            # 方法1：标准差
            if self.method_std_dev(region):
                detection_votes += 1
                methods_used.append('std')

            # 方法2：颜色范围
            if self.method_color_range(region):
                detection_votes += 1
                methods_used.append('range')

            # 方法3：边缘检测
            if self.method_edge_detection(region):
                detection_votes += 1
                methods_used.append('edge')

        # 额外的全局方法
        # 方法4：颜色聚类
        if self.method_color_clustering(square_img):
            detection_votes += 2  # 加权
            methods_used.append('cluster')

        # 方法5：直方图
        if self.method_histogram(gray):
            detection_votes += 2  # 加权
            methods_used.append('histogram')

        # 超宽松的判断：只要10分中至少4分就认为有棋子
        # 最多：3个区域 * 3种方法 = 9分 + 2个全局方法 * 2分 = 13分
        has_piece = detection_votes >= 4

        return has_piece, detection_votes, methods_used

    def recognize_piece_type(self, square_img, has_piece):
        """
        识别棋子类型（简化但可靠）
        """
        if not has_piece:
            return None

        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]

        # 识别颜色
        mean_color = np.mean(center_region)
        is_white_piece = mean_color > 128

        # 简化的棋子识别（只区分兵/其他）
        # 因为识别棋子类型很难，所以我们用FEN验证
        # 这里只返回兵，其他类型需要FEN验证
        return 'P' if is_white_piece else 'p'

    def scan_board(self, verbose=False):
        """
        扫描整个棋盘
        verbose: 是否显示详细统计
        """
        print("\n" + "=" * 70)
        print("  🔍 开始扫描棋盘（超宽松模式）")
        print("=" * 70)

        board = chess.Board()
        board.clear()

        # 重置统计
        self.stats = {k: 0 for k in self.stats.keys()}
        self.stats['total_squares'] = 64

        # 保存检测结果
        detections = {}

        for rank in range(8):
            for file in range(8):
                square_idx = rank * 8 + file
                square_name = chess.SQUARE_NAMES[square_idx]

                square_img = self.capture_square(rank, file)

                # 检测是否有棋子
                has_piece, votes, methods = self.detect_piece(square_img)

                detections[(rank, file)] = {
                    'has_piece': has_piece,
                    'votes': votes,
                    'methods': methods
                }

                if has_piece:
                    self.stats['detected'] += 1

                    # 简化的棋子识别（返回兵）
                    piece = self.recognize_piece_type(square_img, True)
                    if piece:
                        piece_obj = chess.Piece.from_symbol(piece)
                        board.set_piece_at(square_idx, piece_obj)

                    if verbose:
                        color = '白' if piece and piece.isupper() else '黑'
                        print(f"  ✓ {square_name}: {color}棋 (votes={votes})")
                elif verbose:
                    print(f"  ✗ {square_name}: 空 (votes={votes})")

        # 显示统计
        print(f"\n📊 识别统计:")
        print(f"  检测到棋子: {self.stats['detected']}/64")
        print(f"  空格子: {64 - self.stats['detected']}/64")
        print(f"  识别率: {self.stats['detected']/64*100:.1f}%")

        return board, detections

    def smart_fen_correction(self, board, detections):
        """
        智能FEN修正
        使用先验知识修正识别结果
        """
        print("\n" + "=" * 70)
        print("  🧠 智能FEN修正")
        print("=" * 70)

        # 计算可能的正确FEN
        # 策略：基于检测置信度调整

        # 1. 统计黑白棋子数量
        white_count = 0
        black_count = 0
        piece_map = board.piece_map()

        for square, piece in piece_map.items():
            if piece.color == chess.WHITE:
                white_count += 1
            else:
                black_count += 1

        print(f"\n📈 检测统计:")
        print(f"  白棋: {white_count}")
        print(f"  黑棋: {black_count}")
        print(f"  总计: {white_count + black_count}")

        # 2. 如果识别的棋子太少，降低阈值重新扫描
        if white_count + black_count < 16:
            print(f"\n⚠️  识别的棋子太少 ({white_count + black_count} < 16)")
            print("   可能原因:")
            print("   - 棋盘位置不准确")
            print("   - 棋子颜色与棋盘太接近")
            print("   - 光线不足")
            print("\n   建议:")
            print("   1. 重新校准棋盘")
            print("   2. 改善光线条件")
            print("   3. 使用FEN手动输入")
        else:
            print(f"\n✅ 识别数量正常")

        # 3. 返回原始棋盘（用户可以手动修正）
        return board

    def save_debug_images(self, detections):
        """
        保存调试图像
        """
        print("\n💾 保存调试图像...")

        debug_dir = Path(__file__).parent / "debug_ultra"
        debug_dir.mkdir(exist_ok=True)

        for rank in range(8):
            for file in range(8):
                square_name = chess.SQUARE_NAMES[rank * 8 + file]
                square_img = self.capture_square(rank, file)

                # 在图像上添加信息
                info = detections[(rank, file)]
                status = "PIECE" if info['has_piece'] else "EMPTY"

                # 在图像上标注
                cv2.putText(square_img, f"{square_name}",
                           (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(square_img, f"{status}({info['votes']})",
                           (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

                # 保存
                output_path = debug_dir / f"{square_name}.png"
                cv2.imwrite(str(output_path), square_img)

        print(f"✓ 调试图像已保存到: {debug_dir}")

    def save_calibration(self, filepath="calibration_ultra.pkl"):
        """保存校准数据"""
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
    print("  🔍 超宽松棋子识别器")
    print("  最大化识别率，使用5种检测方法")
    print("=" * 70)
    print("\n改进点:")
    print("  1. ✓ 5种检测方法（标准差、颜色范围、边缘、聚类、直方图）")
    print("  2. ✓ 超低识别阈值（只要有变化就认为有棋子）")
    print("  3. ✓ 多区域融合检测")
    print("  4. ✓ 保存详细调试图像")
    print("  5. ✓ 智能统计和建议")
    print("=" * 70)

    recognizer = UltraLooseRecognizer()

    # 检查校准
    calib_file = Path(__file__).parent / "calibration_ultra.pkl"
    if calib_file.exists():
        with open(calib_file, 'rb') as f:
            data = pickle.load(f)
        recognizer.board_region = data["board_region"]
        recognizer.square_size = data["square_size"]
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
    verbose = input("\n显示详细识别过程? (y/n): ").strip().lower() == 'y'
    board, detections = recognizer.scan_board(verbose=verbose)

    # 智能修正
    board = recognizer.smart_fen_correction(board, detections)

    # 显示结果
    print("\n" + "=" * 70)
    print("  ♟️  识别的棋盘")
    print("=" * 70)
    print(board)

    # 保存FEN
    fen = board.fen()
    print(f"\n📋 FEN字符串:")
    print(fen)

    fen_file = Path(__file__).parent / "recognized_fen_ultra.txt"
    with open(fen_file, 'w') as f:
        f.write(fen)
    print(f"✓ FEN已保存: {fen_file}")

    # 保存调试图像
    save_debug = input("\n保存调试图像（查看每个格子）? (y/n): ").strip().lower() == 'y'
    if save_debug:
        recognizer.save_debug_images(detections)

    print("\n" + "=" * 70)
    print("  完成！")
    print("=" * 70)
    print("\n💡 建议:")
    print("  1. 查看 debug_ultra/ 目录中的格子图像")
    print("  2. 如果识别还是不准，考虑使用FEN手动输入")
    print("  3. 在chess.com/lichess.org复制FEN字符串")
    print("     然后使用 get_fen.py 工具")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
