#!/usr/bin/env python3
"""
手动棋盘设置工具
允许用户手动设置每个格子的棋子
完全绕过识别问题
"""

import chess
import pyautogui
import time
from pathlib import Path
import sys


class ManualChessBot:
    """手动棋盘设置机器人"""

    def __init__(self, engine_path: str = None):
        """
        初始化机器人

        Args:
            engine_path: 国际象棋引擎路径
        """
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
        print(f"引擎路径: {self.engine_path}")

        # 棋盘设置
        self.board_region = None
        self.square_size = None
        self.manual_board = {}  # 手动设置的棋盘

    def set_board_region(self, x1: int, y1: int, x2: int, y2: int):
        """设置棋盘区域"""
        self.board_region = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"棋盘区域: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"格子大小: {self.square_size}")

    def setup_board_interactive(self):
        """交互式设置棋盘"""
        print("\n" + "=" * 70)
        print("  手动棋盘设置")
        print("=" * 70)
        print("\n使用说明:")
        print("  1. 程序会显示棋盘格子")
        print("  2. 为每个格子输入棋子符号")
        print("  3. 输入完成后，AI开始对弈")
        print("\n棋子符号:")
        print("  空/无棋子: . 或 直接回车")
        print("  白兵: P, 白马: N, 白象: B, 白车: R, 白后: Q, 白王: K")
        print("  黑兵: p, 黑马: n, 黑象: b, 黑车: r, 黑后: q, 黑王: k")
        print("\n快捷命令:")
        print("  'fen' - 使用FEN字符串设置")
        print("  'load' - 从文件加载")
        print("  'skip' - 跳过某些格子（已设置过的）")
        print("  'clear' - 清除所有设置")
        print("  'done' - 完成设置，开始对弈")
        print("=" * 70)

        # 创建棋盘
        board = chess.Board()
        board.clear()

        # 询问是否使用FEN
        use_fen = input("\n是否使用FEN字符串? (y/n, 默认n): ").strip().lower()
        if use_fen == 'y':
            return self.setup_from_fen()

        # 询问是否从文件加载
        load_file = input("是否从文件加载? (y/n, 默认n): ").strip().lower()
        if load_file == 'y':
            return self.setup_from_file()

        # 询问是否跳过（已经有设置了）
        skip_existing = input("是否跳过已设置的格子? (y/n, 默认y): ").strip().lower()
        if skip_existing != 'n':
            skip_existing = 'y'

        print("\n开始交互式设置...")
        print("为每个格子输入棋子符号，或使用快捷命令")
        print("(按Ctrl+C可以中断设置，已设置的棋子会保留）")

        try:
            # 遍历所有格子
            for rank in range(7, -1, -1):  # 从第8行到第1行
                print(f"\n{'=' * 70}")
                print(f"  第 {8 - rank} 行")
                print(f"{'=' * 70}")

                for file in range(8):  # 从第a列到第h列
                    square_idx = rank * 8 + file
                    square_name = chess.SQUARE_NAMES[square_idx]

                    # 检查是否已设置
                    if skip_existing == 'y' and square_idx in self.manual_board:
                        piece = self.manual_board[square_idx]
                        print(f"  [{square_name}] 已设置为: {piece if piece else '.'}")
                        continue

                    # 询问用户
                    prompt = f"  [{square_name}] 棋子: "
                    user_input = input(prompt).strip()

                    # 处理快捷命令
                    if user_input.lower() == 'fen':
                        board = self.setup_from_fen()
                        return board
                    elif user_input.lower() == 'done':
                        print("\n设置完成，开始对弈...")
                        return self.create_board_from_manual()
                    elif user_input.lower() == 'clear':
                        self.manual_board.clear()
                        print("  已清除所有设置")
                        continue
                    elif user_input.lower() == 'skip':
                        print("  跳过剩余格子")
                        skip_existing = 'y'
                        continue
                    elif not user_input or user_input == '.':
                        # 空格子
                        self.manual_board[square_idx] = None
                        print(f"    设为: 空")
                    else:
                        # 验证棋子符号
                        try:
                            piece_obj = chess.Piece.from_symbol(user_input)
                            self.manual_board[square_idx] = user_input
                            print(f"    设为: {user_input}")
                        except ValueError:
                            print(f"    ✗ 无效的棋子符号: {user_input}")
                            print(f"    有效符号: P, N, B, R, Q, K, p, n, b, r, q, k")
                            # 重新询问
                            file -= 1
                            continue

            print("\n" + "=" * 70)
            print("  所有格子已设置完成")
            print("=" * 70)

            # 创建棋盘
            board = self.create_board_from_manual()

        except KeyboardInterrupt:
            print("\n\n设置已中断，使用已设置的棋子...")

        return board

    def setup_from_fen(self):
        """从FEN设置棋盘"""
        print("\n请输入FEN字符串:")
        print("(标准开局: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1)")

        while True:
            fen = input("FEN: ").strip()

            if not fen:
                print("使用标准开局")
                fen = chess.STARTING_FEN

            try:
                board = chess.Board(fen)
                print(f"\n棋盘设置完成:")
                print(board)

                # 保存到manual_board
                self.save_board_to_manual(board)

                return board
            except ValueError as e:
                print(f"FEN格式错误: {e}")
                print("请重新输入")

    def setup_from_file(self):
        """从文件加载棋盘"""
        print("\n请输入文件路径:")
        print("(默认: manual_board.txt)")

        filepath = input("文件路径: ").strip()
        if not filepath:
            filepath = "manual_board.txt"

        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()

            # 解析FEN
            board = chess.Board(content)
            print(f"\n从文件加载完成:")
            print(board)

            # 保存到manual_board
            self.save_board_to_manual(board)

            return board
        except FileNotFoundError:
            print(f"文件不存在: {filepath}")
            return self.setup_board_interactive()
        except ValueError as e:
            print(f"文件内容无效: {e}")
            return self.setup_board_interactive()

    def create_board_from_manual(self):
        """从手动设置创建棋盘"""
        board = chess.Board()
        board.clear()

        for square_idx, piece_symbol in self.manual_board.items():
            if piece_symbol:
                try:
                    piece_obj = chess.Piece.from_symbol(piece_symbol)
                    board.set_piece_at(square_idx, piece_obj)
                except ValueError:
                    print(f"  警告：跳过无效棋子 {piece_symbol} at {chess.SQUARE_NAMES[square_idx]}")

        print(f"\n最终棋盘:")
        print(board)

        return board

    def save_board_to_manual(self, board: chess.Board):
        """保存棋盘到manual_board"""
        self.manual_board.clear()

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                self.manual_board[square] = piece.symbol()
            else:
                self.manual_board[square] = None

    def save_board_to_file(self, filepath: str = "manual_board.txt"):
        """保存棋盘到文件"""
        # 创建棋盘
        board = self.create_board_from_manual()
        fen = board.fen()

        with open(filepath, 'w') as f:
            f.write(fen)

        print(f"棋盘已保存到: {filepath}")

    def calculate_best_move(self, board: chess.Board, depth: int = 10):
        """使用LCZero计算最佳走法"""
        try:
            import chess.engine

            engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
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
            from_rank = chess.square_rank(from_square)
            from_file = chess.square_file(from_square)

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

            pyautogui.moveTo(from_x, from_y, duration=0.5)
            time.sleep(0.3)
            pyautogui.click(from_x, from_y, button='left')
            print("✓ 已点击起点")
            time.sleep(delay)

            pyautogui.moveTo(to_x, to_y, duration=0.5)
            time.sleep(0.3)
            pyautogui.click(to_x, to_y, button='left')
            print("✓ 已点击终点")
            time.sleep(delay)

            print("✅ 移动执行完成")
        except Exception as e:
            print(f"执行移动时出错: {e}")
            raise


