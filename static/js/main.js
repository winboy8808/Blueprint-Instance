// 主要JavaScript功能

// 文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 移动端菜单切换
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                if (window.getComputedStyle(sidebar).display === 'none') {
                    sidebar.style.display = 'block';
                } else {
                    sidebar.style.display = 'none';
                }
            }
        });
    }

    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // 表格搜索功能
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const table = document.querySelector('.table');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.indexOf(searchText) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // 导出报表功能
    const exportButtons = document.querySelectorAll('.export-report');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const reportType = this.getAttribute('data-report');
            let url = `/export/${reportType}`;
            
            // 如果是销售报表，添加日期参数
            if (reportType === 'sales') {
                const startDate = document.getElementById('start_date').value;
                const endDate = document.getElementById('end_date').value;
                if (startDate && endDate) {
                    url += `?start_date=${startDate}&end_date=${endDate}`;
                }
            }
            
            // 发送AJAX请求
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 创建下载链接
                        const link = document.createElement('a');
                        link.href = data.filename;
                        link.download = data.filename.split('/').pop();
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        // 显示成功消息
                        const alertContainer = document.createElement('div');
                        alertContainer.className = 'alert alert-success alert-dismissible fade show';
                        alertContainer.innerHTML = `
                            报表导出成功！
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.querySelector('.main-content').prepend(alertContainer);
                        
                        // 自动关闭提示
                        setTimeout(function() {
                            const closeButton = alertContainer.querySelector('.btn-close');
                            if (closeButton) {
                                closeButton.click();
                            }
                        }, 5000);
                    } else {
                        // 显示错误消息
                        const alertContainer = document.createElement('div');
                        alertContainer.className = 'alert alert-danger alert-dismissible fade show';
                        alertContainer.innerHTML = `
                            报表导出失败：${data.message || '未知错误'}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.querySelector('.main-content').prepend(alertContainer);
                    }
                })
                .catch(error => {
                    console.error('导出报表出错:', error);
                    // 显示错误消息
                    const alertContainer = document.createElement('div');
                    alertContainer.className = 'alert alert-danger alert-dismissible fade show';
                    alertContainer.innerHTML = `
                        报表导出失败：网络错误
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.querySelector('.main-content').prepend(alertContainer);
                });
        });
    });

    // 销售订单添加商品计算
    const quantityInput = document.getElementById('quantity');
    const productSelect = document.getElementById('product_id');
    const unitPriceSpan = document.getElementById('unit_price');
    const amountSpan = document.getElementById('amount');
    
    if (quantityInput && productSelect && unitPriceSpan && amountSpan) {
        // 产品选择变化时更新单价
        productSelect.addEventListener('change', updatePrice);
        // 数量变化时更新金额
        quantityInput.addEventListener('input', updateAmount);
        
        function updatePrice() {
            const selectedOption = productSelect.options[productSelect.selectedIndex];
            const price = selectedOption.getAttribute('data-price');
            if (price) {
                unitPriceSpan.textContent = parseFloat(price).toFixed(2);
                updateAmount();
            } else {
                unitPriceSpan.textContent = '0.00';
                amountSpan.textContent = '0.00';
            }
        }
        
        function updateAmount() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(unitPriceSpan.textContent) || 0;
            const amount = quantity * price;
            amountSpan.textContent = amount.toFixed(2);
        }
        
        // 初始化价格和金额
        updatePrice();
    }

    // 订单折扣计算
    const discountInput = document.getElementById('discount');
    const totalAmountSpan = document.getElementById('total_amount');
    const actualAmountSpan = document.getElementById('actual_amount');
    
    if (discountInput && totalAmountSpan && actualAmountSpan) {
        discountInput.addEventListener('input', updateActualAmount);
        
        function updateActualAmount() {
            const totalAmount = parseFloat(totalAmountSpan.textContent) || 0;
            const discount = parseFloat(discountInput.value) || 0;
            const actualAmount = totalAmount - discount;
            actualAmountSpan.textContent = actualAmount.toFixed(2);
        }
    }

    // 日期选择器初始化
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });

    // 打印功能
    const printButtons = document.querySelectorAll('.print-button');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.print();
        });
    });
});
