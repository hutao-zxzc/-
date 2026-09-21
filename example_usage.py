#!/usr/bin/env python3
"""
示例：如何使用国际象棋机器人

这个脚本展示了如何以编程方式使用机器人的各个功能
"""

from chess_bot import ChessBot
import time
import chess


def example_1_basic_setup():
    """示例1：基本设置"""
    print("\n=== 示例1：基本设置 ===")

    # 创建机器人实例
    bot = ChessBot()

    # 设置棋盘区域（假设棋盘在屏幕上的位置）
    # 这些坐标需要根据你的屏幕和棋盘位置进行调整
    bot.set_board_region(x1=100, y1=200, x2=600, y2=700)

    # 捕获棋盘
    board_img = bot.capture_board()
    print(f"棋盘图像尺寸: {board_img.shape}")

    # 保存棋盘预览
    import cv2
    cv2.imwrite("example_board.png", board_img)
    print("棋盘预览已保存: example_board.png")


def example_2_calibrate_and_save():
    """示例2：校准并保存"""
    print("\n=== 示例2：校准并保存 ===")

    bot = ChessBot()

    # 运行校准
    print("请点击棋盘的四个角...")
    bot.calibrate_board()

    # 保存校准数据
    bot.save_calibration("example_calibration.pkl")
    print("校准数据已保存")


def example_3_load_calibration():
    """示例3：加载校准数据"""
    print("\n=== 示例3：加载校准数据 ===")

    bot = ChessBot()

    # 加载之前保存的校准数据
    bot.load_calibration("example_calibration.pkl")

    # 现在可以直接使用
    board_img = bot.capture_board()
    print("使用加载的校准数据捕获棋盘")


def example_4_extract_squares():
    """示例4：提取格子"""
    print("\n=== 示例4：提取格子 ===")

    bot = ChessBot()
    bot.set_board_region(100, 100, 500, 500)

    # 捕获棋盘
    board_img = bot.capture_board()

    # 提取所有格子
    squares = bot.extract_squares(board_img)
    print(f"提取到 {len(squares)} 个格子")

    # 显示几个格子
    print("\n中心4个格子的尺寸:")
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    for rank, file in center_squares:
        square = squares[(rank, file)]
        print(f"格子 ({rank}, {file}): {square.shape}")


def example_5_calculate_best_move():
    """示例5：计算最佳走法"""
    print("\n=== 示例5：计算最佳走法 ===")

    bot = ChessBot()

    # 创建一个测试棋盘
    board = chess.Board()
    print("初始棋盘:")
    print(board)

    # 计算最佳走法
    move = bot.calculate_best_move(board, depth=10)

    if move:
        print(f"\nStockfish推荐: {move.uci()}")
        print(f"描述: {move}")


def example_6_execute_move_simulation():
    """示例6：模拟执行移动（不实际点击）"""
    print("\n=== 示例6：模拟执行移动 ===")

    bot = ChessBot()
    bot.set_board_region(100, 100, 500, 500)

    # 创建一个移动
    move = chess.Move.from_uci("e2e4")

    # 显示要点击的坐标（不实际执行）
    square_w, square_h = bot.square_size
    x1 = bot.board_region["left"]
    y1 = bot.board_region["top"]

    from_square = move.from_square
    from_rank = chess.rank_index(from_square)
    from_file = chess.file_index(from_square)

    from_x = x1 + from_file * square_w + square_w // 2
    from_y = y1 + (7 - from_rank) * square_h + square_h // 2

    print(f"移动: {move.uci()}")
    print(f"起点坐标: ({from_x}, {from_y})")
    print("(实际使用时将自动点击这些坐标)")


def example_7_play_full_game_simulation():
    """示例7：模拟完整对局（不实际点击）"""
    print("\n=== 示例7：模拟完整对局 ===")

    bot = ChessBot()
    bot.set_board_region(100, 100, 500, 500)

    # 创建棋盘
    board = chess.Board()
    print("开始模拟对局...")
    print(board)
    print()

    # 模拟5轮
    for round_num in range(5):
        print(f"--- 第 {round_num + 1} 轮 ---")

        # 白方移动
        move = bot.calculate_best_move(board, depth=5)
        if move:
            print(f"白方: {move.uci()}")
            board.push(move)
        else:
            print("白方无棋可走")
            break

        # 黑方移动
        move = bot.calculate_best_move(board, depth=5)
        if move:
            print(f"黑方: {move.uci()}")
            board.push(move)
        else:
            print("黑方无棋可走")
            break

        print()

        # 检查游戏状态
        if board.is_checkmate():
            print("将死！游戏结束")
            break
        if board.is_stalemate():
            print("逼和！游戏结束")
            break
        if board.is_insufficient_material():
            print("棋子不足，和棋")
            break

    print("\n最终棋盘状态:")
    print(board)


