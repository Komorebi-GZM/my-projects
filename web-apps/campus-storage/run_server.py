#!/usr/bin/env python
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app

if __name__ == "__main__":
    app = create_app()
    print("Starting server on http://0.0.0.0:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
