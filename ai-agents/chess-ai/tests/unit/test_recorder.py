"""
棋谱记录器单元测试
"""

import json
import os
import tempfile

import pytest

from chess_ai.board import Board
from chess_ai.gui.recorder import GameRecorder
from chess_ai.rules import FENSerializer


class TestGameRecorder:
    """棋谱记录器测试"""

    def test_init_creates_recorder(self):
        """初始化创建记录器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)
            assert recorder is not None
            assert recorder._current_game_id is None
            assert recorder._move_count == 0

    def test_start_game_creates_record(self):
        """开始游戏创建对局记录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")

            assert game_id > 0
            assert recorder._current_game_id == game_id
            assert recorder._move_count == 0

    def test_record_move_increments_count(self):
        """记录走子增加步数"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            recorder.start_game(initial_fen, "red")

            # 记录一步走子（不指定序号，自动递增）
            move_id = recorder.record_move("h2e2", initial_fen, "red")

            assert move_id > 0
            assert recorder._move_count == 1

    def test_record_move_auto_increment(self):
        """记录走子自动递增序号"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            recorder.start_game(initial_fen, "red")

            # 记录两步走子，不提供序号
            recorder.record_move("h2e2", initial_fen, "red")
            recorder.record_move("h9e6", initial_fen, "black")

            assert recorder._move_count == 2

    def test_end_game_updates_result(self):
        """结束游戏更新结果"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red")  # 不指定序号，自动递增

            recorder.end_game("red_win")

            # 检查数据库中的结果
            game_record = recorder._db.load_game(game_id)
            assert game_record.result == "red_win"
            assert game_record.total_moves == 1
            assert game_record.end_time is not None

    def test_get_game_moves_returns_list(self):
        """获取对局走子返回列表"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.record_move("h9e6", initial_fen, "black", 2)
            recorder.end_game("ongoing")

            moves = recorder.get_game_moves(game_id)
            assert len(moves) == 2
            assert moves[0].move_number == 1
            assert moves[0].move_ucci == "h2e2"
            assert moves[0].side == "red"
            assert moves[1].move_number == 2
            assert moves[1].move_ucci == "h9e6"
            assert moves[1].side == "black"

    def test_get_all_games_returns_list(self):
        """获取所有对局返回列表"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            # 创建两个对局
            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id1 = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.end_game("red_win")

            game_id2 = recorder.start_game(initial_fen, "black")
            recorder.record_move("h9e6", initial_fen, "black", 1)
            recorder.end_game("black_win")

            games = recorder.get_all_games()
            assert len(games) == 2
            # 应该按时间倒序
            assert games[0].id == game_id2  # 后创建的在前面
            assert games[1].id == game_id1

    def test_load_game_returns_tuple(self):
        """加载对局返回(游戏, 走子)元组"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.record_move("h9e6", initial_fen, "black", 2)
            recorder.end_game("draw")

            game, moves = recorder.load_game(game_id)

            assert game is not None
            assert game.id == game_id
            assert game.result == "draw"
            assert len(moves) == 2

    def test_load_nonexistent_game_returns_none(self):
        """加载不存在的对局返回None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            game, moves = recorder.load_game(99999)
            assert game is None
            assert moves == []

    def test_export_to_json_structure(self):
        """导出为JSON的结构正确"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.record_move("h9e6", initial_fen, "black", 2)
            recorder.end_game("red_win")

            json_data = recorder.export_to_json(game_id)

            assert json_data["game_id"] == game_id
            assert json_data["fen_initial"] == initial_fen
            assert json_data["result"] == "red_win"
            assert json_data["player_side"] == "red"
            assert len(json_data["moves"]) == 2
            assert json_data["moves"][0]["number"] == 1
            assert json_data["moves"][0]["ucci"] == "h2e2"
            assert json_data["moves"][0]["side"] == "red"
            assert json_data["moves"][1]["number"] == 2
            assert json_data["moves"][1]["ucci"] == "h9e6"
            assert json_data["moves"][1]["side"] == "black"

    def test_export_to_file_creates_file(self):
        """导出到文件创建文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.end_game("ongoing")

            file_path = os.path.join(tmpdir, "test.json")
            result = recorder.export_to_file(game_id, file_path)

            assert result is True
            assert os.path.exists(file_path)

            # 检查文件内容
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            assert data["game_id"] == game_id

    def test_import_from_file_works(self):
        """从文件导入棋谱"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            # 先创建一个对局并导出
            initial_fen = FENSerializer.to_fen(Board.create_initial())
            game_id = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.record_move("h9e6", initial_fen, "black", 2)
            recorder.end_game("draw")

            file_path = os.path.join(tmpdir, "export.json")
            recorder.export_to_file(game_id, file_path)

            # 从文件导入
            imported_id = recorder.import_from_file(file_path)
            assert imported_id is not None
            assert imported_id > 0

            # 检查导入的数据
            game, moves = recorder.load_game(imported_id)
            assert game.result == "draw"
            assert len(moves) == 2

    def test_import_nonexistent_file_returns_none(self):
        """导入不存在的文件返回None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            file_path = os.path.join(tmpdir, "nonexistent.json")
            result = recorder.import_from_file(file_path)
            assert result is None

    def test_close_method(self):
        """关闭方法不抛异常"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)
            recorder.close()  # 应该不抛异常

    def test_multiple_games_isolated(self):
        """多个对局互不影响"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            recorder = GameRecorder(db_path)

            initial_fen = FENSerializer.to_fen(Board.create_initial())

            # 第一个对局
            game_id1 = recorder.start_game(initial_fen, "red")
            recorder.record_move("h2e2", initial_fen, "red", 1)
            recorder.end_game("red_win")

            # 第二个对局
            game_id2 = recorder.start_game(initial_fen, "black")
            recorder.record_move("h9e6", initial_fen, "black", 1)
            recorder.record_move("h2e4", initial_fen, "red", 2)
            recorder.end_game("black_win")

            # 检查第一个对局
            game1, moves1 = recorder.load_game(game_id1)
            assert game1.result == "red_win"
            assert len(moves1) == 1
            assert moves1[0].move_ucci == "h2e2"

            # 检查第二个对局
            game2, moves2 = recorder.load_game(game_id2)
            assert game2.result == "black_win"
            assert len(moves2) == 2
            assert moves2[0].move_ucci == "h9e6"
            assert moves2[1].move_ucci == "h2e4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
