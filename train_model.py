#!/usr/bin/env python3
"""
模型训练脚本
训练棋子识别神经网络
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
from pathlib import Path
import pickle
import json
import time
from tqdm import tqdm


class ChessPieceCNN(nn.Module):
    """棋子识别CNN"""

    def __init__(self, num_classes=13):
        super(ChessPieceCNN, self).__init__()

        self.features = nn.Sequential(
            # 第一层
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # 第二层
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # 第三层
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # 第四层
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 3 * 3, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


class ChessPieceDataset(Dataset):
    """棋子数据集"""

    # 棋子类型映射
    PIECE_TYPES = {
        'empty': 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12,
    }

    def __init__(self, root_dir, transform=None):
        """
        Args:
            root_dir: 训练数据根目录
            transform: 数据增强
        """
        self.root_dir = Path(root_dir)
        self.transform = transform

        # 加载所有数据
        self.samples = []
        self.load_data()

    def load_data(self):
        """加载所有标注的数据"""
        raw_dir = self.root_dir / "raw"

        if not raw_dir.exists():
            raise FileNotFoundError(f"未找到数据目录: {raw_dir}")

        # 遍历所有数据集
        for dataset_dir in raw_dir.iterdir():
            if not dataset_dir.is_dir():
                continue

            # 加载标注
            label_file = dataset_dir / "labels.json"
            if not label_file.exists():
                print(f"⚠️  跳过未标注的数据集: {dataset_dir.name}")
                continue

            with open(label_file, 'r') as f:
                labels = json.load(f)

            # 加载图像
            for square_name, label_data in labels.items():
                img_file = dataset_dir / f"{square_name}.png"
                if not img_file.exists():
                    continue

                label_str = label_data['label']
                if label_str not in self.PIECE_TYPES:
                    print(f"⚠️  跳过未知标签: {label_str}")
                    continue

                label = self.PIECE_TYPES[label_str]

                self.samples.append({
                    'image_path': img_file,
                    'label': label,
                    'square_name': square_name,
                    'dataset': dataset_dir.name
                })

        print(f"✓ 加载了 {len(self.samples)} 个样本")

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


def train_model(model, train_loader, val_loader, epochs, device, learning_rate):
    """训练模型"""

    # 损失函数
    criterion = nn.CrossEntropyLoss()

    # 优化器
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 学习率调度器
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    # 训练历史
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }

    best_val_acc = 0
    best_model_state = None

    print("\n开始训练...")
    print("=" * 70)

    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [训练]")
        for images, labels in train_pbar:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()

            train_pbar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'acc': f"{100*train_correct/train_total:.1f}%"
            })

        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total

        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [验证]"):
                images, labels = images.to(device), labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()

        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total

        # 更新学习率
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

        # 打印进度
        print(f"Epoch {epoch+1}/{epochs}:")
        print(f"  训练 - Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
        print(f"  验证 - Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")
        print(f"  学习率: {scheduler.get_last_lr()[0]:.6f}")
        print("-" * 70)

    print("\n训练完成！")
    print(f"最佳验证准确率: {best_val_acc:.2f}%")

    # 加载最佳模型
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    return model, history


def main():
    """主程序"""
    print("=" * 70)
    print("  🧠 棋子识别模型训练")
    print("=" * 70)

    # 配置
    DATA_ROOT = Path(__file__).parent / "training_data"
    MODEL_DIR = Path(__file__).parent / "models"
    LOG_DIR = Path(__file__).parent / "training_logs"

    # 创建目录
    MODEL_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    # 训练参数
    IMAGE_SIZE = 48
    BATCH_SIZE = 32
    EPOCHS = 50
    LEARNING_RATE = 0.001
    TRAIN_RATIO = 0.8

    print(f"\n训练配置:")
    print(f"  图像大小: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"  批次大小: {BATCH_SIZE}")
    print(f"  训练轮数: {EPOCHS}")
    print(f"  学习率: {LEARNING_RATE}")
    print(f"  训练比例: {TRAIN_RATIO*100:.0f}%")

    # 数据增强
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
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
    full_dataset = ChessPieceDataset(DATA_ROOT, transform=None)

    if len(full_dataset) == 0:
        print("\n❌ 未找到训练数据！")
        print("   请先运行 collect_data.py 和 label_data.py")
        return

    print(f"✓ 总样本数: {len(full_dataset)}")

    # 分割训练集和验证集
    train_size = int(TRAIN_RATIO * len(full_dataset))
    val_size = len(full_dataset) - train_size

    full_dataset.transform = train_transform
    train_dataset = torch.utils.data.Subset(full_dataset, range(train_size))

    full_dataset.transform = val_transform
    val_dataset = torch.utils.data.Subset(full_dataset, range(train_size, len(full_dataset)))

    print(f"✓ 训练集: {len(train_dataset)}")
    print(f"✓ 验证集: {len(val_dataset)}")

    # 数据加载器
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 创建模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n使用设备: {device}")

    model = ChessPieceCNN(num_classes=13).to(device)
    print(f"✓ 模型已创建")

    # 训练模型
    model, history = train_model(
        model, train_loader, val_loader,
        EPOCHS, device, LEARNING_RATE
    )

    # 保存模型
    model_path = MODEL_DIR / "chess_pieces_trained.pth"
    torch.save({
        'model_state_dict': model.state_dict(),
        'history': history,
        'config': {
            'image_size': IMAGE_SIZE,
            'num_classes': 13,
            'epochs': EPOCHS,
            'learning_rate': LEARNING_RATE,
        }
    }, model_path)

    print(f"\n✓ 模型已保存: {model_path}")

    # 保存训练历史
    history_path = LOG_DIR / f"training_history_{int(time.time())}.json"
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"✓ 训练历史已保存: {history_path}")

    print("\n" + "=" * 70)
    print("  🎉 训练完成！")
    print("=" * 70)

    print(f"\n模型文件: {model_path}")
    print(f"\n下一步:")
    print(f"  1. 运行 use_trained_model.py 使用模型")
    print(f"  2. 运行 validate_model.py 验证模型性能")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n训练已停止")
    except Exception as e:
        print(f"\n\n训练出错: {e}")
        import traceback
        traceback.print_exc()
