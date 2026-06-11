"""
CloudBase 云函数: getOrderList
获取订单列表
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

        # 解析查询参数
        query_params = event.get('queryStringParameters', {}) or {}
        status_filter = query_params.get('status')
        page = int(query_params.get('page', '1'))
        page_size = int(query_params.get('pageSize', '10'))

        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        # 检查管理员权限
        admin_openids = os.environ.get('ADMIN_OPENIDS', '').split(',')
        is_admin = openid in admin_openids

        # 初始化CloudBase
        env_id = os.environ.get('TCB_ENV_ID')
        cb = CloudBase(env_id)

        # 构建查询条件
        # 管理员可以查看所有订单，普通用户只能查看自己的
        if is_admin:
            conditions = {}
        else:
            conditions = {'openid': openid}

        if status_filter:
            conditions['status'] = status_filter

        # 查询总数
        total = cb.collection('orders').where(conditions).count()['total']

        # 查询列表
        orders = cb.collection('orders').where(conditions) \
            .order_by('createTime', 'desc') \
            .skip((page - 1) * page_size) \
            .limit(page_size) \
            .get()['data']

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'code': 0,
                'message': 'success',
                'data': {
                    'list': orders,
                    'total': total,
                    'page': page,
                    'pageSize': page_size
                }
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'code': 5001, 'message': str(e), 'data': None})
        }
