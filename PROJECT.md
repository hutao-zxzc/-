# 项目结构说明

## 概述

这是一个完整的国际象棋自动对弈机器人项目，包含屏幕识别、棋子识别、AI计算和自动执行等功能模块。

## 目录结构

```
chess-bot/
├── chess_bot.py              # 主程序
├── piece_recognizer.py       # 棋子识别模块（神经网络）
├── calibration_tool.py       # 棋盘校准工具
├── test.py                   # 测试脚本
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── README.md                # 完整说明文档
├── QUICKSTART.md            # 快速开始指南
├── PROJECT.md               # 本文件（项目结构说明）
├── install.sh               # Linux/macOS安装脚本
├── install.bat              # Windows安装脚本
│
├── models/                  # 模型目录（需自行创建）
│   └── chess_pieces.pth     # 预训练的棋子识别模型
│
├── logs/                    # 日志目录（需自行创建）
│   └── chess_bot.log       # 运行日志
│
├── calibration.pkl          # 棋盘校准数据（自动生成）
└── board_preview.png        # 棋盘预览（自动生成）
```

## 核心模块说明

### 1. chess_bot.py - 主程序

**功能：**
- 棋盘区域设置和校准
- 屏幕捕获
- 棋盘格子提取
- AI走法计算（Stockfish）
- 自动移动执行

**主要类：**
- `ChessBot`: 主机器人类

**主要方法：**
- `set_board_region()`: 设置棋盘区域
- `capture_board()`: 捕获棋盘图像
- `detect_board_automatically()`: 自动检测棋盘
- `extract_squares()`: 提取格子图像
- `scan_board()`: 扫描棋盘状态
- `calculate_best_move()`: 计算最佳走法
- `execute_move()`: 执行移动
- `calibrate_board()`: 棋盘校准

**使用流程：**
1. 初始化机器人
2. 设置或校准棋盘区域
3. 扫描当前棋局
4. 计算最佳走法
5. 执行移动
6. 重复3-5

### 2. piece_recognizer.py - 棋子识别模块

**功能：**
- 神经网络模型定义
- 棋子图像识别
- 基于规则的备用识别方法

**主要类：**
- `ChessPieceCNN`: 卷积神经网络模型
- `PieceRecognizer`: 棋子识别器

**主要方法：**
- `predict()`: 预测格子上的棋子
- `load_model()`: 加载预训练模型
- `train()`: 训练模型
- `save_model()`: 保存模型

**识别逻辑：**
1. 如果加载了神经网络，使用模型预测
2. 否则使用基于规则的方法（颜色+轮廓）
3. 返回棋子符号（如 'P', 'N', 'B' 等）

### 3. calibration_tool.py - 棋盘校准工具

**功能：**
- 交互式校准界面
- 棋盘区域手动选择
- 校准数据保存和加载

**主要类：**
- `CalibrationTool`: 校准工具类

**主要方法：**
- `run_interactive_calibration()`: 运行交互式校准
- `draw_calibration_ui()`: 绘制校准UI
- `save_calibration()`: 保存校准数据
- `load_calibration()`: 加载校准数据
- `preview_board()`: 预览棋盘区域

**校准流程：**
1. 捕获屏幕
2. 绘制校准UI（网格线+说明）
3. 用户点击棋盘四个角
4. 计算棋盘区域
5. 保存校准数据
6. 显示预览

### 4. test.py - 测试脚本

**功能：**
- 单元测试
- 集成测试
- 交互式测试

**主要函数：**
- `test_screen_capture()`: 测试屏幕捕获
- `test_square_extraction()`: 测试格子提取
- `test_piece_recognition()`: 测试棋子识别
- `test_chess_logic()`: 测试国际象棋逻辑
- `test_stockfish()`: 测试Stockfish引擎
- `run_all_tests()`: 运行所有测试
- `interactive_test()`: 交互式测试

**使用方法：**
```bash
# 运行所有测试
python3 test.py --all

# 交互式测试
python3 test.py
```

### 5. config.py - 配置文件

**功能：**
- 集中管理所有配置项
- 保存和加载用户配置

**主要配置项：**
```python
STOCKFISH_PATH         # Stockfish引擎路径
STOCKFISH_DEPTH         # 搜索深度
CAPTURE_INTERVAL        # 捕获间隔
CLICK_DELAY            # 点击延迟
BOARD_REGION           # 棋盘区域
USE_NEURAL_NETWORK     # 是否使用神经网络
LOG_LEVEL             # 日志级别
DEBUG_MODE            # 调试模式
```

**使用方法：**
```python
from config import STOCKFISH_DEPTH

# 修改配置
STOCKFISH_DEPTH = 15

# 保存用户配置
config.save_config("config_user.py")

# 加载用户配置
config.load_config("config_user.py")
```

## 数据流图

```
屏幕 → 屏幕捕获 → 棋盘区域 → 格子提取 → 棋子识别 → 棋盘状态
                                                          ↓
对弈循环 ← 自动移动 ← 最佳走法 ← Stockfish AI ← 棋盘状态
```

## 扩展开发

### 添加新的棋子识别方法

1. 在 `piece_recognizer.py` 中添加新的识别函数
2. 在 `PieceRecognizer.predict()` 中调用新方法
3. 运行测试验证

### 集成其他AI引擎

在 `chess_bot.py` 中修改 `calculate_best_move()` 方法：

```python
def calculate_best_move_with_custom_engine(self, board, engine_path):
    # 使用其他引擎
    pass
```

### 添加对弈记录功能

在 `chess_bot.py` 中添加PGN记录：

```python
import chess.pgn

def record_move(self, game, move):
    # 记录走法到PGN
    game = game.add_variation(move)
    return game
```

### 添加多人对弈模式

在 `chess_bot.py` 中添加：

```python
def play_two_players(self, player1_bot, player2_bot):
    # 两个AI互相对弈
    pass
```

## 性能优化

### 提高识别速度
- 降低图像分辨率
- 使用更小的神经网络
- 减少不必要的中间结果保存

### 提高AI计算速度
- 降低搜索深度
- 设置时间限制
- 使用更快的电脑

### 减少内存占用
- 及时释放图像数据
- 使用生成器处理大量数据
- 避免重复加载模型

## 故障排查

### 问题：棋盘检测失败

**排查步骤：**
1. 检查屏幕捕获是否正常
2. 检查棋盘区域设置是否正确
3. 查看校准数据是否有效
4. 检查棋盘是否有明显的网格线

### 问题：棋子识别错误

**排查步骤：**
1. 查看棋盘预览图片
2. 检查格子提取是否正确
3. 尝试使用神经网络识别
4. 调整识别阈值

### 问题：AI走法无效

**排查步骤：**
1. 检查棋盘状态识别是否正确
2. 检查Stockfish是否正常工作
3. 验证移动是否符合规则
4. 检查棋盘坐标计算是否正确

## 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
git clone <repository>
cd chess-bot
pip install -r requirements.txt
python3 test.py --all
```

### 代码风格
- 遵循PEP 8规范
- 添加类型注解
- 编写文档字符串
- 编写单元测试

### 提交规范
- 清晰的commit消息
- 包含测试用例
- 更新相关文档

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过GitHub Issue联系。
