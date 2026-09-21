#!/usr/bin/env python3
"""
简单的测试脚本 - 验证LCZero引擎是否正常工作
"""

import chess
import chess.engine
import time
from pathlib import Path
import sys

def test_lc0():
    """测试LCZero引擎"""
    print("=" * 60)
    print("LCZero 引擎测试")
    print("=" * 60)

    # 查找引擎
    if sys.platform == "win32":
        script_dir = Path(__file__).parent
        lc0_path = script_dir / "lc0.exe"
        if lc0_path.exists():
            engine_path = str(lc0_path)
        else:
            engine_path = "lc0"
    else:
        engine_path = "lc0"

    print(f"\n引擎路径: {engine_path}")

    # 检查文件是否存在
    if not Path(engine_path).exists():
        print("❌ 错误: 找不到 lc0.exe")
        print("\n请确保:")
        print("1. lc0.exe 在当前目录")
        print("2. 或者 lc0.exe 在系统PATH中")
        return False

    print("✅ 引擎文件存在")

    # 测试启动引擎
    print("\n启动引擎...")
    try:
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        print("✅ 引擎启动成功")
    except Exception as e:
        print(f"❌ 引擎启动失败: {e}")
        return False

    # 测试基本功能
    print("\n测试计算最佳走法...")
    board = chess.Board()

    try:
        start_time = time.time()
        limit = chess.engine.Limit(nodes=1000)
        result = engine.play(board, limit)
        elapsed = time.time() - start_time

        print(f"✅ 计算成功")
        print(f"  最佳走法: {result.move.uci()}")
        print(f"  计算时间: {elapsed:.2f}秒")
        print(f"  速度: ~{int(1000/elapsed)} NPS")
    except Exception as e:
        print(f"❌ 计算失败: {e}")
        engine.quit()
        return False

    # 关闭引擎
    engine.quit()
    print("\n✅ 测试通过！引擎正常工作")

    return True

if __name__ == "__main__":
    try:
        success = test_lc0()
        if success:
            print("\n🎉 你的LCZero配置正确，可以开始对弈了！")
        else:
            print("\n⚠️  测试失败，请检查配置")
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
