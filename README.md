# AI Novel Creator - 启动指南

## 项目结构

```
easy-novel-creator/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── conf/           # 配置文件目录
│   │   │   └── config.yaml # 后端配置文件
│   │   ├── sql/            # SQL脚本目录
│   │   │   └── init_db.sql # 数据库初始化脚本
│   │   ├── api/            # API路由
│   │   ├── dao/            # 数据访问层
│   │   ├── models/         # 数据模型
│   │   ├── service/        # 业务逻辑层
│   │   ├── config.py       # 配置加载模块
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # 后端启动入口
│   └── requirements.txt    # Python依赖
└── frontend/               # 前端服务
    ├── index.html          # 登录/注册页面
    ├── dashboard.html      # 仪表盘页面
    ├── css/                # 样式文件
    └── js/                 # JavaScript文件
```

## 配置说明

### 数据库配置

配置文件位于：`backend/app/conf/config.yaml`

```yaml
mysql:
  host: 127.0.0.1           # MySQL服务器地址
  port: 3306                # MySQL端口
  user: root                # MySQL用户名
  password: root            # MySQL密码
  database: auth_system     # 数据库名称
  charset: utf8mb4          # 字符集
```

**注意**：首次运行前需要确保MySQL已启动，并创建数据库：

```sql
CREATE DATABASE auth_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

或者手动执行初始化脚本：`backend/app/sql/init_db.sql`

### 应用配置

```yaml
app:
  name: AI Novel Creator
  version: 1.0.0
  debug: true
  server:
    host: 0.0.0.0
    port: 8000
```

### JWT配置

```yaml
jwt:
  secret_key: your-secret-key-change-in-production-2024
  algorithm: HS256
  access_token_expire_minutes: 60
```

**注意**：生产环境请修改 `secret_key`

### CORS配置

```yaml
cors:
  origins:
    - http://localhost:3000
    - http://127.0.0.1:3000
    - http://localhost:8000
    - http://127.0.0.1:8000
```

## 启动步骤

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

确保MySQL已启动，并根据需要修改 `backend/app/conf/config.yaml` 中的数据库配置。

### 3. 启动后端服务

**使用 uv 启动（推荐）：**

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**或者使用传统方式：**

```bash
cd backend
python -m app.main
```

后端服务启动后：
- API地址：http://localhost:8000
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 4. 启动前端服务

```bash
cd frontend
python -m http.server 3000
```

前端服务启动后：
- 前端地址：http://localhost:3000
- 登录页面：http://localhost:3000/index.html
- 仪表盘：http://localhost:3000/dashboard.html

## API接口

### 认证接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录

### 用户接口

- `GET /api/v1/user/me` - 获取当前用户信息
- `PUT /api/v1/user/me` - 更新当前用户信息

详细接口文档请访问：http://localhost:8000/docs

## 测试登录和注册

### 方式一：使用API文档

1. 访问 http://localhost:8000/docs
2. 在Swagger UI中找到 `/api/v1/auth/register` 接口
3. 点击 "Try it out"，输入用户信息：
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "password123"
   }
   ```
4. 点击 "Execute" 执行注册
5. 使用相同方式测试 `/api/v1/auth/login` 接口

### 方式二：使用前端页面

1. 访问 http://localhost:3000/index.html
2. 填写注册表单进行注册
3. 注册成功后使用登录表单进行登录
4. 登录成功后会跳转到仪表盘页面

## 常见问题

### 数据库连接失败

检查MySQL是否启动，配置文件中的数据库信息是否正确。

### 前端无法连接后端

检查CORS配置是否包含前端地址，确保后端服务正常运行。

### 端口被占用

如果端口8000或3000被占用，可以修改配置文件中的端口号。

## 开发模式

在 `config.yaml` 中设置 `debug: true` 可以启用开发模式，支持代码热重载。
