# 从零构建的国际象棋AI引擎

本项目包含三种不同范式的国际象棋AI引擎，完全从零开始构建，不依赖现成的引擎（如Stockfish）。

## 📚 引擎类型

### 1. **Minimax引擎** (chess_engine.py)
基于经典博弈论的搜索引擎

**特点：**
- 使用Minimax算法和Alpha-Beta剪枝
- 包含局面评估函数
- 支持置换表加速
- 搜索深度可调

**适用场景：**
- 快速开局评估
- 有限搜索深度
- 作为训练对手

**代码示例：**
```python
from chess_engine import MinimaxEngine

# 创建引擎（搜索深度4）
engine = MinimaxEngine(depth=4)

# 获取最佳走法
board = chess.Board()
best_move = engine.get_best_move(board)
print(f"最佳走法: {best_move.uci()}")
```

---

### 2. **强化学习引擎** (chess_engine.py)
基于Q-Learning的自学习引擎

**特点：**
- 从零开始学习，只知道规则
- 通过自我对弈提升
- Q-table存储经验
- Epsilon-greedy探索策略

**适用场景：**
- 持续训练和改进
- 自我提升
- 体验AI学习过程

**代码示例：**
```python
from chess_engine import ReinforcementLearningEngine

# 创建RL引擎
rl_engine = ReinforcementLearningEngine(
    learning_rate=0.1,
    discount_factor=0.95,
    epsilon=0.1  # 探索率
)

# 训练（自我对弈100局）
stats = rl_engine.self_play(num_games=100, engine_depth=3)
print(f"训练结果: {stats}")

# 保存训练好的模型
rl_engine.save_model("my_chess_model.pkl")

# 加载模型
rl_engine.load_model("my_chess_model.pkl")

# 使用训练好的模型
board = chess.Board()
best_move = rl_engine.get_best_move(board)
```

**学习曲线示例：**
```
开始自我对弈训练 (100 局)...
已完成 10/100 局
胜: 2, 负: 7, 和: 1
探索率: 0.299
已完成 20/100 局
胜: 5, 负: 13, 和: 2
探索率: 0.278
...
已完成 100/100 局
胜: 35, 负: 55, 和: 10
```

---

### 3. **神经网络AI** (neural_chess_ai.py)
AlphaZero风格的深度强化学习

**特点：**
- 策略-价值网络
- 蒙特卡洛树搜索（MCTS）
- 自我对弈训练
- 深度残差网络

**架构：**
```
输入 (8x8x12) → 卷积层 → 6个残差块
                              ↓
                 ┌────────────┴────────────┐
                 ↓                         ↓
            策略头（走法概率）          价值头（局面评分）
                 ↓                         ↓
            走法分布                    -1到+1评分
```

**适用场景：**
- 高水平对弈
- 研究深度学习
- 长期训练项目

**代码示例：**
```python
from neural_chess_ai import (
    ChessPolicyValueNet,
    MCTS,
    AlphaZeroTrainer
)

# 创建网络
network = ChessPolicyValueNet(num_actions=4096)

# 创建MCTS
mcts = MCTS(network, c_puct=1.0, num_simulations=800)

# 创建训练器
trainer = AlphaZeroTrainer(network, mcts)

# 开始训练（1000局对弈，20轮训练）
trainer.train(num_games=1000, num_epochs=20)

# 保存模型
trainer.save_model("alphazero_chess.pth")

# 推理使用
board = chess.Board()
best_move, probs = mcts.search(board)
print(f"最佳走法: {best_move.uci()}")
```

---

## 🚀 快速开始

### 安装依赖

```bash
cd chess-bot
pip install torch numpy python-chess
```

### 选择引擎

**初学者/快速体验：** Minimax引擎
```bash
python3 -c "from chess_engine import MinimaxEngine; engine=MinimaxEngine(depth=3); print(engine.get_best_move(chess.Board()).uci())"
```

**学习AI原理：** 强化学习引擎
```python
from chess_engine import ReinforcementLearningEngine
engine = ReinforcementLearningEngine()
stats = engine.self_play(num_games=10, engine_depth=2)
```

**深入研究：** 神经网络AI
```python
from neural_chess_ai import AlphaZeroTrainer, ChessPolicyValueNet, MCTS
network = ChessPolicyValueNet()
mcts = MCTS(network, num_simulations=100)
trainer = AlphaZeroTrainer(network, mcts)
trainer.train(num_games=10, num_epochs=5)
```

---

## 📊 性能对比

| 引擎类型 | 训练时间 | 强度 | 资源需求 | 可解释性 |
|---------|---------|------|---------|---------|
| Minimax | 无 | 中 | 低 | 高 |
| Q-Learning | 数小时 | 低-中 | 低 | 中 |
| AlphaZero | 数天 | 高 | 高 | 低 |

---

## 🔧 高级用法

### 自定义评估函数

```python
from chess_engine import PositionEvaluator

class MyEvaluator(PositionEvaluator):
    def evaluate(self, board):
        # 自定义评估逻辑
        score = super().evaluate(board)

        # 添加自定义因素
        if board.has_queenside_castling_rights(chess.WHITE):
            score += 20

        return score

# 使用自定义评估器
engine = MinimaxEngine(depth=4)
engine.evaluator = MyEvaluator()
```

### 混合引擎

结合Minimax和强化学习：

```python
from chess_engine import HybridEngine

hybrid = HybridEngine(minimax_depth=3)

# 训练RL部分
hybrid.train(num_games=100)

# 使用RL模型
move = hybrid.get_best_move(board, use_rl=True)

# 使用Minimax
move = hybrid.get_best_move(board, use_rl=False)
```

