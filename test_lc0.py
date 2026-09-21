#!/usr/bin/env python3
"""
LCZero引擎测试脚本
验证引擎配置是否正确
"""

import chess
import chess.engine
import time
from pathlib import Path
import sys

def find_lc0():
    """查找lc0.exe"""
    # 当前目录
    current_dir = Path(__file__).parent
    lc0_path = current_dir / "lc0.exe"

    if lc0_path.exists():
        return str(lc0_path)

    # PATH中查找
    return "lc0"

def test_lc0_basic():
    """基本功能测试"""
    print("=" * 60)
    print("LCZero 基本功能测试")
    print("=" * 60)

    # 查找引擎
    lc0_path = find_lc0()
    print(f"\n引擎路径: {lc0_path}")

    # 检查文件是否存在
    if not Path(lc0_path).exists():
        print("❌ 错误: 找不到 lc0.exe")
        print("\n解决方案:")
        print("1. 下载LCZero: https://github.com/LeelaChessZero/lc0/releases")
        print("2. 将lc0.exe放到与test_lc0.py相同的目录下")
        return False

    print("✅ 引擎文件存在")

    # 测试1: 启动引擎
    print("\n[测试1] 启动引擎...")
    try:
        engine = chess.engine.SimpleEngine.popen_uci(lc0_path)
        print("✅ 引擎启动成功")
    except Exception as e:
        print(f"❌ 引擎启动失败: {e}")
        return False

    # 测试2: 获取引擎信息
    print("\n[测试2] 获取引擎信息...")
    try:
        engine_info = engine.id
        print(f"✅ 引擎信息:")
        print(f"  名称: {engine_info['name']}")
        print(f"  作者: {engine_info['author']}")
    except Exception as e:
        print(f"❌ 获取引擎信息失败: {e}")

    # 测试3: 配置引擎
    print("\n[测试3] 配置引擎...")
    try:
        engine.configure({
            "Threads": 4,
            "NNCacheSize": 200,
        })
        print("✅ 引擎配置成功")
    except Exception as e:
        print(f"⚠️  引擎配置警告: {e}")
        print("   某些选项可能不支持")

    # 测试4: 分析初始局面
    print("\n[测试4] 分析初始局面...")
    board = chess.Board()

    try:
        # 快速测试：100 nodes
        start_time = time.time()
        limit = chess.engine.Limit(nodes=100)
        result = engine.play(board, limit)
        elapsed = time.time() - start_time

        print(f"✅ 分析成功")
        print(f"  最佳走法: {result.move.uci()}")
        print(f"  计算时间: {elapsed:.2f}秒")
        print(f"  速度: ~{int(100/elapsed)} NPS (Nodes Per Second)")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        engine.quit()
        return False

    # 测试5: 性能测试
    print("\n[测试5] 性能测试 (1000 nodes)...")
    board = chess.Board()

    try:
        start_time = time.time()
        limit = chess.engine.Limit(nodes=1000)
        result = engine.play(board, limit)
        elapsed = time.time() - start_time

        nps = int(1000 / elapsed)
        print(f"✅ 性能测试完成")
        print(f"  最佳走法: {result.move.uci()}")
        print(f"  计算时间: {elapsed:.2f}秒")
        print(f"  速度: {nps} NPS")

        # 性能评估
        if nps < 100:
            print(f"  ⚠️  速度较慢，建议:")
            print(f"     - 减少 nodes 数量")
            print(f"     - 检查系统负载")
        elif nps < 1000:
            print(f"  ✅ 速度正常")
        else:
            print(f"  🚀 速度优秀")

    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        engine.quit()
        return False

    # 测试6: 测试复杂局面
    print("\n[测试6] 测试复杂局面...")
    # 著名的意大利开局
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R bKQkq - 3 3"
    board = chess.Board(fen)
    print(f"局面: {board.fen()}")

    try:
        limit = chess.engine.Limit(nodes=500)
        result = engine.play(board, limit)
        print(f"✅ 复杂局面分析成功")
        print(f"  最佳走法: {result.move.uci()}")
    except Exception as e:
        print(f"❌ 复杂局面分析失败: {e}")

    # 关闭引擎
    engine.quit()
    print("\n✅ 引擎已正常关闭")

    return True

def print_recommendations():
    """打印配置建议"""
    print("\n" + "=" * 60)
    print("配置建议")
    print("=" * 60)
    print("""
基于测试结果，建议以下配置：

【快速对弈】
nodes = 1000-2000
Threads = 2-4

【标准对弈】
nodes = 5000-10000
Threads = 4-6

【深度计算】
nodes = 20000-50000
Threads = 6-12

【GPU加速】
下载CUDA版本的lc0.exe
设置 Threads = 0

详细配置请查看: lc0_config.txt
""")

def main():
    """主函数"""
    try:
        success = test_lc0_basic()

        if success:
            print("\n" + "=" * 60)
            print("✅ LCZero引擎测试通过！")
            print("=" * 60)
            print("\n你的引擎配置正确，可以正常使用。")
            print_recommendations()
        else:
            print("\n" + "=" * 60)
            print("❌ LCZero引擎测试失败")
            print("=" * 60)
            print("\n请检查:")
            print("1. lc0.exe是否在正确位置")
            print("2. 是否有足够的权限")
            print("3. 神经网络权重文件是否存在")

    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    main()
