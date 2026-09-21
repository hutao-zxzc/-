#!/usr/bin/env python3
"""
从棋盘截取棋子照片
用于收集训练数据
"""

import cv2
import numpy as np
import pyautogui
import mss
from pathlib import Path
import pickle
import time


class PieceCapturer:
    """棋子截图工具"""

    def __init__(self):
        self.screen_capturer = mss.mss()
        self.board_region = None
        self.square_size = None

    def set_board_region(self, x1, y1, x2, y2):
        """设置棋盘区域"""
        self.board_region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        self.square_size = ((x2 - x1) // 8, (y2 - y1) // 8)
        print(f"✓ 棋盘区域设置完成")

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

    def capture_all_squares(self):
        """捕获所有格子"""
        print("\n" + "=" * 70)
        print("  📸 截取所有格子")
        print("=" * 70)

        # 捕获整个棋盘
        screenshot = self.screen_capturer.grab(self.board_region)
        board_img = np.array(screenshot)
        board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        # 保存棋盘图像
        board_path = Path(__file__).parent / "training_images" / "board_reference.png"
        board_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(board_path), board_img)
        print(f"\n✓ 棋盘参考图已保存: {board_path}")

        # 截取所有格子
        squares = {}
        for rank in range(8):
            for file in range(8):
                square_img = self.capture_square(rank, file, board_img)
                squares[(rank, file)] = square_img

        print(f"✓ 已截取 {len(squares)} 个格子")
        return squares

    def label_and_save_squares(self, squares):
        """标注并保存格子"""
        print("\n" + "=" * 70)
        print("  🏷️  标注格子")
        print("=" * 70)

        # 创建输出目录
        output_dir = Path(__file__).parent / "training_images"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化计数器
        counters = {}
        class_names = [
            'empty',
            'white_pawn', 'white_knight', 'white_bishop', 'white_rook', 'white_queen', 'white_king',
            'black_pawn', 'black_knight', 'black_bishop', 'black_rook', 'black_queen', 'black_king'
        ]
        for class_name in class_names:
            counters[class_name] = 0

        # 按棋盘顺序显示
        window_name = "标注 - 按1-0标注, ESC退出, S跳过"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        for rank in range(8):
            for file in range(8):
                square_name = f"{'abcdefgh'[file]}{'87654321'[rank]}"

                # 获取格子图像
                square_img = squares[(rank, file)]

                # 调整大小
                display_img = cv2.resize(square_img, (300, 300))

                # 添加信息
                cv2.putText(display_img, square_name,
                           (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(display_img, square_name,
                           (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

                # 显示
                cv2.imshow(window_name, display_img)

                # 获取按键
                key = cv2.waitKey(0) & 0xFF

                # ESC退出
                if key == 27:
                    cv2.destroyAllWindows()
                    return False

                # 快捷键
                if key == ord('s'):  # 跳过
                    print(f"  跳过: {square_name}")
                    continue

                # 1-9, q, w, e
                key_map = {
                    ord('1'): 'white_pawn',
                    ord('2'): 'white_knight',
                    ord('3'): 'white_bishop',
                    ord('4'): 'white_rook',
                    ord('5'): 'white_queen',
                    ord('6'): 'white_king',
                    ord('7'): 'black_pawn',
                    ord('8'): 'black_knight',
                    ord('9'): 'black_bishop',
                    ord('q'): 'black_rook',
                    ord('w'): 'black_queen',
                    ord('e'): 'black_king',
                    ord('0'): 'empty',
                }

                if key in key_map:
                    class_name = key_map[key]
                    counters[class_name] += 1

                    # 保存图像
                    filename = f"{counters[class_name]:03d}.png"
                    save_dir = output_dir / class_name
                    save_dir.mkdir(parents=True, exist_ok=True)

                    save_path = save_dir / filename
                    cv2.imwrite(str(save_path), square_img)

                    print(f"  ✓ {square_name} -> {class_name} ({filename})")
                else:
                    print(f"  ✗ 无效按键，跳过: {square_name}")

        cv2.destroyAllWindows()
        return True

    def batch_capture(self, num_boards=3):
        """
        批量截取多个棋盘
        用于增加数据多样性
        """
        print("\n" + "=" * 70)
        print(f"  📸 批量截取 ({num_boards}个棋盘)")
        print("=" * 70)

        print("\n说明:")
        print("  1. 移动几步棋，改变棋子位置")
        print("  2. 按Enter截图")
        print("  3. 重复直到完成")
        print("")
        print("提示:")
        print("  - 尝试不同的棋子组合")
        print("  - 确保每种棋子都被截取到")

        for i in range(num_boards):
            print(f"\n{'='*70}")
            print(f"  棋盘 {i+1}/{num_boards}")
            print(f"{'='*70}")

            input("\n移动几步棋，准备好后按Enter...")

            # 截取所有格子
            squares = self.capture_all_squares()

            # 标注并保存
            print("\n开始标注...")
            success = self.label_and_save_squares(squares)

            if not success:
                print("\n已取消")
                break

        print("\n" + "=" * 70)
        print("  🎉 批量截取完成！")
        print("=" * 70)

        # 统计
        output_dir = Path(__file__).parent / "training_images"
        total = 0
        class_counts = {}

        for class_dir in output_dir.iterdir():
            if not class_dir.is_dir():
                continue

            count = len(list(class_dir.glob("*.png")))
            class_counts[class_dir.name] = count
            total += count

        print(f"\n截取统计:")
        print(f"  总计: {total} 张")

        for class_name, count in sorted(class_counts.items()):
            print(f"  {class_name}: {count}")

        print("\n下一步:")
        print("  1. 继续截取更多棋盘（可选）")
        print("  2. 或添加其他来源的照片")
        print("  3. 运行 easy_train.py 训练模型")

    def save_calibration(self, filepath="calibration_capture.pkl"):
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
    print("  📸 棋子截图工具")
    print("  从棋盘快速收集训练数据")
    print("=" * 70)

    capturer = PieceCapturer()

    # 检查校准
    calib_file = Path(__file__).parent / "calibration_capture.pkl"
    if calib_file.exists():
        with open(calib_file, 'rb') as f:
            data = pickle.load(f)
        capturer.board_region = data["board_region"]
        capturer.square_size = data["square_size"]
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

        capturer.set_board_region(x1, y1, x2, y2)
        capturer.save_calibration()

    # 选择模式
    print("\n请选择模式:")
    print("1. 单个棋盘（截取64个格子）")
    print("2. 批量截取（推荐，3个棋盘）")
    print("3. 自定义数量")

    choice = input("\n选择 (1-3): ").strip()

    if choice == '1':
        print("\n" + "=" * 70)
        print("  单个棋盘截取")
        print("=" * 70)

        input("\n确保棋盘完全可见，按Enter开始...")

        # 截取所有格子
        squares = capturer.capture_all_squares()

        # 标注并保存
        print("\n开始标注...")
        capturer.label_and_save_squares(squares)

        print("\n🎉 截取完成！")

    elif choice == '2':
        capturer.batch_capture(num_boards=3)

    elif choice == '3':
        num = input("要截取几个棋盘? (默认3): ").strip()
        try:
            num_boards = int(num) if num else 3
            num_boards = max(1, min(num_boards, 10))
        except ValueError:
            num_boards = 3

        capturer.batch_capture(num_boards)

    else:
        print("❌ 无效选择")

    print("\n" + "=" * 70)
    print("  完成！")
    print("=" * 70)

    print("\n下一步:")
    print("  运行 easy_train.py 开始训练")
    print("  或添加更多照片到 training_images/ 目录")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
