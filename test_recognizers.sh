#!/bin/bash
# 测试所有识别器并对比结果

echo "======================================"
echo "  Chess Bot 识别器测试工具"
echo "======================================"
echo ""

cd /home/ubuntu/workspace/chess-bot

# 检查文件是否存在
if [ ! -f "QUICK_FIX.py" ]; then
    echo "❌ 未找到 QUICK_FIX.py"
    exit 1
fi

if [ ! -f "ULTRA_LOOSE.py" ]; then
    echo "❌ 未找到 ULTRA_LOOSE.py"
    exit 1
fi

if [ ! -f "COLOR_MATCH.py" ]; then
    echo "❌ 未找到 COLOR_MATCH.py"
    exit 1
fi

echo "请选择测试模式："
echo "1. 快速测试 (选择一个识别器)"
echo "2. 完整测试 (所有识别器，自动对比)"
echo "3. 仅对比已有结果"
echo ""
read -p "选择 (1-3): " mode

case $mode in
    1)
        echo ""
        echo "请选择识别器："
        echo "1. QUICK_FIX.py (基础识别，中等准确度)"
        echo "2. ULTRA_LOOSE.py (超宽松，高识别率)"
        echo "3. COLOR_MATCH.py (颜色匹配，适合高对比)"
        echo ""
        read -p "选择 (1-3): " recognizer

        case $recognizer in
            1)
                echo ""
                echo "======================================"
                echo "  运行: QUICK_FIX.py"
                echo "======================================"
                python3 QUICK_FIX.py
                ;;
            2)
                echo ""
                echo "======================================"
                echo "  运行: ULTRA_LOOSE.py"
                echo "======================================"
                python3 ULTRA_LOOSE.py
                ;;
            3)
                echo ""
                echo "======================================"
                echo "  运行: COLOR_MATCH.py"
                echo "======================================"
                python3 COLOR_MATCH.py
                ;;
            *)
                echo "❌ 无效选择"
                exit 1
                ;;
        esac
        ;;

    2)
        echo ""
        echo "======================================"
        echo "  完整测试模式"
        echo "======================================"
        echo ""
        echo "这将依次运行所有识别器，请按照提示操作："
        echo ""
        read -p "按Enter开始..."

        # 运行基础识别器
        echo ""
        echo "======================================"
        echo "  测试 1/3: QUICK_FIX.py (基础识别)"
        echo "======================================"
        python3 QUICK_FIX.py
        echo ""
        read -p "按Enter继续下一个识别器..."

        # 运行超宽松识别器
        echo ""
        echo "======================================"
        echo "  测试 2/3: ULTRA_LOOSE.py (超宽松)"
        echo "======================================"
        python3 ULTRA_LOOSE.py
        echo ""
        read -p "按Enter继续下一个识别器..."

        # 运行颜色匹配识别器
        echo ""
        echo "======================================"
        echo "  测试 3/3: COLOR_MATCH.py (颜色匹配)"
        echo "======================================"
        python3 COLOR_MATCH.py

        # 对比结果
        echo ""
        echo "======================================"
        echo "  测试完成！"
        echo "======================================"
        echo ""
        echo "识别结果对比："
        echo "--------------------------------------"
        echo "1. QUICK_FIX.py:"
        if [ -f "recognized_fen.txt" ]; then
            echo "   FEN: $(cat recognized_fen.txt)"
            python3 -c "
import chess
try:
    board = chess.Board(open('recognized_fen.txt').read().strip())
    pieces = len(list(board.piece_map()))
    print(f'   棋子数: {pieces}/64')
except:
    print('   FEN无效')
"
        else
            echo "   未找到结果"
        fi
        echo ""
        echo "2. ULTRA_LOOSE.py:"
        if [ -f "recognized_fen_ultra.txt" ]; then
            echo "   FEN: $(cat recognized_fen_ultra.txt)"
            python3 -c "
import chess
try:
    board = chess.Board(open('recognized_fen_ultra.txt').read().strip())
    pieces = len(list(board.piece_map()))
    print(f'   棋子数: {pieces}/64')
except:
    print('   FEN无效')
"
        else
            echo "   未找到结果"
        fi
        echo ""
        echo "3. COLOR_MATCH.py:"
        if [ -f "recognized_fen_color.txt" ]; then
            echo "   FEN: $(cat recognized_fen_color.txt)"
            python3 -c "
import chess
try:
    board = chess.Board(open('recognized_fen_color.txt').read().strip())
    pieces = len(list(board.piece_map()))
    print(f'   棋子数: {pieces}/64')
except:
    print('   FEN无效')
"
        else
            echo "   未找到结果"
        fi
        echo "--------------------------------------"
        echo ""
        echo "💡 提示："
        echo "  1. 使用 get_fen.py 验证每个FEN"
        echo "  2. 选择识别效果最好的识别器"
        echo "  3. 如果都不准确，使用FEN手动输入"
        ;;

    3)
        echo ""
        echo "======================================"
        echo "  对比已有结果"
        echo "======================================"
        echo ""

        found=false

        if [ -f "recognized_fen.txt" ]; then
            echo "1. QUICK_FIX.py:"
            echo "   FEN: $(cat recognized_fen.txt)"
            python3 -c "
import chess
try:
    board = chess.Board(open('recognized_fen.txt').read().strip())
    pieces = len(list(board.piece_map()))
    print(f'   棋子数: {pieces}/64')
except Exception as e:
    print(f'   错误: {e}')
"
            echo ""
            found=true
        fi

        if [ -f "recognized_fen_ultra.txt" ]; then
            echo "2. ULTRA_LOOSE.py:"
            echo "   FEN: $(cat recognized_fen_ultra.txt)"
            python3 -c "
import chess
try:
    board = chess.Board(open('recognized_fen_ultra.txt').read().strip())
    pieces = len(list(board.piece_map()))
    print(f'   棋子数: {pieces}/64')
except Exception as e:
    print(f'   错误: {e}')
"
            echo ""
            found=true
        fi

        if [ -f "recognized_fen_color.txt" ]; then
            echo "3. COLOR_MATCH.py:"
            echo "   FEN: $(cat recognized_fen_color.txt)"
            python3 -c "
import chess
try:
    board = chess.Board(open('recognized_fen_color.txt').read().strip())
    pieces = len(list(board.piece_map()))
    print(f'   棋子数: {pieces}/64')
except Exception as e:
    print(f'   错误: {e}')
"
            echo ""
            found=true
        fi

        if [ "$found" = false ]; then
            echo "❌ 未找到任何识别结果"
            echo "   请先运行识别器"
        else
            echo "======================================"
            echo ""
            echo "💡 提示："
            echo "  1. 运行 get_fen.py 验证每个FEN"
            echo "  2. 选择识别效果最好的识别器"
        fi
        ;;

    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "  完成！"
echo "======================================"
