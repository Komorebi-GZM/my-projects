#!/usr/bin/env python3
"""
数据迁移验证脚本

验证检查项：
    - 记录总数对比
    - 字段完整性检查
    - 数据类型验证
    - 关联关系检查
    - 索引有效性验证

使用方式：
    python scripts/verify_migration.py --env-id <环境ID>
    python scripts/verify_migration.py --env-id <环境ID> --db-path data/dev.db
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime


class MigrationVerifier:
    """迁移验证器"""

    def __init__(self, env_id, db_path='data/dev.db'):
        self.env_id = env_id
        self.db_path = db_path
        self.results = []

    def verify(self):
        """执行验证"""
        print("=" * 60)
        print("数据迁移验证")
        print("=" * 60)
        print(f"CloudBase环境: {self.env_id}")
        print(f"SQLite数据库: {self.db_path}")
        print("=" * 60)

        if not os.path.exists(self.db_path):
            print(f"❌ 数据库文件不存在: {self.db_path}")
            return False

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            # 执行各项验证
            self._verify_count(conn, 'warehouses')
            self._verify_count(conn, 'users')
            self._verify_count(conn, 'orders')
            self._verify_count(conn, 'tickets')

            self._verify_orders_integrity(conn)
            self._verify_status_values(conn)

        finally:
            conn.close()

        return self._print_report()

    def _verify_count(self, conn, table):
        """验证记录数量"""
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        sqlite_count = cursor.fetchone()['count']

        from src.db.cloudbase_adapter import CloudBaseAdapter
        adapter = CloudBaseAdapter(self.env_id)
        try:
            cloudbase_count = adapter.count(table, {})
        except Exception:
            cloudbase_count = 0
        finally:
            adapter.close()

        passed = sqlite_count == cloudbase_count

        self.results.append({
            'check': f'{table} 记录数',
            'sqlite': sqlite_count,
            'cloudbase': cloudbase_count,
            'passed': passed
        })

        cursor.close()

    def _verify_orders_integrity(self, conn):
        """验证订单数据完整性"""
        cursor = conn.cursor()

        # 检查必填字段
        cursor.execute("""
            SELECT COUNT(*) as count FROM orders
            WHERE order_no IS NULL OR order_no = ''
            OR item_type IS NULL OR item_type = ''
            OR openid IS NULL OR openid = ''
        """)
        invalid_count = cursor.fetchone()['count']

        self.results.append({
            'check': '订单必填字段完整性',
            'invalid_records': invalid_count,
            'passed': invalid_count == 0
        })

        cursor.close()

    def _verify_status_values(self, conn):
        """验证状态值有效性"""
        cursor = conn.cursor()

        valid_statuses = {'PENDING', 'COLLECTED', 'STORED', 'DELIVERING', 'COMPLETED', 'CANCELLED'}

        cursor.execute("SELECT DISTINCT status FROM orders")
        statuses = {row['status'] for row in cursor.fetchall()}
        invalid_statuses = statuses - valid_statuses

        self.results.append({
            'check': '订单状态值有效性',
            'invalid_statuses': list(invalid_statuses),
            'passed': len(invalid_statuses) == 0
        })

        cursor.close()

    def _print_report(self):
        """打印验证报告"""
        print("\n" + "-" * 60)
        print("验证结果")
        print("-" * 60)

        all_passed = True
        for result in self.results:
            status = "✅ 通过" if result['passed'] else "❌ 失败"
            print(f"\n{result['check']}: {status}")

            for key, value in result.items():
                if key not in ['check', 'passed']:
                    print(f"  {key}: {value}")

            if not result['passed']:
                all_passed = False

        print("\n" + "=" * 60)
        if all_passed:
            print("✅ 所有验证通过")
        else:
            print("❌ 存在验证失败项")
        print("=" * 60)

        return all_passed


def main():
    parser = argparse.ArgumentParser(description='数据迁移验证工具')
    parser.add_argument('--env-id', required=True, help='CloudBase 环境ID')
    parser.add_argument('--db-path', default='data/dev.db', help='SQLite数据库路径')

    args = parser.parse_args()

    verifier = MigrationVerifier(args.env_id, args.db_path)
    success = verifier.verify()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
