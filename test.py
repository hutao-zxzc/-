#!/usr/bin/env python3
"""
测试脚本
验证各个模块的功能
"""

import cv2
import numpy as np
from chess_bot import ChessBot
from piece_recognizer import PieceRecognizer
from pathlib import Path


def test_screen_capture():
    """测试屏幕捕获"""
    print("\n=== 测试屏幕捕获 ===")

    bot = ChessBot()

    # 获取屏幕尺寸
    import pyautogui
    screen_w, screen_h = pyautogui.size()
    print(f"屏幕尺寸: {screen_w} x {screen_h}")

    # 设置测试区域（屏幕中心）
    x1, y1 = screen_w // 4, screen_h // 4
    x2, y2 = screen_w * 3 // 4, screen_h * 3 // 4
    bot.set_board_region(x1, y1, x2, y2)

    # 捕获测试区域
    img = bot.capture_board()
    print(f"捕获图像尺寸: {img.shape}")

    # 保存测试图像
    test_path = Path(__file__).parent / "test_capture.png"
    cv2.imwrite(str(test_path), img)
    print(f"测试图像已保存: {test_path}")

    return img


def test_square_extraction():
    """测试格子提取"""
    print("\n=== 测试格子提取 ===")

    bot = ChessBot()
    bot.set_board_region(100, 100, 500, 500)

    # 捕获棋盘
    board_img = bot.capture_board()

    # 提取格子
    squares = bot.extract_squares(board_img)
    print(f"提取到 {len(squares)} 个格子")

    # 显示几个格子的中心点
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    for rank, file in center_squares:
        square = squares[(rank, file)]
        print(f"格子 ({rank}, {file}) 尺寸: {square.shape}")

    return squares


def test_piece_recognition():
    """测试棋子识别"""
    print("\n=== 测试棋子识别 ===")

    recognizer = PieceRecognizer()

    # 创建测试图像
    test_images = []

    # 1. 空格子
    empty = np.zeros((100, 100, 3), dtype=np.uint8) + 200
    test_images.append(("空格子", empty))

    # 2. 白色棋子（模拟）
    white_piece = np.zeros((100, 100, 3), dtype=np.uint8) + 180
    cv2.circle(white_piece, (50, 50), 30, (220, 220, 220), -1)
    test_images.append(("白色棋子", white_piece))

    # 3. 黑色棋子（模拟）
    black_piece = np.zeros((100, 100, 3), dtype=np.uint8) + 180
    cv2.circle(black_piece, (50, 50), 30, (50, 50, 50), -1)
    test_images.append(("黑色棋子", black_piece))

    # 测试识别
    for name, img in test_images:
        result = recognizer.predict(img)
        print(f"{name}: 识别结果 = {result}")

        # 保存测试图像
        test_path = Path(__file__).parent / f"test_{name}.png"
        cv2.imwrite(str(test_path), img)


def test_chess_logic():
    """测试国际象棋逻辑"""
    print("\n=== 测试国际象棋逻辑 ===")

    import chess

    # 创建棋盘
    board = chess.Board()
    print("初始棋盘:")
    print(board)

    # 获取所有合法走法
    moves = list(board.legal_moves)
    print(f"\n初始合法走法数量: {len(moves)}")
    print(f"前5个走法: {[move.uci() for move in moves[:5]]}")

    # 执行一步走法
    move = chess.Move.from_uci("e2e4")
    board.push(move)
    print(f"\n执行走法: {move.uci()}")
    print("棋盘状态:")
    print(board)

    # 检查将军
    if board.is_check():
        print("将军!")
    if board.is_checkmate():
        print("将死!")
    if board.is_stalemate():
        print("逼和!")


def test_stockfish():
    """测试Stockfish引擎"""
    print("\n=== 测试Stockfish引擎 ===")

    bot = ChessBot()

    # 创建测试棋盘
    board = chess.Board()

    # 尝试计算最佳走法
    print("正在计算最佳走法...")
    move = bot.calculate_best_move(board, depth=10)

    if move:
        print(f"Stockfish推荐走法: {move.uci()}")
    else:
        print("无法计算走法（可能未安装Stockfish）")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始运行测试...")
    print("=" * 50)

    try:
        test_screen_capture()
        test_square_extraction()
        test_piece_recognition()
        test_chess_logic()
        test_stockfish()

        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def interactive_test():
    """交互式测试"""
    print("=== 交互式测试模式 ===\n")
    print("可用的测试:")
    print("1. 屏幕捕获测试")
    print("2. 格子提取测试")
    print("3. 棋子识别测试")
    print("4. 国际象棋逻辑测试")
    print("5. Stockfish引擎测试")
    print("6. 运行所有测试")
    print("0. 退出")

    while True:
        choice = input("\n请选择测试 (0-6): ").strip()

        if choice == "0":
            print("退出测试模式")
            break
        elif choice == "1":
            test_screen_capture()
        elif choice == "2":
            test_square_extraction()
        elif choice == "3":
            test_piece_recognition()
        elif choice == "4":
            test_chess_logic()
        elif choice == "5":
            test_stockfish()
        elif choice == "6":
            run_all_tests()
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all_tests()
    else:
        interactive_test()
