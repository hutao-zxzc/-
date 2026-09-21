#!/bin/bash
# 国际象棋自动对弈机器人 - 安装脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "国际象棋自动对弈机器人 - 安装程序"
echo "=========================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version || {
    echo "错误: 未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
}

# 检查pip
echo "检查pip..."
python3 -m pip --version || {
    echo "错误: 未找到pip，请先安装pip"
    exit 1
}

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n): " create_venv
if [ "$create_venv" = "y" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "虚拟环境已激活"
fi

# 安装Python依赖
echo ""
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查并安装Stockfish
echo ""
echo "检查Stockfish引擎..."

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v stockfish &> /dev/null; then
        echo "Stockfish已安装: $(stockfish --version)"
    else
        echo "尝试安装Stockfish..."
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y stockfish
        elif command -v yum &> /dev/null; then
            # CentOS/Fedora
            sudo yum install -y stockfish
        elif command -v pacman &> /dev/null; then
            # Arch Linux
            sudo pacman -S stockfish
        else
            echo "警告: 无法自动安装Stockfish"
            echo "请手动从 https://stockfishchess.org/download/ 下载"
        fi
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        if brew list stockfish &> /dev/null; then
            echo "Stockfish已安装"
        else
            echo "通过Homebrew安装Stockfish..."
            brew install stockfish
        fi
    else
        echo "警告: 未找到Homebrew"
        echo "请手动安装Stockfish: brew install stockfish"
    fi
else
    echo "警告: 不支持的操作系统: $OSTYPE"
    echo "请手动安装Stockfish"
fi

# 验证安装
echo ""
echo "验证安装..."

# 测试Python模块
echo "测试Python模块..."
python3 -c "import cv2; print('✓ OpenCV')"
python3 -c "import numpy; print('✓ NumPy')"
python3 -c "import pyautogui; print('✓ PyAutoGUI')"
python3 -c "import chess; print('✓ Python-Chess')"

# 测试Stockfish
if command -v stockfish &> /dev/null; then
    echo "✓ Stockfish: $(stockfish --version)"
else
    echo "⚠ Stockfish未安装或不在PATH中"
fi

# 创建必要的目录
echo ""
echo "创建必要的目录..."
mkdir -p models
mkdir -p logs

# 设置权限
chmod +x chess_bot.py
chmod +x piece_recognizer.py
chmod +x calibration_tool.py
chmod +x test.py

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "下一步操作:"
echo "1. 运行校准工具: python3 calibration_tool.py"
echo "2. 开始对弈: python3 chess_bot.py"
echo "3. 运行测试: python3 test.py --all"
echo ""
echo "如需帮助，请查看 README.md"
echo ""