### 调整超参数

```python
# Q-Learning参数
rl_engine = ReinforcementLearningEngine(
    learning_rate=0.2,      # 更高学习率
    discount_factor=0.9,     # 更少重视未来
    epsilon=0.2             # 更多探索
)

# AlphaZero参数
trainer = AlphaZeroTrainer(
    network=network,
    mcts=mcts,
    learning_rate=0.0001,   # 更低学习率
    batch_size=64           # 更大批次
)
```

---

## 📈 训练指南

### Q-Learning训练流程

1. **初始化：** 创建空的Q-table
2. **探索：** 随机走棋，收集经验
3. **学习：** 使用Q-learning公式更新Q值
4. **迭代：** 重复自我对弈，逐渐降低探索率
5. **收敛：** 模型稳定后保存

**训练参数建议：**
- 初期：epsilon=0.3（大量探索）
- 中期：epsilon=0.1（平衡探索和利用）
- 后期：epsilon=0.05（主要利用已知策略）

### AlphaZero训练流程

1. **随机初始化网络**
2. **自我对弈：** 使用MCTS+当前网络生成训练数据
3. **训练网络：** 从数据中学习改进策略和价值预测
4. **迭代：** 重复2-3，模型不断改进

**训练时间估算：**
- 100局对弈：约10-30分钟（CPU）
- 1000局对弈：约2-5小时（CPU）
- 10000局对弈：约1-3天（GPU推荐）

---

## 🎯 实战应用

### 与人类对弈

```python
from chess_bot import ChessBot
from chess_engine import ReinforcementLearningEngine

# 创建机器人
bot = ChessBot()
bot.set_board_region(100, 100, 600, 600)

# 加载训练好的RL模型
rl_engine = ReinforcementLearningEngine()
rl_engine.load_model("trained_model.pkl")

# 替换棋盘扫描中的AI部分
def custom_scan_and_move():
    board = bot.scan_board()
    move = rl_engine.get_best_move(board)
    bot.execute_move(move)
```

### 分析对局

```python
import chess.pgn

# 加载对局记录
pgn_file = open("game.pgn")
game = chess.pgn.read_game(pgn_file)
board = game.board()

# 使用AI分析每一步
engine = MinimaxEngine(depth=5)
for move in game.mainline_moves():
    best_move = engine.get_best_move(board)
    print(f"实际走法: {move.uci()}")
    print(f"推荐走法: {best_move.uci()}")
    board.push(move)
```

---

## 🧪 实验

### 实验1：学习率影响

```python
learning_rates = [0.05, 0.1, 0.2, 0.3]

for lr in learning_rates:
    engine = ReinforcementLearningEngine(learning_rate=lr)
    stats = engine.self_play(num_games=100)
    print(f"LR={lr}: {stats['wins']}胜")
```

### 实验2：探索率衰减

```python
# 指数衰减
epsilon = 0.3
for game in range(100):
    epsilon = max(0.01, epsilon * 0.99)
    # 使用当前epsilon进行对弈
```

### 实验3：搜索深度对比

```python
depths = [2, 3, 4, 5]

for depth in depths:
    engine = MinimaxEngine(depth=depth)
    start = time.time()
    move = engine.get_best_move(board)
    elapsed = time.time() - start
    print(f"深度={depth}, 耗时={elapsed:.2f}s")
```

---

## 💡 最佳实践

### Q-Learning

✅ **推荐：**
- 从小的搜索深度开始（engine_depth=2）
- 逐步增加训练局数
- 定期保存模型
- 使用较大的学习率（0.1-0.2）

❌ **避免：**
- 训练局数太少（<50局）
- 探索率过高（>0.5）
- 不保存中间结果

### AlphaZero

✅ **推荐：**
- 使用GPU加速
- 分批训练（100局/批次）
- 定期评估模型性能
- 使用合适的MCTS模拟次数（100-1000）

❌ **避免：**
- 一次性训练过多对局（>10000局）
- MCTS模拟次数过少（<50）
- 不监控训练曲线

---

## 📚 参考资料

### 理论基础

1. **Minimax算法**
   - 博弈论基础
   - Alpha-Beta剪枝原理

2. **强化学习**
   - Q-Learning算法
   - 探索-利用权衡

3. **深度强化学习**
   - AlphaZero论文
   - 策略-价值网络

### 扩展阅读

- "Mastering the game of Go with deep neural networks" (Nature)
- "Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm" (AlphaZero)
- "Human-level control through deep reinforcement learning" (DQN)

---

## 🔧 故障排查

### Q-Learning收敛慢

**问题：** 胜率提升不明显

**解决方案：**
- 增加训练局数
- 提高学习率
- 调整探索率衰减
- 使用更强的对手（降低engine_depth）

### 内存不足

**问题：** AlphaZero训练时内存溢出

**解决方案：**
- 减小batch_size
- 使用梯度累积
- 减小模型尺寸
- 限制经验缓冲区大小

### 训练不稳定

**问题：** 损失震荡或发散

**解决方案：**
- 降低学习率
- 增加训练数据
- 使用学习率衰减
- 添加正则化

---

## 🚀 未来方向

1. **改进网络架构**
   - 使用Transformer
   - 注意力机制
   - 多尺度特征提取

2. **高级训练技巧**
   - 课程学习
   - 对抗训练
   - 迁移学习

3. **集成优化**
   - 模型蒸馏
   - 集成学习
   - 神经网络+传统算法混合

---

## 📄 许可证

MIT License

---

**祝你探索愉快！让AI从零开始成为国际象棋大师！♟️**
