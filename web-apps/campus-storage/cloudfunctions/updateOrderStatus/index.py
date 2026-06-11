"""
CloudBase 云函数: updateOrderStatus
更新订单状态（管理员接口）
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloudbase import CloudBase


# 状态转换矩阵（与后端 order_state.py 保持一致）
VALID_TRANSITIONS = {
    'PENDING': ['COLLECTED', 'CANCELLED', 'EXCEPTION'],
    'COLLECTED': ['TRANSIT', 'EXCEPTION'],
    'TRANSIT': ['STORED', 'EXCEPTION'],
    'STORED': ['DELIVERING', 'EXCEPTION'],
    'DELIVERING': ['COMPLETED', 'EXCEPTION'],
    'COMPLETED': [],      # 终止状态
    'CANCELLED': [],     # 终止状态
    'EXCEPTION': ['COMPLETED', 'CANCELLED']  # 可从异常恢复
}


def main(event, context):
    """云函数入口"""
    try:
        # 获取openid
        headers = event.get('headers', {})
        openid = headers.get('x-openid') or headers.get('X-OpenId')

        if not openid:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1002, 'message': '未授权，缺少openid', 'data': None})
            }

        # 检查管理员权限
        admin_openids = os.environ.get('ADMIN_OPENIDS', '').split(',')
        is_admin = openid in admin_openids
        is_user = not is_admin  # 非管理员即为普通用户

        # 获取订单ID
        path_params = event.get('pathParameters', {}) or {}
        order_id = path_params.get('orderId')

        if not order_id:
            query = event.get('queryStringParameters', {}) or {}
            order_id = query.get('orderId')

        if not order_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1001, 'message': '缺少orderId参数', 'data': None})
            }

        # 解析请求体
        body = json.loads(event.get('body', '{}'))
        new_status = body.get('newStatus') or body.get('status')
        operator_type = body.get('operatorType', 'ADMIN' if is_admin else 'USER')
        reason = body.get('reason', '')

        if not new_status:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1001, 'message': '缺少newStatus参数', 'data': None})
            }

        # 校验状态值
        valid_statuses = ['PENDING', 'COLLECTED', 'TRANSIT', 'STORED', 'DELIVERING', 'COMPLETED', 'CANCELLED', 'EXCEPTION']
        if new_status not in valid_statuses:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1001, 'message': f'无效的状态值: {new_status}', 'data': None})
            }

        # 初始化CloudBase
        env_id = os.environ.get('TCB_ENV_ID')
        cb = CloudBase(env_id)

        # 查询订单
        result = cb.collection('orders').doc(order_id).get()
        order = result['data'][0] if result['data'] else None

        if not order:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 2001, 'message': '订单不存在', 'data': None})
            }

        # 检查权限（用户只能操作自己的订单）
        if is_user and order.get('openid') != openid:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1003, 'message': '无权操作该订单', 'data': None})
            }

        # 状态流转校验
        current_status = order.get('status', 'PENDING')
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_transitions:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'code': 2002,
                    'message': f'无效的状态流转: {current_status} -> {new_status}',
                    'data': {
                        'currentStatus': current_status,
                        'requestedStatus': new_status,
                        'allowedTransitions': allowed_transitions
                    }
                })
            }

        # 生成状态变更记录
        status_record = {
            'from': current_status,
            'to': new_status,
            'operatorType': operator_type,
            'operatorId': openid,
            'time': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
        }
        if reason:
            status_record['reason'] = reason

        # 更新订单状态
        update_data = {
            'status': new_status,
            'updateTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
            'version': order.get('version', 1) + 1
        }

        # 如果状态变为COMPLETED，更新完成时间
        if new_status == 'COMPLETED':
            update_data['completedTime'] = datetime.now(timezone.utc).isoformat(timespec='milliseconds')

        # 实际更新
        cb.collection('orders').doc(order_id).update(update_data)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'code': 0,
                'message': 'success',
                'data': {
                    '_id': order_id,
                    'status': new_status,
                    'statusHistory': status_record
                }
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'code': 5001, 'message': str(e), 'data': None})
        }
