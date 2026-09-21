# ♟️ Chess Bot 完整使用指南

## 📋 快速导航

| 需求 | 解决方案 | 命令 |
|------|----------|------|
| **从头启动** | 启动指南 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md) |
| **识别不准** | 改进方案 | [RECOGNITION_IMPROVE.md](RECOGNITION_IMPROVE.md) |
| **获取FEN** | FEN工具 | [FEN_GUIDE.md](FEN_GUIDE.md) |
| **测试识别器** | 测试脚本 | `./test_recognizers.sh` |

---

## 🚀 立即开始

### 第一次使用？

```bash
cd /home/ubuntu/workspace/chess-bot

# 方法1：使用启动脚本（推荐）
./start.sh

# 方法2：直接运行快速修复版
python QUICK_FIX.py
```

### 识别不准？

```bash
# 测试所有识别器，找到最好的
./test_recognizers.sh

# 选择完整测试模式（选项2）
```

### 需要FEN字符串？

```bash
# 查看当前识别的FEN
python show_current_fen.py

# 或使用FEN工具
python get_fen.py
```

---

## 🎯 识别器选择

| 识别器 | 识别率 | 准确度 | 推荐场景 |
|--------|--------|--------|----------|
| **QUICK_FIX.py** | ⚡⚡⚡ | ⚡⚡⚡ | 一般情况，首次使用 |
| **ULTRA_LOOSE.py** | ⚡⚡⚡⚡⚡ | ⚡⚡ | 识别困难，需要高识别率 |
| **COLOR_MATCH.py** | ⚡⚡⚡⚡ | ⚡⚡⚡ | 颜色对比明显的棋盘 |

---

## 📊 工作流程

### 典型使用流程：

```
1. 运行 ./test_recognizers.sh
        ↓
2. 选择"完整测试"模式
        ↓
3. 按提示依次测试所有识别器
        ↓
4. 查看对比结果，选择最准确的
        ↓
5. 日常使用时直接运行最佳识别器
```

### 如果所有识别器都不准：

```
→ 使用FEN手动输入模式
        ↓
1. 去 chess.com 或 lichess.org
        ↓
2. 点击"分享"复制FEN
        ↓
3. 使用 get_fen.py 验证
        ↓
4. 直接使用FEN字符串
```

---

## 🛠️ 所有工具

| 工具 | 功能 | 命令 |
|------|------|------|
| `start.sh` | 一键启动脚本 | `./start.sh` |
| `test_recognizers.sh` | 测试所有识别器 | `./test_recognizers.sh` |
| `QUICK_FIX.py` | 基础识别器 | `python QUICK_FIX.py` |
| `ULTRA_LOOSE.py` | 超宽松识别器 | `python ULTRA_LOUSE.py` |
| `COLOR_MATCH.py` | 颜色匹配识别器 | `python COLOR_MATCH.py` |
| `get_fen.py` | FEN工具 | `python get_fen.py` |
| `show_current_fen.py` | 显示当前FEN | `python show_current_fen.py` |
| `debug_recognition.py` | 调试工具 | `python debug_recognition.py` |
| `chess_bot.py` | 完整对弈程序 | `python chess_bot.py` |

---

## 📚 文档列表

| 文档 | 说明 |
|------|------|
| `README.md` | 项目介绍 |
| `STARTUP_GUIDE.md` | 完整启动指南 |
| `RECOGNITION_IMPROVE.md` | 识别改进方案 |
| `FEN_GUIDE.md` | FEN获取指南 |

---

## 🔧 常见问题

### Q: 识别不到棋子
**A:** 运行 `ULTRA_LOOSE.py`（超宽松模式）

### Q: 识别不准确
**A:** 运行 `./test_recognizers.sh` 测试所有识别器

### Q: 棋盘位置不对
**A:** 删除校准文件后重新运行：
```bash
rm calibration_*.pkl
python QUICK_FIX.py
```

### Q: 如何获取准确的FEN？
**A:** 去 chess.com/lichess 点击"分享"，复制FEN

### Q: 找不到引擎文件
**A:** 安装 Stockfish：
```bash
sudo apt-get install stockfish
```

### Q: 如何查看识别结果？
**A:** 运行：
```bash
python show_current_fen.py
```

---

## 💡 最佳实践

### 1. 首次使用
```bash
./test_recognizers.sh
# 选择完整测试
# 找到最准确的识别器
```

### 2. 日常使用
```bash
# 直接运行最佳识别器
python ULTRA_LOOSE.py  # 或其他
```

### 3. 在线对局
```bash
# 使用FEN复制
python get_fen.py
# 粘贴从chess.com/lichess复制的FEN
```

### 4. 调试问题
```bash
python debug_recognition.py
# 测试指定格子
```

---

## 🎯 快速命令参考

```bash
# 启动
./start.sh

# 测试识别器
./test_recognizers.sh

# 快速识别
python QUICK_FIX.py
python ULTRA_LOOSE.py
python COLOR_MATCH.py

# 查看FEN
python show_current_fen.py
python get_fen.py

# 调试
python debug_recognition.py

# 完整对弈
python chess_bot.py
```

---

## 📈 识别率优化

### 如果识别率 < 70%：
1. 运行 `ULTRA_LOOSE.py`
2. 检查棋盘位置
3. 改善光线
4. 尝试 `COLOR_MATCH.py`

### 如果识别率 70-90%：
1. 使用 `QUICK_FIX.py`
2. 查看调试图像
3. 调整阈值

### 如果识别率 > 90%：
1. 继续使用当前识别器
2. 保存校准数据

---

## 📞 获取帮助

### 查看详细文档：
```bash
cat STARTUP_GUIDE.md
cat RECOGNITION_IMPROVE.md
cat FEN_GUIDE.md
```

### 运行诊断：
```bash
python debug_recognition.py
```

---

## ✅ 检查清单

### 启动前：
- [ ] 棋盘完全可见
- [ ] 棋子摆放正确
- [ ] 光线充足
- [ ] 无遮挡

### 识别后：
- [ ] 查看识别结果
- [ ] 验证FEN是否正确
- [ ] 检查棋子数量
- [ ] 保存校准数据

---

## 🎉 开始使用

选择一个开始方式：

```bash
# 方式1：使用启动脚本（推荐新手）
./start.sh

# 方式2：测试所有识别器（推荐遇到问题时）
./test_recognizers.sh

# 方式3：直接运行快速修复版
python QUICK_FIX.py
```

祝使用愉快！♟️

---

**最后更新：** 2024年
**版本：** 2.0
