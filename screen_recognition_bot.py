#!/usr/bin/env python3
"""
自动识别屏幕棋盘的国际象棋机器人
结合棋子识别和LCZero引擎
"""

import cv2
import numpy as np
import pyautogui
import mss
import chess
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import pickle


class ScreenChessBot:
    """屏幕识别国际象棋机器人"""

    def __init__(self, engine_path: str = None):
        """
        初始化机器人

        Args:
            engine_path: 国际象棋引擎路径
        """
        import sys
        from pathlib import Path

        # 自动检测引擎路径
        if engine_path is None:
            if sys.platform == "win32":
                script_dir = Path(__file__).parent
                local_lc0 = script_dir / "lc0.exe"
                if local_lc0.exists():
                    engine_path = str(local_lc0)
                else:
                    engine_path = "lc0"
            else:
                engine_path = "lc0"

        self.engine_path = engine_path
        self.screen_capturer = mss.mss()
        self.board_state = chess.Board()

        # 棋盘区域
        self.board_region = None
        self.board_size = None
        self.square_size = None

        # 棋子模板缓存
        self.piece_templates = {}
        self.use_templates = False

        print(f"引擎路径: {self.engine_path}")

    def set_board_region(self, x1: int, y1: int, x2: int, y2: int):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.board_size = (x2 - x1, y2 - y1)
        self.square_size = (x2 - x1) // 8, (y2 - y1) // 8
        print(f"棋盘区域: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"格子大小: {self.square_size}")

    def capture_board(self) -> np.ndarray:
        """捕获棋盘区域"""
        if not self.board_region:
            raise ValueError("请先设置棋盘区域")

        screenshot = self.screen_capturer.grab(self.board_region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_board_from_screen(self) -> bool:
        """
        从屏幕自动检测棋盘

        Returns:
            是否成功检测到棋盘
        """
        print("正在从屏幕检测棋盘...")

        # 获取整个屏幕
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # 转换为灰度图
        gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # 使用霍夫变换检测直线
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=200)

        if lines is None or len(lines) < 8:
            print("未检测到足够的棋盘线")
            return False

        # 提取水平和垂直线
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            rho, theta = line[0]
            if abs(theta) < 0.1 or abs(theta - np.pi) < 0.1:
                horizontal_lines.append(rho)
            elif abs(theta - np.pi / 2) < 0.1:
                vertical_lines.append(rho)

        if len(horizontal_lines) < 8 or len(vertical_lines) < 8:
            print("未检测到完整的棋盘网格")
            return False

        # 找到棋盘边界
        horizontal_lines.sort()
        vertical_lines.sort()

        # 去除异常值
        horizontal_lines = self._remove_outliers(horizontal_lines)
        vertical_lines = self._remove_outliers(vertical_lines)

        if len(horizontal_lines) < 8 or len(vertical_lines) < 8:
            print("检测到的线条数量不足")
            return False

        x1 = int(vertical_lines[0])
        x2 = int(vertical_lines[-1])
        y1 = int(horizontal_lines[0])
        y2 = int(horizontal_lines[-1])

        # 扩展边界
        padding = 30
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(screen_np.shape[1], x2 + padding)
        y2 = min(screen_np.shape[0], y2 + padding)

        self.set_board_region(x1, y1, x2, y2)
        return True

    def _remove_outliers(self, values: List[int], threshold: float = 2.0) -> List[int]:
        """去除异常值"""
        if not values:
            return []

        mean_val = np.mean(values)
        std_val = np.std(values)

        filtered = [v for v in values if abs(v - mean_val) < threshold * std_val]
        return sorted(filtered)[:8]

    def extract_squares(self, board_img: np.ndarray) -> Dict[Tuple[int, int], np.ndarray]:
        """提取棋盘上的所有格子"""
        squares = {}
        square_w, square_h = self.square_size

        for rank in range(8):
            for file in range(8):
                y = (7 - rank) * square_h
                x = file * square_w

                # 提取格子（保留一些边距）
                padding = 2
                square = board_img[y + padding:y + square_h - padding,
                                x + padding:x + square_w - padding]
                squares[(rank, file)] = square

        return squares

    def recognize_piece_enhanced(self, square_img: np.ndarray) -> Optional[str]:
        """
        增强的棋子识别方法（更宽松的识别）

        Args:
            square_img: 格子图像

        Returns:
            棋子符号
        """
        # 转换为灰度图
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

        # 获取中心区域（避免边缘干扰）
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]

        # 计算标准差（检测是否有棋子）
        std_dev = np.std(center_region)
        mean_val = np.mean(center_region)

        # 降低阈值，更容易识别棋子
        # 原来是20，现在改为10
        if std_dev < 10:
            return None

        # 检测棋子颜色
        is_white_piece = mean_val > 128

        # 使用多种方法检测棋子
        # 方法1：标准差
        has_piece_by_std = std_dev > 10

        # 方法2：像素统计
        _, binary = cv2.threshold(center_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        white_pixels = np.sum(binary == 255)
        black_pixels = np.sum(binary == 0)
        total = white_pixels + black_pixels

        # 如果非背景像素比例超过一定阈值，认为有棋子
        # 降低阈值从0.1到0.05
        has_piece_by_pixels = (black_pixels / total) > 0.05

        # 方法3：边缘检测
        edges = cv2.Canny(center_region, 30, 100)  # 降低阈值
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        has_piece_by_edges = len(contours) > 0

        # 使用多个方法的"或"逻辑（任一方法检测到棋子就认为有）
        has_piece = has_piece_by_std or has_piece_by_pixels or has_piece_by_edges

        if not has_piece:
            return None

        # 如果有棋子，识别类型
        if has_piece_by_edges and len(contours) > 0:
            # 使用轮廓分析
            max_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_contour)
            perimeter = cv2.arcLength(max_contour, True)

            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
            else:
                circularity = 0

            x, y, w_rect, h_rect = cv2.boundingRect(max_contour)
            aspect_ratio = w_rect / h_rect if h_rect > 0 else 0

            piece_type = self._classify_piece(area, circularity, aspect_ratio, is_white_piece)
            return piece_type
        else:
            # 使用简单的规则
            # 根据像素比例和均值判断
            if has_piece_by_pixels:
                if black_pixels / total > 0.7:
                    # 大部分是黑色，可能是黑棋
                    return 'p'  # 简化识别为兵
                elif white_pixels / total > 0.7:
                    # 大部分是白色，可能是白棋
                    return 'P'  # 简化识别为兵

            # 默认根据颜色判断
            return 'P' if is_white_piece else 'p'

    def scan_board_simple(self) -> chess.Board:
        """
        简化的棋盘扫描（用于识别失败时的备用方案）

        Returns:
            识别的棋盘状态
        """
        print("\n使用简化识别方法...")
        board_img = self.capture_board()
        squares = self.extract_squares(board_img)

        # 创建棋盘
        board = chess.Board()
        board.clear()

        # 更简单的识别方法
        # 只识别白棋和黑棋，不区分具体类型
        for rank in range(8):
            for file in range(8):
                square_idx = rank * 8 + file
                square_img = squares[(rank, file)]

                # 转换为灰度图
                gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

                # 获取中心区域
                h, w = gray.shape
                center_region = gray[h//4:3*h//4, w//4:3*w//4]

                # 计算标准差
                std_dev = np.std(center_region)
                mean_val = np.mean(center_region)

                # 判断是否有棋子
                if std_dev > 30:  # 有棋子
                    # 简单的判断：只是设置兵，让引擎可以工作
                    # 实际应用中应该使用更准确的识别
                    piece_type = 'P' if mean_val > 128 else 'p'

                    try:
                        piece_obj = chess.Piece.from_symbol(piece_type)
                        board.set_piece_at(square_idx, piece_obj)
                    except:
                        pass

        print(f"简化识别完成（可能不准确，建议使用FEN输入）")
        return board

    def _classify_piece(self, area: int, circularity: float,
                      aspect_ratio: float, is_white_piece: bool) -> Optional[str]:
        """
        根据特征分类棋子

        Args:
            area: 轮廓面积
            circularity: 圆形度
            aspect_ratio: 宽高比
            is_white_piece: 是否为白棋

        Returns:
            棋子符号
        """
        center_area = area  # 假设是中心区域的面积
        # 标准化面积（相对格子大小）
        # 假设中心区域大约是格子大小的1/4
        max_area = 50 * 50  # 假设中心区域最大50x50
        area_ratio = center_area / max_area

        # 阈值设置（需要根据实际情况调整）
        if area_ratio < 0.1:
            return None  # 可能是噪声

        # 棋子类型识别逻辑
        if circularity > 0.7:  # 比较圆形
            if area_ratio > 0.4:
                return 'Q' if is_white_piece else 'q'  # 后
            else:
                return 'P' if is_white_piece else 'p'  # 兵（顶部比较圆）
        else:
            if circularity < 0.3:  # 比较不规则
                if aspect_ratio > 0.7 and aspect_ratio < 1.3:
                    return 'R' if is_white_piece else 'r'  # 车
                else:
                    return 'B' if is_white_piece else 'b'  # 象（对角线形状）
            else:
                return 'N' if is_white_piece else 'n'  # 马（马头形状）

    def scan_board_advanced(self) -> chess.Board:
        """
        高级棋盘扫描

        Returns:
            识别的棋盘状态
        """
        print("\n正在扫描棋盘...")
        board_img = self.capture_board()
        squares = self.extract_squares(board_img)

        # 创建棋盘
        board = chess.Board()
        board.clear()

        # 识别每个格子
        recognized_pieces = []
        for rank in range(8):
            for file in range(8):
                square_idx = rank * 8 + file
                square_img = squares[(rank, file)]

                piece = self.recognize_piece_enhanced(square_img)

                if piece:
                    # 设置棋子
                    try:
                        piece_obj = chess.Piece.from_symbol(piece)
                        board.set_piece_at(square_idx, piece_obj)
                        recognized_pieces.append(f"{piece} at {chess.SQUARE_NAMES[square_idx]}")
                    except Exception as e:
                        print(f"  警告：无法设置棋子 {piece} at {chess.SQUARE_NAMES[square_idx]}: {e}")

        print(f"识别到 {len(recognized_pieces)} 个棋子:")
        for p in recognized_pieces[:10]:  # 显示前10个
            print(f"  {p}")

        # 验证棋盘状态
        if len(recognized_pieces) < 10:
            print("\n⚠️  警告：识别到的棋子太少，可能识别不准确")
            print("建议：")
            print("  1. 改善光线条件")
            print("  2. 确保棋盘对比度高")
            print("  3. 重新校准棋盘")
            print("  4. 使用FEN输入模式")

        # 检查棋盘是否有效
        try:
            if len(recognized_pieces) > 0:
                # 检查是否有合法的走法
                legal_moves = list(board.legal_moves)

                if len(legal_moves) == 0:
                    print("\n❌ 错误：没有合法的走法，棋盘状态可能无效")
                    print("建议：重新校准棋盘或使用FEN输入模式")
                else:
                    print(f"✓ 找到 {len(legal_moves)} 个合法走法")

            return board
        except Exception as e:
            print(f"❌ 棋盘状态验证失败: {e}")
            print("建议：重新校准棋盘或使用FEN输入模式")
            return board

    def calculate_best_move(self, board: chess.Board, depth: int = 10) -> Optional[chess.Move]:
        """使用LCZero计算最佳走法"""
        try:
            import chess.engine

            engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

            # 配置LCZero
            engine.configure({
                "Threads": 4,
                "NNCacheSize": 200,
            })

            limit = chess.engine.Limit(nodes=depth * 1000)
            result = engine.play(board, limit)
            engine.close()

            return result.move
        except Exception as e:
            print(f"引擎错误: {e}")
            return None

    def execute_move(self, move: chess.Move, delay: float = 0.5):
        """执行移动"""
        try:
            if not self.board_region:
                raise ValueError("请先设置棋盘区域")

            square_w, square_h = self.square_size
            x1 = self.board_region["left"]
            y1 = self.board_region["top"]

            # 起始格子
            from_square = move.from_square
            from_rank = chess.square_rank(from_square)  # 0-7, 从下到上
            from_file = chess.square_file(from_square)  # 0-7, 从左到右

            from_x = x1 + from_file * square_w + square_w // 2
            from_y = y1 + (7 - from_rank) * square_h + square_h // 2

            # 目标格子
            to_square = move.to_square
            to_rank = chess.square_rank(to_square)
            to_file = chess.square_file(to_square)

            to_x = x1 + to_file * square_w + square_w // 2
            to_y = y1 + (7 - to_rank) * square_h + square_h // 2

            print(f"执行移动: {move.uci()}")
            print(f"点击起点: ({from_x}, {from_y})")
            print(f"点击终点: ({to_x}, {to_y})")

            # 获取当前鼠标位置（调试）
            current_mouse = pyautogui.position()
            print(f"当前鼠标位置: ({current_mouse.x}, {current_mouse.y})")

            # 移动鼠标到起点（动画方式）
            pyautogui.moveTo(from_x, from_y, duration=0.5)
            time.sleep(0.3)

            # 点击起点
            pyautogui.click(from_x, from_y, button='left')
            print("✓ 已点击起点")
            time.sleep(delay)

            # 移动鼠标到终点（动画方式）
            pyautogui.moveTo(to_x, to_y, duration=0.5)
            time.sleep(0.3)

            # 点击终点
            pyautogui.click(to_x, to_y, button='left')
            print("✓ 已点击终点")
            time.sleep(delay)

            print("✅ 移动执行完成")
        except Exception as e:
            print(f"执行移动时出错: {e}")
            raise

    def save_calibration(self, filepath: str):
        """保存校准数据"""
        calibration_data = {
            "board_region": self.board_region,
            "board_size": self.board_size,
            "square_size": self.square_size
        }

        with open(filepath, 'wb') as f:
            pickle.dump(calibration_data, f)
        print(f"校准数据已保存: {filepath}")

    def load_calibration(self, filepath: str):
        """加载校准数据"""
        try:
            with open(filepath, 'rb') as f:
                calibration_data = pickle.load(f)

            self.board_region = calibration_data["board_region"]
            self.board_size = calibration_data["board_size"]
            self.square_size = calibration_data["square_size"]
            print(f"校准数据已加载: {filepath}")
        except FileNotFoundError:
            print(f"文件不存在: {filepath}")


def main():
    """主程序"""
    print("=" * 70)
    print("  国际象棋自动识别机器人")
    print("  结合屏幕识别和LCZero引擎")
    print("=" * 70)

    bot = ScreenChessBot()

    # 检查是否有保存的校准数据
    calib_file = Path(__file__).parent / "calibration.pkl"

    if calib_file.exists():
        print("\n找到已保存的校准数据")
        bot.load_calibration(str(calib_file))
    else:
        # 校准棋盘
        print("\n请选择棋盘校准方式:")
        print("1. 手动校准（点击棋盘的左上角和右下角）")
        print("2. 自动检测（从屏幕识别棋盘）")

        choice = input("\n请输入选择 (1/2): ").strip()

        if choice == "1":
            print("\n请点击棋盘左上角...")
            x1, y1 = pyautogui.position()
            time.sleep(1)

            print("请点击棋盘右下角...")
            x2, y2 = pyautogui.position()

            bot.set_board_region(x1, y1, x2, y2)
            bot.save_calibration(str(calib_file))
        elif choice == "2":
            if bot.detect_board_from_screen():
                bot.save_calibration(str(calib_file))
                print("自动检测成功！")
            else:
                print("自动检测失败，请手动校准")
                print("请点击棋盘左上角...")
                x1, y1 = pyautogui.position()
                time.sleep(1)

                print("请点击棋盘右下角...")
                x2, y2 = pyautogui.position()

                bot.set_board_region(x1, y1, x2, y2)
                bot.save_calibration(str(calib_file))

    # 测试棋盘识别
    print("\n测试棋盘识别...")
    try:
        board = bot.scan_board_advanced()
        print(f"\n识别的棋盘状态:")
        print(board)
    except Exception as e:
        print(f"棋盘识别失败: {e}")
        print("提示：确保棋盘可见且光线充足")

    # 主循环
    print("\n" + "=" * 70)
    print("  开始自动对弈")
    print("=" * 70)
    print("\n使用方法:")
    print("  - 按Enter键识别棋盘并让AI走棋")
    print("  - 输入 'fen' 手动输入棋局")
    print("  - 输入 'quit' 退出")
    print("  - 输入 'recalibrate' 重新校准")
    print("  - 输入 'test' 测试识别")
    print("\n" + "=" * 70)

    try:
        while True:
            user_input = input("\n按Enter走棋，或输入命令: ").strip().lower()

            if user_input == 'quit':
                print("退出程序")
                break

            elif user_input == 'recalibrate':
                print("\n请点击棋盘左上角...")
                x1, y1 = pyautogui.position()
                time.sleep(1)

                print("请点击棋盘右下角...")
                x2, y2 = pyautogui.position()

                bot.set_board_region(x1, y1, x2, y2)
                bot.save_calibration(str(calib_file))
                print("校准完成！")
                continue

            elif user_input == 'test':
                print("\n测试棋盘识别...")
                try:
                    board = bot.scan_board_advanced()
                    print(f"\n识别的棋盘:")
                    print(board)
                except Exception as e:
                    print(f"测试失败: {e}")
                continue

            elif user_input == 'fen':
                fen = input("请输入FEN字符串: ").strip()
                try:
                    board = chess.Board(fen)
                    print(f"\n当前棋局:")
                    print(board)
                except ValueError as e:
                    print(f"FEN格式错误: {e}")
                    continue
            else:
                # 识别棋盘
                print("\n正在识别棋盘...")
                try:
                    board = bot.scan_board_advanced()

                    # 检查棋盘是否有合法走法
                    legal_moves = list(board.legal_moves)
                    if len(legal_moves) == 0:
                        print("\n❌ 错误：没有合法的走法")
                        print("可能的原因：")
                        print("  1. 棋盘识别不准确")
                        print("  2. 棋盘状态无效")
                        print("  3. 已经是游戏结束状态")

                        # 询问用户是否使用FEN输入
                        use_fen = input("\n是否改用FEN输入模式? (y/n, 默认y): ").strip().lower()
                        if use_fen != 'n':
                            print("\n切换到FEN输入模式")
                            fen = input("请输入FEN字符串: ").strip()
                            try:
                                board = chess.Board(fen)
                                print(f"\n当前棋局:")
                                print(board)
                            except ValueError as e:
                                print(f"FEN格式错误: {e}")
                                input("按Enter重试...")
                                continue
                        else:
                            input("按Enter重试...")
                            continue

                except Exception as e:
                    print(f"识别失败: {e}")
                    print("提示：使用 'test' 命令测试识别")
                    print("或者使用 'fen' 命令手动输入棋局")

                    # 询问是否使用FEN输入
                    use_fen = input("\n是否改用FEN输入模式? (y/n, 默认y): ").strip().lower()
                    if use_fen != 'n':
                        fen = input("请输入FEN字符串: ").strip()
                        try:
                            board = chess.Board(fen)
                            print(f"\n当前棋局:")
                            print(board)
                        except ValueError as e:
                            print(f"FEN格式错误: {e}")
                            input("按Enter重试...")
                            continue
                    else:
                        input("按Enter重试...")
                        continue

            # AI走棋
            print("\nAI思考中...")
            try:
                move = bot.calculate_best_move(board, depth=10)
            except Exception as e:
                print(f"计算最佳走法失败: {e}")

                # 询问是否使用FEN输入
                use_fen = input("\n是否改用FEN输入模式? (y/n, 默认y): ").strip().lower()
                if use_fen != 'n':
                    fen = input("请输入FEN字符串: ").strip()
                    try:
                        board = chess.Board(fen)
                        print(f"\n当前棋局:")
                        print(board)
                        # 继续处理这个FEN棋盘
                        print("\nAI思考中...")
                        try:
                            move = bot.calculate_best_move(board, depth=10)
                        except Exception as e2:
                            print(f"计算FEN棋盘最佳走法失败: {e2}")
                            input("按Enter继续...")
                            continue
                    except ValueError as e:
                        print(f"FEN格式错误: {e}")
                        input("按Enter重试...")
                        continue
                else:
                    input("按Enter重试...")
                    continue

            if move:
                print(f"AI推荐: {move.uci()}")

                # 验证走法是否有效
                if move not in board.legal_moves:
                    print(f"\n⚠️  警告：推荐走法 {move.uci()} 不在合法走法列表中")
                    print("可能的原因：")
                    print("  1. 棋盘识别不准确")
                    print("  2. 引擎计算错误")

                    use_fen = input("\n是否改用FEN输入模式? (y/n, 默认y): ").strip().lower()
                    if use_fen != 'n':
                        fen = input("请输入FEN字符串: ").strip()
                        try:
                            board = chess.Board(fen)
                            print(f"\n当前棋局:")
                            print(board)
                            print("\nAI思考中...")
                            move = bot.calculate_best_move(board, depth=10)
                        except ValueError as e:
                            print(f"FEN格式错误: {e}")
                            input("按Enter继续...")
                            continue
                        except Exception as e2:
                            print(f"计算FEN棋盘最佳走法失败: {e2}")
                            input("按Enter继续...")
                            continue
                    else:
                        input("按Enter继续...")
                        continue

                # 直接自动执行移动
                try:
                    bot.execute_move(move)
                    print("✅ 移动已自动执行")
                except Exception as e:
                    print(f"❌ 执行移动失败: {e}")
                    print("提示：请手动执行移动，或在chess.com/lichess.org上操作")
                    input("按Enter继续...")
            else:
                print("AI无法找到有效走法")

                # 询问是否使用FEN输入
                use_fen = input("\n是否改用FEN输入模式? (y/n, 默认y): ").strip().lower()
                if use_fen != 'n':
                    fen = input("请输入FEN字符串: ").strip()
                    try:
                        board = chess.Board(fen)
                        print(f"\n当前棋局:")
                        print(board)
                    except ValueError as e:
                        print(f"FEN格式错误: {e}")
                        input("按Enter重试...")
                        continue
                else:
                    input("按Enter继续...")
                    continue

    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
