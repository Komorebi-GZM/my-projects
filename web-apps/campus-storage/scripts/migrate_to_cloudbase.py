#!/usr/bin/env python3
"""
数据迁移脚本：SQLite → CloudBase NoSQL

使用方式：
    python scripts/migrate_to_cloudbase.py --env-id <环境ID>
    python scripts/migrate_to_cloudbase.py --env-id <环境ID> --dry-run  # 仅预览
    python scripts/migrate_to_cloudbase.py --env-id <环境ID> --backup   # 先备份再迁移

迁移流程：
    1. 读取本地SQLite数据库
    2. 按依赖顺序遍历表（warehouses → users → orders → tickets）
    3. 逐行转换数据格式（类型转换、字段映射）
    4. 批量写入CloudBase对应集合
    5. 输出迁移报告（成功数、失败数、跳过数）
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


class MigrationReporter:
    """迁移报告生成器"""

    def __init__(self):
        self.stats = {
            'warehouses': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0},
            'users': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0},
            'orders': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0},
            'tickets': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0},
        }
        self.errors = []
        self.start_time = datetime.now()

    def record(self, table, success=True, skipped=False, error=None):
        """记录迁移结果"""
        self.stats[table]['total'] += 1
        if skipped:
            self.stats[table]['skipped'] += 1
        elif success:
            self.stats[table]['success'] += 1
        else:
            self.stats[table]['failed'] += 1
            if error:
                self.errors.append({'table': table, 'error': str(error)})

    def print_summary(self):
        """打印迁移报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print("\n" + "=" * 60)
        print("数据迁移报告")
        print("=" * 60)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration:.2f} 秒")
        print("-" * 60)

        total_records = 0
        total_success = 0
        total_failed = 0
        total_skipped = 0

        for table, stats in self.stats.items():
            print(f"\n{table.upper()}:")
            print(f"  总计: {stats['total']}")
            print(f"  成功: {stats['success']}")
            print(f"  失败: {stats['failed']}")
            print(f"  跳过: {stats['skipped']}")
            total_records += stats['total']
            total_success += stats['success']
            total_failed += stats['failed']
            total_skipped += stats['skipped']

        print("\n" + "-" * 60)
        print(f"总计: {total_records} 条记录")
        print(f"  成功: {total_success}")
        print(f"  失败: {total_failed}")
        print(f"  跳过: {total_skipped}")
        print(f"  成功率: {(total_success / total_records * 100):.1f}%" if total_records > 0 else "  成功率: N/A")

        if self.errors:
            print("\n错误详情:")
            for i, err in enumerate(self.errors[:10], 1):
                print(f"  {i}. [{err['table']}] {err['error']}")
            if len(self.errors) > 10:
                print(f"  ... 还有 {len(self.errors) - 10} 个错误")

        print("=" * 60)

        return total_failed == 0


class DataTransformer:
    """数据转换器"""

    @staticmethod
    def transform_warehouse(row):
        """转换仓库数据"""
        return {
            '_id': str(row['id']),
            'name': row['name'],
            'address': row['address'],
            'contact': row.get('contact', ''),
            'createTime': row.get('create_time', datetime.now().isoformat())
        }

    @staticmethod
    def transform_user(row):
        """转换用户数据"""
        return {
            '_id': str(row['id']),
            '_openid': row['openid'],
            'openid': row['openid'],
            'nickname': row.get('nickname', ''),
            'avatar': row.get('avatar', ''),
            'isAdmin': bool(row.get('is_admin', 0)),
            'createTime': row.get('create_time', datetime.now().isoformat())
        }

    @staticmethod
    def transform_order(row):
        """转换订单数据"""
        # 解析状态历史
        status_history = []
        try:
            if row.get('status_history'):
                status_history = json.loads(row['status_history'])
        except json.JSONDecodeError:
            pass

        # 解析金额JSON
        amount = {}
        try:
            if row.get('amount'):
                amount = json.loads(row['amount'])
        except json.JSONDecodeError:
            pass

        return {
            '_id': str(row['id']),
            '_openid': row['openid'],
            'openid': row['openid'],
            'orderNo': row['order_no'],
            'status': row['status'],
            'isPaid': bool(row.get('is_paid', 0)),
            'userId': row.get('user_id', ''),
            'warehouseId': str(row.get('warehouse_id', '')),
            'warehouseName': row.get('warehouse_name', ''),
            'city': row.get('city', ''),
            'itemType': row.get('item_type', ''),
            'volume': row.get('volume', ''),
            'estimatedWeight': row.get('estimated_weight', 0),
            'serviceType': row.get('service_type', ''),
            'storageDays': row.get('storage_days', 7),
            'deliveryAddress': row.get('delivery_address', ''),
            'deliveryTime': row.get('delivery_time', ''),
            'amount': amount,
            'declaredValue': row.get('declared_value', 0),
            'storagePhotoUrl': row.get('storage_photo_url', ''),
            'statusHistory': status_history,
            'createTime': row['create_time'],
            'updateTime': row.get('update_time', row['create_time'])
        }

    @staticmethod
    def transform_ticket(row):
        """转换配送单数据"""
        return {
            '_id': str(row['id']),
            '_openid': row['openid'],
            'openid': row['openid'],
            'orderId': str(row['order_id']),
            'deliveryAddress': row['delivery_address'],
            'contactName': row.get('contact_name', ''),
            'contactPhone': row.get('contact_phone', ''),
            'deliveryTime': row.get('delivery_time', ''),
            'status': row.get('status', 'PENDING'),
            'createTime': row.get('create_time', datetime.now().isoformat())
        }


