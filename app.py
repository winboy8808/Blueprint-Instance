from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import json
import pandas as pd
from sqlalchemy import func

# 创建应用实例
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 初始化多语言支持
babel = Babel(app)

@babel.localeselector
def get_locale():
    # 如果用户已设置语言偏好，则使用用户设置
    if 'language' in session:
        return session['language']
    # 默认使用中文
    return 'zh'

# 数据模型定义
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text)  # JSON格式存储权限
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def get_permissions(self):
        return json.loads(self.permissions) if self.permissions else []

class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    products = db.relationship('Product', backref='category', lazy='dynamic')
    subcategories = db.relationship('ProductCategory', backref=db.backref('parent', remote_side=[id]))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    specification = db.Column(db.String(100))
    unit = db.Column(db.String(20))
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    min_stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    inventory = db.relationship('Inventory', backref='product', uselist=False)
    inventory_records = db.relationship('InventoryRecord', backref='product', lazy='dynamic')
    sales_items = db.relationship('SalesOrderItem', backref='product', lazy='dynamic')
    project_materials = db.relationship('ProjectMaterial', backref='product', lazy='dynamic')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), unique=True)
    quantity = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

class InventoryRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    type = db.Column(db.String(10))  # 入库/出库
    quantity = db.Column(db.Integer)
    source_type = db.Column(db.String(20))  # 采购/销售/调整
    source_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    user = db.relationship('User', backref='inventory_records')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    type = db.Column(db.String(20))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy='dynamic')
    projects = db.relationship('Project', backref='customer', lazy='dynamic')

class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    order_date = db.Column(db.Date, default=datetime.date.today)
    total_amount = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    actual_amount = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(20))  # 现金/扫码美金
    payment_status = db.Column(db.String(20), default='未支付')  # 未支付/已支付/部分支付
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    items = db.relationship('SalesOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='sales_orders')

class SalesOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    discount = db.Column(db.Float, default=0)
    amount = db.Column(db.Float)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='未开始')  # 未开始/进行中/已完成
    budget = db.Column(db.Float)
    actual_cost = db.Column(db.Float, default=0)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    materials = db.relationship('ProjectMaterial', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    manager = db.relationship('User', backref='managed_projects')

class ProjectMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    planned_quantity = db.Column(db.Integer)
    actual_quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='未领用')  # 未领用/已领用/已退回
    remarks = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由定义
