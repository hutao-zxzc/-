#!/usr/bin/env python3
"""
快速修复脚本 - 自动修复 chess_bot.py 中的 rank_index 错误
"""

import re
from pathlib import Path

def fix_file(filepath):
    """修复文件中的 rank_index 和 file_index"""
    print(f"正在修复: {filepath}")

    # 读取文件
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换错误的函数调用
    original_content = content

    # rank_index -> square_rank
    content = re.sub(r'chess\.rank_index\(', 'chess.square_rank(', content)

    # file_index -> square_file
    content = re.sub(r'chess\.file_index\(', 'chess.square_file(', content)

    # 检查是否有修改
    if content != original_content:
        # 备份原文件
        backup_path = str(filepath) + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  备份已保存: {backup_path}")

        # 保存修复后的文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 修复完成")
        return True
    else:
        print(f"  ℹ️  文件已经正确，无需修复")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("  chess_bot.py 自动修复脚本")
    print("=" * 60)

    # 查找当前目录
    current_dir = Path(__file__).parent
    print(f"\n当前目录: {current_dir}")

    # 需要修复的文件
    files_to_fix = [
        'chess_bot.py',
        'screen_recognition_bot.py',
    ]

    fixed_count = 0

    for filename in files_to_fix:
        filepath = current_dir / filename
        if filepath.exists():
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"  ⚠️  文件不存在: {filename}")

    # 总结
    print("\n" + "=" * 60)
    if fixed_count > 0:
        print(f"  ✅ 已修复 {fixed_count} 个文件")
        print("\n现在可以运行:")
        print("  python chess_bot.py")
        print("  或")
        print("  python screen_recognition_bot.py")
    else:
        print("  ℹ️  没有需要修复的文件")
        print("\n你的文件已经是正确的版本了")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 修复过程中出错: {e}")
        import traceback
        traceback.print_exc()
