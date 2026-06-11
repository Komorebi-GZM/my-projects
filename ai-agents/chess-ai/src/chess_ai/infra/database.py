"""
数据库管理器 - SQLite 对局记录 CRUD
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from ..board.types import Side


@dataclass
class GameRecord:
    """对局记录数据模型"""

    fen_initial: str = ""
    result: Literal["red_win", "black_win", "draw", "ongoing"] = "ongoing"
    player_side: Side = "red"
    id: int | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    total_moves: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "fen_initial": self.fen_initial,
            "result": self.result,
            "start_time": self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            "end_time": self.end_time.isoformat() if isinstance(self.end_time, datetime) else self.end_time,
            "player_side": self.player_side,
            "total_moves": self.total_moves,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameRecord:
        start_time = data.get("start_time")
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        end_time = data.get("end_time")
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        return cls(
            id=data.get("id"),
            fen_initial=data.get("fen_initial", ""),
            result=data.get("result", "ongoing"),
            start_time=start_time or datetime.now(),
            end_time=end_time,
            player_side=data.get("player_side", "red"),
            total_moves=data.get("total_moves", 0),
        )


@dataclass
class MoveRecord:
    """走子记录数据模型"""

    game_id: int
    move_number: int
    fen_before: str = ""
    move_ucci: str = ""
    side: Side = "red"
    id: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "game_id": self.game_id,
            "move_number": self.move_number,
            "fen_before": self.fen_before,
            "move_ucci": self.move_ucci,
            "side": self.side,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoveRecord:
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        return cls(
            id=data.get("id"),
            game_id=data.get("game_id") or 0,
            move_number=data.get("move_number") or 0,
            fen_before=data.get("fen_before", ""),
            move_ucci=data.get("move_ucci", ""),
            side=data.get("side", "red"),
            timestamp=timestamp or datetime.now(),
        )


class DatabaseManager:
    """
    SQLite 数据库管理器

    管理对局记录和走子历史的持久化存储
    """

    def __init__(self, db_path: str | Path = "./data/chess.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接（延迟初始化）"""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_tables(self) -> None:
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 对局记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fen_initial TEXT NOT NULL,
                result TEXT NOT NULL DEFAULT 'ongoing',
                start_time TEXT NOT NULL,
                end_time TEXT,
                player_side TEXT NOT NULL DEFAULT 'red',
                total_moves INTEGER NOT NULL DEFAULT 0
            )
        """)

        # 走子记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                move_number INTEGER NOT NULL,
                fen_before TEXT NOT NULL,
                move_ucci TEXT NOT NULL,
                side TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
            )
        """)

        # 检查点记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL UNIQUE,
                state_json TEXT NOT NULL,
                fen_history TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_moves_game_id ON moves (game_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON checkpoints (thread_id)")

        conn.commit()

    def save_game(self, game: GameRecord) -> int:
        """
        保存对局记录

        Args:
            game: 对局记录

        Returns:
            新对局的 ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if game.id is None:
            cursor.execute(
                """
                INSERT INTO games (fen_initial, result, start_time, end_time, player_side, total_moves)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    game.fen_initial,
                    game.result,
                    game.start_time.isoformat() if isinstance(game.start_time, datetime) else game.start_time,
                    game.end_time.isoformat() if isinstance(game.end_time, datetime) else game.end_time,
                    game.player_side,
                    game.total_moves,
                ),
            )
            game.id = cursor.lastrowid
        else:
            cursor.execute(
                """
                UPDATE games SET
                    result = ?, end_time = ?, total_moves = ?
                WHERE id = ?
            """,
                (game.result, game.end_time, game.total_moves, game.id),
            )

        conn.commit()
        return game.id if game.id is not None else 0

    def load_game(self, game_id: int) -> GameRecord | None:
        """
        加载对局记录

        Args:
            game_id: 对局 ID

        Returns:
            对局记录，不存在则返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return GameRecord(
            id=row["id"],
            fen_initial=row["fen_initial"],
            result=row["result"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            player_side=row["player_side"],
            total_moves=row["total_moves"],
        )

    def get_all_games(self) -> list[GameRecord]:
        """获取所有对局记录（按时间倒序）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM games ORDER BY start_time DESC")
        rows = cursor.fetchall()

        return [
            GameRecord(
                id=row["id"],
                fen_initial=row["fen_initial"],
                result=row["result"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                player_side=row["player_side"],
                total_moves=row["total_moves"],
            )
            for row in rows
        ]

    def save_move(self, move: MoveRecord) -> int:
        """
        保存走子记录

        Args:
            move: 走子记录

        Returns:
            新走子记录的 ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO moves (game_id, move_number, fen_before, move_ucci, side, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                move.game_id,
                move.move_number,
                move.fen_before,
                move.move_ucci,
                move.side,
                move.timestamp.isoformat() if isinstance(move.timestamp, datetime) else move.timestamp,
            ),
        )

        move.id = cursor.lastrowid
        conn.commit()
        return move.id if move.id is not None else 0

    def get_game_moves(self, game_id: int) -> list[MoveRecord]:
        """
        获取对局的走子历史

        Args:
            game_id: 对局 ID

        Returns:
            按走子序号排序的走子记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM moves WHERE game_id = ? ORDER BY move_number", (game_id,))
        rows = cursor.fetchall()

        return [
            MoveRecord(
                id=row["id"],
                game_id=row["game_id"],
                move_number=row["move_number"],
                fen_before=row["fen_before"],
                move_ucci=row["move_ucci"],
                side=row["side"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
            )
            for row in rows
        ]

    def save_checkpoint(self, thread_id: str, state_json: str, fen_history: list[str] | None = None) -> None:
        """
        保存检查点

        Args:
            thread_id: 对局唯一标识
            state_json: 状态 JSON 字符串
            fen_history: FEN 历史列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT OR REPLACE INTO checkpoints (thread_id, state_json, fen_history, created_at, updated_at)
            VALUES (?, ?, ?, COALESCE((SELECT created_at FROM checkpoints WHERE thread_id = ?), ?), ?)
        """,
            (thread_id, state_json, json.dumps(fen_history or []), thread_id, now, now),
        )

        conn.commit()

    def load_checkpoint(self, thread_id: str) -> tuple[str, list[str]] | None:
        """
        加载检查点

        Args:
            thread_id: 对局唯一标识

        Returns:
            (state_json, fen_history) 元组，不存在则返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT state_json, fen_history FROM checkpoints WHERE thread_id = ?", (thread_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return row["state_json"], json.loads(row["fen_history"] or "[]")

    def delete_checkpoint(self, thread_id: str) -> bool:
        """
        删除检查点

        Args:
            thread_id: 对局唯一标识

        Returns:
            是否删除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        conn.commit()

        return cursor.rowcount > 0

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
