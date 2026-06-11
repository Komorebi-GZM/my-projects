"""
CloudBase 云函数: getOrderDetail
获取订单详情
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloudbase import CloudBase


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

        # 获取订单ID
        path_params = event.get('pathParameters', {}) or {}
        order_id = path_params.get('orderId')

        if not order_id:
            # 从query参数获取
            query = event.get('queryStringParameters', {}) or {}
            order_id = query.get('orderId')

        if not order_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1001, 'message': '缺少orderId参数', 'data': None})
            }

        # 检查管理员权限
        admin_openids = os.environ.get('ADMIN_OPENIDS', '').split(',')
        is_admin = openid in admin_openids

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

        # 权限检查：用户只能查看自己的订单，管理员可以查看所有
        if not is_admin and order.get('openid') != openid:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1003, 'message': '无权访问该订单', 'data': None})
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'code': 0,
                'message': 'success',
                'data': order
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'code': 5001, 'message': str(e), 'data': None})
        }
