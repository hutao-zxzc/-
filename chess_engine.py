#!/usr/bin/env python3
"""
国际象棋AI引擎 - 从零构建
基于Minimax、Alpha-Beta剪枝和强化学习
"""

import chess
import numpy as np
import random
import time
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from collections import deque
import pickle
from pathlib import Path


@dataclass
class TrainingExperience:
    """训练经验样本"""
    state: str  # FEN格式
    action: chess.Move
    reward: float
    next_state: Optional[str]
    done: bool


class PieceSquareTables:
    """棋子-位置价值表（开局中局和残局不同）"""

    # 兵的位置价值
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]

    # 马的位置价值
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]

    # 象的位置价值
    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]

    # 车的位置价值
    ROOK_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]

    # 后的位置价值
    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]

    # 王的位置价值（中局）
    KING_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]

    # 王的位置价值（残局）
    KING_TABLE_ENDGAME = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-50,-30,-30,-30,-30,-30,-30,-50]
    ]


class PositionEvaluator:
    """局面评估器"""

    # 棋子基本价值
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    def __init__(self):
        self.tables = PieceSquareTables()

    def evaluate(self, board: chess.Board) -> float:
        """
        评估局面

        Args:
            board: 棋盘状态

        Returns:
            评估分数（正数白方优势，负数黑方优势）
        """
        if board.is_checkmate():
            return -10000 if board.turn == chess.WHITE else 10000

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        # 计算棋子总价值
        score = 0

        # 统计双方棋子数量
        white_pieces = 0
        black_pieces = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_value = self.PIECE_VALUES[piece.piece_type]

                # 获取位置价值
                square_index = 63 - square  # 转换坐标
                rank = square_index // 8
                file = square_index % 8

                pos_value = self._get_position_value(piece, rank, file)

                if piece.color == chess.WHITE:
                    white_pieces += piece_value
                    score += piece_value + pos_value
                else:
                    black_pieces += piece_value
                    score -= piece_value + pos_value

        # 其他评估因素
        score += self._evaluate_mobility(board)
        score += self._evaluate_control(board)
        score += self._evaluate_safety(board)

        return score

    def _get_position_value(self, piece: chess.Piece, rank: int, file: int) -> float:
        """获取棋子的位置价值"""
        table_map = {
            chess.PAWN: self.tables.PAWN_TABLE,
            chess.KNIGHT: self.tables.KNIGHT_TABLE,
            chess.BISHOP: self.tables.BISHOP_TABLE,
            chess.ROOK: self.tables.ROOK_TABLE,
            chess.QUEEN: self.tables.QUEEN_TABLE,
            chess.KING: self.tables.KING_TABLE
        }

        table = table_map.get(piece.piece_type, [[0]*8 for _ in range(8)])

        if piece.color == chess.BLACK:
            # 黑方需要翻转表格
            return table[7 - rank][7 - file]
        else:
            return table[rank][file]

    def _evaluate_mobility(self, board: chess.Board) -> float:
        """评估机动性（可移动步数）"""
        if board.turn == chess.WHITE:
            return len(list(board.legal_moves)) * 2
        else:
            return -len(list(board.legal_moves)) * 2

    def _evaluate_control(self, board: chess.Board) -> float:
        """评估中心控制"""
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        score = 0

        for square in center_squares:
            attackers = board.attackers(chess.WHITE, square)
            if attackers:
                score += 10 * len(list(attackers))

            attackers = board.attackers(chess.BLACK, square)
            if attackers:
                score -= 10 * len(list(attackers))

        return score

    def _evaluate_safety(self, board: chess.Board) -> float:
        """评估王的安全性"""
        score = 0

        # 检查是否被将军
        if board.is_check():
            if board.turn == chess.WHITE:
                score -= 50
            else:
                score += 50

        return score


