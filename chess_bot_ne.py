"""
Chess Bot - 全自动国际象棋机器人 (Stockfish 19 + 合法移动验证)
修复:
1. 添加移动历史记录
2. 严格验证所有移动合法性
3. 改进对手移动检测
4. 添加移动确认机制
"""

import cv2
import numpy as np
import pyautogui
import chess
import chess.engine
import time
import os
from datetime import datetime

try:
    import mss

    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class ChessBot:
    def __init__(self):
        self.board_region = None
        self.square_size = 0
        self.board = chess.Board()
        self.previous_board_image = None
        self.player_color = chess.WHITE
        self.sct = None
        self.engine = None
        self.move_history = []  # 移动历史记录
        self.consecutive_errors = 0  # 连续错误计数

        # Stockfish 路径
        self.stockfish_path = r"C:\Users\12991\Desktop\stockfish\stockfish-windows-x86-64-universal.exe"

        if MSS_AVAILABLE:
            try:
                self.sct = mss.mss()
            except:
                self.sct = None

    def init_engine(self):
        """初始化 Stockfish 引擎"""
        try:
            if os.path.exists(self.stockfish_path):
                self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
                print(f"✓ Stockfish 引擎已加载")
                self.engine.configure({
                    "Hash": 128,
                    "Threads": 4
                })
                return True
            else:
                print(f"✗ Stockfish 路径不存在")
                return False
        except Exception as e:
            print(f"✗ 加载 Stockfish 失败: {e}")
            return False

    def capture_screen(self, region=None):
        """截取屏幕区域"""
        try:
            if MSS_AVAILABLE and self.sct:
                if region:
                    region = self.validate_region(region)
                    if not region:
                        return None
                    monitor = {
                        "left": region['left'],
                        "top": region['top'],
                        "width": region['width'],
                        "height": region['height']
                    }
                else:
                    monitor = self.sct.monitors[1]

                screenshot = self.sct.grab(monitor)
                img = np.array(screenshot)
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            else:
                if region:
                    region = self.validate_region(region)
                    if not region:
                        return None
                    screenshot = pyautogui.screenshot(region=(
                        region['left'], region['top'],
                        region['width'], region['height']
                    ))
                else:
                    screenshot = pyautogui.screenshot()
                return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def validate_region(self, region):
        """验证并修正区域坐标"""
        if not region:
            return None
        try:
            left = max(int(region.get('left', 0)), 0)
            top = max(int(region.get('top', 0)), 0)
            width = abs(int(region.get('width', 0)))
            height = abs(int(region.get('height', 0)))
            width = max(width, 100)
            height = max(height, 100)
            return {'left': left, 'top': top, 'width': width, 'height': height}
        except:
            return None

    def detect_board(self, image=None):
        """检测棋盘位置"""
        if image is None:
            image = self.capture_screen()
        if image is None:
            return None

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            best_rect = None
            best_area = 0

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                if area > best_area and w > 200 and h > 200:
                    aspect_ratio = w / float(h)
                    if 0.8 <= aspect_ratio <= 1.2:
                        best_area = area
                        best_rect = (x, y, w, h)

            if best_rect:
                x, y, w, h = best_rect
                self.board_region = {'left': x, 'top': y, 'width': w, 'height': h}
                self.square_size = w // 8
                return self.board_region
        except Exception as e:
            print(f"棋盘检测失败: {e}")
        return None

    def manual_select_board(self):
        """手动框选棋盘区域"""
        print("\n=== 手动框选棋盘 ===")
        print("请将鼠标移到棋盘【左上角】，按 Enter 确认")
        input()
        x1, y1 = pyautogui.position()

        print("请将鼠标移到棋盘【右下角】，按 Enter 确认")
        input()
        x2, y2 = pyautogui.position()

        left = max(min(x1, x2), 0)
        top = max(min(y1, y2), 0)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if width < 100 or height < 100:
            print("区域太小，请重新选择")
            return self.manual_select_board()

        self.board_region = {'left': left, 'top': top, 'width': width, 'height': height}
        self.square_size = width // 8
        print(f"✓ 已选择区域: {self.board_region}")
        return self.board_region

    def get_square_image(self, board_image, square_name):
        """获取单个格子的图像"""
        if not self.board_region or not self.square_size:
            return None

        try:
            file = ord(square_name[0]) - ord('a')
            rank = int(square_name[1]) - 1

            x = file * self.square_size
            y = (7 - rank) * self.square_size

            # 确保不超出图像边界
            h, w = board_image.shape[:2]
            if x + self.square_size > w or y + self.square_size > h:
                return None

            square_img = board_image[y:y + self.square_size, x:x + self.square_size]
            return square_img
        except:
            return None

    def detect_move_by_comparison(self, old_image, new_image):
        """改进的对手移动检测"""
        if old_image is None or new_image is None:
            return None

        try:
            # 确保图像大小一致
            if old_image.shape != new_image.shape:
                new_image = cv2.resize(new_image, (old_image.shape[1], old_image.shape[0]))

            diff = cv2.absdiff(old_image, new_image)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # 使用更高的阈值减少误报
            _, thresh = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)

            changed_squares = []
            change_scores = {}

            for square in chess.SQUARES:
                square_name = chess.square_name(square)
                old_sq = self.get_square_image(old_image, square_name)
                new_sq = self.get_square_image(new_image, square_name)

                if old_sq is not None and new_sq is not None:
                    # 确保大小一致
                    if old_sq.shape != new_sq.shape:
                        new_sq = cv2.resize(new_sq, (old_sq.shape[1], old_sq.shape[0]))

                    sq_diff = cv2.absdiff(old_sq, new_sq)
                    change_score = np.mean(sq_diff)
                    change_scores[square_name] = change_score

                    # 提高阈值到50减少误报
                    if change_score > 50:
                        changed_squares.append(square_name)

            print(f"变化的格子: {changed_squares}")

            # 必须检测到至少2个变化（起始格和目标格）
            if len(changed_squares) < 2:
                return None

            # 在合法移动中查找匹配
            best_move = None
            best_score = float('inf')

            for move in self.board.legal_moves:
                uci = move.uci()
                from_sq = uci[:2]
                to_sq = uci[2:4]

                # 检查起始格和目标格是否都变化
                if from_sq in changed_squares and to_sq in changed_squares:
                    # 计算这个移动的总变化分数
                    score = change_scores.get(from_sq, 0) + change_scores.get(to_sq, 0)
                    if score < best_score:
                        best_score = score
                        best_move = uci

            return best_move

        except Exception as e:
            print(f"检测移动失败: {e}")
            return None

    def get_square_position(self, square_name):
        """获取棋格在屏幕上的位置"""
        if not self.board_region or not self.square_size:
            return None
        try:
            file = ord(square_name[0]) - ord('a')
            rank = int(square_name[1]) - 1
            x = self.board_region['left'] + file * self.square_size + self.square_size // 2
            y = self.board_region['top'] + (7 - rank) * self.square_size + self.square_size // 2
            return (x, y)
        except:
            return None

    def make_move(self, move_uci):
        """执行移动 - 带验证"""
        try:
            # 验证移动合法性
            move = chess.Move.from_uci(move_uci)
            if move not in self.board.legal_moves:
                print(f"✗ 非法移动: {move_uci}")
                print(f"当前合法移动: {[m.uci() for m in list(self.board.legal_moves)[:10]]}...")
                return False

            from_sq = move_uci[:2]
            to_sq = move_uci[2:4]

            from_pos = self.get_square_position(from_sq)
            to_pos = self.get_square_position(to_sq)

            if from_pos and to_pos:
                print(f"执行移动: {from_sq} -> {to_sq}")

                # 点击起始位置
                pyautogui.click(from_pos[0], from_pos[1])
                time.sleep(0.3)

                # 点击目标位置
                pyautogui.click(to_pos[0], to_pos[1])
                time.sleep(0.3)

                # 处理升变
                if len(move_uci) > 4:
                    promotion = move_uci[4]
                    print(f"升变为: {promotion}")
                    time.sleep(0.5)

                # 记录移动
                self.move_history.append({
                    'move': move_uci,
                    'turn': 'white' if self.board.turn == chess.WHITE else 'black',
                    'time': datetime.now().strftime('%H:%M:%S')
                })

                return True
        except Exception as e:
            print(f"✗ 执行移动失败: {e}")
        return False

    def get_ai_move(self):
        """获取AI移动 - 严格合法"""
        legal_moves = list(self.board.legal_moves)

        if not legal_moves:
            print("没有合法移动")
            return None

        if self.engine:
            try:
                # 使用 Stockfish 计算
                result = self.engine.play(
                    self.board,
                    chess.engine.Limit(time=1.0, depth=20)
                )
                move = result.move

                # 双重验证
                if move in legal_moves:
                    print(f"Stockfish 选择: {move.uci()}")
                    return move.uci()
                else:
                    print("Stockfish 返回非法移动，使用备用")
            except Exception as e:
                print(f"Stockfish 错误: {e}")

        # 备用：随机选择合法移动
        import random
        move = random.choice(legal_moves)
        print(f"随机选择: {move.uci()}")
        return move.uci()

    def verify_and_update_board(self, move_uci):
        """验证移动并更新棋盘状态"""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                print(f"✗ 移动 {move_uci} 不合法")
                return False
        except:
            print(f"✗ 移动格式错误: {move_uci}")
            return False

    def wait_for_opponent_move(self, timeout=60):
        """等待对手移动 - 改进版"""
        print("等待对手下棋...")
        start_time = time.time()

        self.previous_board_image = self.capture_board_region()
        stable_count = 0  # 稳定帧计数

        while time.time() - start_time < timeout:
            time.sleep(0.5)

            current_image = self.capture_board_region()
            if current_image is None:
                continue

            move = self.detect_move_by_comparison(self.previous_board_image, current_image)

            if move:
                # 验证移动合法性
                if self.verify_and_update_board(move):
                    print(f"✓ 检测到对手移动: {move}")
                    self.previous_board_image = current_image
                    self.consecutive_errors = 0  # 重置错误计数
                    return move
                else:
                    print(f"✗ 检测到的移动 {move} 不合法，继续等待...")
                    self.consecutive_errors += 1

                    # 连续错误太多，请求手动输入
                    if self.consecutive_errors >= 3:
                        print("连续检测失败，请手动输入")
                        return None
            else:
                stable_count += 1
                # 每10秒提示一次
                if stable_count % 20 == 0:
                    print(f"已等待 {stable_count // 2} 秒...")

        print("未检测到对手移动，超时")
        return None

    def capture_board_region(self):
        """只截取棋盘区域"""
        if not self.board_region:
            return None
        return self.capture_screen(self.board_region)

    def print_board_state(self):
        """打印当前棋盘状态"""
        print("\n当前棋盘:")
        print(self.board)
        print(f"FEN: {self.board.fen()}")
        print(f"轮到: {'白方' if self.board.turn == chess.WHITE else '黑方'}")

    def print_move_history(self):
        """打印移动历史"""
        print("\n移动历史:")
        for i, record in enumerate(self.move_history, 1):
            print(f"{i}. {record['turn']}: {record['move']} ({record['time']})")

    def play_auto(self):
        """全自动游戏循环 - 改进版"""
        print("\n" + "=" * 60)
        print("=== 全自动模式 (Stockfish 19 + 合法验证) ===")
        print("=" * 60)
        print("改进:")
        print("1. 严格验证所有移动合法性")
        print("2. 记录完整移动历史")
        print("3. 改进对手移动检测")
        print("4. 连续错误保护机制")
        print("=" * 60 + "\n")

        # 初始化引擎
        self.init_engine()

        move_count = 0

        try:
            while not self.board.is_game_over():
                print(f"\n{'=' * 60}")
                print(f"--- 第 {move_count + 1} 回合 ---")
                self.print_board_state()

                if self.board.turn == self.player_color:
                    # AI回合
                    print("\n[AI思考中...]")

                    ai_move = self.get_ai_move()
                    if ai_move:
                        # 执行移动
                        if self.make_move(ai_move):
                            # 验证并更新棋盘
                            if self.verify_and_update_board(ai_move):
                                move_count += 1
                                print("✓ AI移动完成")
                                self.consecutive_errors = 0
                            else:
                                print("✗ 移动验证失败")
                                break
                        else:
                            print("✗ 执行移动失败")
                            break
                    else:
                        print("没有合法移动")
                        break
                else:
                    # 对手回合
                    print("\n[等待对手...]")
                    opponent_move = self.wait_for_opponent_move()

                    if opponent_move:
                        print(f"✓ 对手移动: {opponent_move}")
                    else:
                        # 手动输入后备
                        print("\n未检测到对手移动")
                        self.print_board_state()
                        manual = input("请输入对手移动 (如e2e4) 或输入 'skip' 跳过: ").strip()

                        if manual.lower() == 'skip':
                            continue
                        elif manual:
                            if self.verify_and_update_board(manual):
                                print(f"✓ 手动输入: {manual}")
                            else:
                                print("✗ 非法移动，请重试")
                                continue

                time.sleep(1)

            # 游戏结束
            print("\n" + "=" * 60)
            print("游戏结束!")
            print(f"结果: {self.board.result()}")
            print(f"总回合数: {move_count}")
            self.print_move_history()
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\n游戏已停止")
            print(f"进行了 {move_count} 回合")
            self.print_move_history()

    def run(self):
        """主运行循环"""
        print("=" * 60)
        print("=== 国际象棋机器人 (Stockfish 19 + 合法验证) ===")
        print("=" * 60)

        print("\n请选择模式:")
        print("1. 自动识别屏幕棋盘（默认）")
        print("2. 手动框选棋盘区域")

        mode = input("\n请选择 (1/2, 默认1): ").strip() or "1"

        if mode == "1":
            print("\n=== 自动识别棋盘 ===")
            print("【重要】请在5秒内切换到浏览器页面...")
            for i in range(5, 0, -1):
                print(f"  {i}...")
                time.sleep(1)
            print("  截图中!")

            region = self.detect_board()
            if region:
                print(f"✓ 识别成功: {region}")
            else:
                print("✗ 自动识别失败，切换到手动框选...")
                self.manual_select_board()
        elif mode == "2":
            self.manual_select_board()
        else:
            print("无效选择")
            return

        print("\n=== 准备就绪 ===")
        print(f"棋盘区域: {self.board_region}")
        print(f"格子大小: {self.square_size}")

        color = input("\n选择你的颜色 (w/b, 默认w): ").strip().lower() or "w"
        self.player_color = chess.WHITE if color == "w" else chess.BLACK
        print(f"你是: {'白方' if self.player_color == chess.WHITE else '黑方'}")

        self.play_auto()

    def __del__(self):
        """清理资源"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
        if self.sct:
            try:
                self.sct.close()
            except:
                pass


def main():
    bot = ChessBot()
    bot.run()


if __name__ == "__main__":
    main()
