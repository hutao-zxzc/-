#!/usr/bin/env python3
"""
AI引擎训练和对弈演示
展示三种不同的AI引擎如何从零开始学习和对弈
"""

import chess
import time
from pathlib import Path
import matplotlib.pyplot as plt


def demo_minimax():
    """演示Minimax引擎"""
    print("\n" + "="*60)
    print("1. Minimax引擎演示")
    print("="*60)

    from chess_engine import MinimaxEngine

    # 创建不同深度的引擎
    depths = [1, 2, 3, 4]

    print("\n测试不同搜索深度的表现:")
    print("-" * 60)

    board = chess.Board()

    for depth in depths:
        engine = MinimaxEngine(depth=depth)

        start_time = time.time()
        move = engine.get_best_move(board)
        elapsed = time.time() - start_time

        if move:
            print(f"深度={depth}: {move.uci():>6s} | "
                  f"节点数={engine.nodes_visited:>8d} | "
                  f"耗时={elapsed:.4f}s")

    print("\n分析开局走法:")
    print("-" * 60)

    # 比较不同引擎的开局选择
    board = chess.Board()
    engines = {
        "深度2": MinimaxEngine(depth=2),
        "深度3": MinimaxEngine(depth=3),
        "深度4": MinimaxEngine(depth=4),
    }

    for name, engine in engines.items():
        move = engine.get_best_move(board)
        if move:
            # 查询开局库
            opening = chess.polyglot.opening_data.get(move.uci())
            opening_name = opening if opening else "未知开局"

            print(f"{name:>6s}: {move.uci():>6s} ({opening_name})")


def demo_q_learning():
    """演示Q-Learning训练"""
    print("\n" + "="*60)
    print("2. Q-Learning引擎演示")
    print("="*60)

    from chess_engine import ReinforcementLearningEngine

    # 创建引擎
    print("\n初始化Q-Learning引擎...")
    rl_engine = ReinforcementLearningEngine(
        learning_rate=0.15,
        discount_factor=0.95,
        epsilon=0.3
    )

    # 分阶段训练
    stages = [
        (10, 1, "第一阶段：快速探索（对手强度低）"),
        (20, 2, "第二阶段：逐步提高难度"),
        (30, 3, "第三阶段：接近正常水平"),
    ]

    print("\n开始分阶段训练:")
    print("-" * 60)

    training_history = []

    for num_games, opponent_depth, stage_name in stages:
        print(f"\n{stage_name}")
        print(f"训练 {num_games} 局，对手搜索深度={opponent_depth}")

        stats_before = {
            'wins': rl_engine.wins,
            'losses': rl_engine.losses,
            'draws': rl_engine.draws,
            'total': rl_engine.games_played
        }

        stats = rl_engine.self_play(num_games=num_games,
                                   engine_depth=opponent_depth)

        stats_after = {
            'wins': rl_engine.wins,
            'losses': rl_engine.losses,
            'draws': rl_engine.draws,
            'total': rl_engine.games_played
        }

        # 计算本阶段战绩
        stage_wins = stats_after['wins'] - stats_before['wins']
        stage_losses = stats_after['losses'] - stats_before['losses']
        stage_draws = stats_after['draws'] - stats_before['draws']

        win_rate = stage_wins / num_games * 100

        print(f"本阶段: {stage_wins}胜 {stage_losses}负 {stage_draws}和 "
              f"(胜率 {win_rate:.1f}%)")
        print(f"探索率: {rl_engine.epsilon:.3f}")

        training_history.append({
            'stage': stage_name,
            'wins': stage_wins,
            'losses': stage_losses,
            'draws': stage_draws,
            'win_rate': win_rate,
            'epsilon': rl_engine.epsilon
        })

    # 显示训练总结
    print("\n训练总结:")
    print("-" * 60)
    print(f"总场次: {rl_engine.games_played}")
    print(f"总战绩: {rl_engine.wins}胜 {rl_engine.losses}负 {rl_engine.draws}和")
    print(f"最终胜率: {rl_engine.wins/rl_engine.games_played*100:.1f}%")
    print(f"最终探索率: {rl_engine.epsilon:.3f}")

    # 保存模型
    model_path = Path(__file__).parent / "demo_rl_model.pkl"
    rl_engine.save_model(str(model_path))

    # 测试训练好的模型
    print("\n测试训练好的模型:")
    print("-" * 60)
    rl_engine.epsilon = 0  # 不探索，只利用

    board = chess.Board()
    for i in range(5):
        move = rl_engine.get_best_move(board)
        if move:
            print(f"第{i+1}步: {move.uci()}")
            board.push(move)

    return training_history


