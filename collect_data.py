#!/usr/bin/env python3
"""
数据收集工具
自动从棋盘收集训练图像
"""

import cv2
import numpy as np
import pyautogui
import mss
from pathlib import Path
import pickle
import time


class DataCollector:
    """训练数据收集器"""

    def __init__(self):
        self.screen_capturer = mss.mss()
        self.board_region = None
        self.square_size = None

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"✓ 棋盘区域设置完成")
        print(f"  格子大小: {self.square_size}")

    def capture_square(self, rank, file, board_img=None):
        """捕获单个格子"""
        if board_img is None:
            screenshot = self.screen_capturer.grab(self.board_region)
            board_img = np.array(screenshot)
            board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        square_w, square_h = self.square_size
        y = (7 - rank) * square_h
        x = file * square_w

        return board_img[y:y + square_h, x:x + square_w]

    def collect_all_squares(self, dataset_name="batch_1"):
        """
        收集所有格子的图像

        Args:
            dataset_name: 数据集名称
        """
        print("\n" + "=" * 70)
        print("  📸 收集训练数据")
        print("=" * 70)

        # 创建数据目录
        raw_dir = Path(__file__).parent / "training_data" / "raw" / dataset_name
        raw_dir.mkdir(parents=True, exist_ok=True)

        # 捕获整个棋盘
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        # 保存棋盘图像
        board_path = raw_dir / "board.png"
        cv2.imwrite(str(board_path), board_img)
        print(f"\n✓ 棋盘图像已保存: {board_path}")

        # 提取并保存所有格子
        print("\n提取格子...")
        for rank in range(8):
            for file in range(8):
                square_name = self.file_rank_to_name(file, rank)
                square_img = self.capture_square(rank, file, board_img)

                # 保存格子图像
                square_path = raw_dir / f"{square_name}.png"
                cv2.imwrite(str(square_path), square_img)

        print(f"✓ 64个格子已保存到: {raw_dir}")

        # 保存元数据
        metadata = {
            "dataset_name": dataset_name,
            "timestamp": time.time(),
            "board_region": self.board_region,
            "square_size": self.square_size,
        }

        meta_path = raw_dir / "metadata.pkl"
        with open(meta_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✓ 元数据已保存: {meta_path}")

        return raw_dir

    def collect_multiple_boards(self, num_boards=5):
        """
        收集多个棋盘位置的图像
        用于增加数据多样性

        Args:
            num_boards: 要收集的棋盘数量
        """
        print("\n" + "=" * 70)
        print(f"  📸 收集多个棋盘 ({num_boards}个)")
        print("=" * 70)

        print("\n说明:")
        print("  1. 改变棋盘位置（移动几步棋）")
        print("  2. 按Enter拍照")
        print("  3. 重复直到完成")
        print("\n提示:")
        print("  - 尝试不同的棋子位置")
        print("  - 尝试不同的光线条件")
        print("  - 收集更多数据=更好的模型")

        collected_datasets = []

        for i in range(num_boards):
            print(f"\n{'='*70}")
            print(f"  棋盘 {i+1}/{num_boards}")
            print(f"{'='*70}")

            input("\n准备好后按Enter拍照...")

            dataset_name = f"board_{i+1:03d}"
            dataset_dir = self.collect_all_squares(dataset_name)
            collected_datasets.append(dataset_dir)

            print(f"✓ 棋盘 {i+1} 完成")

        print("\n" + "=" * 70)
        print("  🎉 所有棋盘收集完成！")
        print("=" * 70)
        print(f"\n收集的数据集:")
        for dataset_dir in collected_datasets:
            print(f"  - {dataset_dir}")

        return collected_datasets

    @staticmethod
    def file_rank_to_name(file, rank):
        """将file和rank转换为格子名称"""
        files = 'abcdefgh'
        ranks = '87654321'
        return f"{files[file]}{ranks[rank]}"

    def save_calibration(self, filepath="calibration_collector.pkl"):
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
    print("  📸 训练数据收集工具")
    print("=" * 70)
    print("\n功能:")
    print("  1. 收集单个棋盘的所有格子")
    print("  2. 收集多个棋盘位置（推荐）")
    print("  3. 收集指定格子")
    print("=" * 70)

    collector = DataCollector()

    # 检查校准
    calib_file = Path(__file__).parent / "calibration_collector.pkl"
    if calib_file.exists():
        with open(calib_file, 'rb') as f:
            data = pickle.load(f)
        collector.board_region = data["board_region"]
        collector.square_size = data["square_size"]
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

        collector.set_board_region(x1, y1, x2, y2)
        collector.save_calibration()

    # 选择收集模式
    print("\n请选择收集模式:")
    print("1. 收集单个棋盘（64个格子）")
    print("2. 收集多个棋盘（推荐，增加多样性）")
    print("3. 收集指定格子（如特定棋子）")

    choice = input("\n选择 (1-3): ").strip()

    if choice == '1':
        dataset_name = input("\n输入数据集名称 (如: board_001): ").strip() or "board_001"
        collector.collect_all_squares(dataset_name)

    elif choice == '2':
        num_boards = input("\n要收集多少个棋盘位置? (推荐5-10): ").strip()
        try:
            num_boards = int(num_boards)
            num_boards = max(1, min(num_boards, 20))  # 限制在1-20之间
        except ValueError:
            num_boards = 5

        collector.collect_multiple_boards(num_boards)

    elif choice == '3':
        print("\n请输入要收集的格子名称（用空格分隔）:")
        print("例如: e4 d4 e5 d5")
        squares = input("格子名称: ").strip().split()

        if squares:
            print(f"\n收集 {len(squares)} 个格子...")

            dataset_name = input("输入数据集名称: ").strip() or "custom"
            raw_dir = Path(__file__).parent / "training_data" / "raw" / dataset_name
            raw_dir.mkdir(parents=True, exist_ok=True)

            for square_name in squares:
                # 解析格子名称
                files = 'abcdefgh'
                ranks = '87654321'
                try:
                    file = files.index(square_name[0])
                    rank = ranks.index(square_name[1])
                except (IndexError, ValueError):
                    print(f"⚠️  跳过无效的格子: {square_name}")
                    continue

                # 捕获格子
                square_img = collector.capture_square(rank, file)
                square_path = raw_dir / f"{square_name}.png"
                cv2.imwrite(str(square_path), square_img)
                print(f"✓ {square_name}: {square_path}")

    else:
        print("❌ 无效选择")

    print("\n" + "=" * 70)
    print("  🎉 数据收集完成！")
    print("=" * 70)
    print("\n下一步:")
    print("  1. 运行 label_data.py 标注数据")
    print("  2. 或收集更多数据以增加多样性")
    print(f"\n数据位置:")
    print(f"  {Path(__file__).parent / 'training_data' / 'raw'}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
