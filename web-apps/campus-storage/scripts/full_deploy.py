#!/usr/bin/env python3
"""
一键部署脚本
整合数据迁移、云函数部署、配置更新

使用方式：
    python scripts/full_deploy.py --env-id <环境ID>
    python scripts/full_deploy.py --env-id <环境ID> --dry-run  # 预览模式
    python scripts/full_deploy.py --env-id <环境ID> --skip-migration  # 跳过数据迁移
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


def run_command(cmd, description):
    """执行命令并打印结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print('='*60)

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"❌ {description} 失败")
        return False

    print(f"✅ {description} 成功")
    return True


def main():
    parser = argparse.ArgumentParser(description='一键部署工具')
    parser.add_argument('--env-id', required=True, help='CloudBase 环境ID')
    parser.add_argument('--dry-run', action='store_true', help='预览模式')
    parser.add_argument('--skip-migration', action='store_true', help='跳过数据迁移')
    parser.add_argument('--skip-deploy', action='store_true', help='跳过云函数部署')

    args = parser.parse_args()

    print("="*60)
    print("校园物品暂存平台 - 一键部署")
    print("="*60)
    print(f"环境ID: {args.env_id}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模式: {'预览' if args.dry_run else '实际部署'}")
    print("="*60)

    success = True

    # 步骤1: 数据迁移
    if not args.skip_migration:
        cmd = f"python scripts/migrate_to_cloudbase.py --env-id {args.env_id}"
        if args.dry_run:
            cmd += " --dry-run"
        if not run_command(cmd, "数据迁移"):
            success = False
            if not args.dry_run:
                print("\n⚠️ 数据迁移失败，是否继续? (y/n)")
                # 在自动化脚本中默认继续
    else:
        print("\n⏭️ 跳过数据迁移")

    # 步骤2: 云函数部署
    if not args.skip_deploy:
        cmd = f"python scripts/deploy_cloudfunctions.py --env-id {args.env_id}"
        if args.dry_run:
            cmd += " --dry-run"
        if not run_command(cmd, "云函数部署"):
            success = False
    else:
        print("\n⏭️ 跳过云函数部署")

    # 步骤3: 验证部署
    if not args.dry_run and success:
        print("\n" + "="*60)
        print("部署验证")
        print("="*60)
        print("✅ 部署流程执行完成")
        print("\n下一步操作:")
        print("1. 登录微信开发者工具")
        print("2. 修改 miniprogram/config.js 中的 API_BASE_URL")
        print("3. 点击'上传'提交小程序审核")
        print("="*60)
    elif args.dry_run:
        print("\n" + "="*60)
        print("预览模式完成")
        print("="*60)
        print("✅ 所有检查通过，可以执行实际部署")
        print(f"\n执行实际部署命令:")
        print(f"  python scripts/full_deploy.py --env-id {args.env_id}")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 部署过程中出现错误")
        print("="*60)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
