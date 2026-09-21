#!/usr/bin/env python3
"""
简化的棋子识别模型训练
直接从照片训练，不使用任何规则判断
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
from pathlib import Path
import json
import time
from tqdm import tqdm
import os


class SimpleCNN(nn.Module):
    """简化的CNN网络"""

    def __init__(self, num_classes=13):
        super(SimpleCNN, self).__init__()

        self.features = nn.Sequential(
            # 第1层
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # 第2层
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # 第3层
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # 第4层
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),  # 64x64 -> 4x4 after 4 maxpools
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


class PieceImageDataset(Dataset):
    """棋子图像数据集"""

    # 类别名称到索引的映射
    CLASS_NAMES = [
        'empty',
        'white_pawn', 'white_knight', 'white_bishop', 'white_rook', 'white_queen', 'white_king',
        'black_pawn', 'black_knight', 'black_bishop', 'black_rook', 'black_queen', 'black_king'
    ]

    # 棋子符号映射
    PIECE_SYMBOLS = {
        0: None,
        1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
        7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'
    }

    def __init__(self, root_dir, transform=None):
        """
        Args:
            root_dir: 训练图像根目录
            transform: 图像变换
        """
        self.root_dir = Path(root_dir)
        self.transform = transform

        # 加载所有图像
        self.samples = []
        self.load_images()

    def load_images(self):
        """加载所有训练图像"""
        if not self.root_dir.exists():
            raise FileNotFoundError(f"未找到训练数据目录: {self.root_dir}")

        # 遍历每个类别
        for class_idx, class_name in enumerate(self.CLASS_NAMES):
            class_dir = self.root_dir / class_name

            if not class_dir.exists():
                print(f"⚠️  跳过不存在的类别: {class_name}")
                continue

            # 获取所有图像文件
            image_files = list(class_dir.glob("*.jpg")) + \
                         list(class_dir.glob("*.jpeg")) + \
                         list(class_dir.glob("*.png")) + \
                         list(class_dir.glob("*.bmp"))

            for img_file in image_files:
                self.samples.append({
                    'image_path': img_file,
                    'label': class_idx,
                    'class_name': class_name
                })

        print(f"✓ 加载了 {len(self.samples)} 张图像")

        # 统计每个类别的数量
        class_counts = {}
        for sample in self.samples:
            class_name = sample['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        print("\n各类别数量:")
        for class_name in self.CLASS_NAMES:
            count = class_counts.get(class_name, 0)
            print(f"  {class_name}: {count}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        # 加载图像
        image = Image.open(sample['image_path']).convert('RGB')

        # 应用变换
        if self.transform:
            image = self.transform(image)

        label = sample['label']

        return image, label


def train_epoch(model, dataloader, criterion, optimizer, device):
    """训练一个epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc="训练")
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        # 前向传播
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)

        # 反向传播
        loss.backward()
        optimizer.step()

        # 统计
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        # 更新进度条
        pbar.set_postfix({
            'loss': f"{loss.item():.4f}",
            'acc': f"{100*correct/total:.1f}%"
        })

    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total

    return epoch_loss, epoch_acc