def main():
    """主程序"""
    print("=" * 70)
    print("  手动棋盘设置机器人")
    print("  完全绕过识别问题")
    print("=" * 70)

    bot = ManualChessBot()

    # 设置棋盘区域
    print("\n请设置棋盘区域（用于执行移动）:")
    print("1. 点击棋盘左上角")

    input("\n按Enter继续...")
    x1, y1 = pyautogui.position()
    print("  ✓ 左上角已记录")

    print("2. 点击棋盘右下角")
    x2, y2 = pyautogui.position()
    print("  ✓ 右下角已记录")

    bot.set_board_region(x1, y1, x2, y2)

    # 设置棋盘
    board = bot.setup_board_interactive()

    # 保存到文件
    bot.save_board_to_file()

    print("\n" + "=" * 70)
    print("  开始对弈")
    print("=" * 70)

    try:
        while True:
            # 检查游戏是否结束
            if board.is_game_over():
                print(f"\n游戏结束！结果: {board.result()}")
                break

            # AI走棋
            print("\nAI思考中...")
            move = bot.calculate_best_move(board)

            if move:
                print(f"AI推荐: {move.uci()}")

                # 询问是否执行
                execute = input("\n是否自动执行移动? (y/n, 默认y): ").strip().lower()
                if execute != 'n':
                    bot.execute_move(move)

                    # 更新棋盘
                    board.push(move)

                    # 检查游戏是否结束
                    if board.is_game_over():
                        print(f"\n游戏结束！结果: {board.result()}")
                        break
                else:
                    # 手动更新棋盘
                    print("\n请手动更新棋盘:")
                    print("选择操作:")
                    print("  1. AI走了，对手已走棋，更新棋盘")
                    print("  2. AI走了，对手还没走，跳过")
                    print("  3. 重新设置整个棋盘")
                    print("  4. 使用FEN更新")
                    print("  5. 退出")

                    choice = input("\n请选择 (1-5): ").strip()

                    if choice == '1':
                        # 交互式更新
                        print("\n请输入对手的走法 (UCI格式，例如 e2e4):")
                        opponent_move = input("对手走法: ").strip()

                        try:
                            move_obj = chess.Move.from_uci(opponent_move)
                            if move_obj in board.legal_moves:
                                board.push(move_obj)
                                print(f"✓ 已执行: {opponent_move}")
                                print(f"\n当前棋盘:")
                                print(board)
                            else:
                                print(f"✗ 无效走法: {opponent_move}")
                        except ValueError:
                            print(f"✗ 走法格式错误: {opponent_move}")

                    elif choice == '2':
                        # 跳过，继续AI走棋
                        print("跳过，保持当前棋盘")
                        board.push(move)
                        continue

                    elif choice == '3':
                        # 重新设置整个棋盘
                        board = bot.setup_board_interactive()
                        bot.save_board_to_file()

                    elif choice == '4':
                        # 使用FEN更新
                        board = bot.setup_from_fen()
                        bot.save_board_to_file()

                    elif choice == '5':
                        print("退出程序")
                        break

                    else:
                        print("无效选择")
            else:
                print("AI无法找到有效走法")

            print("\n" + "=" * 60)

    except KeyboardInterrupt:
        print("\n\n程序已停止")


if __name__ == "__main__":
    main()
