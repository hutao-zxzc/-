# 修复说明

## ✅ 已修复的问题

### AttributeError: module 'chess' has no attribute 'rank_index'

**问题原因：**
`chess` 库没有 `rank_index` 和 `file_index` 函数。

**解决方案：**
使用正确的API：
- `chess.rank_index()` → `chess.square_rank()`
- `chess.file_index()` → `chess.square_file()`

### 已修复的文件

1. **chess_bot.py** - 已修复
2. **screen_recognition_bot.py** - 已修复

## 🔄 如何更新

**在Windows上，你需要更新这两个文件：**

### 方法1：复制服务器文件

从 `/home/ubuntu/workspace/chess-bot/` 复制：
- `chess_bot.py`
- `screen_recognition_bot.py`

到你的 Windows 电脑。

### 方法2：手动修复

如果你已经下载了文件，可以手动修复：

**查找所有 `rank_index`，替换为 `square_rank`**
**查找所有 `file_index`，替换为 `square_file`**

## 🧪 测试修复

运行测试脚本验证：

```bash
cd C:\Users\Administrator\Desktop\chess-bot
python simple_test.py
```

如果显示 "🎉 测试通过"，说明一切正常。

## 🚀 运行程序

修复后，直接运行：

```bash
python screen_recognition_bot.py
```

或

```bash
python chess_bot.py
```

## 📋 修复后的使用流程

1. **启动程序**
2. **校准棋盘**（首次使用）
3. **在 chess.com/lichess.org 上打开对局**
4. **按 Enter**
5. **程序自动识别棋盘**
6. **AI 自动执行移动**
7. **按 Enter 继续**
8. **重复步骤 4-7**

---

**现在应该不会再出现 `rank_index` 错误了！** 🎉
