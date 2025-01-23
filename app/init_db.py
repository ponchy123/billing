from app import create_app
from app.extensions import db
from app.models.product import Product
from app.models.user import User
from app.models.role import Role
from datetime import datetime, timezone
import traceback
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import pymysql

def create_database():
    try:
        # 连接MySQL服务器
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root'
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute("DROP DATABASE IF EXISTS billing")
        cursor.execute("CREATE DATABASE billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("数据库创建成功")
        
        # 选择数据库
        cursor.execute("USE billing")
        print("数据库选择成功")
        
        # 创建表
        cursor.execute("""
            CREATE TABLE roles (
                id INTEGER NOT NULL AUTO_INCREMENT,
                name VARCHAR(64) NOT NULL,
                description VARCHAR(256),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                PRIMARY KEY (id),
                UNIQUE (name)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER NOT NULL AUTO_INCREMENT,
                username VARCHAR(64) NOT NULL,
                email VARCHAR(120) NOT NULL,
                password_hash VARCHAR(512),
                role_id INTEGER,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                PRIMARY KEY (id),
                UNIQUE (username),
                UNIQUE (email),
                FOREIGN KEY(role_id) REFERENCES roles (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER NOT NULL AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                weight FLOAT,
                price FLOAT,
                zone INTEGER,
                enabled BOOL,
                start_time DATETIME,
                end_time DATETIME,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                PRIMARY KEY (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE remote_postal_codes (
                id INTEGER NOT NULL AUTO_INCREMENT,
                postal_code VARCHAR(5) NOT NULL,
                postal_type VARCHAR(20) NOT NULL COMMENT '邮编类型',
                created_at DATETIME COMMENT '创建时间',
                updated_at DATETIME COMMENT '更新时间',
                PRIMARY KEY (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE start_postal_codes (
                id INTEGER NOT NULL AUTO_INCREMENT,
                postal_code VARCHAR(5) NOT NULL COMMENT '起始邮编',
                created_at DATETIME COMMENT '创建时间',
                updated_at DATETIME COMMENT '更新时间',
                PRIMARY KEY (id),
                UNIQUE (postal_code)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE receiver_postal_codes (
                id INTEGER NOT NULL AUTO_INCREMENT,
                start_postal_id INTEGER NOT NULL,
                start_range VARCHAR(5) NOT NULL COMMENT '起始范围',
                end_range VARCHAR(5) NOT NULL COMMENT '结束范围',
                zone VARCHAR(10) NOT NULL COMMENT '分区',
                created_at DATETIME COMMENT '创建时间',
                updated_at DATETIME COMMENT '更新时间',
                PRIMARY KEY (id),
                FOREIGN KEY(start_postal_id) REFERENCES start_postal_codes (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE fuel_rates (
                id INTEGER NOT NULL AUTO_INCREMENT,
                rate FLOAT NOT NULL COMMENT '燃油费率(%)',
                effective_date DATETIME NOT NULL COMMENT '生效日期',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                PRIMARY KEY (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE calculation_histories (
                id INTEGER NOT NULL AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                length FLOAT NOT NULL COMMENT '长度(cm)',
                width FLOAT NOT NULL COMMENT '宽度(cm)',
                height FLOAT NOT NULL COMMENT '高度(cm)',
                weight FLOAT NOT NULL COMMENT '重量(kg)',
                start_postal_code VARCHAR(5) NOT NULL COMMENT '起始邮编',
                receiver_postal_code VARCHAR(5) NOT NULL COMMENT '收件邮编',
                is_residential BOOL COMMENT '是否住宅配送',
                base_fee FLOAT NOT NULL COMMENT '基本费用',
                handling_fee FLOAT NOT NULL COMMENT '操作费',
                oversize_fee FLOAT NOT NULL COMMENT '超大件费用',
                residential_fee FLOAT NOT NULL COMMENT '住宅配送费',
                remote_area_fee FLOAT NOT NULL COMMENT '偏远地区费',
                total_fee FLOAT NOT NULL COMMENT '总费用',
                created_at DATETIME COMMENT '创建时间',
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id),
                FOREIGN KEY(product_id) REFERENCES products (id)
            )
        """)
        
        print("表创建成功")
        
        # 插入初始数据
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建角色
        cursor.execute(f"""
            INSERT INTO roles (name, description, created_at, updated_at)
            VALUES ('管理员', '系统管理员，拥有所有权限', '{now}', '{now}'),
                   ('普通用户', '普通用户，仅有查看权限', '{now}', '{now}')
        """)
        print("角色创建成功")
        
        # 创建管理员用户
        admin = User(
            username='admin',
            email='admin@example.com',
            role_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        admin.set_password('admin123')
        cursor.execute(f"""
            INSERT INTO users (username, email, password_hash, role_id, created_at, updated_at)
            VALUES ('admin', 'admin@example.com', '{admin.password_hash}', 1, '{now}', '{now}')
        """)
        print("管理员用户创建成功")
        
        # 创建测试产品
        cursor.execute(f"""
            INSERT INTO products (name, weight, price, zone, enabled, created_at, updated_at)
            VALUES ('FedEx Ground', 1.0, 10.0, 1, 1, '{now}', '{now}')
        """)
        print("测试产品创建成功")
        
        # 提交事务
        conn.commit()
        print("初始数据创建成功")
        
        # 关闭连接
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"创建数据库时出错: {str(e)}")
        raise

app = create_app()

if __name__ == '__main__':
    create_database() 