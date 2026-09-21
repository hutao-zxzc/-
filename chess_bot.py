#!/usr/bin/env python3
"""
国际象棋自动对弈机器人
功能：自动识别屏幕棋盘，与AI进行对弈
"""

import cv2
import numpy as np
import pyautogui
import mss
import chess
import time
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict
import pickle

# 禁用pyautogui的安全机制
pyautogui.FAILSAFE = False


class ChessBot:
    """国际象棋自动对弈机器人"""

    def __init__(self, engine_path: str = None):
        """
        初始化棋盘机器人

        Args:
            engine_path: 国际象棋引擎路径（默认为LCZero）
        """
        self.screen_capturer = mss.mss()
        self.board_state = chess.Board()

        # 自动检测引擎路径
        if engine_path is None:
            # Windows环境下查找lc0.exe
            if sys.platform == "win32":
                # 先查找同目录下的lc0.exe
                script_dir = Path(__file__).parent
                local_lc0 = script_dir / "lc0.exe"
                if local_lc0.exists():
                    engine_path = str(local_lc0)
                else:
                    # 使用PATH中的lc0
                    engine_path = "lc0"
            else:
                # Linux/Mac环境
                engine_path = "lc0"

        self.engine_path = engine_path
        self.stockfish_path = engine_path  # 保持向后兼容
        print(f"引擎路径: {self.engine_path}")

        # 棋盘区域（左上角和右下角坐标）
        self.board_region = None
        self.board_size = None

        # 棋盘格子大小
        self.square_size = None

        # 棋子模板（用于识别）
        self.piece_templates = {}

    def set_board_region(self, x1: int, y1: int, x2: int, y2: int):
        """
        设置棋盘区域

        Args:
            x1, y1: 左上角坐标
            x2, y2: 右下角坐标
        """
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.board_size = (x2 - x1, y2 - y1)
        self.square_size = (x2 - x1) // 8, (y2 - y1) // 8
        print(f"棋盘区域设置完成: {self.board_region}")
        print(f"格子大小: {self.square_size}")

    def capture_board(self) -> np.ndarray:
        """
        捕获棋盘区域

        Returns:
            棋盘图像 (numpy数组)
        """
        if not self.board_region:
            raise ValueError("请先设置棋盘区域")

        screenshot = self.screen_capturer.grab(self.board_region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def detect_board_automatically(self) -> bool:
        """
        自动检测棋盘位置（通过寻找棋盘网格）

        Returns:
            是否成功检测到棋盘
        """
        print("正在自动检测棋盘...")

        # 获取整个屏幕
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # 转换为灰度图
        gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        # 使用Hough变换检测直线（棋盘线）
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=200)

        if lines is None or len(lines) < 8:
            print("未能检测到足够的棋盘线，请手动设置棋盘区域")
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
            print("未能检测到完整的棋盘网格")
            return False

        # 找到棋盘边界
        horizontal_lines.sort()
        vertical_lines.sort()

        x1 = int(vertical_lines[0])
        x2 = int(vertical_lines[-1])
        y1 = int(horizontal_lines[0])
        y2 = int(horizontal_lines[-1])

        # 扩展边界以包含整个棋盘
        padding = 50
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(screen_np.shape[1], x2 + padding)
        y2 = min(screen_np.shape[0], y2 + padding)

        self.set_board_region(x1, y1, x2, y2)
        return True

    def extract_squares(self, board_img: np.ndarray) -> Dict[Tuple[int, int], np.ndarray]:
        """
        提取棋盘上的所有格子

        Args:
            board_img: 棋盘图像

        Returns:
            字典，键是格子坐标(rank, file)，值是格子图像
        """
        squares = {}
        square_w, square_h = self.square_size

        for rank in range(8):  # 0-7, 从下到上
            for file in range(8):  # 0-7, 从左到右
                # 在图像中，y坐标从上到下
                y = (7 - rank) * square_h
                x = file * square_w

                square = board_img[y:y + square_h, x:x + square_w]
                squares[(rank, file)] = square

        return squares

    def recognize_piece(self, square_img: np.ndarray) -> Optional[str]:
        """
        识别格子上的棋子

        Args:
            square_img: 格子图像

        Returns:
            棋子符号（如 'P', 'N', 'B', 'R', 'Q', 'K' 或 None）
        """
        # 转换为灰度图
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

        # 简单的模板匹配识别（可以替换为机器学习模型）
        # 这里使用基于颜色和轮廓的简单识别方法

        # 获取格子中心区域（避免边缘干扰）
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]

        # 检测是否有棋子（通过阈值分割）
        _, binary = cv2.threshold(center_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 计算白色和黑色像素的比例
        white_pixels = np.sum(binary == 255)
        black_pixels = np.sum(binary == 0)
        total = white_pixels + black_pixels

        if black_pixels / total < 0.1:  # 空格子
            return None

        # 识别棋子颜色（深色还是浅色）
        mean_color = np.mean(center_region)
        is_white_piece = mean_color > 128

        # 识别棋子类型（简化的方法）
        # 在实际应用中，应该使用训练好的神经网络
        # 这里返回占位符，需要用户输入或使用更复杂的识别方法
        return "UNKNOWN"

    def scan_board(self) -> chess.Board:
        """
        扫描整个棋盘，识别棋局状态

        Returns:
            chess.Board对象，表示当前棋局状态
        """
        board_img = self.capture_board()
        squares = self.extract_squares(board_img)

        # 创建新的棋盘
        board = chess.Board()
        board.clear()

        # TODO: 这里需要实现完整的棋子识别
        # 由于棋子识别比较复杂，建议使用以下方法之一：
        # 1. 使用预训练的神经网络模型
        # 2. 手动输入棋局状态
        # 3. 使用在线棋盘API

        print("提示：棋子识别功能需要进一步的机器学习模型支持")
        print("当前使用简单的颜色识别，可能不够准确")

        return board

    def recognize_piece_enhanced(self, square_img: np.ndarray) -> Optional[str]:
        """
        增强的棋子识别方法

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

        # 如果标准差很小，可能是空格子
        if std_dev < 20:
            return None

        # 检测棋子颜色
        is_white_piece = mean_val > 128

        # 使用边缘检测和轮廓分析
        edges = cv2.Canny(center_region, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return None

        # 获取最大轮廓
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)

        # 计算轮廓的周长
        perimeter = cv2.arcLength(max_contour, True)

        # 计算圆形度
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
        else:
            circularity = 0

        # 计算矩形的宽高比
        x, y, w_rect, h_rect = cv2.boundingRect(max_contour)
        aspect_ratio = w_rect / h_rect if h_rect > 0 else 0

        # 根据特征识别棋子类型
        piece_type = self._classify_piece(area, circularity, aspect_ratio, is_white_piece)

        return piece_type

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
        # 标准化面积（相对格子大小）
        max_area = 50 * 50  # 假设中心区域最大50x50
        area_ratio = area / max_area

        # 阈值设置
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
                    piece_obj = chess.Piece.from_symbol(piece)
                    board.set_piece_at(square_idx, piece_obj)
                    recognized_pieces.append(f"{piece} at {chess.SQUARE_NAMES[square_idx]}")

        print(f"识别到 {len(recognized_pieces)} 个棋子:")
        for p in recognized_pieces[:8]:  # 只显示前8个
            print(f"  {p}")

        # 验证棋盘状态
        try:
            # 检查棋盘是否有效
            if len(recognized_pieces) > 0:
                # 尝试检查合法性
                if board.is_check():
                    print("提示：检测到将军状态")

            return board
        except Exception as e:
            print(f"棋盘状态验证失败: {e}")
            return board

    def calculate_best_move(self, board: chess.Board, depth: int = 10) -> Optional[chess.Move]:
        """
        使用LCZero引擎计算最佳走法

        Args:
            board: 当前棋盘状态
            depth: 搜索深度（LCZero使用nodes数）

        Returns:
            最佳走法
        """
        try:
            import chess.engine

            # 检查引擎文件是否存在
            engine_file = Path(self.stockfish_path)
            if not engine_file.exists():
                raise FileNotFoundError(f"引擎文件不存在: {self.stockfish_path}")

            print(f"正在启动引擎: {self.stockfish_path}")

            # 使用LCZero引擎（UCI协议兼容）
            engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

            # 配置LCZero的UCI选项
            # 这些选项可以提高性能和准确性
            engine.configure({
                "Threads": 4,              # 线程数，根据CPU核心数调整
                "NNCacheSize": 200,       # 神经网络缓存大小(MB)
                "MaxCollisionEvents": 32,  # 最大碰撞事件
                "VerboseMoveStats": True,  # 显示详细移动统计
            })

            # LCZero推荐使用nodes而不是depth
            # nodes=10000表示计算10000个节点，性能越好可以设置越高
            limit = chess.engine.Limit(nodes=depth * 1000)

            print(f"计算最佳走法 (nodes={limit.nodes})...")
            result = engine.play(board, limit)
            engine.close()

            return result.move
        except FileNotFoundError as e:
            print(f"错误: {e}")
            print("\n解决方案:")
            print("1. 下载LCZero: https://github.com/LeelaChessZero/lc0/releases")
            print("2. 将lc0.exe放到与chess_bot.py相同的目录下")
            print("3. 或者修改代码中的引擎路径")
        except Exception as e:
            print(f"LCZero引擎错误: {e}")
            print("提示：请确保已安装LCZero引擎（lc0.exe）并配置正确路径")
            print("LCZero下载: https://github.com/LeelaChessZero/lc0/releases")

        return None

    def execute_move(self, move: chess.Move, delay: float = 0.5):
        """
        执行移动（通过鼠标点击）

        Args:
            move: 要执行的移动
            delay: 点击之间的延迟
        """
        try:
            if not self.board_region:
                raise ValueError("请先设置棋盘区域")

            square_w, square_h = self.square_size
            x1 = self.board_region["left"]
            y1 = self.board_region["top"]

            # 起始格子的中心坐标
            from_square = move.from_square
            from_rank = chess.square_rank(from_square)  # 0-7, 从下到上
            from_file = chess.square_file(from_square)  # 0-7, 从左到右

            from_x = x1 + from_file * square_w + square_w // 2
            from_y = y1 + (7 - from_rank) * square_h + square_h // 2

            # 目标格子的中心坐标
            to_square = move.to_square
            to_rank = chess.square_rank(to_square)
            to_file = chess.square_file(to_square)

            to_x = x1 + to_file * square_w + square_w // 2
            to_y = y1 + (7 - to_rank) * square_h + square_h // 2

            # 执行点击
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

    def calibrate_board(self):
        """
        棋盘校准：让用户点击棋盘的四个角
        """
        print("=== 棋盘校准 ===")
        print("请按照提示点击屏幕上的位置...")

        print("1. 请点击棋盘左上角")
        x1, y1 = pyautogui.position()
        time.sleep(1)

        print("2. 请点击棋盘右下角")
        x2, y2 = pyautogui.position()

        self.set_board_region(x1, y1, x2, y2)
        print("校准完成！")

    def play_move(self, input_mode: str = "auto"):
        """
        执行一步AI移动

        Args:
            input_mode: 输入模式 ("auto", "fen", "manual")
        """
        if input_mode == "auto":
            # 自动识别屏幕
            print("\n正在自动识别棋盘...")
            try:
                board = self.scan_board_advanced()
                print(f"识别的棋局:\n{board}")
            except Exception as e:
                print(f"自动识别失败: {e}")
                print("切换到手动输入模式...")
                fen = input("请输入FEN字符串: ").strip()
                try:
                    board = chess.Board(fen)
                    print(f"当前棋局:\n{board}")
                except ValueError as e:
                    print(f"FEN格式错误: {e}")
                    return
        else:
            # 手动输入
            fen = input("请输入FEN字符串: ").strip()
            try:
                board = chess.Board(fen)
                print(f"当前棋局:\n{board}")
            except ValueError as e:
                print(f"FEN格式错误: {e}")
                return

        # 计算最佳走法
        move = self.calculate_best_move(board)

        if move:
            # 执行移动
            self.execute_move(move)
            print(f"AI走棋: {move.uci()}")
        else:
            print("无法找到有效走法")

    def save_calibration(self, filepath: str):
        """
        保存校准数据

        Args:
            filepath: 保存路径
        """
        calibration_data = {
            "board_region": self.board_region,
            "board_size": self.board_size,
            "square_size": self.square_size
        }

        with open(filepath, 'wb') as f:
            pickle.dump(calibration_data, f)
        print(f"校准数据已保存到: {filepath}")

    def load_calibration(self, filepath: str):
        """
        加载校准数据

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'rb') as f:
                calibration_data = pickle.load(f)

            self.board_region = calibration_data["board_region"]
            self.board_size = calibration_data["board_size"]
            self.square_size = calibration_data["square_size"]
            print(f"校准数据已加载: {filepath}")
        except FileNotFoundError:
            print(f"文件不存在: {filepath}")
        except Exception as e:
            print(f"加载校准数据失败: {e}")


