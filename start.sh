#!/bin/bash
# Chess Bot 一键启动脚本

echo "======================================"
echo "  Chess Bot 启动脚本"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
missing_deps=()

python3 -c "import cv2" 2>/dev/null || missing_deps+=("opencv-python")
python3 -c "import numpy" 2>/dev/null || missing_deps+=("numpy")
python3 -c "import torch" 2>/dev/null || missing_deps+=("torch")
python3 -c "import pyautogui" 2>/dev/null || missing_deps+=("pyautogui")
python3 -c "import mss" 2>/dev/null || missing_deps+=("mss")
python3 -c "import chess" 2>/dev/null || missing_deps+=("chess")

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "⚠️  缺少依赖: ${missing_deps[*]}"
    echo "正在安装..."
    pip install "${missing_deps[@]}"
    if [ $? -ne 0 ]; then
        echo "❌ 安装失败，请手动运行: pip install ${missing_deps[*]}"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 所有依赖已安装"
fi

echo ""
echo "======================================"
echo "  请选择启动模式："
echo "======================================"
echo "1. 快速修复版 (推荐新手) ⭐"
echo "   - 识别阈值更宽松"
echo "   - 更容易检测到棋子"
echo ""
echo "2. 完整对弈版"
echo "   - 完整的AI对弈功能"
echo "   - 支持自动移动棋子"
echo "   - 需要国际象棋引擎"
echo ""
echo "3. 调试工具"
echo "   - 诊断识别问题"
echo "   - 查看详细分析"
echo ""
echo "4. 查看启动指南"
echo ""
echo "======================================"

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动快速修复版..."
        echo ""
        python3 QUICK_FIX.py
        ;;
    2)
        echo ""
        echo "🚀 启动完整对弈版..."
        echo ""
        # 检查引擎
        if ! command -v stockfish &> /dev/null && [ ! -f "lc0.exe" ]; then
            echo "⚠️  未找到国际象棋引擎"
            echo "   建议: sudo apt-get install stockfish"
            echo "   继续运行吗? (y/n)"
            read -r confirm
            if [ "$confirm" != "y" ]; then
                exit 0
            fi
        fi
        python3 chess_bot.py
        ;;
    3)
        echo ""
        echo "🔧 启动调试工具..."
        echo ""
        python3 debug_recognition.py
        ;;
    4)
        echo ""
        echo "📚 查看启动指南..."
        echo ""
        cat STARTUP_GUIDE.md
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
