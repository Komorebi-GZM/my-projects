"""
棋谱记录器 - 对局和走子的持久化存储
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

from ..board.types import Side
from ..infra.database import DatabaseManager, GameRecord, MoveRecord

logger = logging.getLogger(__name__)


class GameRecorder:
    """
    棋谱记录器 - 管理对局和走子的持久化

    职责:
    - 创建/保存对局记录
    - 记录每步走子
    - 导出棋谱为 JSON 格式
    - 加载历史棋谱
    """

    def __init__(self, db_path: str | Path = "./data/chess.db"):
        self._db = DatabaseManager(db_path=db_path)
        self._current_game_id: int | None = None
        self._move_count: int = 0

    def start_game(self, fen_initial: str, player_side: Side = "red") -> int:
        """
        开始新对局

        Args:
            fen_initial: 初始 FEN
            player_side: 玩家执子方

        Returns:
            对局 ID
        """
        game = GameRecord(
            fen_initial=fen_initial,
            result="ongoing",
            player_side=player_side,
            start_time=datetime.now(),
            total_moves=0,
        )
        self._current_game_id = self._db.save_game(game)
        self._move_count = 0
        logger.info(f"开始新对局: {self._current_game_id}")
        return self._current_game_id

    def record_move(
        self,
        move_ucci: str,
        fen_before: str,
        side: Side,
        move_number: int | None = None,
    ) -> int:
        """
        记录一步走子

        Args:
            move_ucci: UCCI 格式走子
            fen_before: 走子前的 FEN
            side: 走子方 (red/black)
            move_number: 走子序号，默认自动递增

        Returns:
            走子记录 ID
        """
        if self._current_game_id is None:
            logger.warning("没有活动的对局，先调用 start_game")
            return 0

        if move_number is None:
            self._move_count += 1
            move_number = self._move_count

        move = MoveRecord(
            game_id=self._current_game_id,
            move_number=move_number,
            fen_before=fen_before,
            move_ucci=move_ucci,
            side=side,
            timestamp=datetime.now(),
        )
        move_id = self._db.save_move(move)
        logger.info(f"记录走子 #{move_number}: {move_ucci} ({side})")
        return move_id

    def end_game(self, result: Literal["red_win", "black_win", "draw", "ongoing"] = "ongoing") -> None:
        """
        结束对局

        Args:
            result: 对局结果
        """
        if self._current_game_id is None:
            logger.warning("没有活动的对局")
            return

        game = self._db.load_game(self._current_game_id)
        if game:
            game.result = result
            game.end_time = datetime.now()
            game.total_moves = self._move_count
            self._db.save_game(game)

        logger.info(f"对局结束: {result}, 总步数: {self._move_count}")
        self._current_game_id = None
        self._move_count = 0

    def get_game_moves(self, game_id: int) -> list[MoveRecord]:
        """
        获取对局的走子历史

        Args:
            game_id: 对局 ID

        Returns:
            走子记录列表
        """
        return self._db.get_game_moves(game_id)

    def get_all_games(self) -> list[GameRecord]:
        """
        获取所有对局记录

        Returns:
            对局记录列表（按时间倒序）
        """
        return self._db.get_all_games()

    def load_game(self, game_id: int) -> tuple[GameRecord | None, list[MoveRecord]]:
        """
        加载对局

        Args:
            game_id: 对局 ID

        Returns:
            (对局记录, 走子历史) 元组
        """
        game = self._db.load_game(game_id)
        moves = self._db.get_game_moves(game_id) if game else []
        return game, moves

    def export_to_json(self, game_id: int) -> dict:
        """
        导出棋谱为 JSON

        Args:
            game_id: 对局 ID

        Returns:
            棋谱 JSON 字典
        """
        game, moves = self.load_game(game_id)
        if not game:
            return {}

        return {
            "game_id": game.id,
            "fen_initial": game.fen_initial,
            "result": game.result,
            "player_side": game.player_side,
            "start_time": game.start_time.isoformat() if isinstance(game.start_time, datetime) else game.start_time,
            "end_time": game.end_time.isoformat() if isinstance(game.end_time, datetime) else game.end_time,
            "total_moves": game.total_moves,
            "moves": [
                {
                    "number": m.move_number,
                    "ucci": m.move_ucci,
                    "fen_before": m.fen_before,
                    "side": m.side,
                    "timestamp": m.timestamp.isoformat() if isinstance(m.timestamp, datetime) else m.timestamp,
                }
                for m in moves
            ],
        }

    def export_to_file(self, game_id: int, file_path: str | Path) -> bool:
        """
        导出棋谱到文件

        Args:
            game_id: 对局 ID
            file_path: 文件路径

        Returns:
            是否成功
        """
        try:
            data = self.export_to_json(game_id)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"棋谱已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出棋谱失败: {e}")
            return False

    def import_from_file(self, file_path: str | Path) -> int | None:
        """
        从文件导入棋谱

        Args:
            file_path: 文件路径

        Returns:
            导入的对局 ID，失败返回 None
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # 创建对局记录
            game = GameRecord(
                fen_initial=data.get("fen_initial", ""),
                result=data.get("result", "ongoing"),
                player_side=data.get("player_side", "red"),
                start_time=datetime.fromisoformat(data["start_time"]) if "start_time" in data else datetime.now(),
                end_time=datetime.fromisoformat(data["end_time"]) if "end_time" in data else None,
                total_moves=data.get("total_moves", 0),
            )
            game_id = self._db.save_game(game)

            # 导入走子记录
            for move_data in data.get("moves", []):
                move = MoveRecord(
                    game_id=game_id,
                    move_number=move_data["number"],
                    fen_before=move_data.get("fen_before", ""),
                    move_ucci=move_data["ucci"],
                    side=move_data.get("side", "red"),
                    timestamp=datetime.fromisoformat(move_data["timestamp"])
                    if "timestamp" in move_data
                    else datetime.now(),
                )
                self._db.save_move(move)

            logger.info(f"棋谱已从文件导入: {file_path}")
            return game_id
        except Exception as e:
            logger.error(f"导入棋谱失败: {e}")
            return None

    def close(self) -> None:
        """关闭数据库连接"""
        self._db.close()