def main():
    """主程序"""
    print("=" * 70)
    print("  国际象棋自动对弈机器人")
    print("  支持自动识别屏幕棋盘")
    print("=" * 70)

    # 自动查找引擎
    # - 如果lc0.exe在同目录，自动使用
    # - 否则使用PATH中的lc0
    # - 如需自定义，可以传入完整路径，例如：
    #   engine_path = "C:/Users/YourName/Downloads/lc0-v0.32.1-windows-cpu-dnnl/lc0.exe"

    bot = ChessBot()  # 自动检测引擎路径

    # 检查是否已保存校准数据
    calib_file = Path(__file__).parent / "calibration.pkl"

    if calib_file.exists():
        print("\n找到已保存的校准数据")
        bot.load_calibration(str(calib_file))
    else:
        # 选择校准方式
        print("\n请选择棋盘校准方式:")
        print("1. 手动校准（点击棋盘四角）")
        print("2. 自动检测（尝试自动识别棋盘）")

        choice = input("请输入选择 (1/2): ").strip()

        if choice == "1":
            print("\n请点击棋盘左上角...")
            x1, y1 = pyautogui.position()
            time.sleep(1)

            print("请点击棋盘右下角...")
            x2, y2 = pyautogui.position()

            bot.set_board_region(x1, y1, x2, y2)
            bot.save_calibration(str(calib_file))
        elif choice == "2":
            if not bot.detect_board_automatically():
                print("自动检测失败，请手动校准")
                print("\n请点击棋盘左上角...")
                x1, y1 = pyautogui.position()
                time.sleep(1)

                print("请点击棋盘右下角...")
                x2, y2 = pyautogui.position()

                bot.set_board_region(x1, y1, x2, y2)
                bot.save_calibration(str(calib_file))

    # 测试棋盘捕获
    print("\n测试棋盘捕获...")
    try:
        board_img = bot.capture_board()
        preview_path = Path(__file__).parent / "board_preview.png"
        cv2.imwrite(str(preview_path), board_img)
        print(f"棋盘预览已保存: {preview_path}")

        # 测试识别
        print("\n测试棋盘识别...")
        test_board = bot.scan_board_advanced()
        print(f"测试识别完成，棋盘状态:\n{test_board}")
    except Exception as e:
        print(f"测试失败: {e}")
        print("提示：确保棋盘可见且已正确校准")

    print("\n" + "=" * 70)

    # 主循环
    print("\n=== 开始对弈 ===")
    print("提示：按 Ctrl+C 停止程序\n")

    print("使用模式:")
    print("  1. 自动识别屏幕棋盘（默认）")
    print("  2. 手动输入FEN字符串")

    mode_choice = input("\n请选择模式 (1/2, 默认1): ").strip()
    auto_mode = mode_choice != '2'

    try:
        while True:
            # 识别棋盘
            print("=== 识别棋盘 ===")

            if auto_mode:
                # 自动识别
                print("正在识别屏幕棋盘...")
                try:
                    current_board = bot.scan_board_advanced()
                    print(f"识别的棋局:\n{current_board}")
                except Exception as e:
                    print(f"自动识别失败: {e}")
                    print("切换到手动输入模式...")
                    fen = input("请输入FEN字符串: ").strip()
                    try:
                        current_board = chess.Board(fen)
                        print(f"当前棋局:\n{current_board}")
                    except ValueError as e:
                        print(f"FEN格式错误: {e}")
                        continue
            else:
                # 手动输入FEN
                fen = input("请输入FEN字符串 (或输入 'auto' 切换到自动识别): ").strip()

                if fen.lower() == 'auto':
                    auto_mode = True
                    print("切换到自动识别模式")
                    continue

                try:
                    current_board = chess.Board(fen)
                    print(f"当前棋局:\n{current_board}")
                except ValueError as e:
                    print(f"FEN格式错误: {e}")
                    continue

            # 检查游戏是否结束
            if current_board.is_game_over():
                print(f"游戏结束！结果: {current_board.result()}")
                break

            # AI走棋
            print("\n=== AI思考中 ===")
            try:
                ai_move = bot.calculate_best_move(current_board)
            except Exception as e:
                print(f"计算最佳走法失败: {e}")
                input("按Enter重试...")
                continue

            if ai_move:
                print(f"AI推荐走法: {ai_move.uci()}")

                # 直接自动执行移动
                try:
                    bot.execute_move(ai_move)
                    print("✅ 移动已自动执行")
                except Exception as e:
                    print(f"❌ 执行移动失败: {e}")
                    print("提示：请手动执行移动，或在chess.com/lichess.org上操作")

                # 模拟AI移动（为了下一轮识别）
                try:
                    current_board.push(ai_move)
                except Exception as e:
                    print(f"更新棋盘状态失败: {e}")

                # 检查游戏是否结束
                if current_board.is_game_over():
                    print(f"\n游戏结束！结果: {current_board.result()}")
                    break
            else:
                print("AI无法找到有效走法")
                input("按Enter继续...")
                continue

            print("\n" + "=" * 60)
            print("等待对手走棋，然后按Enter继续...")
            input()

    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
