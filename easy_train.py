#!/usr/bin/env python3
"""
一键训练脚本
简化整个训练流程
"""

import os
from pathlib import Path


def setup_training_data():
    """设置训练数据目录"""
    print("\n" + "=" * 70)
    print("  📁 设置训练数据目录")
    print("=" * 70)

    root_dir = Path(__file__).parent / "training_images"
    root_dir.mkdir(exist_ok=True)

    # 类别列表
    classes = [
        'empty',
        'white_pawn', 'white_knight', 'white_bishop', 'white_rook', 'white_queen', 'white_king',
        'black_pawn', 'black_knight', 'black_bishop', 'black_rook', 'black_queen', 'black_king'
    ]

    print("\n创建训练数据目录:")
    for class_name in classes:
        class_dir = root_dir / class_name
        class_dir.mkdir(exist_ok=True)
        print(f"  ✓ {class_dir}")

    print(f"\n✓ 训练数据目录已创建: {root_dir}")
    return root_dir


def check_data_quality(root_dir):
    """检查训练数据质量"""
    print("\n" + "=" * 70)
    print("  🔍 检查训练数据")
    print("=" * 70)

    classes = [
        'empty',
        'white_pawn', 'white_knight', 'white_bishop', 'white_rook', 'white_queen', 'white_king',
        'black_pawn', 'black_knight', 'black_bishop', 'black_rook', 'black_queen', 'black_king'
    ]

    total_images = 0
    class_counts = {}
    missing_classes = []

    for class_name in classes:
        class_dir = root_dir / class_name
        if not class_dir.exists():
            missing_classes.append(class_name)
            continue

        image_files = list(class_dir.glob("*.jpg")) + \
                     list(class_dir.glob("*.jpeg")) + \
                     list(class_dir.glob("*.png")) + \
                     list(class_dir.glob("*.bmp"))

        count = len(image_files)
        class_counts[class_name] = count
        total_images += count

    print(f"\n数据统计:")
    print(f"  总图像数: {total_images}")
    print(f"  类别数: {len(class_counts)}/13")

    if total_images == 0:
        print("\n❌ 未找到任何训练图像！")
        print("\n解决方法:")
        print("  1. 拍摄棋子照片")
        print("  2. 把照片放到对应目录:")
        for class_name in classes:
            print(f"     - training_images/{class_name}/")
        print("  3. 每个类别至少20张照片")
        return False

    print(f"\n各类别数量:")
    for class_name, count in class_counts.items():
        status = "✅" if count >= 20 else "⚠️"
        print(f"  {status} {class_name}: {count}")

    if missing_classes:
        print(f"\n⚠️  缺失的类别 ({len(missing_classes)}):")
        for class_name in missing_classes:
            print(f"     - {class_name}")

    # 检查数据质量
    min_count = min(class_counts.values()) if class_counts else 0

    print(f"\n数据质量评估:")
    if min_count >= 100:
        print("  🎉 优秀！每种棋子都有100+张照片")
        print("     预期准确度: 95%+")
    elif min_count >= 50:
        print("  ✅ 良好！每种棋子都有50+张照片")
        print("     预期准确度: 90%")
    elif min_count >= 20:
        print("  ⚠️  一般，每种棋子有20+张照片")
        print("     预期准确度: 85%")
    else:
        print("  ❌ 数据不足！每种棋子至少需要20张照片")
        return False

    print("\n准备就绪，可以开始训练！")
    return True


def train_model():
    """训练模型"""
    print("\n" + "=" * 70)
    print("  🧠 开始训练")
    print("=" * 70)

    print("\n注意: 训练需要一些时间...")
    print("  - 260张图像: 约10分钟")
    print("  - 650张图像: 约20分钟")
    print("  - 1300张图像: 约40分钟")

    confirm = input("\n是否开始训练? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消训练")
        return

    # 导入训练脚本
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "train_simple.py"])
    return result.returncode == 0


