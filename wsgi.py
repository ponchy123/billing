from app import create_app
from app.config import Config

# 创建应用实例
app = create_app(Config)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 