# 今天吃啥？— 菜谱管理系统

FastAPI + SQLAlchemy（异步）+ MySQL 的菜谱小站，带前端页面、登录、心情推荐、节气推荐和做法视频。

## 目录结构

```
├── main.py              应用入口：组装路由、中间件、异常处理
├── requirements.txt     依赖清单
├── .env.example         配置模板（复制成 .env 再改）
├── sync_frontend.py     一键同步前端 + 打包整个项目到桌面
├── test_main.http       接口测试请求
│
├── core/
│   ├── config.py        配置（从 .env 读）
│   ├── exceptions.py    全局异常处理
│   ├── auth.py          登录 token（HMAC 签名）
│   └── solar_terms.py   二十四节气数据
│
├── db/
│   ├── base.py          Base（公共字段）
│   └── session.py       引擎 / 会话工厂 / get_database
│
├── models/chichi.py     表结构
├── schemas/             出入参校验（Pydantic）
├── crud/chichi.py       数据库操作层
│
├── routers/
│   ├── auth.py          登录 / 退出
│   ├── menu.py          增删改查
│   └── recommend.py     随机 / 心情 / 节气推荐
│
├── templates/           页面（index.html / login.html）
└── static/              样式、脚本、背景视频
```

## 跑起来

### 1. 准备环境

- Python 3.12+
- MySQL 8（本地）

### 2. 创建数据库

```sql
CREATE DATABASE shunyi7qi_chishachi DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> `create_all` 只建表、不建库，库必须先手动创建。

### 3. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. 配置

```bash
cp .env.example .env
```

然后编辑 `.env`：

```ini
ASYNC_DATABASE_URL=mysql+aiomysql://root:你的密码@127.0.0.1:3306/shunyi7qi_chishachi?charset=utf8mb4
ADMIN_PASSWORD=你的登录密码
SECRET_KEY=一串随机字符
```

### 5. 启动

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器打开 <http://127.0.0.1:8000/>，用 `.env` 里的账号密码登录。

## 一键同步 / 打包

```bash
python sync_frontend.py
```

会做三件事：

1. 同步前端到 `~/Desktop/今天吃啥-前端/`
2. 把整个项目（不含 .env）复制到 `~/Desktop/今天吃啥-完整项目/`
3. 打包成 `~/Desktop/今天吃啥-完整项目.zip`

## 功能

| 功能 | 说明 |
|---|---|
| 菜谱管理 | 增、删、改、查，分页 + 搜索 + 标签筛选 + 排序 |
| 心情推荐 | 开心 / 不开心 / 累了 / 饿了 / 想减脂 / 赶时间 |
| 节气推荐 | 24 节气按日期自动判断，附应季食物 |
| 菜谱详情 | 美食介绍 + 分步做法 + B 站视频内嵌播放 |
| 图片预览 | 鼠标悬停列表行，圆形图片跟随光标 |
| 今日卡片 | 左上角显示当前节气 + 今日推荐 |
| 登录保护 | Cookie 会话，接口未登录返回 401 |

## 接口一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/login` | 登录 |
| POST | `/logout` | 退出 |
| POST | `/add_menu` | 新增菜谱 |
| GET | `/query_menu?menu_id=` | 查单条 |
| GET | `/query_all_menu?name=` | 查全部（可按名搜索） |
| PUT | `/update_menu?menu_id=` | 更新 |
| DELETE | `/delete_menu?menu_id=` | 删除 |
| GET | `/recommend/simple?limit=` | 随机推荐 |
| GET | `/recommend/moods` | 可选心情 |
| GET | `/recommend/mood?mood=` | 按心情推荐 |
| GET | `/recommend/solar-terms` | 全部节气 |
| GET | `/recommend/solar-term?term=` | 按节气推荐 |

## 说明

- 表结构用 `create_all` 自动创建；**后续加字段要手动 `ALTER TABLE`**（正式项目应改用 Alembic）
- 背景视频来自 Mixkit，免费可商用
- 菜品图片来自 Wikimedia Commons，外链加载
- 做法视频通过 B 站官方播放器内嵌，不下载不转存