def demo_alphazero_lite():
    """演示轻量级AlphaZero训练"""
    print("\n" + "="*60)
    print("3. AlphaZero风格AI演示（轻量级）")
    print("="*60)

    from neural_chess_ai import ChessPolicyValueNet, MCTS, AlphaZeroTrainer

    # 检查是否有GPU
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n使用设备: {device}")

    # 创建网络（小规模）
    print("\n创建神经网络...")
    network = ChessPolicyValueNet(num_actions=4096)
    network = network.to(device)

    # 创建MCTS（模拟次数少，用于演示）
    print("创建MCTS搜索...")
    mcts = MCTS(network,
                c_puct=1.0,
                num_simulations=50)  # 减少模拟次数用于快速演示

    # 创建训练器
    print("创建训练器...")
    trainer = AlphaZeroTrainer(network, mcts,
                              learning_rate=0.001,
                              batch_size=16)

    # 小规模训练演示
    print("\n开始训练（小规模演示）:")
    print("-" * 60)
    print("警告: 这只是演示，实际训练需要大量时间")

    try:
        trainer.train(num_games=20, num_epochs=10)

        # 保存模型
        model_path = Path(__file__).parent / "demo_alphazero.pth"
        trainer.save_model(str(model_path))

        print("\n演示训练完成!")
        print("完整训练建议：1000局对弈，20轮训练")
        print(f"完整训练需要: 约{1000/20*trainer.training_steps/60:.1f}小时")

    except Exception as e:
        print(f"\n训练过程中出现错误: {e}")
        print("这可能是由于资源限制或设备不支持")
        print("建议在实际训练前检查系统配置")


