"""
CloudBase 云函数: pendingTimeoutChecker
定时任务 - 检查PENDING超时订单
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

        # 获取超时配置
        timeout_days = int(os.environ.get('TIMEOUT_DAYS', '7'))
        timeout_threshold = datetime.now(timezone.utc) - timedelta(days=timeout_days)

        # 查询超时的PENDING订单
        conditions = {
            'status': 'PENDING',
            'createTime': {'$lt': timeout_threshold.isoformat()}
        }

        # 查询并处理
        orders = cb.collection('orders').where(conditions).get()['data']
        cancelled_count = 0
        failed_count = 0

        for order in orders:
            try:
                # 生成状态变更记录
                status_record = {
                    'from': 'PENDING',
                    'to': 'CANCELLED',
                    'operatorType': 'SYSTEM',
                    'operatorId': 'TIMEOUT_CHECKER',
                    'time': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                    'reason': f'超时未支付，系统自动取消（超过{timeout_days}天）'
                }

                # 更新订单
                cb.collection('orders').doc(order['_id']).update({
                    'status': 'CANCELLED',
                    'updateTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                    'cancelReason': f'超时未支付（超过{timeout_days}天）'
                })
                cancelled_count += 1

            except Exception as e:
                failed_count += 1
                print(f"取消订单失败 {order['_id']}: {e}")

        # 返回结果
        result = {
            'code': 0,
            'message': 'success',
            'data': {
                'task': 'pendingTimeoutChecker',
                'runTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                'timeoutDays': timeout_days,
                'threshold': timeout_threshold.isoformat(),
                'totalScanned': len(orders),
                'cancelledCount': cancelled_count,
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
                'task': 'pendingTimeoutChecker',
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