def example_8_custom_ai_settings():
    """示例8：自定义AI设置"""
    print("\n=== 示例8：自定义AI设置 ===")

    bot = ChessBot()
    board = chess.Board()

    # 使用不同的搜索深度
    depths = [5, 10, 15]

    print("不同搜索深度的表现:")
    for depth in depths:
        start_time = time.time()
        move = bot.calculate_best_move(board, depth=depth)
        elapsed = time.time() - start_time

        if move:
            print(f"深度 {depth}: {move.uci()} (用时 {elapsed:.2f}秒)")


def example_9_piece_recognition_demo():
    """示例9：棋子识别演示"""
    print("\n=== 示例9：棋子识别演示 ===")

    from piece_recognizer import PieceRecognizer
    import cv2
    import numpy as np

    # 创建识别器
    recognizer = PieceRecognizer()

    # 创建测试图像
    test_cases = [
        ("空格子", np.zeros((100, 100, 3), dtype=np.uint8) + 200),
        ("白色圆形", np.zeros((100, 100, 3), dtype=np.uint8) + 200),
        ("黑色圆形", np.zeros((100, 100, 3), dtype=np.uint8) + 200),
    ]

    # 绘制棋子
    cv2.circle(test_cases[1][1], (50, 50), 30, (220, 220, 220), -1)
    cv2.circle(test_cases[2][1], (50, 50), 30, (50, 50, 50), -1)

    # 识别测试
    for name, img in test_cases:
        result = recognizer.predict(img)
        print(f"{name}: {result}")

        # 保存图像
        cv2.imwrite(f"example_{name}.png", img)


def example_10_full_workflow():
    """示例10：完整工作流程"""
    print("\n=== 示例10：完整工作流程 ===")

    print("步骤1：创建机器人")
    bot = ChessBot()

    print("步骤2：校准棋盘（或加载已保存的校准）")
    # bot.calibrate_board()
    # bot.load_calibration("calibration.pkl")

    print("步骤3：设置棋盘区域")
    bot.set_board_region(100, 100, 500, 500)

    print("步骤4：捕获棋盘")
    board_img = bot.capture_board()

    print("步骤5：提取格子")
    squares = bot.extract_squares(board_img)

    print("步骤6：识别棋子（简化版）")
    print("提示：完整的棋子识别需要训练好的模型")

    print("步骤7：计算最佳走法")
    board = chess.Board()
    move = bot.calculate_best_move(board, depth=10)

    if move:
        print(f"步骤8：准备执行移动 {move.uci()}")
        print("提示：实际使用时会自动点击屏幕")

    print("\n完整工作流程演示完成！")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("国际象棋机器人 - 使用示例")
    print("=" * 60)

    examples = [
        ("1. 基本设置", example_1_basic_setup),
        ("2. 校准并保存", example_2_calibrate_and_save),
        ("3. 加载校准数据", example_3_load_calibration),
        ("4. 提取格子", example_4_extract_squares),
        ("5. 计算最佳走法", example_5_calculate_best_move),
        ("6. 模拟执行移动", example_6_execute_move_simulation),
        ("7. 模拟完整对局", example_7_play_full_game_simulation),
        ("8. 自定义AI设置", example_8_custom_ai_settings),
        ("9. 棋子识别演示", example_9_piece_recognition_demo),
        ("10. 完整工作流程", example_10_full_workflow),
    ]

    print("\n可用示例:")
    for desc, func in examples:
        print(f"  {desc}")

    print("\n选择示例:")
    print("  输入数字运行特定示例")
    print("  输入 'all' 运行所有示例")
    print("  输入 'quit' 退出")

    while True:
        choice = input("\n请选择: ").strip().lower()

        if choice == "quit":
            print("退出示例")
            break
        elif choice == "all":
            print("\n运行所有示例...\n")
            for i, (desc, func) in enumerate(examples, 1):
                try:
                    print(f"\n{'=' * 60}")
                    func()
                except Exception as e:
                    print(f"示例运行失败: {e}")
                    import traceback
                    traceback.print_exc()
            print("\n所有示例运行完成！")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            idx = int(choice) - 1
            try:
                examples[idx][1]()
            except Exception as e:
                print(f"示例运行失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    main()
