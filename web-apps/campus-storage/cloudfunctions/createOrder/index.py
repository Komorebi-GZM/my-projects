"""
CloudBase 云函数: createOrder
创建订单
"""
import json
import os
import sys
from datetime import datetime, timezone

# 添加共享代码路径
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

        # 解析请求体
        body = json.loads(event.get('body', '{}'))

        # 参数校验（简化版）
        required_fields = ['itemType', 'warehouseId', 'city']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'code': 1001, 'message': f'缺少必填字段: {field}', 'data': None})
                }

        # 初始化CloudBase
        env_id = os.environ.get('TCB_ENV_ID')
        cb = CloudBase(env_id)

        # 生成订单号
        import time
        order_no = f"ORD{int(time.time() * 1000)}"

        # 计算费用（简化版）
        storage_fee = float(os.environ.get('STORAGE_FEE_RATE', '0.5')) * body.get('estimatedDuration', 3)
        storage_fee = round(storage_fee, 2)

        # 创建订单文档
        order_doc = {
            '_openid': openid,
            'openid': openid,
            'orderNo': order_no,
            'itemType': body['itemType'],
            'city': body['city'],
            'warehouseId': body['warehouseId'],
            'status': 'PENDING',
            'amount': {
                'storageFee': storage_fee,
                'deliveryFee': 0,
                'insuranceFee': 0,
                'totalFee': storage_fee
            },
            'isPaid': False,
            'statusHistory': [{
                'from': None,
                'to': 'PENDING',
                'operatorType': 'USER',
                'operatorId': openid,
                'time': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                'reason': '订单创建'
            }],
            'createTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
            'updateTime': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
            'version': 1
        }

        # 插入订单
        result = cb.collection('orders').add(order_doc)

        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'code': 0,
                'message': 'success',
                'data': {
                    '_id': result['id'],
                    'orderNo': order_no,
                    'status': 'PENDING',
                    'amount': order_doc['amount']
                }
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'code': 5001, 'message': str(e), 'data': None})
        }
