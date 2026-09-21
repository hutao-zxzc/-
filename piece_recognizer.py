#!/usr/bin/env python3
"""
棋子识别模块
使用机器学习模型识别棋盘上的棋子
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from typing import Optional, List, Tuple
import pickle
from pathlib import Path


class ChessPieceCNN(nn.Module):
    """用于识别棋子的卷积神经网络"""

    def __init__(self, num_classes=13):  # 12种棋子 + 空格
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


class PieceRecognizer:
    """棋子识别器"""

    # 棋子类型映射
    PIECE_TYPES = {
        0: None,       # 空格
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
        12: 'k'        # 黑王
    }

    def __init__(self, model_path: Optional[str] = None):
        """
        初始化识别器

        Args:
            model_path: 预训练模型路径
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ChessPieceCNN().to(self.device)
        self.transform = transforms.Compose([
            transforms.Resize((48, 48)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            self.model.eval()
        else:
            print("警告：未加载模型，将使用基于规则的识别方法")

    def load_model(self, model_path: str):
        """
        加载预训练模型

        Args:
            model_path: 模型路径
        """
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f"模型已加载: {model_path}")
        except Exception as e:
            print(f"加载模型失败: {e}")

    def predict(self, square_img: np.ndarray) -> Optional[str]:
        """
        预测格子上的棋子

        Args:
            square_img: 格子图像

        Returns:
            棋子符号
        """
        # 如果没有加载模型，使用基于规则的方法
        if not hasattr(self.model, 'loaded'):
            return self._rule_based_recognition(square_img)

        # 使用神经网络预测
        try:
            img = Image.fromarray(cv2.cvtColor(square_img, cv2.COLOR_BGR2RGB))
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(img_tensor)
                _, predicted = torch.max(outputs, 1)

            piece_idx = predicted.item()
            return self.PIECE_TYPES[piece_idx]
        except Exception as e:
            print(f"预测失败: {e}")
            return self._rule_based_recognition(square_img)

    def _rule_based_recognition(self, square_img: np.ndarray) -> Optional[str]:
        """
        基于规则的识别方法（备用方案）

        Args:
            square_img: 格子图像

        Returns:
            棋子符号
        """
        # 转换为灰度图
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

        # 获取中心区域
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]

        # 计算标准差（检测是否有棋子）
        std_dev = np.std(center_region)

        # 如果标准差很小，说明是空格子
        if std_dev < 30:
            return None

        # 检测棋子颜色
        mean_color = np.mean(center_region)
        is_white_piece = mean_color > 128

        # 简单的轮廓检测
        edges = cv2.Canny(center_region, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return None

        # 获取最大轮廓
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)

        # 根据面积和形状识别棋子类型（简化版）
        # 实际应用中需要更复杂的特征提取或使用神经网络

        piece_type = None
        if area > center_region.size * 0.5:
            # 面积较大，可能是后或王
            piece_type = 'Q' if is_white_piece else 'q'
        elif area > center_region.size * 0.3:
            # 面积中等，可能是车或象
            piece_type = 'R' if is_white_piece else 'r'
        else:
            # 面积较小，可能是马或兵
            piece_type = 'N' if is_white_piece else 'n'

        return piece_type

    def create_training_dataset(self, board_images: List[np.ndarray],
                                annotations: List[List[Optional[str]]]) -> None:
        """
        创建训练数据集

        Args:
            board_images: 棋盘图像列表
            annotations: 标注列表，每个元素是8x8的棋子符号矩阵
        """
        # 这个方法用于生成训练数据
        # 实际应用中，需要从棋盘图像中提取每个格子并标注
        pass

    def train(self, train_loader, epochs: int = 50, learning_rate: float = 0.001):
        """
        训练模型

        Args:
            train_loader: 训练数据加载器
            epochs: 训练轮数
            learning_rate: 学习率
        """
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)

        self.model.train()

        for epoch in range(epochs):
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)

                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

    def save_model(self, save_path: str):
        """
        保存模型

        Args:
            save_path: 保存路径
        """
        torch.save({
            'model_state_dict': self.model.state_dict(),
        }, save_path)
        print(f"模型已保存: {save_path}")


def create_piece_templates():
    """
    创建棋子模板（用于模板匹配）

    这个方法可以生成标准棋子的模板图像
    用于简单的模板匹配识别
    """
    # TODO: 实现棋子模板生成
    pass


if __name__ == "__main__":
    # 测试代码
    recognizer = PieceRecognizer()

    # 加载测试图像
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)

    # 测试预测
    result = recognizer.predict(test_img)
    print(f"识别结果: {result}")