def demo_engine_comparison():
    """演示不同引擎的对比"""
    print("\n" + "="*60)
    print("4. 引擎对比测试")
    print("="*60)

    from chess_engine import MinimaxEngine, ReinforcementLearningEngine

    # 创建引擎
    engines = {
        "Minimax(深度2)": MinimaxEngine(depth=2),
        "Minimax(深度3)": MinimaxEngine(depth=3),
        "Q-Learning": ReinforcementLearningEngine(),
    }

    # 测试开局局面
    test_positions = [
        ("初始局面", chess.Board()),
        ("意大利开局", chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")),
        ("西西里防御", chess.Board("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2")),
    ]

    print("\n在不同开局局面下，各引擎的选择:")
    print("-" * 60)

    for name, board in test_positions:
        print(f"\n{name}:")
        for engine_name, engine in engines.items():
            move = engine.get_best_move(board)
            if move:
                print(f"  {engine_name:>15s}: {move.uci()}")


def demo_learning_curve():
    """演示学习曲线"""
    print("\n" + "="*60)
    print("5. 学习曲线可视化")
    print("="*60)

    from chess_engine import ReinforcementLearningEngine

    print("\n进行长时间训练以生成学习曲线...")

    engine = ReinforcementLearningEngine(epsilon=0.4)

    # 记录训练数据
    win_rates = []
    game_numbers = []

    # 训练200局
    batch_size = 20
    num_batches = 10

    for batch in range(num_batches):
        print(f"\n批次 {batch+1}/{num_batches}")

        start_wins = engine.wins
        engine.self_play(num_games=batch_size, engine_depth=2)
        batch_wins = engine.wins - start_wins

        win_rate = batch_wins / batch_size * 100
        win_rates.append(win_rate)
        game_numbers.append((batch + 1) * batch_size)

        print(f"本批次胜率: {win_rate:.1f}%")
        print(f"总场次: {engine.games_played}")

    # 绘制学习曲线
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(game_numbers, win_rates, 'b-o', linewidth=2, markersize=8)
        plt.xlabel('对弈局数', fontsize=12)
        plt.ylabel('胜率 (%)', fontsize=12)
        plt.title('Q-Learning引擎学习曲线', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)

        # 添加趋势线
        import numpy as np
        z = np.polyfit(game_numbers, win_rates, 2)
        p = np.poly1d(z)
        plt.plot(game_numbers, p(game_numbers), "r--", alpha=0.7,
                label='趋势线')

        plt.legend(fontsize=10)
        plt.tight_layout()

        # 保存图表
        chart_path = Path(__file__).parent / "learning_curve.png"
        plt.savefig(chart_path, dpi=150)
        print(f"\n学习曲线已保存: {chart_path}")

        # 显示统计信息
        print("\n学习曲线分析:")
        print("-" * 60)
        print(f"初始胜率: {win_rates[0]:.1f}%")
        print(f"最终胜率: {win_rates[-1]:.1f}%")
        print(f"平均胜率: {np.mean(win_rates):.1f}%")
        print(f"最高胜率: {max(win_rates):.1f}%")
        print(f"胜率提升: {win_rates[-1] - win_rates[0]:.1f}%")

    except Exception as e:
        print(f"\n无法生成图表: {e}")
        print("请确保已安装matplotlib: pip install matplotlib")


def demo_ai_vs_ai():
    """演示AI vs AI对弈"""
    print("\n" + "="*60)
    print("6. AI vs AI 对弈")
    print("="*60)

    from chess_engine import MinimaxEngine, ReinforcementLearningEngine

    # 创建两个引擎
    engine1 = MinimaxEngine(depth=3)
    engine2 = MinimaxEngine(depth=3)

    # 或者：Minimax vs Q-Learning
    # engine2 = ReinforcementLearningEngine()

    board = chess.Board()
    move_history = []

    print("\n开始对弈:")
    print("-" * 60)
    print(board)

    while not board.is_game_over():
        # 判断轮到谁
        if board.turn == chess.WHITE:
            move = engine1.get_best_move(board)
            player = "白方(Minimax)"
        else:
            move = engine2.get_best_move(board)
            player = "黑方(Minimax)"

        if move is None:
            break

        print(f"\n{player}: {move.uci()}")
        board.push(move)
        move_history.append(move.uci())

        print(board)

        # 每10步暂停一下
        if len(move_history) % 10 == 0:
            input("\n按Enter继续...")

    # 游戏结束
    result = board.result()

    print("\n" + "="*60)
    print("对弈结束")
    print("="*60)
    print(f"结果: {result}")
    print(f"总步数: {len(move_history)}")
    print(f"\n对弈记录:")
    for i, move in enumerate(move_history, 1):
        print(f"{i}. {move}")


def main():
    """主程序"""
    print("="*60)
    print("国际象棋AI引擎演示")
    print("从零开始学习和对弈")
    print("="*60)

    print("\n可用的演示:")
    print("1. Minimax引擎演示")
    print("2. Q-Learning引擎训练演示")
    print("3. AlphaZero风格AI演示（轻量级）")
    print("4. 引擎对比测试")
    print("5. 学习曲线可视化")
    print("6. AI vs AI 对弈")
    print("0. 运行所有演示")
    print("q. 退出")

    while True:
        choice = input("\n请选择演示 (0-6, q): ").strip().lower()

        if choice == "q":
            print("退出演示")
            break
        elif choice == "0":
            print("\n运行所有演示...")
            try:
                demo_minimax()
                demo_q_learning()
                demo_alphazero_lite()
                demo_engine_comparison()
                demo_learning_curve()
                print("\n所有演示完成!")
            except Exception as e:
                print(f"\n演示过程中出现错误: {e}")
        elif choice == "1":
            demo_minimax()
        elif choice == "2":
            demo_q_learning()
        elif choice == "3":
            demo_alphazero_lite()
        elif choice == "4":
            demo_engine_comparison()
        elif choice == "5":
            demo_learning_curve()
        elif choice == "6":
            demo_ai_vs_ai()
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    main()