def validate(model, dataloader, criterion, device):
    """验证模型"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        pbar = tqdm(dataloader, desc="验证")
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)

            # 前向传播
            outputs = model(images)
            loss = criterion(outputs, labels)

            # 统计
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            # 更新进度条
            pbar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'acc': f"{100*correct/total:.1f}%"
            })

    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total

    return epoch_loss, epoch_acc


def main():
    """主程序"""
    print("=" * 70)
    print("  🧠 棋子识别模型训练")
    print("  完全基于深度学习，不使用规则判断")
    print("=" * 70)

    # 配置
    DATA_ROOT = Path(__file__).parent / "training_images"
    MODEL_DIR = Path(__file__).parent / "models"
    LOG_DIR = Path(__file__).parent / "training_logs"

    # 创建目录
    MODEL_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    # 训练参数
    IMAGE_SIZE = 64
    BATCH_SIZE = 16
    EPOCHS = 30
    LEARNING_RATE = 0.001
    TRAIN_RATIO = 0.8

    print(f"\n训练配置:")
    print(f"  训练数据: {DATA_ROOT}")
    print(f"  图像大小: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"  批次大小: {BATCH_SIZE}")
    print(f"  训练轮数: {EPOCHS}")
    print(f"  学习率: {LEARNING_RATE}")
    print(f"  训练比例: {TRAIN_RATIO*100:.0f}%")

    # 检查数据
    if not DATA_ROOT.exists():
        print("\n❌ 未找到训练数据目录！")
        print(f"   期望位置: {DATA_ROOT}")
        print("\n解决方法:")
        print("  1. 创建训练数据目录:")
        print(f"     mkdir -p {DATA_ROOT}/{{empty,white_pawn,white_knight,...}}")
        print("  2. 把照片放到对应目录")
        print("  3. 每个类别至少20张照片")
        return

    # 数据增强
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])

    # 加载数据
    print("\n加载训练数据...")
    full_dataset = PieceImageDataset(DATA_ROOT, transform=None)

    if len(full_dataset) == 0:
        print("\n❌ 未找到任何训练图像！")
        print("   请确保照片已放到对应目录")
        return

    # 分割数据集
    train_size = int(TRAIN_RATIO * len(full_dataset))
    val_size = len(full_dataset) - train_size

    full_dataset.transform = train_transform
    train_dataset = torch.utils.data.Subset(full_dataset, range(train_size))

    full_dataset.transform = val_transform
    val_dataset = torch.utils.data.Subset(full_dataset, range(train_size, len(full_dataset)))

    print(f"✓ 训练集: {len(train_dataset)} 张")
    print(f"✓ 验证集: {len(val_dataset)} 张")

    # 数据加载器
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # 创建模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n使用设备: {device}")

    model = SimpleCNN(num_classes=13).to(device)
    print(f"✓ 模型已创建")

    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    # 训练
    print("\n开始训练...")
    print("=" * 70)

    best_val_acc = 0
    best_model_state = None
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch+1}/{EPOCHS}")
        print("-" * 70)

        # 训练
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)

        # 验证
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        # 学习率调整
        scheduler.step()

        # 记录历史
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict().copy()

        print(f"\n训练: Loss={train_loss:.4f}, Acc={train_acc:.2f}%")
        print(f"验证: Loss={val_loss:.4f}, Acc={val_acc:.2f}%")
        print(f"学习率: {scheduler.get_last_lr()[0]:.6f}")
        print(f"最佳验证准确率: {best_val_acc:.2f}%")

    # 加载最佳模型
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    print("\n" + "=" * 70)
    print("  训练完成！")
    print("=" * 70)
    print(f"最佳验证准确率: {best_val_acc:.2f}%")

    # 保存模型
    model_path = MODEL_DIR / "piece_classifier.pth"
    torch.save({
        'model_state_dict': model.state_dict(),
        'class_names': PieceImageDataset.CLASS_NAMES,
        'piece_symbols': PieceImageDataset.PIECE_SYMBOLS,
        'history': history,
        'config': {
            'image_size': IMAGE_SIZE,
            'num_classes': 13,
            'epochs': EPOCHS,
            'learning_rate': LEARNING_RATE,
            'batch_size': BATCH_SIZE
        }
    }, model_path)

    print(f"\n✓ 模型已保存: {model_path}")

    # 保存训练历史
    history_path = LOG_DIR / f"training_history_{int(time.time())}.json"
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"✓ 训练历史已保存: {history_path}")

    # 显示最终统计
    print("\n" + "=" * 70)
    print("  训练统计")
    print("=" * 70)
    print(f"总图像数: {len(full_dataset)}")
    print(f"训练集: {len(train_dataset)}")
    print(f"验证集: {len(val_dataset)}")
    print(f"最佳准确率: {best_val_acc:.2f}%")
    print(f"训练轮数: {EPOCHS}")

    if best_val_acc >= 90:
        print("\n🎉 训练效果优秀！")
    elif best_val_acc >= 80:
        print("\n✅ 训练效果良好！")
    elif best_val_acc >= 70:
        print("\n⚠️  训练效果一般，建议:")
        print("   1. 增加训练图像数量")
        print("   2. 提高图像质量")
        print("   3. 增加训练轮数")
    else:
        print("\n❌ 训练效果不理想，建议:")
        print("   1. 检查图像标注是否正确")
        print("   2. 增加训练图像数量（每种至少50张）")
        print("   3. 提高图像质量")

    print("\n下一步:")
    print("  运行 use_model.py 使用训练好的模型")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n训练已停止")
    except Exception as e:
        print(f"\n\n训练出错: {e}")
        import traceback
        traceback.print_exc()
