# 运费计算系统

一个基于Flask的运费计算系统，支持产品管理、燃油费率管理、邮编分区管理、用户管理和运费计算功能。

## 功能特点

- 用户认证和授权（管理员、客服、客户）
- 产品管理（添加、编辑、删除产品）
- 燃油费率管理
- 邮编分区管理
- 运费计算（单件计算和批量计算）
- 导入导出功能
- 日志记录
- 错误处理
- 邮件通知

## 技术栈

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-Login
- Flask-Mail
- Flask-WTF
- Bootstrap
- Pandas
- ReportLab

## 安装

1. 克隆仓库
```bash
git clone https://gitee.com/hx1696107281/freightbilling.git
cd freightbilling
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

5. 初始化数据库
```bash
flask db upgrade
flask deploy
```

6. 运行应用
```bash
flask run
```

## 使用说明

1. 管理员账号
- 用户名: admin
- 密码: admin123

2. 功能模块
- 后台管理
  - 产品管理
  - 燃油费率管理
  - 邮编分区管理
  - 用户管理
- 客服功能
  - 运费计算
  - 客户管理
  - 批量计算
- 客户功能
  - 运费计算
  - 历史记录

## 开发

1. 运行测试
```bash
flask test
```

2. 数据库迁移
```bash
flask db migrate -m "migration message"
flask db upgrade
```

## 部署

1. 设置环境变量
```bash
export FLASK_ENV=production
```

2. 配置生产环境
- 设置安全的SECRET_KEY
- 配置数据库URL
- 配置邮件服务器

3. 运行部署命令
```bash
flask deploy
```

## 贡献

1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加一些功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 邮箱: 1696107281@qq.com
- Gitee: https://gitee.com/hx1696107281 