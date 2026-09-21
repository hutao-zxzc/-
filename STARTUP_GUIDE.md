# 🚀 Chess Bot 完整启动指南

## 📋 前置检查清单

启动前，请确保：
- ✅ 棋盘在屏幕上完全可见
- ✅ 棋子已按初始位置摆放
- ✅ 光线充足，棋子清晰可见
- ✅ 已安装必要的Python依赖

---

## 🎯 推荐启动方式（3种选择）

### 方式1：快速修复版（推荐新手）⭐

**适合：** 想快速测试，不追求完美识别

```bash
cd /home/ubuntu/workspace/chess-bot
python QUICK_FIX.py
```

**步骤：**
1. 运行命令
2. 鼠标点击棋盘左上角 → 按Enter
3. 鼠标点击棋盘右下角 → 按Enter
4. 查看识别结果

**特点：**
- ✅ 识别阈值更宽松，更容易检测到棋子
- ✅ 自动保存校准数据
- ✅ 保存识别出的FEN字符串

---

### 方式2：原始主程序（完整功能）

**适合：** 需要完整对弈功能

```bash
cd /home/ubuntu/workspace/chess-bot
python chess_bot.py
```

**步骤：**
1. 运行命令
2. 选择校准方式：
   - `1` = 手动点击四角
   - `2` = 自动检测棋盘
3. 选择模式：
   - `1` = 自动识别屏幕
   - `2` = 手动输入FEN
4. 开始对弈！

**特点：**
- ✅ 完整的AI对弈功能
- ✅ 支持自动移动（鼠标点击）
- ✅ 支持LCZero/Stockfish引擎

**⚠️ 注意：** 需要先安装国际象棋引擎
- Stockfish: https://stockfishchess.org/download/
- LCZero: https://github.com/LeelaChessZero/lc0/releases

---

### 方式3：调试工具（诊断问题）

**适合：** 识别不准，想找原因

```bash
cd /home/ubuntu/workspace/chess-bot
python debug_recognition.py
```

**步骤：**
1. 运行命令
2. 点击棋盘左上角 → 按Enter
3. 点击棋盘右下角 → 按Enter
4. 选择测试模式：
   - `1` = 测试指定格子（如 e4, d4, e5, d5）
   - `2` = 测试所有64个格子（会保存大量图片）
   - `3` = 测试中心区域（推荐）

**特点：**
- ✅ 详细显示每个格子的分析数据
- ✅ 保存格子截图到 `debug_squares/` 目录
- ✅ 帮助识别问题所在

---

## 🔧 第一次运行？需要这些

### 1. 安装依赖

```bash
cd /home/ubuntu/workspace/chess-bot
pip install -r requirements.txt
```

**如果没有requirements.txt，手动安装：**

```bash
pip install opencv-python numpy torch torchvision pyautogui mss chess
```

### 2. （可选）安装国际象棋引擎

**Stockfish（推荐，速度快）：**
```bash
# Linux
sudo apt-get install stockfish

# 或者下载
wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64-avx2.tar.bz2
tar -xjf stockfish-ubuntu-x86-64-avx2.tar.bz2
```

**LCZero（更强，但需要神经网络）：**
```bash
# 下载并解压
# https://github.com/LeelaChessZero/lc0/releases
```

### 3. 配置引擎路径（如果需要）

编辑 `config.py`:
```python
STOCKFISH_PATH = "stockfish"  # 如果在PATH中
# 或者完整路径
STOCKFISH_PATH = "/path/to/your/engine"
```

---

## 📊 启动流程图

```
开始
  ↓
[1] 选择启动方式
  ├─→ 方式1: QUICK_FIX.py（快速测试）
  ├─→ 方式2: chess_bot.py（完整对弈）
  └─→ 方式3: debug_recognition.py（调试）
  ↓
[2] 校准棋盘
  ├─→ 自动检测
  └─→ 手动点击（左上角 → 右下角）
  ↓
[3] 测试识别
  ├─→ 查看识别结果
  └─→ 检查FEN字符串
  ↓
[4] 开始使用
  ├─→ 自动对弈（方式2）
  ├─→ FEN输入模式（任何方式）
  └─→ 继续调试（方式3）
```

---

## ⚡ 快速启动命令（复制即用）

### 第一次运行
```bash
cd /home/ubuntu/workspace/chess-bot && python QUICK_FIX.py
```

### 常规启动（已校准过）
```bash
cd /home/ubuntu/workspace/chess-bot && python chess_bot.py
```

### 调试识别问题
```bash
cd /home/ubuntu/workspace/chess-bot && python debug_recognition.py
```

### 测试特定格子（如e4）
```bash
cd /home/ubuntu/workspace/chess-bot && python -c "
import debug_recognition, pyautogui, time
d = debug_recognition.PieceRecognitionDebugger()
print('点击左上角...'); input(); x1,y1=pyautogui.position()
print('点击右下角...'); input(); x2,y2=pyautogui.position()
d.set_board_region(x1,y1,x2,y2)
d.test_specific_squares(['e4','d4','e5','d5'])
"
```

---

## 🎨 常见问题解决

### Q1: "No module named 'xxx'"

**解决：**
```bash
pip install opencv-python numpy torch torchvision pyautogui mss chess
```