@app.route('/')
@login_required
def index():
    # 获取统计数据
    product_count = Product.query.count()
    customer_count = Customer.query.count()
    sales_count = SalesOrder.query.count()
    project_count = Project.query.count()
    
    # 获取库存预警产品
    inventory_warning = db.session.query(Product, Inventory).join(Inventory).filter(
        Inventory.quantity <= Product.min_stock
    ).all()
    
    # 获取最近销售订单
    recent_sales = SalesOrder.query.order_by(SalesOrder.created_at.desc()).limit(5).all()
    
    # 获取进行中的项目
    ongoing_projects = Project.query.filter_by(status='进行中').all()
    
    return render_template('index.html', 
                          product_count=product_count,
                          customer_count=customer_count,
                          sales_count=sales_count,
                          project_count=project_count,
                          inventory_warning=inventory_warning,
                          recent_sales=recent_sales,
                          ongoing_projects=ongoing_projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.status:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash(_('Invalid username or password'), 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

# 产品管理路由
@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    categories = ProductCategory.query.all()
    return render_template('products/index.html', products=products, categories=categories)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        specification = request.form.get('specification')
        unit = request.form.get('unit')
        purchase_price = request.form.get('purchase_price')
        selling_price = request.form.get('selling_price')
        min_stock = request.form.get('min_stock')
        description = request.form.get('description')
        
        # 检查产品编码是否已存在
        if Product.query.filter_by(code=code).first():
            flash(_('Product code already exists'), 'danger')
            return redirect(url_for('add_product'))
        
        product = Product(
            code=code,
            name=name,
            category_id=category_id,
            specification=specification,
            unit=unit,
            purchase_price=float(purchase_price) if purchase_price else 0,
            selling_price=float(selling_price) if selling_price else 0,
            min_stock=int(min_stock) if min_stock else 0,
            description=description
        )
        
        db.session.add(product)
        db.session.commit()
        
        # 创建库存记录
        inventory = Inventory(product_id=product.id, quantity=0)
        db.session.add(inventory)
        db.session.commit()
        
        flash(_('Product added successfully'), 'success')
        return redirect(url_for('products'))
    
    categories = ProductCategory.query.all()
    return render_template('products/add.html', categories=categories)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category_id = request.form.get('category_id')
        product.specification = request.form.get('specification')
        product.unit = request.form.get('unit')
        product.purchase_price = float(request.form.get('purchase_price')) if request.form.get('purchase_price') else 0
        product.selling_price = float(request.form.get('selling_price')) if request.form.get('selling_price') else 0
        product.min_stock = int(request.form.get('min_stock')) if request.form.get('min_stock') else 0
        product.description = request.form.get('description')
        
        db.session.commit()
        flash(_('Product updated successfully'), 'success')
        return redirect(url_for('products'))
    
    categories = ProductCategory.query.all()
    return render_template('products/edit.html', product=product, categories=categories)

@app.route('/products/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # 检查是否有关联的销售订单或项目
    if SalesOrderItem.query.filter_by(product_id=id).first() or ProjectMaterial.query.filter_by(product_id=id).first():
        flash(_('Cannot delete product with associated sales or projects'), 'danger')
        return redirect(url_for('products'))
    
    # 删除库存记录
    inventory = Inventory.query.filter_by(product_id=id).first()
    if inventory:
        db.session.delete(inventory)
    
    # 删除库存历史记录
    InventoryRecord.query.filter_by(product_id=id).delete()
    
    db.session.delete(product)
    db.session.commit()
    
    flash(_('Product deleted successfully'), 'success')
    return redirect(url_for('products'))

# 库存管理路由
@app.route('/inventory')
@login_required
def inventory():
    inventory = db.session.query(Product, Inventory).join(Inventory).all()
    return render_template('inventory/index.html', inventory=inventory)

@app.route('/inventory/in', methods=['GET', 'POST'])
@login_required
def inventory_in():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        remarks = request.form.get('remarks')
        
        # 更新库存
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        if inventory:
            inventory.quantity += quantity
        else:
            inventory = Inventory(product_id=product_id, quantity=quantity)
            db.session.add(inventory)
        
        # 添加库存记录
        record = InventoryRecord(
            product_id=product_id,
            type='入库',
            quantity=quantity,
            source_type='采购',
            user_id=current_user.id,
            remarks=remarks
        )
        
        db.session.add(record)
        db.session.commit()
        
        flash(_('Inventory updated successfully'), 'success')
        return redirect(url_for('inventory'))
    
    products = Product.query.all()
    return render_template('inventory/in.html', products=products)

@app.route('/inventory/out', methods=['GET', 'POST'])
@login_required
def inventory_out():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        source_type = request.form.get('source_type')
        remarks = request.form.get('remarks')
        
        # 检查库存是否足够
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory or inventory.quantity < quantity:
            flash(_('Insufficient inventory'), 'danger')
            return redirect(url_for('inventory_out'))
        
        # 更新库存
        inventory.quantity -= quantity
        
        # 添加库存记录
        record = InventoryRecord(
            product_id=product_id,
            type='出库',
            quantity=quantity,
            source_type=source_type,
            user_id=current_user.id,
            remarks=remarks
        )
        
        db.session.add(record)
        db.session.commit()
        
        flash(_('Inventory updated successfully'), 'success')
        return redirect(url_for('inventory'))
    
    products = Product.query.all()
    return render_template('inventory/out.html', products=products)

@app.route('/inventory/records')
@login_required
def inventory_records():
    records = db.session.query(InventoryRecord, Product, User).join(
        Product, InventoryRecord.product_id == Product.id
    ).join(
        User, InventoryRecord.user_id == User.id
    ).order_by(InventoryRecord.created_at.desc()).all()
    
    return render_template('inventory/records.html', records=records)

# 客户管理路由
@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template('customers/index.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        type = request.form.get('type')
        remarks = request.form.get('remarks')
        
        customer = Customer(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            type=type,
            remarks=remarks
        )
        
        db.session.add(customer)
        db.session.commit()
        
        flash(_('Customer added successfully'), 'success')
        return redirect(url_for('customers'))
    
    return render_template('customers/add.html')

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.contact_person = request.form.get('contact_person')
        customer.phone = request.form.get('phone')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        customer.type = request.form.get('type')
        customer.remarks = request.form.get('remarks')
        
        db.session.commit()
        flash(_('Customer updated successfully'), 'success')
        return redirect(url_for('customers'))
    
    return render_template('customers/edit.html', customer=customer)

@app.route('/customers/delete/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    
    # 检查是否有关联的销售订单或项目
    if SalesOrder.query.filter_by(customer_id=id).first() or Project.query.filter_by(customer_id=id).first():
        flash(_('Cannot delete customer with associated sales or projects'), 'danger')
        return redirect(url_for('customers'))
    
    db.session.delete(customer)
    db.session.commit()
    
    flash(_('Customer deleted successfully'), 'success')
    return redirect(url_for('customers'))

# 销售管理路由
@app.route('/sales')
@login_required
def sales():
    sales = db.session.query(SalesOrder, Customer).join(
        Customer, SalesOrder.customer_id == Customer.id
    ).order_by(SalesOrder.created_at.desc()).all()
    
    return render_template('sales/index.html', sales=sales)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        payment_method = request.form.get('payment_method')
        remarks = request.form.get('remarks')
        
        # 生成订单编号
        order_no = 'SO' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 创建销售订单
        order = SalesOrder(
            order_no=order_no,
            customer_id=customer_id,
            payment_method=payment_method,
            user_id=current_user.id,
            remarks=remarks
        )
        
        db.session.add(order)
        db.session.commit()
        
        flash(_('Sales order created successfully'), 'success')
        return redirect(url_for('edit_sale', id=order.id))
    
    customers = Customer.query.all()
    return render_template('sales/add.html', customers=customers)

@app.route('/sales/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sale(id):
    order = SalesOrder.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'add_item' in request.form:
            # 添加订单项
            product_id = request.form.get('product_id')
            quantity = int(request.form.get('quantity'))
            
            # 获取产品信息
            product = Product.query.get(product_id)
            if not product:
                flash(_('Product not found'), 'danger')
                return redirect(url_for('edit_sale', id=id))
            
            # 检查库存
            inventory = Inventory.query.filter_by(product_id=product_id).first()
            if not inventory or inventory.quantity < quantity:
                flash(_('Insufficient inventory'), 'danger')
                return redirect(url_for('edit_sale', id=id))
            
            # 计算金额
            unit_price = product.selling_price
            amount = unit_price * quantity
            
            # 创建订单项
            item = SalesOrderItem(
                order_id=id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                amount=amount
            )
            
            db.session.add(item)
            
            # 更新订单总金额
            order.total_amount += amount
            order.actual_amount = order.total_amount - order.discount
            
            # 更新库存
            inventory.quantity -= quantity
            
            # 添加库存记录
            record = InventoryRecord(
                product_id=product_id,
                type='出库',
                quantity=quantity,
                source_type='销售',
                source_id=id,
                user_id=current_user.id,
                remarks=f'销售订单 {order.order_no}'
            )
            
            db.session.add(record)
            db.session.commit()
            
            flash(_('Item added to order'), 'success')
            return redirect(url_for('edit_sale', id=id))
        
        elif 'update_order' in request.form:
            # 更新订单信息
            discount = float(request.form.get('discount')) if request.form.get('discount') else 0
            payment_status = request.form.get('payment_status')
            remarks = request.form.get('remarks')
            
            order.discount = discount
            order.actual_amount = order.total_amount - discount
            order.payment_status = payment_status
            order.remarks = remarks
            
            db.session.commit()
            
            flash(_('Order updated successfully'), 'success')
            return redirect(url_for('sales'))
    
    products = Product.query.all()
    items = db.session.query(SalesOrderItem, Product).join(
        Product, SalesOrderItem.product_id == Product.id
    ).filter(SalesOrderItem.order_id == id).all()
    
    return render_template('sales/edit.html', order=order, products=products, items=items)

@app.route('/sales/delete_item/<int:id>')
@login_required
def delete_sale_item(id):
    item = SalesOrderItem.query.get_or_404(id)
    order_id = item.order_id
    order = SalesOrder.query.get(order_id)
    
    # 更新订单总金额
    order.total_amount -= item.amount
    order.actual_amount = order.total_amount - order.discount
    
    # 恢复库存
    inventory = Inventory.query.filter_by(product_id=item.product_id).first()
    if inventory:
        inventory.quantity += item.quantity
    
    # 添加库存记录
    record = InventoryRecord(
        product_id=item.product_id,
        type='入库',
        quantity=item.quantity,
        source_type='销售退回',
        source_id=order_id,
        user_id=current_user.id,
        remarks=f'从销售订单 {order.order_no} 中删除项目'
    )
    
    db.session.add(record)
    db.session.delete(item)
    db.session.commit()
    
    flash(_('Item removed from order'), 'success')
    return redirect(url_for('edit_sale', id=order_id))

@app.route('/sales/view/<int:id>')
@login_required
def view_sale(id):
    order = SalesOrder.query.get_or_404(id)
    customer = Customer.query.get(order.customer_id)
    items = db.session.query(SalesOrderItem, Product).join(
        Product, SalesOrderItem.product_id == Product.id
    ).filter(SalesOrderItem.order_id == id).all()
    
    return render_template('sales/view.html', order=order, customer=customer, items=items)

@app.route('/sales/delete/<int:id>')
@login_required
def delete_sale(id):
    order = SalesOrder.query.get_or_404(id)
    
    # 恢复库存
    for item in order.items:
        inventory = Inventory.query.filter_by(product_id=item.product_id).first()
        if inventory:
            inventory.quantity += item.quantity
        
        # 添加库存记录
        record = InventoryRecord(
            product_id=item.product_id,
            type='入库',
            quantity=item.quantity,
            source_type='销售取消',
            source_id=id,
            user_id=current_user.id,
            remarks=f'取消销售订单 {order.order_no}'
        )
        
        db.session.add(record)
    
    db.session.delete(order)
    db.session.commit()
    
    flash(_('Sales order deleted successfully'), 'success')
    return redirect(url_for('sales'))

# 工程项目管理路由
@app.route('/projects')
@login_required
def projects():
    projects = db.session.query(Project, Customer, User).join(
        Customer, Project.customer_id == Customer.id
    ).join(
        User, Project.manager_id == User.id
    ).all()
    
    return render_template('projects/index.html', projects=projects)

@app.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        customer_id = request.form.get('customer_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        manager_id = request.form.get('manager_id')
        description = request.form.get('description')
        
        project = Project(
            name=name,
            customer_id=customer_id,
            start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            budget=float(budget) if budget else 0,
            manager_id=manager_id,
            description=description
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash(_('Project added successfully'), 'success')
        return redirect(url_for('projects'))
    
    customers = Customer.query.all()
    managers = User.query.all()
    return render_template('projects/add.html', customers=customers, managers=managers)

@app.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'update_project' in request.form:
            project.name = request.form.get('name')
            project.customer_id = request.form.get('customer_id')
            project.start_date = datetime.datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date() if request.form.get('start_date') else None
            project.end_date = datetime.datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None
            project.status = request.form.get('status')
            project.budget = float(request.form.get('budget')) if request.form.get('budget') else 0
            project.manager_id = request.form.get('manager_id')
            project.description = request.form.get('description')
            
            db.session.commit()
            flash(_('Project updated successfully'), 'success')
            return redirect(url_for('projects'))
        
        elif 'add_material' in request.form:
            product_id = request.form.get('product_id')
            planned_quantity = int(request.form.get('planned_quantity'))
            unit_price = float(request.form.get('unit_price'))
            remarks = request.form.get('remarks')
            
            material = ProjectMaterial(
                project_id=id,
                product_id=product_id,
                planned_quantity=planned_quantity,
                unit_price=unit_price,
                remarks=remarks
            )
            
            db.session.add(material)
            
            # 更新项目成本
            project.actual_cost += planned_quantity * unit_price
            
            db.session.commit()
            flash(_('Material added to project'), 'success')
            return redirect(url_for('edit_project', id=id))
    
    customers = Customer.query.all()
    managers = User.query.all()
    products = Product.query.all()
    materials = db.session.query(ProjectMaterial, Product).join(
        Product, ProjectMaterial.product_id == Product.id
    ).filter(ProjectMaterial.project_id == id).all()
    
    return render_template('projects/edit.html', 
                          project=project, 
                          customers=customers, 
                          managers=managers,
                          products=products,
                          materials=materials)

@app.route('/projects/delete_material/<int:id>')
@login_required
def delete_project_material(id):
    material = ProjectMaterial.query.get_or_404(id)
    project_id = material.project_id
    project = Project.query.get(project_id)
    
    # 更新项目成本
    project.actual_cost -= material.planned_quantity * material.unit_price
    
    db.session.delete(material)
    db.session.commit()
    
    flash(_('Material removed from project'), 'success')
    return redirect(url_for('edit_project', id=project_id))

@app.route('/projects/view/<int:id>')
@login_required
def view_project(id):
    project = Project.query.get_or_404(id)
    customer = Customer.query.get(project.customer_id)
    manager = User.query.get(project.manager_id)
    materials = db.session.query(ProjectMaterial, Product).join(
        Product, ProjectMaterial.product_id == Product.id
    ).filter(ProjectMaterial.project_id == id).all()
    
    return render_template('projects/view.html', 
                          project=project, 
                          customer=customer, 
                          manager=manager,
                          materials=materials)

@app.route('/projects/delete/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    
    db.session.delete(project)
    db.session.commit()
    
    flash(_('Project deleted successfully'), 'success')
    return redirect(url_for('projects'))

# 用户管理路由
@app.route('/users')
@login_required
def users():
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    users = db.session.query(User, Role).join(
        Role, User.role_id == Role.id
    ).all()
    
    return render_template('users/index.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role_id = request.form.get('role_id')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash(_('Username already exists'), 'danger')
            return redirect(url_for('add_user'))
        
        user = User(
            username=username,
            name=name,
            email=email,
            phone=phone,
            role_id=role_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('User added successfully'), 'success')
        return redirect(url_for('users'))
    
    roles = Role.query.all()
    return render_template('users/add.html', roles=roles)

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin' and current_user.id != id:
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        
        # 只有管理员可以修改角色
        if current_user.role.name == 'Admin':
            user.role_id = request.form.get('role_id')
            user.status = 'status' in request.form
        
        # 如果提供了新密码
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash(_('User updated successfully'), 'success')
        return redirect(url_for('users') if current_user.role.name == 'Admin' else url_for('index'))
    
    roles = Role.query.all()
    return render_template('users/edit.html', user=user, roles=roles)

@app.route('/users/delete/<int:id>')
@login_required
def delete_user(id):
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    
    # 不能删除自己
    if user.id == current_user.id:
        flash(_('You cannot delete your own account'), 'danger')
        return redirect(url_for('users'))
    
    # 检查是否有关联的销售订单或项目
    if SalesOrder.query.filter_by(user_id=id).first() or Project.query.filter_by(manager_id=id).first():
        flash(_('Cannot delete user with associated sales or projects'), 'danger')
        return redirect(url_for('users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(_('User deleted successfully'), 'success')
    return redirect(url_for('users'))

# 角色管理路由
@app.route('/roles')
@login_required
def roles():
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    roles = Role.query.all()
    return render_template('roles/index.html', roles=roles)

@app.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # 获取权限
        permissions = []
        for key in request.form:
            if key.startswith('perm_'):
                permissions.append(key[5:])
        
        # 检查角色名是否已存在
        if Role.query.filter_by(name=name).first():
            flash(_('Role name already exists'), 'danger')
            return redirect(url_for('add_role'))
        
        role = Role(
            name=name,
            description=description,
            permissions=json.dumps(permissions)
        )
        
        db.session.add(role)
        db.session.commit()
        
        flash(_('Role added successfully'), 'success')
        return redirect(url_for('roles'))
    
    return render_template('roles/add.html')

@app.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    role = Role.query.get_or_404(id)
    
    if request.method == 'POST':
        role.name = request.form.get('name')
        role.description = request.form.get('description')
        
        # 获取权限
        permissions = []
        for key in request.form:
            if key.startswith('perm_'):
                permissions.append(key[5:])
        
        role.permissions = json.dumps(permissions)
        
        db.session.commit()
        flash(_('Role updated successfully'), 'success')
        return redirect(url_for('roles'))
    
    permissions = role.get_permissions()
    return render_template('roles/edit.html', role=role, permissions=permissions)

@app.route('/roles/delete/<int:id>')
@login_required
def delete_role(id):
    # 检查是否有管理员权限
    if current_user.role.name != 'Admin':
        flash(_('You do not have permission to access this page'), 'danger')
        return redirect(url_for('index'))
    
    role = Role.query.get_or_404(id)
    
    # 检查是否有关联的用户
    if User.query.filter_by(role_id=id).first():
        flash(_('Cannot delete role with associated users'), 'danger')
        return redirect(url_for('roles'))
    
    db.session.delete(role)
    db.session.commit()
    
    flash(_('Role deleted successfully'), 'success')
    return redirect(url_for('roles'))

# 报表和数据导出路由
@app.route('/reports')
@login_required
def reports():
    return render_template('reports/index.html')

@app.route('/reports/sales', methods=['GET', 'POST'])
@login_required
def sales_report():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # 转换日期格式
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.date(1900, 1, 1)
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else datetime.date(2100, 12, 31)
        
        # 查询销售数据
        sales = db.session.query(SalesOrder, Customer).join(
            Customer, SalesOrder.customer_id == Customer.id
        ).filter(
            SalesOrder.order_date >= start,
            SalesOrder.order_date <= end
        ).order_by(SalesOrder.order_date.desc()).all()
        
        # 计算统计数据
        total_sales = sum(order.actual_amount for order, _ in sales)
        total_orders = len(sales)
        
        # 按支付方式统计
        payment_stats = db.session.query(
            SalesOrder.payment_method,
            func.count(SalesOrder.id).label('count'),
            func.sum(SalesOrder.actual_amount).label('total')
        ).filter(
            SalesOrder.order_date >= start,
            SalesOrder.order_date <= end
        ).group_by(SalesOrder.payment_method).all()
        
        # 按客户统计
        customer_stats = db.session.query(
            Customer.name,
            func.count(SalesOrder.id).label('count'),
            func.sum(SalesOrder.actual_amount).label('total')
        ).join(
            Customer, SalesOrder.customer_id == Customer.id
        ).filter(
            SalesOrder.order_date >= start,
            SalesOrder.order_date <= end
        ).group_by(Customer.name).all()
        
        return render_template('reports/sales.html', 
                              sales=sales, 
                              total_sales=total_sales,
                              total_orders=total_orders,
                              payment_stats=payment_stats,
                              customer_stats=customer_stats,
                              start_date=start_date,
                              end_date=end_date)
    
    return render_template('reports/sales.html')

@app.route('/reports/inventory')
@login_required
def inventory_report():
    # 查询库存数据
    inventory = db.session.query(Product, Inventory, ProductCategory).join(
        Inventory, Product.id == Inventory.product_id
    ).join(
        ProductCategory, Product.category_id == ProductCategory.id
    ).all()
    
    # 计算统计数据
    total_products = len(inventory)
    total_value = sum(product.purchase_price * inv.quantity for product, inv, _ in inventory)
    
    # 按分类统计
    category_stats = {}
    for product, inv, category in inventory:
        if category.name not in category_stats:
            category_stats[category.name] = {
                'count': 0,
                'value': 0
            }
        category_stats[category.name]['count'] += 1
        category_stats[category.name]['value'] += product.purchase_price * inv.quantity
    
    # 库存预警
    warnings = [
        (product, inv, category) for product, inv, category in inventory
        if inv.quantity <= product.min_stock
    ]
    
    return render_template('reports/inventory.html', 
                          inventory=inventory, 
                          total_products=total_products,
                          total_value=total_value,
                          category_stats=category_stats,
                          warnings=warnings)

@app.route('/reports/customers')
@login_required
def customers_report():
    # 查询客户数据
    customers = Customer.query.all()
    
    # 计算统计数据
    total_customers = len(customers)
    
    # 按类型统计
    type_stats = {}
    for customer in customers:
        if customer.type not in type_stats:
            type_stats[customer.type] = 0
        type_stats[customer.type] += 1
    
    # 客户购买统计
    purchase_stats = db.session.query(
        Customer.id,
        Customer.name,
        func.count(SalesOrder.id).label('order_count'),
        func.sum(SalesOrder.actual_amount).label('total_amount')
    ).outerjoin(
        SalesOrder, Customer.id == SalesOrder.customer_id
    ).group_by(Customer.id).all()
    
    return render_template('reports/customers.html', 
                          customers=customers, 
                          total_customers=total_customers,
                          type_stats=type_stats,
                          purchase_stats=purchase_stats)

@app.route('/reports/projects')
@login_required
def projects_report():
    # 查询项目数据
    projects = db.session.query(Project, Customer, User).join(
        Customer, Project.customer_id == Customer.id
    ).join(
        User, Project.manager_id == User.id
    ).all()
    
    # 计算统计数据
    total_projects = len(projects)
    total_budget = sum(project.budget for project, _, _ in projects)
    total_cost = sum(project.actual_cost for project, _, _ in projects)
    
    # 按状态统计
    status_stats = {}
    for project, _, _ in projects:
        if project.status not in status_stats:
            status_stats[project.status] = {
                'count': 0,
                'budget': 0,
                'cost': 0
            }
        status_stats[project.status]['count'] += 1
        status_stats[project.status]['budget'] += project.budget
        status_stats[project.status]['cost'] += project.actual_cost
    
    return render_template('reports/projects.html', 
                          projects=projects, 
                          total_projects=total_projects,
                          total_budget=total_budget,
                          total_cost=total_cost,
                          status_stats=status_stats)

@app.route('/export/<report_type>')
@login_required
def export_report(report_type):
    if report_type == 'sales':
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 转换日期格式
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.date(1900, 1, 1)
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else datetime.date(2100, 12, 31)
        
        # 查询销售数据
        sales = db.session.query(
            SalesOrder.order_no,
            SalesOrder.order_date,
            Customer.name.label('customer_name'),
            SalesOrder.total_amount,
            SalesOrder.discount,
            SalesOrder.actual_amount,
            SalesOrder.payment_method,
            SalesOrder.payment_status,
            User.name.label('salesperson'),
            SalesOrder.remarks
        ).join(
            Customer, SalesOrder.customer_id == Customer.id
        ).join(
            User, SalesOrder.user_id == User.id
        ).filter(
            SalesOrder.order_date >= start,
            SalesOrder.order_date <= end
        ).all()
        
        # 创建DataFrame
        df = pd.DataFrame([
            {
                '订单编号': s.order_no,
                '订单日期': s.order_date,
                '客户名称': s.customer_name,
                '总金额': s.total_amount,
                '折扣': s.discount,
                '实际金额': s.actual_amount,
                '支付方式': s.payment_method,
                '支付状态': s.payment_status,
                '销售员': s.salesperson,
                '备注': s.remarks
            } for s in sales
        ])
        
        # 导出到Excel
        filename = f'sales_report_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        filepath = os.path.join(app.root_path, 'static', 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_excel(filepath, index=False)
        
        return jsonify({'success': True, 'filename': url_for('static', filename=f'exports/{filename}')})
    
    elif report_type == 'inventory':
        # 查询库存数据
        inventory = db.session.query(
            Product.code,
            Product.name,
            ProductCategory.name.label('category'),
            Product.specification,
            Product.unit,
            Inventory.quantity,
            Product.purchase_price,
            Product.selling_price,
            (Product.purchase_price * Inventory.quantity).label('value')
        ).join(
            Inventory, Product.id == Inventory.product_id
        ).join(
            ProductCategory, Product.category_id == ProductCategory.id
        ).all()
        
        # 创建DataFrame
        df = pd.DataFrame([
            {
                '产品编码': i.code,
                '产品名称': i.name,
                '分类': i.category,
                '规格': i.specification,
                '单位': i.unit,
                '库存数量': i.quantity,
                '采购价': i.purchase_price,
                '销售价': i.selling_price,
                '库存价值': i.value
            } for i in inventory
        ])
        
        # 导出到Excel
        filename = f'inventory_report_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        filepath = os.path.join(app.root_path, 'static', 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_excel(filepath, index=False)
        
        return jsonify({'success': True, 'filename': url_for('static', filename=f'exports/{filename}')})
    
    elif report_type == 'customers':
        # 查询客户数据
        customers = db.session.query(
            Customer.name,
            Customer.contact_person,
            Customer.phone,
            Customer.email,
            Customer.address,
            Customer.type,
            func.count(SalesOrder.id).label('order_count'),
            func.sum(SalesOrder.actual_amount).label('total_amount')
        ).outerjoin(
            SalesOrder, Customer.id == SalesOrder.customer_id
        ).group_by(Customer.id).all()
        
        # 创建DataFrame
        df = pd.DataFrame([
            {
                '客户名称': c.name,
                '联系人': c.contact_person,
                '电话': c.phone,
                '邮箱': c.email,
                '地址': c.address,
                '客户类型': c.type,
                '订单数量': c.order_count or 0,
                '消费总额': c.total_amount or 0
            } for c in customers
        ])
        
        # 导出到Excel
        filename = f'customers_report_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        filepath = os.path.join(app.root_path, 'static', 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_excel(filepath, index=False)
        
        return jsonify({'success': True, 'filename': url_for('static', filename=f'exports/{filename}')})
    
    elif report_type == 'projects':
        # 查询项目数据
        projects = db.session.query(
            Project.name,
            Customer.name.label('customer_name'),
            Project.start_date,
            Project.end_date,
            Project.status,
            Project.budget,
            Project.actual_cost,
            User.name.label('manager'),
            Project.description
        ).join(
            Customer, Project.customer_id == Customer.id
        ).join(
            User, Project.manager_id == User.id
        ).all()
        
        # 创建DataFrame
        df = pd.DataFrame([
            {
                '项目名称': p.name,
                '客户名称': p.customer_name,
                '开始日期': p.start_date,
                '结束日期': p.end_date,
                '状态': p.status,
                '预算': p.budget,
                '实际成本': p.actual_cost,
                '项目经理': p.manager,
                '描述': p.description
            } for p in projects
        ])
        
        # 导出到Excel
        filename = f'projects_report_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        filepath = os.path.join(app.root_path, 'static', 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_excel(filepath, index=False)
        
        return jsonify({'success': True, 'filename': url_for('static', filename=f'exports/{filename}')})
    
    return jsonify({'success': False, 'message': 'Invalid report type'})

# 初始化数据库
@app.before_first_request
def init_db():
    db.create_all()
    
    # 检查是否已有管理员角色
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        # 创建角色
        admin_role = Role(
            name='Admin',
            description='系统管理员',
            permissions=json.dumps(['all'])
        )
        db.session.add(admin_role)
        
        sales_role = Role(
            name='Sales',
            description='销售人员',
            permissions=json.dumps(['sales', 'customers', 'inventory_view', 'reports_view'])
        )
        db.session.add(sales_role)
        
        inventory_role = Role(
            name='Inventory',
            description='库存管理员',
            permissions=json.dumps(['products', 'inventory', 'reports_view'])
        )
        db.session.add(inventory_role)
        
        project_role = Role(
            name='Project',
            description='项目经理',
            permissions=json.dumps(['projects', 'inventory_view', 'reports_view'])
        )
        db.session.add(project_role)
        
        db.session.commit()
        
        # 创建管理员用户
        admin_user = User(
            username='admin',
            name='系统管理员',
            email='admin@example.com',
            role_id=admin_role.id
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
