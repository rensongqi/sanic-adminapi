# Python sanic template

## 项目介绍


> 数据库切换、打印机连接、数据同步、操作记录

## 组织结构

```lua
admin
├── core             -- 应用中心
├────├── __init__.py -- 应用服务注册
├────├── libs        -- 应用库
├────├── listeners   -- 监听服务
├────├── middlewares -- 中间件
├────├── views       -- 视图函数
├────└── shell       -- 处理程序
├──────────├── project_post    -- 项目数据转发程序
├──────────└── work            -- 项目数据接入与处理
├── settings         -- 配置中心
├── static           -- 网页静态文件
├── templatess       -- 网页文件
├── main.py          -- 程序运行入口
├── socketio_server.py    -- socket.io独立运行文件
└── log              -- 日志
```

## 环境搭建

    pip3 install -r requirements

### 运行

集成运行

    python3 main.py

## 运行效果展示

http://0.0.0.0:8011/

## 开发规范

请求类型:

- 查询：get
- 数据操作：post

响应：

    {
        'code':'0',
        'data':{},
        'msg':成功
    }

错误码：
| 值 | 类型 | 描述 |
| -------- | ---------------------- | --------------------- |
| 0 | string | 成功 |
| -1 | string | 失败 |

### 基础表管理 API

> /类型前缀/基础表/数据操作

类型前缀：

- 基础表操作：/adminapi
- 功能浏览 API：/webapi

数据操作：
添加：/add [list]

删除：/delete [list]

更新：/update [list]

请求：/get?page=[true/false]&limit=10&currentpage=1

基础表：

- 用户管理：user
