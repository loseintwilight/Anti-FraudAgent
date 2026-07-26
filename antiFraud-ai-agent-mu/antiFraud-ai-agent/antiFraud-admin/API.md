# 管理后台 API 接口文档

## 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 登录 |
| POST | /api/v1/auth/register | 注册 |
| GET  | /api/v1/auth/userinfo | 获取用户信息 |

## 仪表盘
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/dashboard/stats | 统计概览 |
| GET | /api/v1/dashboard/risk-distribution | 风险分布 |

## 检测记录管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/detection/list   | 分页列表 |
| GET    | /api/v1/detection/{id}   | 详情 |
| POST   | /api/v1/detection        | 新增 |
| PUT    | /api/v1/detection        | 修改 |
| DELETE | /api/v1/detection/{id}   | 删除 |

## 报告管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/report/list   | 分页列表 |
| GET    | /api/v1/report/{id}   | 详情 |
| POST   | /api/v1/report        | 新增 |
| PUT    | /api/v1/report        | 修改 |
| DELETE | /api/v1/report/{id}   | 删除 |

## 黑名单管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/blacklist/list   | 分页列表 |
| GET    | /api/v1/blacklist/{id}   | 详情 |
| POST   | /api/v1/blacklist        | 新增 |
| PUT    | /api/v1/blacklist        | 修改 |
| PUT    | /api/v1/blacklist/status | 启用/禁用 |
| DELETE | /api/v1/blacklist/{id}   | 删除 |

## 用户画像管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/profile/list   | 分页列表 |
| GET    | /api/v1/profile/{id}   | 详情 |
| POST   | /api/v1/profile        | 新增 |
| PUT    | /api/v1/profile        | 修改 |
| DELETE | /api/v1/profile/{id}   | 删除 |

## 用户管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/user/list   | 分页列表 |
| GET    | /api/v1/user/{id}   | 详情 |
| POST   | /api/v1/user        | 新增 |
| PUT    | /api/v1/user        | 修改 |
| DELETE | /api/v1/user/{id}   | 删除 |

## 角色管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/role/list   | 分页列表 |
| GET    | /api/v1/role/{id}   | 详情 |
| POST   | /api/v1/role        | 新增 |
| PUT    | /api/v1/role        | 修改 |
| DELETE | /api/v1/role/{id}   | 删除 |

## 菜单管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/v1/menu/list   | 菜单列表（树形） |
| GET    | /api/v1/menu/{id}   | 详情 |
| POST   | /api/v1/menu        | 新增 |
| PUT    | /api/v1/menu        | 修改 |
| DELETE | /api/v1/menu/{id}   | 删除 |

## 通用说明

### 请求格式
- Content-Type: `application/json`
- 认证方式：请求头 `Authorization: Bearer {token}`

### 分页参数
- `pageNum`: 页码，默认 1
- `pageSize`: 每页条数，默认 10

### 响应格式
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {}
}
```

### 错误码
| code | 说明 |
|------|------|
| 200  | 成功 |
| 401  | 未授权 |
| 403  | 无权限 |
| 500  | 服务器错误 |