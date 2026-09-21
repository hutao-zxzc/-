@echo off
REM 国际象棋自动对弈机器人 - Windows安装脚本

echo ==========================================
echo 国际象棋自动对弈机器人 - 安装程序
echo ==========================================
echo.

REM 检查Python版本
echo 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查pip
echo 检查pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到pip
    pause
    exit /b 1
)

REM 安装Python依赖
echo.
echo 安装Python依赖...
pip install -r requirements.txt

REM 检查Stockfish
echo.
echo 检查Stockfish引擎...
where stockfish >nul 2>&1
if errorlevel 1 (
    echo 警告: 未找到Stockfish
    echo 请从 https://stockfishchess.org/download/ 下载并解压到项目目录
    echo 或者将Stockfish添加到系统PATH
    echo.
    set /p STOCKFISH_PATH="请输入Stockfish可执行文件路径 (直接回车跳过): "
    if not "%STOCKFISH_PATH%"=="" (
        echo STOCKFISH_PATH=%STOCKFISH_PATH% >> .env
        echo Stockfish路径已保存到 .env 文件
    )
) else (
    echo Stockfish已安装
    stockfish --version
)

REM 验证安装
echo.
echo 验证安装...
echo 测试Python模块...
python -c "import cv2; print('✓ OpenCV')" 2>nul || echo ✗ OpenCV安装失败
python -c "import numpy; print('✓ NumPy')" 2>nul || echo ✗ NumPy安装失败
python -c "import pyautogui; print('✓ PyAutoGUI')" 2>nul || echo ✗ PyAutoGUI安装失败
python -c "import chess; print('✓ Python-Chess')" 2>nul || echo ✗ Python-Chess安装失败

REM 创建必要的目录
echo.
echo 创建必要的目录...
if not exist models mkdir models
if not exist logs mkdir logs

echo.
echo ==========================================
echo 安装完成！
echo ==========================================
echo.
echo 下一步操作:
echo 1. 运行校准工具: python calibration_tool.py
echo 2. 开始对弈: python chess_bot.py
echo 3. 运行测试: python test.py --all
echo.
echo 如需帮助，请查看 README.md
echo.
pause
