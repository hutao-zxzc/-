#!/usr/bin/env python3
"""
神经网络国际象棋AI - AlphaZero风格
使用深度强化学习从零开始训练
"""

import chess
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from typing import List, Tuple, Optional
import random
from collections import deque
import pickle
from pathlib import Path


class ChessBoardEncoder:
    """将棋盘状态编码为神经网络输入"""

    def __init__(self):
        # 棋子到通道的映射
        self.piece_to_channel = {
            (chess.WHITE, chess.PAWN): 0,
            (chess.WHITE, chess.KNIGHT): 1,
            (chess.WHITE, chess.BISHOP): 2,
            (chess.WHITE, chess.ROOK): 3,
            (chess.WHITE, chess.QUEEN): 4,
            (chess.WHITE, chess.KING): 5,
            (chess.BLACK, chess.PAWN): 6,
            (chess.BLACK, chess.KNIGHT): 7,
            (chess.BLACK, chess.BISHOP): 8,
            (chess.BLACK, chess.ROOK): 9,
            (chess.BLACK, chess.QUEEN): 10,
            (chess.BLACK, chess.KING): 11,
        }

    def encode(self, board: chess.Board) -> np.ndarray:
        """
        将棋盘编码为8x8x12的张量

        Args:
            board: 棋盘状态

        Returns:
            形状为(12, 8, 8)的numpy数组
        """
        # 创建8x8x12的数组
        encoding = np.zeros((12, 8, 8), dtype=np.float32)

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                channel = self.piece_to_channel.get((piece.color, piece.piece_type))
                if channel is not None:
                    # 转换坐标
                    rank = chess.rank_index(square)  # 0-7
                    file = chess.file_index(square)  # 0-7
                    encoding[channel, rank, file] = 1.0

        # 添加额外特征（可选）
        # 可以添加：回合数、王车易用权、吃过路兵等

        return encoding

    def encode_batch(self, boards: List[chess.Board]) -> torch.Tensor:
        """批量编码棋盘"""
        encodings = [self.encode(board) for board in boards]
        return torch.from_numpy(np.stack(encodings))


