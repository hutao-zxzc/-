#!/usr/bin/env python3
"""
快速获取FEN字符串的工具
支持：验证FEN、查看常用局面、从棋盘生成FEN
"""

import chess
import sys


def print_fen(fen_str):
    """打印FEN和棋盘"""
    try:
        board = chess.Board(fen_str)
        print("=" * 70)
        print("📋 FEN字符串:")
        print(fen_str)
        print()
        print("♟️  棋盘:")
        print(board)
        print()
        print("📊 棋局信息:")
        print(f"  当前回合: {'白方' if board.turn else '黑方'}")
        print(f"  王车易位权: {board.castling_rights}")
        print(f"  吃过路兵目标格: {board.ep_square if board.ep_square else '无'}")
        print(f"  半回合计数: {board.halfmove_clock}")
        print(f"  回合数: {board.fullmove_number}")
        print("=" * 70)
        return True
    except ValueError as e:
        print(f"❌ 无效的FEN: {e}")
        return False


def interactive_fen():
    """交互式生成FEN"""
    board = chess.Board()

    print("\n🎮 交互式棋盘生成器")
    print("=" * 70)
    print("当前棋盘:")
    print(board)
    print(f"\nFEN: {board.fen()}")
    print("\n💡 输入UCI格式走棋，如 'e2e4', 'g1f3'")
    print("   输入 'q' 退出并显示最终FEN")
    print("   输入 'u' 撤销上一步\n")

    while True:
        move_str = input("👉 输入走棋: ").strip()

        if move_str.lower() == 'q':
            print("\n" + "=" * 70)
            print("📋 最终FEN字符串:")
            print(board.fen())
            print("=" * 70)
            break

        if move_str.lower() == 'u':
            if board.move_stack:
                board.pop()
                print("\n✅ 已撤销")
                print("当前棋盘:")
                print(board)
                print(f"\nFEN: {board.fen()}")
            else:
                print("❌ 没有可撤销的走棋")
            continue

        try:
            move = chess.Move.from_uci(move_str)
            if move in board.legal_moves:
                board.push(move)
                print("\n✅ 走棋成功")
                print("当前棋盘:")
                print(board)
                print(f"\nFEN: {board.fen()}")
            else:
                print(f"❌ 非法走棋: {move_str}")
                print(f"💡 提示: 输入 'moves' 查看所有合法走棋")
        except ValueError:
            print(f"❌ 无效的走棋格式: {move_str}")
            print("💡 正确格式: 'e2e4', 'g1f3' 等")


def show_openings():
    """显示常用开局FEN"""
    print("\n" + "=" * 70)
    print("📚 常用开局FEN")
    print("=" * 70)

    openings = [
        ("初始局面", chess.Board().fen()),
        ("1. e4", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"),
        ("1. d4", "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1"),
        ("1. c4", "rnbqkbnr/pppppppp/8/8/2P4/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1"),
        ("1. Nf3", "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1"),
        ("西班牙开局", "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"),
        ("意大利开局", "r1bqk1nr/pppp1ppp/2n5/4p3/2b1P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 4 4"),
        ("西西里防御", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"),
        ("法兰西防御", "rnbqkbnr/ppp2ppp/4p3/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"),
    ]

    for name, fen in openings:
        print(f"\n🎯 {name}:")
        print(f"   {fen}")


def copy_to_clipboard(fen):
    """复制到剪贴板（如果支持）"""
    try:
        import pyperclip
        pyperclip.copy(fen)
        print("✅ 已复制到剪贴板")
    except ImportError:
        print("💡 提示: 安装 pyperclip 可自动复制到剪贴板")
        print("   pip install pyperclip")
    except Exception as e:
        print(f"⚠️  无法复制到剪贴板: {e}")


def main():
    """主程序"""
    print("=" * 70)
    print("  📋 FEN字符串工具")
    print("=" * 70)

    while True:
        print("\n请选择:")
        print("1. 输入FEN字符串（验证和显示）")
        print("2. 交互式棋盘生成器")
        print("3. 查看常用开局FEN")
        print("4. 查看棋盘历史走棋")
        print("5. 从FEN生成走棋列表")
        print("0. 退出")

        choice = input("\n👉 选择 (0-5): ").strip()

        if choice == '0':
            print("\n👋 再见！")
            break

        elif choice == '1':
            print("\n" + "-" * 70)
            fen = input("📝 请输入FEN字符串: ").strip()
            if fen:
                if print_fen(fen):
                    copy_choice = input("\n📋 复制到剪贴板? (y/n): ").strip().lower()
                    if copy_choice == 'y':
                        copy_to_clipboard(fen)

        elif choice == '2':
            print("\n" + "-" * 70)
            interactive_fen()

        elif choice == '3':
            show_openings()

        elif choice == '4':
            print("\n" + "-" * 70)
            fen = input("📝 请输入FEN字符串: ").strip()
            if fen:
                try:
                    board = chess.Board(fen)
                    print("\n📜 走棋历史:")
                    if board.move_stack:
                        for i, move in enumerate(board.move_stack, 1):
                            print(f"  {i}. {move.uci()}")
                    else:
                        print("  (无走棋历史)")
                except ValueError as e:
                    print(f"❌ 无效的FEN: {e}")

        elif choice == '5':
            print("\n" + "-" * 70)
            print("📝 请输入FEN字符串和走棋（用空格分隔）")
            print("   例如: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 e2e4 e7e5")
            line = input("📝 输入: ").strip()
            parts = line.split()

            if len(parts) >= 1:
                try:
                    fen = parts[0]
                    moves = parts[1:]
                    board = chess.Board(fen)

                    print(f"\n📋 起始FEN: {fen}")
                    print("\n♟️  起始棋盘:")
                    print(board)

                    if moves:
                        print(f"\n📜 执行 {len(moves)} 步走棋:")
                        for move_str in moves:
                            try:
                                move = chess.Move.from_uci(move_str)
                                if move in board.legal_moves:
                                    board.push(move)
                                    print(f"  ✓ {move_str}")
                                else:
                                    print(f"  ✗ {move_str} (非法走棋)")
                            except ValueError:
                                print(f"  ✗ {move_str} (无效格式)")

                        print("\n♟️  最终棋盘:")
                        print(board)
                        print(f"\n📋 最终FEN: {board.fen()}")

                        copy_choice = input("\n📋 复制最终FEN到剪贴板? (y/n): ").strip().lower()
                        if copy_choice == 'y':
                            copy_to_clipboard(board.fen())

                except ValueError as e:
                    print(f"❌ 无效的FEN: {e}")

        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