class MinimaxEngine:
    """基于Minimax + Alpha-Beta剪枝的搜索引擎"""

    def __init__(self, depth: int = 4):
        """
        初始化引擎

        Args:
            depth: 搜索深度
        """
        self.depth = depth
        self.evaluator = PositionEvaluator()
        self.nodes_visited = 0
        self.transposition_table = {}  # 置换表

    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        获取最佳走法

        Args:
            board: 当前棋盘

        Returns:
            最佳走法
        """
        self.nodes_visited = 0
        start_time = time.time()

        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return None

        # 搜索所有走法
        best_move = None
        best_value = float('-inf')

        for move in legal_moves:
            board.push(move)
            value = -self._alpha_beta(board, self.depth - 1,
                                      float('-inf'), float('inf'),
                                      False)
            board.pop()

            if value > best_value:
                best_value = value
                best_move = move

        elapsed = time.time() - start_time
        print(f"搜索深度: {self.depth}, 节点数: {self.nodes_visited}, 耗时: {elapsed:.2f}s")

        return best_move

    def _alpha_beta(self, board: chess.Board, depth: int,
                    alpha: float, beta: float, is_maximizing: bool) -> float:
        """
        Alpha-Beta剪枝搜索

        Args:
            board: 棋盘
            depth: 剩余深度
            alpha: alpha值（最大玩家的最好选择）
            beta: beta值（最小玩家的最好选择）
            is_maximizing: 是否为最大化玩家

        Returns:
            评估值
        """
        self.nodes_visited += 1

        # 终止条件
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board)

        # 检查置换表
        board_key = board.fen()
        if board_key in self.transposition_table and depth in self.transposition_table[board_key]:
            return self.transposition_table[board_key][depth]

        legal_moves = list(board.legal_moves)

        if is_maximizing:
            value = float('-inf')
            for move in legal_moves:
                board.push(move)
                value = max(value, self._alpha_beta(board, depth - 1,
                                                    alpha, beta, False))
                board.pop()

                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta剪枝
        else:
            value = float('inf')
            for move in legal_moves:
                board.push(move)
                value = min(value, self._alpha_beta(board, depth - 1,
                                                    alpha, beta, True))
                board.pop()

                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha剪枝

        # 存入置换表
        if board_key not in self.transposition_table:
            self.transposition_table[board_key] = {}
        self.transposition_table[board_key][depth] = value

        return value


class ReinforcementLearningEngine:
    """基于强化学习的国际象棋引擎"""

    def __init__(self, learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 0.1):
        """
        初始化强化学习引擎

        Args:
            learning_rate: 学习率
            discount_factor: 折扣因子
            epsilon: 探索率
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # Q-table: state -> (action -> value)
        self.q_table: Dict[str, Dict[str, float]] = {}

        # 经验回放缓冲区
        self.replay_buffer: deque = deque(maxlen=10000)

        # 统计信息
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        获取最佳走法（使用epsilon-greedy策略）

        Args:
            board: 当前棋盘

        Returns:
            最佳走法
        """
        state = board.fen()
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return None

        # Epsilon-greedy探索
        if random.random() < self.epsilon:
            return random.choice(legal_moves)

        # 选择Q值最高的走法
        if state not in self.q_table:
            self.q_table[state] = {}

        # 为未访问的状态-动作对初始化Q值
        for move in legal_moves:
            move_uci = move.uci()
            if move_uci not in self.q_table[state]:
                self.q_table[state][move_uci] = 0.0

        # 选择最佳动作
        best_move = max(self.q_table[state].items(),
                       key=lambda x: x[1])[0]
        return chess.Move.from_uci(best_move)

    def learn(self, experience: TrainingExperience):
        """
        从经验中学习（Q-learning）

        Args:
            experience: 训练经验
        """
        state = experience.state
        action = experience.action.uci()
        reward = experience.reward
        next_state = experience.next_state
        done = experience.done

        # 初始化状态
        if state not in self.q_table:
            self.q_table[state] = {}

        # 初始化动作的Q值
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0

        # Q-learning更新公式
        old_q = self.q_table[state][action]

        if done or next_state is None:
            max_next_q = 0
        else:
            if next_state not in self.q_table:
                self.q_table[next_state] = {}
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0

        new_q = old_q + self.learning_rate * (reward + self.discount_factor * max_next_q - old_q)
        self.q_table[state][action] = new_q

    def self_play(self, num_games: int = 100,
                  engine_depth: int = 3) -> Dict[str, int]:
        """
        自我对弈训练

        Args:
            num_games: 游戏局数
            engine_depth: 对手引擎的搜索深度

        Returns:
            统计信息
        """
        print(f"开始自我对弈训练 ({num_games} 局)...")

        # 对手引擎（用于提供有意义的对战）
        opponent = MinimaxEngine(depth=engine_depth)

        for game_num in range(num_games):
            self._play_one_game(opponent)
            self.games_played += 1

            if (game_num + 1) % 10 == 0:
                print(f"已完成 {game_num + 1}/{num_games} 局")
                print(f"胜: {self.wins}, 负: {self.losses}, 和: {self.draws}")
                print(f"探索率: {self.epsilon:.3f}")

            # 逐渐降低探索率
            self.epsilon = max(0.01, self.epsilon * 0.995)

        print(f"\n训练完成！")
        print(f"总场次: {self.games_played}")
        print(f"胜: {self.wins} ({self.wins/self.games_played*100:.1f}%)")
        print(f"负: {self.losses} ({self.losses/self.games_played*100:.1f}%)")
        print(f"和: {self.draws} ({self.draws/self.games_played*100:.1f}%)")

        return {"wins": self.wins, "losses": self.losses,
                "draws": self.draws, "total": self.games_played}

    def _play_one_game(self, opponent: MinimaxEngine):
        """进行一局自我对弈"""
        board = chess.Board()
        move_history = []
        is_rl_player = True  # RL引擎是否是白方

        while not board.is_game_over():
            if is_rl_player:
                # RL引擎走棋
                move = self.get_best_move(board)
            else:
                # 对手引擎走棋
                move = opponent.get_best_move(board)

            if move is None:
                break

            # 保存这一步的经验
            state = board.fen()
            board.push(move)
            move_history.append((state, move))

            # 切换玩家
            is_rl_player = not is_rl_player

        # 游戏结束，更新RL引擎的学习
        # 简单的奖励：胜+1，负-1，和0
        result = board.result()

        if is_rl_player:  # RL引擎是最后走的
            # 如果游戏结束，RL引擎的对手赢了
            reward = -1 if result != "1/2-1/2" else 0
        else:
            # RL引擎赢了或和了
            if result == "1-0":
                reward = 1 if not is_rl_player else -1
            elif result == "0-1":
                reward = -1 if not is_rl_player else 1
            else:
                reward = 0

        # 反向传播奖励
        for state, move in reversed(move_history):
            experience = TrainingExperience(
                state=state,
                action=move,
                reward=reward,
                next_state=board.fen() if move_history else None,
                done=False
            )
            self.learn(experience)
            reward *= self.discount_factor  # 折扣奖励

        # 更新统计
        if is_rl_player:
            if result == "1-0":
                self.losses += 1
            elif result == "0-1":
                self.wins += 1
            else:
                self.draws += 1
        else:
            if result == "1-0":
                self.wins += 1
            elif result == "0-1":
                self.losses += 1
            else:
                self.draws += 1

    def save_model(self, filepath: str):
        """
        保存训练好的模型

        Args:
            filepath: 保存路径
        """
        model_data = {
            "q_table": self.q_table,
            "epsilon": self.epsilon,
            "stats": {
                "games_played": self.games_played,
                "wins": self.wins,
                "losses": self.losses,
                "draws": self.draws
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"模型已保存: {filepath}")

    def load_model(self, filepath: str):
        """
        加载训练好的模型

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)

            self.q_table = model_data["q_table"]
            self.epsilon = model_data["epsilon"]
            self.games_played = model_data["stats"]["games_played"]
            self.wins = model_data["stats"]["wins"]
            self.losses = model_data["stats"]["losses"]
            self.draws = model_data["stats"]["draws"]

            print(f"模型已加载: {filepath}")
            print(f"历史战绩: {self.wins}胜 {self.losses}负 {self.draws}和")
        except FileNotFoundError:
            print(f"文件不存在: {filepath}")
        except Exception as e:
            print(f"加载模型失败: {e}")