class ChessPolicyValueNet(nn.Module):
    """
    国际象棋策略-价值网络
    同时输出走法概率（策略）和局面评分（价值）
    """

    def __init__(self, num_actions=4096):
        """
        初始化网络

        Args:
            num_actions: 动作数量（所有可能的走法）
        """
        super(ChessPolicyValueNet, self).__init__()

        # 特征提取层
        self.conv1 = nn.Conv2d(12, 256, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(256)

        self.conv2 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(256)

        self.conv3 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(256)

        # 残差块
        self.res_blocks = nn.ModuleList([
            ResidualBlock(256) for _ in range(6)  # 6个残差块
        ])

        # 策略头（输出走法概率）
        self.policy_conv = nn.Conv2d(256, 2, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(2)
        self.policy_fc = nn.Linear(2 * 8 * 8, num_actions)

        # 价值头（输出局面评分）
        self.value_conv = nn.Conv2d(256, 1, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(1 * 8 * 8, 256)
        self.value_fc2 = nn.Linear(256, 1)

    def forward(self, x):
        """
        前向传播

        Args:
            x: 输入张量 (batch_size, 12, 8, 8)

        Returns:
            (policy_logits, value)
            policy_logits: 走法概率 (batch_size, num_actions)
            value: 局面评分 (batch_size, 1)
        """
        # 特征提取
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))

        # 残差块
        for res_block in self.res_blocks:
            x = res_block(x)

        # 策略头
        policy = F.relu(self.policy_bn(self.policy_conv(x)))
        policy = policy.view(policy.size(0), -1)
        policy_logits = self.policy_fc(policy)

        # 价值头
        value = F.relu(self.value_bn(self.value_conv(x)))
        value = value.view(value.size(0), -1)
        value = F.relu(self.value_fc1(value))
        value = torch.tanh(self.value_fc2(value))

        return policy_logits, value


class ResidualBlock(nn.Module):
    """残差块"""

    def __init__(self, num_channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(num_channels, num_channels,
                                kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(num_channels)

        self.conv2 = nn.Conv2d(num_channels, num_channels,
                                kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(num_channels)

    def forward(self, x):
        identity = x

        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))

        out += identity
        out = F.relu(out)

        return out


class MCTS:
    """
    蒙特卡洛树搜索
    用于引导神经网络训练和推理
    """

    def __init__(self, network: ChessPolicyValueNet,
                 c_puct: float = 1.0,
                 num_simulations: int = 800):
        """
        初始化MCTS

        Args:
            network: 策略-价值网络
            c_puct: 探索系数
            num_simulations: 模拟次数
        """
        self.network = network
        self.c_puct = c_puct
        self.num_simulations = num_simulations

        # 树节点存储
        # key: FEN字符串
        # value: {N: 访问次数, W: 总价值, Q: 平均价值, P: 先验概率, children: 子节点}
        self.tree = {}

        self.encoder = ChessBoardEncoder()

    def search(self, board: chess.Board) -> Tuple[chess.Move, np.ndarray]:
        """
        MCTS搜索

        Args:
            board: 当前棋盘

        Returns:
            (最佳走法, 走法概率分布)
        """
        # 运行模拟
        for _ in range(self.num_simulations):
            self._simulate(board.copy())

        # 获取最佳走法
        state = board.fen()
        if state not in self.tree:
            return None, np.zeros(1)

        node = self.tree[state]

        # 选择访问次数最多的走法
        best_move = None
        best_visit_count = -1

        move_probs = []
        total_visits = sum(child['N'] for child in node['children'].values())

        for move, child in node['children'].items():
            move_probs.append(child['N'] / total_visits)

            if child['N'] > best_visit_count:
                best_visit_count = child['N']
                best_move = move

        return best_move, np.array(move_probs)

    def _simulate(self, board: chess.Board):
        """执行一次模拟"""
        state = board.fen()

        # 如果是叶子节点，使用网络评估
        if state not in self.tree:
            self._expand_node(board)
            return self._evaluate(board)

        # 选择
        move = self._select_move(state)
        board.push(move)

        # 递归模拟
        value = -self._simulate(board)

        # 回溯更新
        self._backpropagate(state, move, value)

        return value

    def _expand_node(self, board: chess.Board):
        """展开节点"""
        state = board.fen()

        # 获取网络预测
        state_tensor = self.encoder.encode([board])
        with torch.no_grad():
            policy_logits, value = self.network(state_tensor)

        policy_probs = F.softmax(policy_logits, dim=1)
        policy_probs_np = policy_probs.squeeze().cpu().numpy()
        value_np = value.squeeze().cpu().numpy()

        # 创建节点
        legal_moves = list(board.legal_moves)
        children = {}

        for move in legal_moves:
            # 使用网络预测作为先验概率
            # 这里简化处理，实际应该映射到对应的走法索引
            prior_prob = 1.0 / len(legal_moves)

            children[move] = {
                'N': 0,
                'W': 0.0,
                'Q': 0.0,
                'P': prior_prob
            }

        self.tree[state] = {
            'N': 0,
            'W': 0.0,
            'Q': value_np,
            'P': policy_probs_np,
            'children': children
        }

    def _select_move(self, state: str) -> chess.Move:
        """PUCT算法选择走法"""
        node = self.tree[state]

        best_score = -float('inf')
        best_move = None

        sqrt_N = np.sqrt(node['N'])

        for move, child in node['children'].items():
            # PUCT公式
            u = self.c_puct * child['P'] * sqrt_N / (1 + child['N'])
            score = child['Q'] + u

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _evaluate(self, board: chess.Board) -> float:
        """使用网络评估局面"""
        state_tensor = self.encoder.encode([board])
        with torch.no_grad():
            _, value = self.network(state_tensor)
        return value.squeeze().cpu().numpy()

    def _backpropagate(self, state: str, move: chess.Move, value: float):
        """回溯更新节点"""
        node = self.tree[state]
        child = node['children'][move]

        child['N'] += 1
        child['W'] += value
        child['Q'] = child['W'] / child['N']


class AlphaZeroTrainer:
    """
    AlphaZero训练器
    通过自我对弈训练神经网络
    """

    def __init__(self, network: ChessPolicyValueNet,
                 mcts: MCTS,
                 learning_rate: float = 0.001,
                 batch_size: int = 32):
        """
        初始化训练器

        Args:
            network: 网络
            mcts: MCTS搜索
            learning_rate: 学习率
            batch_size: 批大小
        """
        self.network = network
        self.mcts = mcts
        self.batch_size = batch_size

        self.optimizer = optim.Adam(self.network.parameters(), lr=learning_rate)

        # 经验回放缓冲区
        self.replay_buffer = deque(maxlen=100000)

        # 训练统计
        self.games_played = 0
        self.training_steps = 0

    def self_play(self, num_games: int = 1000) -> List[Tuple]:
        """
        自我对弈生成训练数据

        Args:
            num_games: 对弈局数

        Returns:
            训练数据列表 [(state, policy, value), ...]
        """
        training_data = []

        print(f"开始自我对弈 ({num_games} 局)...")

        for game_num in range(num_games):
            board = chess.Board()
            game_data = []

            while not board.is_game_over():
                # MCTS搜索
                move, policy_probs = self.mcts.search(board)

                if move is None:
                    break

                # 保存训练数据
                state = board.fen()
                game_data.append((state, policy_probs, None))

                # 执行走法
                board.push(move)

            # 游戏结束，确定胜负
            result = board.result()

            # 计算每一步的价值
            if result == "1-0":
                final_value = 1.0  # 白方胜
            elif result == "0-1":
                final_value = -1.0  # 黑方胜
            else:
                final_value = 0.0  # 和棋

            # 奇数步是白方（我们），偶数步是黑方
            for i, (state, policy, _) in enumerate(game_data):
                if i % 2 == 0:
                    # 白方走棋
                    value = final_value
                else:
                    # 黑方走棋（白方的价值是相反的）
                    value = -final_value

                training_data.append((state, policy, value))

            self.games_played += 1

            if (game_num + 1) % 100 == 0:
                print(f"已完成 {game_num + 1}/{num_games} 局对弈")

        print(f"对弈完成，生成 {len(training_data)} 条训练数据")
        return training_data

    def train(self, num_games: int = 100, num_epochs: int = 10):
        """
        训练模型

        Args:
            num_games: 自我对弈局数
            num_epochs: 训练轮数
        """
        # 生成训练数据
        training_data = self.self_play(num_games)

        # 添加到经验缓冲区
        self.replay_buffer.extend(training_data)

        # 训练网络
        print(f"\n开始训练 ({num_epochs} 轮)...")

        encoder = ChessBoardEncoder()
        total_loss = 0

        for epoch in range(num_epochs):
            # 随机采样批次
            batch_data = random.sample(list(self.replay_buffer),
                                      min(len(self.replay_buffer), self.batch_size))

            # 准备数据
            states, policies, values = zip(*batch_data)

            # 编码状态
            boards = [chess.Board(s) for s in states]
            state_tensors = encoder.encode_batch(boards)

            # 转换为tensor
            policy_targets = torch.FloatTensor(policies)
            value_targets = torch.FloatTensor(values).unsqueeze(1)

            # 前向传播
            self.optimizer.zero_grad()
            policy_logits, predicted_values = self.network(state_tensors)

            # 计算损失
            # 策略损失：交叉熵
            policy_loss = F.cross_entropy(policy_logits,
                                        policy_targets.argmax(dim=1))

            # 价值损失：MSE
            value_loss = F.mse_loss(predicted_values, value_targets)

            # 总损失
            loss = policy_loss + value_loss

            # 反向传播
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

            self.training_steps += 1

            if (epoch + 1) % 10 == 0:
                avg_loss = total_loss / 10
                print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")
                total_loss = 0

        print("\n训练完成！")

    def save_model(self, filepath: str):
        """保存模型"""
        checkpoint = {
            'network_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'games_played': self.games_played,
            'training_steps': self.training_steps
        }

        torch.save(checkpoint, filepath)
        print(f"模型已保存: {filepath}")

    def load_model(self, filepath: str):
        """加载模型"""
        checkpoint = torch.load(filepath, map_location='cpu')

        self.network.load_state_dict(checkpoint['network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.games_played = checkpoint['games_played']
        self.training_steps = checkpoint['training_steps']

        print(f"模型已加载: {filepath}")
        print(f"训练统计: {self.games_played} 局, {self.training_steps} 步")


def main():
    """演示AlphaZero训练"""
    print("=== AlphaZero风格国际象棋AI ===\n")

    # 初始化设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}\n")

    # 创建网络
    print("创建神经网络...")
    network = ChessPolicyValueNet(num_actions=4096).to(device)

    # 创建MCTS
    print("创建MCTS搜索...")
    mcts = MCTS(network, c_puct=1.0, num_simulations=100)

    # 创建训练器
    print("创建训练器...")
    trainer = AlphaZeroTrainer(network, mcts,
                              learning_rate=0.001,
                              batch_size=32)

    # 开始训练
    print("\n" + "=" * 50)
    print("开始训练（小规模演示）")
    print("=" * 50 + "\n")

    trainer.train(num_games=50, num_epochs=20)

    # 保存模型
    model_path = Path(__file__).parent / "alphazero_model.pth"
    trainer.save_model(str(model_path))

    print("\n" + "=" * 50)
    print("训练完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
