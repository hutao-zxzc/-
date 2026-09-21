# 快速开始指南

5分钟快速上手国际象棋自动对弈机器人！

## 前置条件

✅ Python 3.8+
✅ 电脑上打开一个国际象棋应用或网站

## 第一步：安装

### Linux/macOS
```bash
cd chess-bot
bash install.sh
```

### Windows
```cmd
cd chess-bot
install.bat
```

## 第二步：校准棋盘

打开你的国际象棋应用（Chess.com, lichess.org, 或任何在线棋盘）

运行校准工具：
```bash
python3 calibration_tool.py
```

### 校准操作：
1. 屏幕会显示校准界面
2. 用鼠标左键点击棋盘的**四个角**（按任意顺序）
3. 按 `SPACE` 或 `ESC` 保存校准结果
4. 程序会显示棋盘预览，确认无误即可

## 第三步：开始对弈

运行主程序：
```bash
python3 chess_bot.py
```

### 对弈操作：
1. 对手走棋后，按 `Enter` 键
2. 程序会自动：
   - 扫描棋盘
   - 计算最佳走法
   - 自动执行移动
3. 重复步骤1-2直到游戏结束
4. 按 `Ctrl+C` 停止程序

## 常见问题快速解决

### Q: 棋盘识别不准确？
**A:** 重新运行 `python3 calibration_tool.py`，精确点击棋盘四个角

### Q: AI走法不对？
**A:** 确保棋盘清晰可见，没有其他窗口遮挡

### Q: 程序无法识别棋子？
**A:**
1. 检查棋盘预览图片（`board_preview.png`）
2. 确保棋盘完全在视野内
3. 确保棋盘没有被其他窗口遮挡

### Q: 如何调整AI强度？
**A:** 在 `config.py` 中修改 `STOCKFISH_DEPTH`（默认10，最高20+）

### Q: 多显示器如何使用？
**A:** 确保棋盘在主显示器上，或在校准时选择正确的显示器

## 提示和技巧

### 🎯 提高识别准确率
- 棋盘尽量放大
- 避免棋盘上有阴影
- 不要有其他窗口遮挡棋盘
- 使用高对比度的棋盘样式

### ⚡ 提高对弈速度
- 降低AI搜索深度：`STOCKFISH_DEPTH = 5`
- 减少点击延迟：`CLICK_DELAY = 0.2`
- 使用更快的电脑

### 🧪 测试功能
```bash
# 运行所有测试
python3 test.py --all

# 交互式测试
python3 test.py
```

## 配置文件说明

在 `config.py` 中可以自定义：

```python
# AI强度
STOCKFISH_DEPTH = 10  # 越高越强

# 速度
CLICK_DELAY = 0.5  # 点击延迟（秒）

# 识别模式
USE_NEURAL_NETWORK = False  # 是否使用神经网络识别
```

## 下一步

- 📖 阅读完整的 [README.md](README.md)
- 🔧 查看 [config.py](config.py) 了解更多配置选项
- 🧪 运行 [test.py](test.py) 测试各项功能

## 注意事项

⚠️ **重要：**
- 此程序仅用于学习和娱乐
- 在线对弈平台可能禁止使用自动化工具
- 使用前请遵守平台规则
- 建议在训练模式或与朋友对弈时使用

---

**祝你玩得愉快！♟️**
