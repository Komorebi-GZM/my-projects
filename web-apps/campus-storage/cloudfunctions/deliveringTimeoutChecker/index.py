"""
CloudBase 云函数: deliveringTimeoutChecker
定时任务 - 检查DELIVERING超时订单
触发器: 每30分钟执行一次
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloudbase import CloudBase


def main(event, context):
    """云函数入口 - 定时触发"""
    try:
        # 初始化CloudBase
        env_id = os.environ.get('TCB_ENV_ID')
        cb = CloudBase(env_id)

        # 获取超时配置（配送超时时间，默认24小时）
        delivering_timeout_hours = int(os.environ.get('DELIVERING_TIMEOUT_HOURS', '24'))
        timeout_threshold = datetime.now(timezone.utc) - timedelta(hours=delivering_timeout_hours)

        # 查询超时的DELIVERING订单
        conditions = {
            'status': 'DELIVERING',
            'updateTime': {'$lt': timeout_threshold.isoformat()}
        }

        # 查询并处理
        orders = cb.collection('orders').where(conditions).get()['data']
        completed_count = 0
        failed_count = 0

        for order in orders:
            try:
                # 更新订单状态
                cb.collection('orders').doc(order['_id']).update({
                    'status': 'COMPLETED',
                    'updateTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                    'completedTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                    'completedType': 'TIMEOUT_AUTO',
                    'completionNote': f'配送超时，系统自动完结（超过{delivering_timeout_hours}小时）'
                })
                completed_count += 1

            except Exception as e:
                failed_count += 1
                print(f"完结订单失败 {order['_id']}: {e}")

        # 返回结果
        result = {
            'code': 0,
            'message': 'success',
            'data': {
                'task': 'deliveringTimeoutChecker',
                'runTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                'timeoutHours': delivering_timeout_hours,
                'threshold': timeout_threshold.isoformat(),
                'totalScanned': len(orders),
                'completedCount': completed_count,
                'failedCount': failed_count
            }
        }

        print(json.dumps(result, ensure_ascii=False))

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }

    except Exception as e:
        error_result = {
            'code': 5001,
            'message': str(e),
            'data': {
                'task': 'deliveringTimeoutChecker',
                'error': str(e),
                'runTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds')
            }
        }
        print(json.dumps(error_result, ensure_ascii=False))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(error_result)
        }
