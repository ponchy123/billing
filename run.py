from app import create_app

app = create_app()

if __name__ == '__main__':
    # 设置host为0.0.0.0使其监听所有网络接口
    # 这样局域网内的其他计算机就可以通过IP地址访问
    app.run(host='0.0.0.0', port=5000, debug=True) 