class CloudBaseMigrator:
    """CloudBase 迁移器"""

    def __init__(self, env_id, dry_run=False):
        self.env_id = env_id
        self.dry_run = dry_run
        self.reporter = MigrationReporter()

    def migrate(self, db_path='data/dev.db'):
        """执行迁移"""
        if not os.path.exists(db_path):
            print(f"错误: 数据库文件不存在: {db_path}")
            return False

        print(f"连接到SQLite数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        try:
            # 按依赖顺序迁移
            self._migrate_table(conn, 'warehouses', DataTransformer.transform_warehouse)
            self._migrate_table(conn, 'users', DataTransformer.transform_user)
            self._migrate_table(conn, 'orders', DataTransformer.transform_order)
            self._migrate_table(conn, 'tickets', DataTransformer.transform_ticket)

        finally:
            conn.close()

        # 打印报告
        return self.reporter.print_summary()

    def _migrate_table(self, conn, table_name, transformer):
        """迁移单个表"""
        print(f"\n迁移表: {table_name}")

        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            print(f"  表 {table_name} 为空，跳过")
            return

        print(f"  发现 {len(rows)} 条记录")

        for row in rows:
            try:
                row_dict = dict(row)
                doc = transformer(row_dict)

                if self.dry_run:
                    # 仅预览，不实际写入
                    self.reporter.record(table_name, success=True)
                    continue

                # 实际写入CloudBase
                # 这里模拟写入成功
                # 实际使用时需要调用 cloudbase-sdk
                success = self._write_to_cloudbase(table_name, doc)
                self.reporter.record(table_name, success=success)

            except Exception as e:
                print(f"  错误: 迁移记录失败 - {e}")
                self.reporter.record(table_name, success=False, error=e)

        cursor.close()

    def _write_to_cloudbase(self, collection, doc):
        """写入CloudBase。"""
        from src.db.cloudbase_adapter import CloudBaseAdapter
        adapter = CloudBaseAdapter(self.env_id)
        try:
            doc_id = adapter.insert(collection, doc)
            return bool(doc_id)
        except Exception:
            return False
        finally:
            adapter.close()


def main():
    parser = argparse.ArgumentParser(description='SQLite 到 CloudBase 数据迁移工具')
    parser.add_argument('--env-id', required=True, help='CloudBase 环境ID')
    parser.add_argument('--db-path', default='data/dev.db', help='SQLite数据库路径')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际写入')
    parser.add_argument('--backup', action='store_true', help='迁移前备份CloudBase数据')

    args = parser.parse_args()

    print("=" * 60)
    print("SQLite → CloudBase 数据迁移")
    print("=" * 60)
    print(f"环境ID: {args.env_id}")
    print(f"数据库: {args.db_path}")
    print(f"模式: {'预览模式' if args.dry_run else '实际迁移'}")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠️  当前为预览模式，不会实际写入数据\n")

    migrator = CloudBaseMigrator(args.env_id, dry_run=args.dry_run)
    success = migrator.migrate(args.db_path)

    if success:
        print("\n✅ 迁移完成")
        return 0
    else:
        print("\n❌ 迁移失败，请查看错误详情")
        return 1


if __name__ == '__main__':
    sys.exit(main())
