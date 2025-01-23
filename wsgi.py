import os
from app import create_app
from app.config import Config

print("\n=== 启动应用 ===")
print(f"[DEBUG] 当前工作目录: {os.getcwd()}")
print(f"[DEBUG] 当前文件位置: {os.path.abspath(__file__)}")
print(f"[DEBUG] 数据库URL: {Config.SQLALCHEMY_DATABASE_URI}")

app = create_app(Config)
Config.init_app(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 