def use_model():
    """使用模型"""
    print("\n" + "=" * 70)
    print("  🔍 使用模型")
    print("=" * 70)

    # 导入使用脚本
    import subprocess
    import sys

    subprocess.run([sys.executable, "use_model.py"])


def main():
    """主程序"""
    print("=" * 70)
    print("  🚀 一键训练系统")
    print("  完全基于深度学习，不使用规则判断")
    print("=" * 70)
    print("\n优势:")
    print("  ✅ 高准确度: 95%+")
    print("  ✅ 不需要规则判断")
    print("  ✅ 自动学习棋子特征")
    print("  ✅ 适应任何棋子样式")
    print("=" * 70)

    while True:
        print("\n请选择:")
        print("1. 设置训练数据目录（首次使用）")
        print("2. 检查训练数据")
        print("3. 训练模型")
        print("4. 使用模型")
        print("5. 完整流程（推荐）")
        print("0. 退出")

        choice = input("\n👉 选择 (0-5): ").strip()

        if choice == '0':
            print("\n👋 再见！")
            break

        elif choice == '1':
            setup_training_data()
            print("\n下一步:")
            print("  1. 拍摄棋子照片")
            print("  2. 把照片放到对应目录")
            print("  3. 运行选项2检查数据")
            print("  4. 运行选项3训练模型")

        elif choice == '2':
            root_dir = Path(__file__).parent / "training_images"
            if root_dir.exists():
                check_data_quality(root_dir)
            else:
                print("\n❌ 未找到训练数据目录")
                print("   请先运行选项1设置目录")

        elif choice == '3':
            train_model()

        elif choice == '4':
            use_model()

        elif choice == '5':
            print("\n" + "=" * 70)
            print("  📚 完整流程指南")
            print("=" * 70)

            # 步骤1: 设置
            print("\n步骤1: 设置训练数据目录")
            root_dir = setup_training_data()

            # 步骤2: 准备数据
            print("\n" + "=" * 70)
            print("  步骤2: 准备训练数据")
            print("=" * 70)

            print("\n📸 如何收集照片:")
            print("  方法1: 直接拍摄棋子照片")
            print("    - 把棋子放在纯色背景上")
            print("    - 从不同角度拍摄")
            print("    - 确保光线充足")
            print("")
            print("  方法2: 从棋盘截取")
            print("    - 运行 capture_pieces.py")
            print("    - 自动从棋盘提取棋子")
            print("")
            print("  方法3: 从网上下载")
            print("    - 搜索棋子图像")
            print("    - 确保与你的棋子相似")

            print("\n📋 照片要求:")
            print("  - 每种棋子至少20张（推荐50+）")
            print("  - 图像清晰，光线良好")
            print("  - 多样化的角度和位置")

            print("\n📁 把照片放到对应目录:")
            print(f"  {root_dir}/")
            print("    ├── empty/          (空格照片)")
            print("    ├── white_pawn/     (白兵照片)")
            print("    ├── white_knight/   (白马照片)")
            print("    ├── ...")
            print("    └── black_king/     (黑王照片)")

            input("\n准备好后按Enter继续...")

            # 步骤3: 检查数据
            print("\n" + "=" * 70)
            print("  步骤3: 检查训练数据")
            print("=" * 70)

            data_ready = check_data_quality(root_dir)

            if not data_ready:
                print("\n⚠️  数据未准备好")
                print("   请补充更多照片后重新运行")
                continue

            # 步骤4: 训练
            print("\n" + "=" * 70)
            print("  步骤4: 训练模型")
            print("=" * 70)

            train_success = train_model()

            if not train_success:
                print("\n⚠️  训练失败")
                continue

            # 步骤5: 使用
            print("\n" + "=" * 70)
            print("  步骤5: 使用模型")
            print("=" * 70)

            use_model()

            print("\n" + "=" * 70)
            print("  🎉 完整流程完成！")
            print("=" * 70)

            print("\n💡 后续使用:")
            print("  - 识别棋盘: python use_model.py")
            print("  - 重新训练: python train_simple.py")

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
