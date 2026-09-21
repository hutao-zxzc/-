#!/usr/bin/env python3
"""
使用训练好的模型进行棋子识别
完全基于深度学习，不使用规则判断
"""

import cv2
import numpy as np
import pyautogui
import mss
import torch
import torchvision.transforms as transforms
from PIL import Image
import chess
from pathlib import Path
import pickle


class TrainedPieceClassifier:
    """基于训练模型的棋子分类器"""

    def __init__(self, model_path=None):
        """初始化分类器"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 图像变换（与训练时一致）
        self.transform = transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        # 加载模型
        if model_path is None:
            model_path = Path(__file__).parent / "models" / "piece_classifier.pth"

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"未找到模型文件: {model_path}\n"
                                     "   请先运行 train_simple.py 训练模型")

        print(f"加载模型: {model_path}")

        # 加载模型和元数据
        checkpoint = torch.load(model_path, map_location=self.device)

        # 创建模型结构
        from train_simple import SimpleCNN
        self.model = SimpleCNN(num_classes=13).to(self.device)

        # 加载模型参数
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        # 加载元数据
        self.class_names = checkpoint.get('class_names', [])
        self.piece_symbols = checkpoint.get('piece_symbols', {})

        print(f"✓ 模型已加载")
        print(f"  设备: {self.device}")
        print(f"  类别数: {len(self.class_names)}")

    def predict(self, square_img):
        """
        预测格子上的棋子

        Args:
            square_img: 格子图像 (BGR格式)

        Returns:
            (棋子符号, 置信度)
            如: ('P', 0.95) 或 (None, 0.0)
        """
        try:
            # 转换为RGB
            img_rgb = cv2.cvtColor(square_img, cv2.COLOR_BGR2RGB)

            # 转换为PIL图像
            img_pil = Image.fromarray(img_rgb)

            # 应用变换
            img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)

            # 预测
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)

            # 获取预测结果
            class_idx = predicted.item()
            conf = confidence.item()

            # 转换为棋子符号
            piece = self.piece_symbols.get(class_idx, None)

            return piece, conf

        except Exception as e:
            print(f"预测失败: {e}")
            return None, 0.0

    def scan_board(self, verbose=False, confidence_threshold=0.7):
        """
        扫描整个棋盘

        Args:
            verbose: 是否显示详细过程
            confidence_threshold: 置信度阈值

        Returns:
            chess.Board对象
        """
        print("\n" + "=" * 70)
        print("  🔍 使用训练模型扫描棋盘")
        print("  完全基于深度学习，不使用规则判断")
        print("=" * 70)

        board = chess.Board()
        board.clear()

        predictions = []

        for rank in range(8):
            for file in range(8):
                square_idx = rank * 8 + file
                square_name = chess.SQUARE_NAMES[square_idx]

                # 捕获格子
                square_img = self.capture_square(rank, file)

                # 预测
                piece, confidence = self.predict(square_img)

                predictions.append({
                    'square': square_name,
                    'piece': piece,
                    'confidence': confidence
                })

                if piece is not None and confidence >= confidence_threshold:
                    # 设置棋子
                    piece_obj = chess.Piece.from_symbol(piece)
                    board.set_piece_at(square_idx, piece_obj)

                    if verbose:
                        class_name = self.class_names[predictions[-1].get('piece', 0) or 0]
                        print(f"  ✓ {square_name}: {piece} ({class_name}) [置信度: {confidence:.2f}]")
                else:
                    if verbose:
                        if confidence > 0:
                            print(f"  ✗ {square_name}: 空格 [置信度: {confidence:.2f}, 低于阈值]")
                        else:
                            print(f"  ✗ {square_name}: 空格")

        # 统计
        piece_count = len(list(board.piece_map()))
        confidences = [p['confidence'] for p in predictions if p['confidence'] > 0]
        avg_conf = np.mean(confidences) if confidences else 0

        print(f"\n识别结果:")
        print(f"  棋子数量: {piece_count}/64")
        print(f"  平均置信度: {avg_conf:.2f}")

        return board

    def capture_square(self, rank, file):
        """捕获单个格子"""
        if not hasattr(self, 'board_region'):
            raise ValueError("请先设置棋盘区域")

        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        square_w, square_h = self.square_size
        y = (7 - rank) * square_h
        x = file * square_w

        return board_img[y:y + square_h, x:x + square_w]

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        self.screen_capturer = mss.mss()
        print(f"✓ 棋盘区域设置完成")

    def save_calibration(self, filepath="calibration_model.pkl"):
        """保存校准数据"""
        calibration_data = {
            "board_region": self.board_region,
            "square_size": self.square_size
        }
        with open(filepath, 'wb') as f:
            pickle.dump(calibration_data, f)
        print(f"✓ 校准数据已保存: {filepath}")


def main():
    """主程序"""
    print("=" * 70)
    print("  🔍 使用训练模型进行棋子识别")
    print("  完全基于深度学习，不使用规则判断")
    print("=" * 70)

    # 初始化分类器
    try:
        classifier = TrainedPieceClassifier()
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\n解决方法:")
        print("  1. 准备训练图像:")
        print("     mkdir -p training_images/{empty,white_pawn,white_knight,...}")
        print("  2. 把照片放到对应目录")
        print("  3. 运行 train_simple.py 训练模型")
        return

    # 检查校准
    calib_file = Path(__file__).parent / "calibration_model.pkl"
    if calib_file.exists():
        with open(calib_file, 'rb') as f:
            data = pickle.load(f)
        classifier.board_region = data["board_region"]
        classifier.square_size = data["square_size"]
        classifier.screen_capturer = mss.mss()
        print(f"\n✓ 已加载校准数据")
    else:
        print("\n=== 棋盘校准 ===")
        print("1. 点击棋盘左上角...")
        input("按Enter后点击左上角，然后按Enter继续...")

        x1, y1 = pyautogui.position()
        print(f"  左上角: ({x1}, {y1})")

        print("2. 点击棋盘右下角...")
        input("按Enter后点击右下角，然后按Enter继续...")

        x2, y2 = pyautogui.position()
        print(f"  右下角: ({x2}, {y2})")

        classifier.set_board_region(x1, y1, x2, y2)
        classifier.save_calibration()

    # 扫描棋盘
    verbose = input("\n显示详细识别过程? (y/n): ").strip().lower() == 'y'
    conf_thresh = input("置信度阈值 (推荐0.7, 默认0.7): ").strip()
    conf_thresh = float(conf_thresh) if conf_thresh else 0.7

    board = classifier.scan_board(verbose=verbose, confidence_threshold=conf_thresh)

    # 显示结果
    print("\n" + "=" * 70)
    print("  ♟️  识别的棋盘")
    print("=" * 70)
    print(board)

    # 保存FEN
    fen = board.fen()
    print(f"\n📋 FEN字符串:")
    print(fen)

    fen_file = Path(__file__).parent / "recognized_fen_model.txt"
    with open(fen_file, 'w') as f:
        f.write(fen)
    print(f"✓ FEN已保存: {fen_file}")

    print("\n" + "=" * 70)
    print("  完成！")
    print("=" * 70)

    print("\n💡 提示:")
    print("  - 训练的模型准确度取决于训练数据质量")
    print("  - 可以调整置信度阈值:")
    print("    * 阈值高=更严格，可能漏掉一些棋子")
    print("    * 阈值低=更宽松，可能有误报")
    print("  - 如果识别不准确，收集更多数据重新训练")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
