# CRM系统架构设计

## 1. 技术栈选择

为了快速开发并确保系统的稳定性和可扩展性，我们选择以下技术栈：

- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5（响应式设计）
- **后端**：Python + Flask（轻量级框架，适合中小型应用）
- **数据库**：SQLite（开发阶段）/ MySQL（生产环境）
- **ORM**：SQLAlchemy（简化数据库操作）
- **多语言支持**：Flask-Babel（国际化和本地化支持）
- **认证与授权**：Flask-Login（用户认证）+ 自定义权限系统
- **报表导出**：pandas + openpyxl（Excel导出）

## 2. 系统模块划分

### 2.1 核心模块

1. **用户认证与权限管理模块**
   - 用户登录/注销
   - 角色管理（管理员、销售员、仓库管理员等）
   - 权限控制

2. **产品管理模块**
   - 产品分类管理
   - 产品信息管理（名称、编号、规格、单价等）
   - 库存管理（入库、出库、库存预警）
   - 供应商管理

3. **销售管理模块**
   - 销售开单
   - 支付方式管理（现金、扫码美金）
   - 销售统计与分析
   - 销售退货处理

4. **客户管理模块**
   - 客户信息管理
   - 客户购买历史
   - 客户分类与标签
   - 客户联系记录

5. **工程项目管理模块**
   - 项目基本信息管理
   - 项目进度跟踪
   - 项目材料管理
   - 项目成本核算
   - 项目文档管理

6. **报表与数据导出模块**
   - 销售报表
   - 库存报表
   - 客户报表
   - 项目报表
   - Excel格式导出

7. **系统设置模块**
   - 基础信息设置
   - 语言切换（中文/英文）
   - 系统参数配置

## 3. 数据库设计

### 3.1 主要数据表

1. **用户表(users)**
   - id: 主键
   - username: 用户名
   - password_hash: 密码哈希
   - name: 姓名
   - role_id: 角色ID（外键）
   - email: 邮箱
   - phone: 电话
   - status: 状态（启用/禁用）
   - created_at: 创建时间
   - updated_at: 更新时间

2. **角色表(roles)**
   - id: 主键
   - name: 角色名称
   - description: 角色描述
   - permissions: 权限列表（JSON格式）

3. **产品分类表(product_categories)**
   - id: 主键
   - name: 分类名称
   - description: 分类描述
   - parent_id: 父分类ID（自关联）

4. **产品表(products)**
   - id: 主键
   - code: 产品编码
   - name: 产品名称
   - category_id: 分类ID（外键）
   - specification: 规格
   - unit: 单位
   - purchase_price: 采购价
   - selling_price: 销售价
   - min_stock: 最低库存量
   - description: 产品描述
   - status: 状态（启用/禁用）
   - created_at: 创建时间
   - updated_at: 更新时间

5. **库存表(inventory)**
   - id: 主键
   - product_id: 产品ID（外键）
   - quantity: 数量
   - updated_at: 更新时间

6. **库存记录表(inventory_records)**
   - id: 主键
   - product_id: 产品ID（外键）
   - type: 类型（入库/出库）
   - quantity: 数量
   - source_type: 来源类型（采购/销售/调整）
   - source_id: 来源ID
   - user_id: 操作用户ID（外键）
   - remarks: 备注
   - created_at: 创建时间

7. **客户表(customers)**
   - id: 主键
   - name: 客户名称
   - contact_person: 联系人
   - phone: 电话
   - email: 邮箱
   - address: 地址
   - type: 客户类型
   - remarks: 备注
   - created_at: 创建时间
   - updated_at: 更新时间

8. **销售订单表(sales_orders)**
   - id: 主键
   - order_no: 订单编号
   - customer_id: 客户ID（外键）
   - order_date: 订单日期
   - total_amount: 总金额
   - discount: 折扣
   - actual_amount: 实际金额
   - payment_method: 支付方式（现金/扫码美金）
   - payment_status: 支付状态
   - user_id: 销售员ID（外键）
   - remarks: 备注
   - created_at: 创建时间
   - updated_at: 更新时间

9. **销售订单明细表(sales_order_items)**
   - id: 主键
   - order_id: 订单ID（外键）
   - product_id: 产品ID（外键）
   - quantity: 数量
   - unit_price: 单价
   - discount: 折扣
   - amount: 金额

