# 📋 如何获取FEN字符串

FEN字符串是国际象棋棋盘状态的标准化表示格式，例如：
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

---

## 🎯 方法1：从在线平台获取（最准确）⭐

### Chess.com

1. 打开你的对局页面
2. 在棋盘下方点击 **"Share"** 或 **"分享"** 按钮
3. 找到 **"FEN"** 部分
4. 点击复制按钮 📋

```
棋盘下方菜单:
[分析] [分享] [设置] → 点击[分享]
     ↓
弹窗中有:
• 分享链接
• FEN: rnbqkbnr/...  ← 复制这个！
• PGN
```

### Lichess.org

1. 打开你的对局页面
2. 在棋盘右侧菜单点击 **"Share the position"** 或 **"分享位置"**
3. 在 **"FEN string"** 旁边点击 **"Copy"** 📋

```
棋盘右侧菜单:
[分析] [分享位置] → 点击[分享位置]
     ↓
弹窗中有:
• FEN string: rnbqkbnr/...  ← 点击 Copy
• Permalink
```

---

## 🎯 方法2：从识别结果获取

使用 Chess Bot 识别后，FEN会自动保存：

### QUICK_FIX.py 版本

运行后，FEN字符串会保存到：
```
chess-bot/recognized_fen.txt
```

查看内容：
```bash
cat /home/ubuntu/workspace/chess-bot/recognized_fen.txt
```

### chess_bot.py 版本

自动识别后，会显示在控制台：
```
识别的棋局:
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

---

## 🎯 方法3：使用Python获取

### 从棋盘对象获取

```python
import chess

# 创建棋盘
board = chess.Board()

# 获取FEN
fen = board.fen()
print(fen)
# 输出: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

# 执行一步棋后获取FEN
board.push(chess.Move.from_uci("e2e4"))
fen = board.fen()
print(fen)
# 输出: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
```

### 从自定义位置获取

```python
import chess

# 从FEN字符串创建棋盘
fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
board = chess.Board(fen)

# 显示棋盘
print(board)
print(f"\nFEN: {board.fen()}")
```

---

## 🎯 方法4：手动构建FEN（不推荐，除非必要）

### FEN字符串格式

```
[棋盘状态] [当前回合] [王车易位权] [吃过路兵目标格] [半回合计数] [回合数]
```

### 示例分解

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
│                                                 │ │ │  │ └─ 回合数(1)
│                                                 │ │ │  └─── 半回合计数(0)
│                                                 │ │  └───── 吃过路兵目标格(-表示无)
│                                                 │  └────── 王车易位权
│                                                 └─────── 当前回合(w=白方)
└────────────────────────────────────────────────── 棋盘状态
```

### 棋盘状态说明

- 从第8行到第1行，用 `/` 分隔
- 大写字母 = 白棋，小写字母 = 黑棋
- `p/P` = 兵, `n/N` = 马, `b/B` = 象, `r/R` = 车, `q/Q` = 后, `k/K` = 王
- 数字表示连续空格

### 构建示例

初始局面：
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

e4走棋后：
```
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
```

---

## 🔧 实用工具脚本

### 工具1：快速获取FEN脚本

创建 `get_fen.py`:

```python
#!/usr/bin/env python3
"""
快速获取FEN字符串的工具
"""

import chess

def print_fen(fen_str):
    """打印FEN和棋盘"""
    board = chess.Board(fen_str)
    print("=" * 60)
    print("FEN字符串:")
    print(fen_str)
    print()
    print("棋盘:")
    print(board)
    print("=" * 60)

def main():
    print("请选择:")
    print("1. 输入FEN字符串（验证和显示）")
    print("2. 查看初始局面")
    print("3. 查看e4开局后的局面")

    choice = input("\n选择 (1/2/3): ").strip()

    if choice == '1':
        fen = input("请输入FEN字符串: ").strip()
        try:
            print_fen(fen)
        except ValueError as e:
            print(f"❌ 无效的FEN: {e}")

    elif choice == '2':
        print_fen(chess.Board().fen())

    elif choice == '3':
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        print_fen(board.fen())

if __name__ == "__main__":
    main()
```

运行：
```bash
python get_fen.py
```

### 工具2：从棋盘生成FEN

创建 `board_to_fen.py`:

```python
#!/usr/bin/env python3
"""
从棋盘位置生成FEN字符串
"""

import chess

def board_to_fen():
    """交互式生成FEN"""
    board = chess.Board()

    print("当前棋盘:")
    print(board)
    print("\nFEN:", board.fen())

    print("\n可以输入UCI格式走棋，如 'e2e4'")
    print("输入 'q' 退出\n")

    while True:
        move_str = input("输入走棋: ").strip()

        if move_str.lower() == 'q':
            break

        try:
            move = chess.Move.from_uci(move_str)
            if move in board.legal_moves:
                board.push(move)
                print("\n新棋盘:")
                print(board)
                print("\nFEN:", board.fen())
            else:
                print("❌ 非法走棋")
        except ValueError:
            print("❌ 无效的走棋格式")

    print("\n最终FEN:")
    print(board.fen())

if __name__ == "__main__":
    board_to_fen()
```

运行：
```bash
python board_to_fen.py
```

---

## 🎯 最快方法总结

### 场景1：已有在线对局
→ 去 **chess.com** 或 **lichess.org** → 点击"分享" → 复制FEN

### 场景2：使用Chess Bot识别
→ 运行识别程序 → 查看 `recognized_fen.txt` 或控制台输出

### 场景3：编程中需要
→ 使用 `board.fen()` 方法

### 场景4：学习/测试
→ 使用 `get_fen.py` 或 `board_to_fen.py` 工具

---

## 💡 FEN字符串示例

### 初始局面
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### e4开局后
```
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
```

### 西班牙开局
```
r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3
```

### 意大利开局
```
r1bqk1nr/pppp1ppp/2n5/4p3/2b1P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 3 4
```

---

## 🚀 快速复制

常用FEN（复制即用）：

**初始局面：**
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**e4开局：**
```
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
```

---

## 📚 更多资源

- FEN规范：https://en.wikipedia.org/wiki/Forsyth–Edwards_Notation
- Chess.com FEN工具：https://www.chess.com/analysis
- Lichess FEN工具：https://lichess.org/analysis

---

## ✅ 总结

| 方法 | 速度 | 准确度 | 推荐场景 |
|------|------|--------|----------|
| Chess.com分享 | ⚡⚡⚡ | ✅✅✅ | 在线对局 |
| Lichess分享 | ⚡⚡⚡ | ✅✅✅ | 在线对局 |
| 识别结果 | ⚡⚡ | ⚠️⚠️ | 屏幕识别 |
| Python生成 | ⚡⚡ | ✅✅✅ | 编程开发 |
| 手动构建 | ⚡ | ✅✅✅ | 学习测试 |

**推荐：** 使用Chess.com或Lichess的分享功能，最快最准确！
