"""
配置文件
自定义机器人的各项参数
"""

# ========================================
# 基本配置
# ========================================

# Stockfish引擎路径
# Linux/macOS: 通常在PATH中，可以直接用 "stockfish"
# Windows: 如果不在PATH中，指定完整路径，如 r"C:\Program Files\stockfish\stockfish.exe"
STOCKFISH_PATH = "C:\Users\12991\Desktop\stockfish\stockfish-windows-x86-64-universal.exe"f

# ========================================
# AI配置
# ========================================

# 搜索深度（越高越强，但计算越慢）
# 推荐值: 10-15
STOCKFISH_DEPTH = 10

# 思考时间限制（毫秒）
STOCKFISH_TIME_LIMIT = 1000

# ========================================
# 屏幕捕获配置
# ========================================

# 捕获间隔（秒）
CAPTURE_INTERVAL = 0.5

# 点击延迟（秒）
CLICK_DELAY = 0.5

# 失败重试次数
MAX_RETRIES = 3

# ========================================
# 棋盘识别配置
# ========================================

# 棋盘区域（校准后自动更新）
BOARD_REGION = None  # {"top": y1, "left": x1, "width": w, "height": h}

# 格子大小（校准后自动更新）
SQUARE_SIZE = None  # (width, height)

# 是否使用自动检测
AUTO_DETECT_BOARD = True

# ========================================
# 棋子识别配置
# ========================================

# 识别模型路径
PIECE_MODEL_PATH = None  # "models/chess_pieces.pth"

# 识别阈值
RECOGNITION_CONFIDENCE_THRESHOLD = 0.8

# 是否使用神经网络识别
USE_NEURAL_NETWORK = False

# ========================================
# 日志配置
# ========================================

# 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# 日志文件路径
LOG_FILE = "logs/chess_bot.log"

# 是否保存棋盘预览
SAVE_BOARD_PREVIEW = True

# 预览图片保存路径
BOARD_PREVIEW_PATH = "board_preview.png"

# ========================================
# 调试配置
# ========================================

# 是否显示调试信息
DEBUG_MODE = False

# 是否显示中间结果
SHOW_INTERMEDIATE_RESULTS = False

# ========================================
# 保存配置到文件的函数
# ========================================

def save_config(filepath: str = "config_user.py"):
    """保存当前配置到文件"""
    import inspect

    # 获取当前模块的所有配置项
    config_items = {}
    for name, value in globals().items():
        if name.isupper() and not name.startswith("_"):
            config_items[name] = value

    # 写入配置文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('# 用户配置文件\n')
        f.write('# 此文件会覆盖config.py中的默认值\n\n')

        for name, value in config_items.items():
            if isinstance(value, str):
                f.write(f'{name} = "{value}"\n')
            else:
                f.write(f'{name} = {value}\n')

    print(f"配置已保存到: {filepath}")


def load_config(filepath: str = "config_user.py"):
    """从文件加载配置"""
    import os

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            exec(f.read())
        print(f"配置已加载: {filepath}")
    else:
        print(f"配置文件不存在: {filepath}")


if __name__ == "__main__":
    # 生成用户配置模板
    print("生成用户配置模板...")
    save_config("config_user_template.py")
    print("完成!")