10. **工程项目表(projects)**
    - id: 主键
    - name: 项目名称
    - customer_id: 客户ID（外键）
    - start_date: 开始日期
    - end_date: 结束日期
    - status: 状态（未开始/进行中/已完成）
    - budget: 预算
    - actual_cost: 实际成本
    - manager_id: 项目经理ID（外键）
    - description: 项目描述
    - created_at: 创建时间
    - updated_at: 更新时间

11. **项目材料表(project_materials)**
    - id: 主键
    - project_id: 项目ID（外键）
    - product_id: 产品ID（外键）
    - planned_quantity: 计划数量
    - actual_quantity: 实际数量
    - unit_price: 单价
    - status: 状态（未领用/已领用/已退回）
    - remarks: 备注

## 4. 用户界面设计

### 4.1 整体布局

- **顶部导航栏**：包含系统名称、语言切换（中/英国旗图标）、用户信息、退出按钮
- **左侧菜单**：根据用户权限显示可访问的模块
- **主内容区**：显示当前操作的模块内容
- **底部信息栏**：版权信息、系统版本等

### 4.2 主要页面

1. **登录页面**
2. **仪表盘/首页**：显示关键业务指标和快捷入口
3. **产品管理页面**：产品列表、添加/编辑产品、库存查询
4. **销售管理页面**：销售开单、订单列表、销售统计
5. **客户管理页面**：客户列表、添加/编辑客户、客户详情
6. **工程项目管理页面**：项目列表、项目详情、项目材料管理
7. **报表页面**：各类报表生成和导出
8. **系统设置页面**：用户管理、角色管理、基础设置

## 5. API接口设计

采用RESTful API设计风格，主要接口包括：

### 5.1 认证接口

- POST /api/auth/login：用户登录
- POST /api/auth/logout：用户登出
- GET /api/auth/user：获取当前用户信息

### 5.2 产品管理接口

- GET /api/products：获取产品列表
- GET /api/products/{id}：获取产品详情
- POST /api/products：创建产品
- PUT /api/products/{id}：更新产品
- DELETE /api/products/{id}：删除产品
- GET /api/product-categories：获取产品分类

### 5.3 库存管理接口

- GET /api/inventory：获取库存列表
- POST /api/inventory/in：产品入库
- POST /api/inventory/out：产品出库
- GET /api/inventory/records：获取库存记录

### 5.4 销售管理接口

- GET /api/sales：获取销售订单列表
- GET /api/sales/{id}：获取销售订单详情
- POST /api/sales：创建销售订单
- PUT /api/sales/{id}：更新销售订单
- DELETE /api/sales/{id}：删除销售订单

### 5.5 客户管理接口

- GET /api/customers：获取客户列表
- GET /api/customers/{id}：获取客户详情
- POST /api/customers：创建客户
- PUT /api/customers/{id}：更新客户
- DELETE /api/customers/{id}：删除客户

### 5.6 工程项目管理接口

- GET /api/projects：获取项目列表
- GET /api/projects/{id}：获取项目详情
- POST /api/projects：创建项目
- PUT /api/projects/{id}：更新项目
- DELETE /api/projects/{id}：删除项目
- GET /api/projects/{id}/materials：获取项目材料
- POST /api/projects/{id}/materials：添加项目材料

### 5.7 报表接口

- GET /api/reports/sales：销售报表
- GET /api/reports/inventory：库存报表
- GET /api/reports/customers：客户报表
- GET /api/reports/projects：项目报表
- GET /api/export/{report_type}：导出报表

## 6. 安全设计

1. **认证安全**：
   - 密码加密存储（bcrypt）
   - 会话管理
   - CSRF防护

2. **授权控制**：
   - 基于角色的访问控制（RBAC）
   - API权限验证
   - 操作日志记录

3. **数据安全**：
   - 输入验证
   - SQL注入防护
   - XSS防护

## 7. 多语言支持

- 使用Flask-Babel实现国际化
- 所有界面文本存储在语言文件中
- 支持中文和英文切换
- 使用国旗图标作为语言切换按钮

## 8. 部署架构

- 开发环境：本地开发服务器
- 生产环境：Web服务器 + 应用服务器 + 数据库服务器
- 数据备份策略：定时备份数据库
