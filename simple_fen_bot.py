#!/usr/bin/env python3
"""
简化的FEN模式国际象棋机器人
不依赖屏幕识别，只使用FEN输入
"""

import chess
import pyautogui
import time
from pathlib import Path
import sys


class SimpleFENBot:
    """简化的FEN模式机器人"""

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

        # 棋盘区域（用于执行移动）
        self.board_region = None
        self.square_size = None

    def set_board_region(self, x1: int, y1: int, x2: int, y2: int):
        """设置棋盘区域"""
        self.board_region = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"棋盘区域: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"格子大小: {self.square_size}")

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

    def play_move_from_fen(self, fen: str):
        """从FEN走棋"""
        try:
            # 解析FEN
            board = chess.Board(fen)
            print(f"\n当前棋局:")
            print(board)

            # 检查游戏是否结束
            if board.is_game_over():
                print(f"\n游戏结束！结果: {board.result()}")
                return False

            # 计算最佳走法
            print("\nAI思考中...")
            move = self.calculate_best_move(board)

            if move:
                print(f"AI推荐: {move.uci()}")

                # 执行移动
                self.execute_move(move)

                # 模拟移动（为了下一轮）
                board.push(move)

                # 检查游戏是否结束
                if board.is_game_over():
                    print(f"\n游戏结束！结果: {board.result()}")
                    return False

                return True
            else:
                print("AI无法找到有效走法")
                return False
        except ValueError as e:
            print(f"FEN格式错误: {e}")
            return False
        except Exception as e:
            print(f"处理失败: {e}")
            return False


def main():
    """主程序"""
    print("=" * 70)
    print("  FEN模式国际象棋机器人")
    print("  不依赖屏幕识别，只使用FEN输入")
    print("=" * 70)

    bot = SimpleFENBot()

    # 询问是否需要执行移动
    execute_moves = input("\n是否需要自动执行移动? (y/n, 默认y): ").strip().lower()
    auto_execute = execute_moves != 'n'

    if auto_execute:
        # 校准棋盘
        print("\n请设置棋盘区域（用于自动执行移动）:")
        print("1. 点击棋盘左上角")
        print("2. 点击棋盘右下角")

        input("\n按Enter开始校准...")
        x1, y1 = pyautogui.position()
        time.sleep(1)
        print("  ✓ 左上角已记录")

        x2, y2 = pyautogui.position()
        print("  ✓ 右下角已记录")

        bot.set_board_region(x1, y1, x2, y2)

    print("\n" + "=" * 70)
    print("  开始对弈")
    print("=" * 70)
    print("\n使用方法:")
    print("  1. 在 chess.com/lichess.org 上打开对局")
    print("  2. 复制FEN字符串")
    print("  3. 在这里粘贴FEN")
    print("  4. AI计算并执行移动（如果已配置）")
    print("\n提示：输入 'help' 查看帮助，'quit' 退出")
    print("=" * 70)

    try:
        while True:
            user_input = input("\n请输入FEN或命令: ").strip()

            if user_input.lower() == 'quit':
                print("退出程序")
                break

            elif user_input.lower() == 'help':
                print("\n可用命令:")
                print("  FEN字符串 - 计算并走棋")
                print("  help - 显示帮助")
                print("  quit - 退出程序")
                continue

            elif not user_input:
                print("请输入FEN字符串或命令")
                continue

            # 处理FEN
            success = bot.play_move_from_fen(user_input)

            if success:
                print("\n" + "=" * 60)
                print("  准备下一轮...")
                print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
