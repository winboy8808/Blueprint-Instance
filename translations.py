from flask_babel import lazy_gettext as _

# 中文翻译
zh_translations = {
    'Hardware CRM System': '五金CRM系统',
    'Dashboard': '仪表盘',
    'Products': '产品管理',
    'Inventory': '库存管理',
    'Sales': '销售管理',
    'Customers': '客户管理',
    'Projects': '工程项目',
    'Reports': '报表统计',
    'User Management': '用户管理',
    'Profile': '个人资料',
    'Logout': '退出登录',
    'Login': '登录',
    'Username': '用户名',
    'Password': '密码',
    'Inventory Warnings': '库存预警',
    'Recent Sales': '最近销售',
    'Ongoing Projects': '进行中的项目',
    'No inventory warnings': '没有库存预警',
    'No recent sales': '没有最近销售',
    'No ongoing projects': '没有进行中的项目',
    'Code': '编码',
    'Product': '产品',
    'Current Stock': '当前库存',
    'Min Stock': '最低库存',
    'Order No': '订单编号',
    'Date': '日期',
    'Amount': '金额',
    'Status': '状态',
    'Project Name': '项目名称',
    'Start Date': '开始日期',
    'End Date': '结束日期',
    'Budget': '预算',
    'Current Cost': '当前成本',
    'Progress': '进度',
    'Add Product': '添加产品',
    'Edit Product': '编辑产品',
    'Product List': '产品列表',
    'Product Information': '产品信息',
    'Product Code': '产品编码',
    'Product Name': '产品名称',
    'Category': '分类',
    'Specification': '规格',
    'Unit': '单位',
    'Purchase Price': '采购价',
    'Selling Price': '销售价',
    'Min Stock Level': '最低库存量',
    'Description': '描述',
    'Save': '保存',
    'Cancel': '取消',
    'Delete': '删除',
    'Back': '返回',
    'Search': '搜索',
    'Actions': '操作',
    'Inventory List': '库存列表',
    'Stock In': '入库',
    'Stock Out': '出库',
    'Inventory Records': '库存记录',
    'Product Selection': '产品选择',
    'Quantity': '数量',
    'Source Type': '来源类型',
    'Remarks': '备注',
    'Submit': '提交',
    'Type': '类型',
    'Operator': '操作员',
    'Time': '时间',
    'Customer List': '客户列表',
    'Add Customer': '添加客户',
    'Edit Customer': '编辑客户',
    'Customer Information': '客户信息',
    'Customer Name': '客户名称',
    'Contact Person': '联系人',
    'Phone': '电话',
    'Email': '邮箱',
    'Address': '地址',
    'Customer Type': '客户类型',
    'Sales List': '销售列表',
    'Add Sale': '添加销售',
    'Edit Sale': '编辑销售',
    'Sale Information': '销售信息',
    'Customer': '客户',
    'Payment Method': '支付方式',
    'Payment Status': '支付状态',
    'Discount': '折扣',
    'Total Amount': '总金额',
    'Actual Amount': '实际金额',
    'Add Item': '添加商品',
    'Unit Price': '单价',
    'Project List': '项目列表',
    'Add Project': '添加项目',
    'Edit Project': '编辑项目',
    'Project Information': '项目信息',
    'Manager': '项目经理',
    'Materials': '材料',
    'Add Material': '添加材料',
    'Planned Quantity': '计划数量',
    'Actual Quantity': '实际数量',
    'Material Status': '材料状态',
    'Report Center': '报表中心',
    'Sales Report': '销售报表',
    'Inventory Report': '库存报表',
    'Customer Report': '客户报表',
    'Project Report': '项目报表',
    'Start Date': '开始日期',
    'End Date': '结束日期',
    'Generate Report': '生成报表',
    'Export to Excel': '导出到Excel',
    'User List': '用户列表',
    'Add User': '添加用户',
    'Edit User': '编辑用户',
    'User Information': '用户信息',
    'Name': '姓名',
    'Role': '角色',
    'Status': '状态',
    'New Password': '新密码',
    'Role List': '角色列表',
    'Add Role': '添加角色',
    'Edit Role': '编辑角色',
    'Role Information': '角色信息',
    'Role Name': '角色名称',
    'Permissions': '权限',
    'Invalid username or password': '用户名或密码无效',
    'Product added successfully': '产品添加成功',
    'Product updated successfully': '产品更新成功',
    'Product deleted successfully': '产品删除成功',
    'Inventory updated successfully': '库存更新成功',
    'Insufficient inventory': '库存不足',
    'Customer added successfully': '客户添加成功',
    'Customer updated successfully': '客户更新成功',
    'Customer deleted successfully': '客户删除成功',
    'Sales order created successfully': '销售订单创建成功',
    'Order updated successfully': '订单更新成功',
    'Item added to order': '商品已添加到订单',
    'Item removed from order': '商品已从订单中移除',
    'Sales order deleted successfully': '销售订单删除成功',
    'Project added successfully': '项目添加成功',
    'Project updated successfully': '项目更新成功',
    'Material added to project': '材料已添加到项目',
    'Material removed from project': '材料已从项目中移除',
    'Project deleted successfully': '项目删除成功',
    'User added successfully': '用户添加成功',
    'User updated successfully': '用户更新成功',
    'User deleted successfully': '用户删除成功',
    'Role added successfully': '角色添加成功',
    'Role updated successfully': '角色更新成功',
    'Role deleted successfully': '角色删除成功',
    'Cash': '现金',
    'Mobile Payment (USD)': '扫码美金',
    'Unpaid': '未支付',
    'Paid': '已支付',
    'Partially Paid': '部分支付',
    'Not Started': '未开始',
    'In Progress': '进行中',
    'Completed': '已完成',
    'Purchase': '采购',
    'Sales': '销售',
    'Adjustment': '调整',
    'Sales Return': '销售退回',
    'Sales Cancellation': '销售取消',
    'Unused': '未领用',
    'Used': '已领用',
    'Returned': '已退回',
    'Regular': '普通',
    'VIP': 'VIP',
    'Distributor': '经销商',
    'You do not have permission to access this page': '您没有权限访问此页面',
    'Product code already exists': '产品编码已存在',
    'Cannot delete product with associated sales or projects': '无法删除已关联销售或项目的产品',
    'Cannot delete customer with associated sales or projects': '无法删除已关联销售或项目的客户',
    'Product not found': '产品未找到',
    'Username already exists': '用户名已存在',
    'You cannot delete your own account': '您不能删除自己的账户',
    'Cannot delete user with associated sales or projects': '无法删除已关联销售或项目的用户',
    'Role name already exists': '角色名称已存在',
    'Cannot delete role with associated users': '无法删除已关联用户的角色',
    'Print': '打印',
    'View': '查看',
    'Edit': '编辑',
    'Delete': '删除',
}

# 英文翻译 (默认)
en_translations = {
    key: key for key in zh_translations.keys()
}

def get_translations(locale):
    if locale == 'zh':
        return zh_translations
    return en_translations
