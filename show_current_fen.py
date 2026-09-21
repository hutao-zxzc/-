#!/usr/bin/env python3
"""
快速显示Chess Bot识别的FEN字符串
"""

import sys
from pathlib import Path

def main():
    """主程序"""
    print("=" * 70)
    print("  📋 当前识别的FEN字符串")
    print("=" * 70)

    # 查找FEN文件
    fen_file = Path(__file__).parent / "recognized_fen.txt"

    if fen_file.exists():
        with open(fen_file, 'r') as f:
            fen = f.read().strip()

        print("\n📋 FEN字符串:")
        print("-" * 70)
        print(fen)
        print("-" * 70)

        # 尝试解析并显示棋盘
        try:
            import chess
            board = chess.Board(fen)
            print("\n♟️  棋盘:")
            print(board)
            print("\n📊 信息:")
            print(f"  当前回合: {'白方' if board.turn else '黑方'}")
            print(f"  棋子数: {len(list(board.piece_map()))}")
            print(f"  是否将军: {'是' if board.is_check() else '否'}")
            print(f"  是否将死: {'是' if board.is_checkmate() else '否'}")
        except Exception as e:
            print(f"\n⚠️  无法解析FEN: {e}")

        print("\n💡 提示:")
        print("  1. 复制这个FEN到chess.com/lichess.org查看")
        print("  2. 重新运行识别程序会更新这个文件")

    else:
        print("\n❌ 未找到识别的FEN文件")
        print(f"   期望位置: {fen_file}")
        print("\n💡 解决方法:")
        print("  1. 运行识别程序: python QUICK_FIX.py")
        print("  2. 或运行完整程序: python chess_bot.py")
        print("  3. 识别完成后会自动保存FEN")

    print("=" * 70)


if __name__ == "__main__":
    main()
