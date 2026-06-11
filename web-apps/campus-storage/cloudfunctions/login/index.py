"""
CloudBase 云函数: login
用户登录获取 openid
"""
import json
import os


def main(event, context):
    """云函数入口"""
    try:
        # 从请求中获取 code
        body = json.loads(event.get('body', '{}'))
        code = body.get('code')

        if not code:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 1001, 'message': '缺少code参数', 'data': None})
            }

        # 调用微信接口获取 openid
        import requests
        appid = os.environ.get('WX_APPID', '')
        secret = os.environ.get('WX_SECRET', '')

        if not appid or not secret:
            # Demo模式: 返回模拟openid
            mock_openid = f'mock_openid_{code[:10]}'
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'openId': mock_openid,
                        'role': 'USER'
                    }
                })
            }

        # 真实微信登录
        url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
        resp = requests.get(url, timeout=10)
        data = resp.json()

        openid = data.get('openid')
        if not openid:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'code': 4001, 'message': '微信登录失败', 'data': data})
            }

        # 检查是否管理员
        admin_openids = os.environ.get('ADMIN_OPENIDS', '').split(',')
        is_admin = openid in admin_openids

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'code': 0,
                'message': 'success',
                'data': {
                    'openId': openid,
                    'isAdmin': is_admin,
                    'role': 'ADMIN' if is_admin else 'USER'
                }
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'code': 5001, 'message': str(e), 'data': None})
        }
