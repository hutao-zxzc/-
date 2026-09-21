#!/usr/bin/env python3
"""
数据标注工具
手动标注收集的棋子图像
"""

import cv2
import numpy as np
from pathlib import Path
import pickle
import json


class DataLabeler:
    """训练数据标注器"""

    # 棋子类型映射
    PIECE_TYPES = {
        0: 'empty',    # 空格
        1: 'P',        # 白兵
        2: 'N',        # 白马
        3: 'B',        # 白象
        4: 'R',        # 白车
        5: 'Q',        # 白后
        6: 'K',        # 白王
        7: 'p',        # 黑兵
        8: 'n',        # 黑马
        9: 'b',        # 黑象
        10: 'r',       # 黑车
        11: 'q',       # 黑后
        12: 'k',       # 黑王
    }

    # 棋子名称映射（用于显示）
    PIECE_NAMES = {
        0: '空格',
        1: '白兵',
        2: '白马',
        3: '白象',
        4: '白车',
        5: '白后',
        6: '白王',
        7: '黑兵',
        8: '黑马',
        9: '黑象',
        10: '黑车',
        11: '黑后',
        12: '黑王',
    }

    # 快捷键映射
    KEY_BINDINGS = {
        '0': 0,  # 空格
        '1': 1,  # 白兵
        '2': 2,  # 白马
        '3': 3,  # 白象
        '4': 4,  # 白车
        '5': 5,  # 白后
        '6': 6,  # 白王
        '7': 7,  # 黑兵
        '8': 8,  # 黑马
        '9': 9,  # 黑象
        'q': 10, # 黑车
        'w': 11, # 黑后
        'e': 12, # 黑王
        's': 'skip',  # 跳过
        'a': 'auto',  # 自动建议
    }

    def __init__(self):
        self.current_dataset = None
        self.labels = {}
        self.auto_suggest = {}

    def list_datasets(self):
        """列出所有数据集"""
        raw_dir = Path(__file__).parent / "training_data" / "raw"
        if not raw_dir.exists():
            print("❌ 未找到训练数据")
            print("   请先运行 collect_data.py 收集数据")
            return []

        datasets = [d for d in raw_dir.iterdir() if d.is_dir()]
        return sorted(datasets)

    def select_dataset(self):
        """选择要标注的数据集"""
        datasets = self.list_datasets()

        if not datasets:
            return None

        print("\n可用的数据集:")
        for i, dataset in enumerate(datasets, 1):
            print(f"{i}. {dataset.name}")

        choice = input("\n选择数据集编号 (或输入名称): ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(datasets):
                self.current_dataset = datasets[idx]
                return self.current_dataset
        else:
            # 直接使用名称
            for dataset in datasets:
                if dataset.name == choice:
                    self.current_dataset = dataset
                    return dataset

        print("❌ 无效选择")
        return None

    def load_squares(self):
        """加载数据集中的所有格子"""
        if not self.current_dataset:
            return {}

        squares = {}
        for img_file in sorted(self.current_dataset.glob("*.png")):
            if img_file.name == "board.png":  # 跳过棋盘图像
                continue

            square_name = img_file.stem
            img = cv2.imread(str(img_file))

            if img is not None:
                squares[square_name] = {
                    'image': img,
                    'path': img_file
                }

        return squares

    def display_help(self):
        """显示帮助信息"""
        print("\n" + "=" * 70)
        print("  快捷键说明")
        print("=" * 70)
        print("数字键 - 标注棋子类型:")
        print("  0 - 空格")
        print("  1 - 白兵    2 - 白马    3 - 白象    4 - 白车    5 - 白后    6 - 白王")
        print("  7 - 黑兵    8 - 黑马    9 - 黑象")
        print("  q - 黑车    w - 黑后    e - 黑王")
        print("")
        print("功能键:")
        print("  s - 跳过当前格子（不确定时使用）")
        print("  a - 显示自动建议（基于历史）")
        print("  h - 显示此帮助")
        print("  n - 下一个格子")
        print("  p - 上一个格子")
        print("  q 或 ESC - 退出并保存")
        print("=" * 70)

    def label_dataset(self):
        """标注整个数据集"""
        if not self.current_dataset:
            print("❌ 请先选择数据集")
            return

        print(f"\n标注数据集: {self.current_dataset.name}")

        # 加载格子
        squares = self.load_squares()

        if not squares:
            print("❌ 数据集中没有图像")
            return

        print(f"找到 {len(squares)} 个格子")
        print("\n提示:")
        print("  - 按h查看快捷键")
        print("  - 按a获取自动建议")
        print("  - 按q或ESC退出并保存")

        # 按棋盘顺序排列
        square_order = sorted(squares.keys())

        # 窗口名称
        window_name = "标注 - 按h查看帮助"

        # 创建窗口
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 300, 300)

        # 当前索引
        idx = 0

        while True:
            if idx < 0 or idx >= len(square_order):
                break

            square_name = square_order[idx]
            square_data = squares[square_name]
            img = square_data['image'].copy()

            # 调整大小以便显示
            display_img = cv2.resize(img, (300, 300))

            # 添加信息
            cv2.putText(display_img, f"{square_name} ({idx+1}/{len(square_order)})",
                       (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_img, f"{square_name} ({idx+1}/{len(square_order)})",
                       (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

            # 显示当前标注（如果有）
            if square_name in self.labels:
                label_idx = self.labels[square_name]
                label_name = self.PIECE_NAMES[label_idx]
                cv2.putText(display_img, f"当前标注: {label_name}",
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(display_img, f"当前标注: {label_name}",
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # 显示图像
            cv2.imshow(window_name, display_img)

            # 获取按键
            key = cv2.waitKey(0) & 0xFF

            # 处理按键
            if key == ord('h'):
                self.display_help()

            elif key == ord('s'):
                # 跳过
                if square_name in self.labels:
                    del self.labels[square_name]
                    print(f"  跳过: {square_name}")

            elif key == ord('a'):
                # 自动建议
                suggestion = self.get_auto_suggestion(square_name)
                if suggestion is not None:
                    self.labels[square_name] = suggestion
                    label_name = self.PIECE_NAMES[suggestion]
                    print(f"  自动建议: {square_name} = {label_name}")
                else:
                    print(f"  无法生成自动建议")

            elif key == ord('n'):
                # 下一个
                idx += 1

            elif key == ord('p'):
                # 上一个
                idx -= 1

            elif key == 27 or key == ord('q'):  # ESC或q
                # 退出
                break

            elif key >= ord('0') and key <= ord('9'):
                # 数字键
                num = key - ord('0')
                self.labels[square_name] = num
                label_name = self.PIECE_NAMES[num]
                print(f"  标注: {square_name} = {label_name}")

            elif key == ord('q') or key == ord('w') or key == ord('e'):
                # qwE键（用于10, 11, 12）
                if key == ord('q'):
                    num = 10
                elif key == ord('w'):
                    num = 11
                else:
                    num = 12

                self.labels[square_name] = num
                label_name = self.PIECE_NAMES[num]
                print(f"  标注: {square_name} = {label_name}")

        # 关闭窗口
        cv2.destroyAllWindows()

        # 保存标注
        self.save_labels()

    def get_auto_suggestion(self, square_name):
        """
        获取自动建议
        基于历史标注和位置
        """
        # 简单的策略：如果之前标注过相同位置的格子，建议相同的类型
        # 例如：a1通常是白车

        if square_name in self.labels:
            return self.labels[square_name]

        # 可以添加更复杂的启发式规则
        # 这里只是一个示例

        return None

    def save_labels(self):
        """保存标注"""
        if not self.current_dataset:
            return

        # 保存为pickle
        label_file = self.current_dataset / "labels.pkl"
        with open(label_file, 'wb') as f:
            pickle.dump(self.labels, f)

        # 保存为JSON（便于查看）
        label_json = self.current_dataset / "labels.json"
        labels_json = {}
        for square_name, label_idx in self.labels.items():
            labels_json[square_name] = {
                'label': self.PIECE_TYPES[label_idx],
                'label_name': self.PIECE_NAMES[label_idx]
            }

        with open(label_json, 'w') as f:
            json.dump(labels_json, f, indent=2, ensure_ascii=False)

        print(f"\n✓ 标注已保存:")
        print(f"  - {label_file}")
        print(f"  - {label_json}")
        print(f"\n标注数量: {len(self.labels)}")


def main():
    """主程序"""
    print("=" * 70)
    print("  🏷️  训练数据标注工具")
    print("=" * 70)

    labeler = DataLabeler()

    # 选择数据集
    dataset = labeler.select_dataset()

    if not dataset:
        print("\n❌ 未选择数据集")
        return

    # 显示帮助
    labeler.display_help()

    # 开始标注
    labeler.label_dataset()

    print("\n" + "=" * 70)
    print("  🎉 标注完成！")
    print("=" * 70)

    # 显示统计
    print(f"\n标注统计:")
    print(f"  数据集: {labeler.current_dataset.name}")
    print(f"  标注数量: {len(labeler.labels)}")

    # 按类型统计
    label_counts = {}
    for label_idx in labeler.labels.values():
        label_name = labeler.PIECE_NAMES[label_idx]
        label_counts[label_name] = label_counts.get(label_name, 0) + 1

    print(f"\n按类型统计:")
    for label_name, count in sorted(label_counts.items()):
        print(f"  {label_name}: {count}")

    print("\n下一步:")
    print("  1. 检查标注是否正确")
    print("  2. 可以继续标注其他数据集")
    print("  3. 收集足够数据后，运行 train_model.py 训练模型")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