class HybridEngine:
    """混合引擎：结合Minimax和强化学习"""

    def __init__(self, minimax_depth: int = 3):
        """
        初始化混合引擎

        Args:
            minimax_depth: Minimax搜索深度
        """
        self.minimax = MinimaxEngine(depth=minimax_depth)
        self.rl = ReinforcementLearningEngine()

    def get_best_move(self, board: chess.Board,
                     use_rl: bool = False) -> Optional[chess.Move]:
        """
        获取最佳走法

        Args:
            board: 棋盘
            use_rl: 是否使用RL模型

        Returns:
            最佳走法
        """
        if use_rl:
            return self.rl.get_best_move(board)
        else:
            return self.minimax.get_best_move(board)

    def train(self, num_games: int = 100):
        """训练RL模型"""
        return self.rl.self_play(num_games)


def main():
    """演示引擎功能"""
    print("=== 国际象棋AI引擎演示 ===\n")

    # 1. Minimax引擎测试
    print("1. 测试Minimax引擎")
    board = chess.Board()
    engine = MinimaxEngine(depth=3)

    print("初始棋盘:")
    print(board)

    move = engine.get_best_move(board)
    print(f"\n最佳走法: {move.uci() if move else 'None'}")

    # 2. 强化学习引擎训练
    print("\n2. 训练强化学习引擎（10局快速演示）")
    rl_engine = ReinforcementLearningEngine(epsilon=0.3)

    stats = rl_engine.self_play(num_games=10, engine_depth=2)
    print(f"\n训练统计: {stats}")

    # 保存模型
    model_path = Path(__file__).parent / "rl_model.pkl"
    rl_engine.save_model(str(model_path))


if __name__ == "__main__":
    main()
