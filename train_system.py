#!/usr/bin/env python3
"""
完整的训练系统
整合数据收集、标注、训练和使用
"""

from pathlib import Path
import sys


def main():
    """主程序"""
    print("=" * 70)
    print("  🎓 棋子识别训练系统")
    print("=" * 70)
    print("\n完整流程:")
    print("  1. 数据收集")
    print("  2. 数据标注")
    print("  3. 模型训练")
    print("  4. 使用模型")
    print("=" * 70)

    while True:
        print("\n请选择:")
        print("1. 数据收集 (collect_data.py)")
        print("2. 数据标注 (label_data.py)")
        print("3. 模型训练 (train_model.py)")
        print("4. 使用模型 (use_trained_model.py)")
        print("5. 完整流程 (推荐新手)")
        print("6. 查看训练指南")
        print("0. 退出")

        choice = input("\n👉 选择 (0-6): ").strip()

        if choice == '0':
            print("\n👋 再见！")
            break

        elif choice == '1':
            print("\n" + "=" * 70)
            print("  📸 数据收集")
            print("=" * 70)
            print("\n启动 collect_data.py...")
            import subprocess
            subprocess.run([sys.executable, "collect_data.py"])

        elif choice == '2':
            print("\n" + "=" * 70)
            print("  🏷️  数据标注")
            print("=" * 70)
            print("\n启动 label_data.py...")
            import subprocess
            subprocess.run([sys.executable, "label_data.py"])

        elif choice == '3':
            print("\n" + "=" * 70)
            print("  🧠 模型训练")
            print("=" * 70)
            print("\n启动 train_model.py...")
            import subprocess
            subprocess.run([sys.executable, "train_model.py"])

        elif choice == '4':
            print("\n" + "=" * 70)
            print("  🔍 使用模型")
            print("=" * 70)
            print("\n启动 use_trained_model.py...")
            import subprocess
            subprocess.run([sys.executable, "use_trained_model.py"])

        elif choice == '5':
            print("\n" + "=" * 70)
            print("  📚 完整流程指南")
            print("=" * 70)
            print("\n步骤1: 收集数据")
            print("  - 运行 collect_data.py")
            print("  - 建议收集5-10个棋盘位置")
            print("  - 每个位置包含64个格子")
            print("")
            print("步骤2: 标注数据")
            print("  - 运行 label_data.py")
            print("  - 手动标注每个格子的棋子类型")
            print("  - 使用快捷键加快标注速度")
            print("")
            print("步骤3: 训练模型")
            print("  - 运行 train_model.py")
            print("  - 自动分割训练集和验证集")
            print("  - 训练约30-60分钟")
            print("")
            print("步骤4: 使用模型")
            print("  - 运行 use_trained_model.py")
            print("  - 高准确度识别棋子")
            print("")
            print("💡 总共需要: 约1-2小时")
            print("   其中收集和标注: 30-60分钟")
            print("         训练: 30-60分钟")

            continue_training = input("\n是否开始完整流程? (y/n): ").strip().lower()

            if continue_training == 'y':
                # 步骤1: 数据收集
                print("\n" + "=" * 70)
                print("  步骤1: 数据收集")
                print("=" * 70)
                import subprocess
                subprocess.run([sys.executable, "collect_data.py"])

                # 步骤2: 数据标注
                print("\n" + "=" * 70)
                print("  步骤2: 数据标注")
                print("=" * 70)

                # 检查是否有数据
                raw_dir = Path(__file__).parent / "training_data" / "raw"
                if raw_dir.exists():
                    print("\n数据已收集，现在进行标注...")
                    subprocess.run([sys.executable, "label_data.py"])
                else:
                    print("\n❌ 未找到数据，请先完成数据收集")
                    continue

                # 步骤3: 模型训练
                print("\n" + "=" * 70)
                print("  步骤3: 模型训练")
                print("=" * 70)
                print("\n⏱️  训练可能需要30-60分钟，请耐心等待...")

                train_choice = input("是否开始训练? (y/n): ").strip().lower()
                if train_choice == 'y':
                    subprocess.run([sys.executable, "train_model.py"])
                else:
                    print("\n⏭️  跳过训练")
                    continue

                # 步骤4: 使用模型
                print("\n" + "=" * 70)
                print("  步骤4: 使用模型")
                print("=" * 70)

                # 检查是否有模型
                model_file = Path(__file__).parent / "models" / "chess_pieces_trained.pth"
                if model_file.exists():
                    print("\n✓ 模型已找到，现在使用模型进行识别...")
                    subprocess.run([sys.executable, "use_trained_model.py"])
                else:
                    print("\n❌ 未找到模型，请先完成训练")
                    continue

                print("\n" + "=" * 70)
                print("  🎉 完整流程完成！")
                print("=" * 70)

        elif choice == '6':
            print("\n" + "=" * 70)
            print("  📖 训练指南")
            print("=" * 70)

            guide_text = """
🎓 棋子识别训练完整指南

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 步骤1: 数据收集

命令: python collect_data.py

说明:
  - 收集棋盘图像，提取所有64个格子
  - 建议收集5-10个不同位置的棋盘
  - 尽量包含各种棋子在不同位置
  - 改善光线条件可以提高数据质量

提示:
  - 尝试不同的棋子位置
  - 尝试不同的光线条件
  - 收集更多数据=更好的模型

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️  步骤2: 数据标注

命令: python label_data.py

说明:
  - 手动标注每个格子的棋子类型
  - 使用快捷键加快标注速度

快捷键:
  0-6: 白棋 (0=空, 1=P, 2=N, 3=B, 4=R, 5=Q, 6=K)
  7,8,9,q,w,e: 黑棋 (7=p, 8=n, 9=b, q=r, w=q, e=k)
  s: 跳过
  a: 自动建议
  h: 帮助
  q/ESC: 退出

提示:
  - 确保标注准确
  - 不确定时使用's'跳过
  - 可以随时退出并保存

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 步骤3: 模型训练

命令: python train_model.py

说明:
  - 使用CNN神经网络训练模型
  - 自动分割训练集和验证集
  - 训练约30-60分钟

配置:
  - 图像大小: 48x48
  - 批次大小: 32
  - 训练轮数: 50
  - 学习率: 0.001
  - 数据增强: 翻转、旋转、颜色抖动

输出:
  - models/chess_pieces_trained.pth
  - training_logs/training_history_*.json

提示:
  - 可以调整batch_size和epochs
  - 如果过拟合，减少epochs
  - 如果欠拟合，增加epochs或数据量

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 步骤4: 使用模型

命令: python use_trained_model.py

说明:
  - 使用训练好的模型识别棋子
  - 高准确度（90%+）
  - 可以调整置信度阈值

配置:
  - 置信度阈值: 默认0.5
  - 设备: 自动检测GPU/CPU

输出:
  - recognized_fen_trained.txt

提示:
  - 阈值高=更严格，可能漏掉一些棋子
  - 阈值低=更宽松，可能有误报
  - 根据实际情况调整

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 最佳实践

1. 数据质量
   - 清晰的图像
   - 良好的光线
   - 多样的棋子位置

2. 数据量
   - 最少: 每类20张 (~260张)
   - 推荐: 每类50+张 (~700张)
   - 最佳: 每类100+张 (~1400张)

3. 训练策略
   - 先用少量数据快速测试
   - 观察loss曲线
   - 逐步增加数据量

4. 模型改进
   - 使用预训练模型（ResNet等）
   - 调整网络结构
   - 增加数据增强

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  常见问题

Q: 训练需要多久？
A: 取决于数据量和硬件
   - 100张: ~5分钟
   - 500张: ~20分钟
   - 1000张: ~40分钟

Q: 准确率不够高？
A: 1. 增加训练数据
   2. 提高数据质量
   3. 调整超参数
   4. 增加训练轮数

Q: 可以用GPU吗？
A: 可以！如果有NVIDIA GPU，
   安装PyTorch的GPU版本即可

Q: 如何验证模型？
A: 使用验证集准确率和混淆矩阵

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            print(guide_text)

        else:
            print("❌ 无效选择")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