### Q2: "引擎文件不存在"

**解决：**
- 安装Stockfish: `sudo apt-get install stockfish`
- 或修改 `config.py` 中的引擎路径

### Q3: 识别不准确

**解决：**
1. 尝试 `QUICK_FIX.py`（更宽松的阈值）
2. 使用FEN输入模式（手动输入最准确）
3. 运行 `debug_recognition.py` 查看具体问题
4. 改善环境：充足光线、清晰的棋盘、清晰的棋子

### Q4: 识别不到任何棋子

**检查：**
- ✅ 棋盘是否完全可见
- ✅ 校准是否正确（左上角和右下角）
- ✅ 是否遮挡了棋盘
- ✅ 棋盘是否有特殊样式（3D、半透明等）

### Q5: 鼠标移动不正确

**检查：**
- ✅ 显示器缩放是否100%
- ✅ 多显示器时坐标是否正确
- ✅ 使用 `debug_recognition.py` 验证棋盘区域

---

## 📝 操作示例

### 示例1：使用快速修复版

```bash
$ python QUICK_FIX.py
======================================================================
  快速修复 - 棋子识别改进版
======================================================================

改进点:
  1. ✓ 降低识别阈值，更容易检测到棋子
  2. ✓ 使用多种检测方法，提高准确率
  3. ✓ 改进棋子分类逻辑
  4. ✓ 保存校准数据，下次使用
======================================================================

按Enter后点击左上角，然后按Enter继续...
[鼠标点击左上角]
[按Enter]
  左上角: (100, 200)

按Enter后点击右下角，然后按Enter继续...
[鼠标点击右下角]
[按Enter]
  右下角: (900, 1000)
✓ 棋盘区域设置完成: (100, 200) -> (900, 1000)
✓ 格子大小: (100, 100)

=== 开始扫描棋盘 ===
  ✓ a1: R
  ✓ b1: N
  ✓ c1: B
  ✗ a2: 空
  ...

识别结果: 32 个棋子, 32 个空格子

当前棋局:
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

✓ FEN字符串已保存: recognized_fen.txt
  FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### 示例2：使用调试工具

```bash
$ python debug_recognition.py
======================================================================
  棋子识别调试工具
======================================================================

请设置棋盘区域:
1. 点击棋盘左上角
按Enter继续...
[点击并按Enter]
2. 点击棋盘右下角
按Enter继续...
[点击并按Enter]
棋盘区域: (100, 200) -> (900, 1000)
格子大小: (100, 100)

请选择测试模式:
1. 测试指定格子（推荐）
2. 测试所有格子
3. 测试中心区域（e4, d4, e5, d5）

请输入选择 (1/2/3): 1

请输入要测试的格子名称（用空格分隔）:
例如: e2 e4 d4 e5

格子名称: e4

==================================================
格子 (4, 4) - e4
==================================================
图像尺寸: (100, 100)
中心区域均值: 120.34
中心区域标准差: 45.67
白色像素: 1234 (45.2%)
黑色像素: 1498 (54.8%)

方法1 (标准差): ✓ 有棋子
方法2 (像素比例): ✓ 有棋子
方法3 (边缘检测): ✓ 有棋子

综合判断: ✓ 有棋子

轮廓面积: 1567.23
轮廓周长: 234.56
圆形度: 0.897

棋子猜测: 白棋 后/兵
==================================================
格子图像已保存: debug_squares/e4.png
```

---

## 🎯 推荐启动顺序

### 第一次使用：
```
1. 安装依赖
2. 运行 QUICK_FIX.py
3. 查看识别结果
4. 如果满意 → 使用 chess_bot.py 完整对弈
   如果不满意 → 运行 debug_recognition.py 找原因
```

### 日常使用（已校准）：
```
1. 确保棋盘可见
2. 运行 chess_bot.py
3. 选择模式（自动/手动）
4. 开始对弈！
```

---

## 💡 最佳实践

1. **首次校准很重要**
   - 准确点击棋盘的四个角
   - 不要包含多余的区域

2. **使用FEN模式更准确**
   - 在chess.com/lichess.org点击"分享"
   - 复制FEN字符串
   - 直接输入，100%准确

3. **保持环境稳定**
   - 固定棋盘位置
   - 充足的光线
   - 清晰的棋子样式

4. **定期调试**
   - 如果识别突然变差
   - 运行 debug_recognition.py 检查
   - 重新校准棋盘

---

## 📚 相关文件说明

| 文件 | 用途 |
|------|------|
| `chess_bot.py` | 主程序，完整对弈功能 |
| `QUICK_FIX.py` | 快速修复版，改进识别算法 |
| `debug_recognition.py` | 调试工具，诊断识别问题 |
| `calibration.pkl` | 校准数据（自动生成） |
| `board_preview.png` | 棋盘预览（自动生成） |
| `debug_squares/` | 调试图片目录 |
| `recognized_fen.txt` | 识别的FEN字符串 |
| `config.py` | 配置文件 |

---

## 🎉 开始吧！

现在，选择一个启动方式，运行命令即可：

```bash
# 推荐：快速修复版
python QUICK_FIX.py

# 或：完整对弈
python chess_bot.py

# 或：调试工具
python debug_recognition.py
```

祝你好运！♟️
