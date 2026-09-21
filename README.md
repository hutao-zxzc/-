# ♟️ Chess Bot - 国际象棋自动对弈机器人

快速识别屏幕棋盘并与AI对弈！

## 🚀 快速开始

### 方式1：一键启动（推荐）

```bash
cd /home/ubuntu/workspace/chess-bot
./start.sh
```

### 方式2：直接运行

```bash
# 快速修复版（推荐新手）
python QUICK_FIX.py

# 完整对弈版
python chess_bot.py

# 调试工具
python debug_recognition.py
```

---

## 📖 详细文档

查看完整启动指南：[STARTUP_GUIDE.md](STARTUP_GUIDE.md)

---

## 🎯 功能特性

- ✅ 自动识别屏幕棋盘
- ✅ 支持多种国际象棋引擎（Stockfish, LCZero）
- ✅ 自动移动棋子（鼠标点击）
- ✅ 调试工具，诊断识别问题
- ✅ FEN输入模式，100%准确

---

## 🔧 第一次使用？

1. 安装依赖
```bash
pip install opencv-python numpy torch torchvision pyautogui mss chess
```

2. 运行启动脚本
```bash
./start.sh
```

3. 按提示操作即可！

---

## 📁 主要文件

| 文件 | 说明 |
|------|------|
| `chess_bot.py` | 主程序，完整对弈功能 |
| `QUICK_FIX.py` | 快速修复版，改进识别算法 |
| `debug_recognition.py` | 调试工具 |
| `start.sh` | 一键启动脚本 |
| `STARTUP_GUIDE.md` | 完整启动指南 |
| `config.py` | 配置文件 |

---

## ⚙️ 配置

编辑 `config.py` 自定义设置：

```python
# 引擎路径
STOCKFISH_PATH = "stockfish"

# 搜索深度
STOCKFISH_DEPTH = 10

# 识别阈值
RECOGNITION_CONFIDENCE_THRESHOLD = 0.8
```

---

## 🐛 遇到问题？

### 识别不准？

1. 运行 `debug_recognition.py` 查看具体问题
2. 尝试 `QUICK_FIX.py`（更宽松的阈值）
3. 使用FEN手动输入模式（最准确）

### 缺少依赖？

```bash
pip install opencv-python numpy torch torchvision pyautogui mss chess
```

### 引擎问题？

```bash
# 安装Stockfish
sudo apt-get install stockfish

# 或修改config.py中的引擎路径
```

---

## 💡 提示

- 首次运行需要校准棋盘（点击左上角和右下角）
- 确保棋盘完全可见
- 充足的光线有助于识别
- 使用FEN模式最准确

---

## 📝 示例

```bash
# 快速启动
./start.sh

# 测试特定格子（如e4）
python -c "
import debug_recognition, pyautogui
d = debug_recognition.PieceRecognitionDebugger()
print('点击左上角...'); input(); x1,y1=pyautogui.position()
print('点击右下角...'); input(); x2,y2=pyautogui.position()
d.set_board_region(x1,y1,x2,y2)
d.test_specific_squares(['e4'])
"
```

---

## 🎉 开始对弈！

```bash
./start.sh
```

祝你好运！♟️
