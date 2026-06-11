// 运营端 JavaScript

const API_BASE_URL = 'http://localhost:5000/api';

// 状态映射
const STATUS_MAP = {
    'PENDING': { text: '待处理', class: 'status-pending' },
    'COLLECTED': { text: '已揽收', class: 'status-collected' },
    'TRANSIT': { text: '运输中', class: 'status-transit' },
    'STORED': { text: '已入库', class: 'status-stored' },
    'DELIVERING': { text: '配送中', class: 'status-delivering' },
    'COMPLETED': { text: '已完成', class: 'status-completed' },
    'CANCELLED': { text: '已取消', class: 'status-cancelled' },
    'EXCEPTION': { text: '异常', class: 'status-exception' }
};

const ITEM_TYPE_MAP = {
    'LUGGAGE': '行李箱',
    'DOCUMENT': '文件',
    'PACKAGE': '包裹'
};

const WAREHOUSE_STATUS_MAP = {
    'ACTIVE': { text: '正常', class: 'status-active' },
    'INACTIVE': { text: '停用', class: 'status-inactive' }
};

// 全局数据
let allOrders = [];
let filteredOrders = [];
let allWarehouses = [];
let filteredWarehouses = [];
let currentPage = 1;
let pageSize = 10;
let currentOrderId = null;
let currentTab = 'orders';

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadOrders();
});

// 初始化导航
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item[data-tab]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = item.dataset.tab;
            switchTab(tab);
        });
    });
}

// 切换Tab
function switchTab(tab) {
    // 更新导航状态
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.tab === tab) {
            item.classList.add('active');
        }
    });

    // 更新页面标题
    const pageTitle = document.getElementById('page-title');
    pageTitle.textContent = tab === 'orders' ? '订单管理' : '仓库管理';

    // 切换面板
    document.getElementById('orders-panel').style.display = tab === 'orders' ? 'block' : 'none';
    document.getElementById('warehouses-panel').style.display = tab === 'warehouses' ? 'block' : 'none';

    currentTab = tab;

    // 加载数据
    if (tab === 'orders') {
        loadOrders();
    } else if (tab === 'warehouses') {
        loadWarehouses();
    }
}

// ========== 订单管理 ==========

// 加载订单数据
async function loadOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/orders?page=1&pageSize=1000`, {
            headers: {
                'X-OpenId': 'admin'
            }
        });
        const result = await response.json();

        if (result.code === 0) {
            allOrders = result.data.list;
            applyFilters();
            updateStats();
        }
    } catch (error) {
        console.error('加载订单失败:', error);
        showToast('加载订单失败', 'error');
    }
}

// 刷新订单
function refreshOrders() {
    loadOrders();
    showToast('数据已刷新', 'success');
}

// 更新统计
function updateStats() {
    const stats = {
        total: allOrders.length,
        pending: allOrders.filter(o => o.status === 'PENDING').length,
        delivering: allOrders.filter(o => o.status === 'DELIVERING').length,
        completed: allOrders.filter(o => o.status === 'COMPLETED').length
    };

    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-pending').textContent = stats.pending;
    document.getElementById('stat-delivering').textContent = stats.delivering;
    document.getElementById('stat-completed').textContent = stats.completed;
}

// 应用筛选
function applyFilters() {
    const statusFilter = document.getElementById('filter-status').value;
    const cityFilter = document.getElementById('filter-city').value;
    const searchFilter = document.getElementById('filter-search').value.toLowerCase();

    filteredOrders = allOrders.filter(order => {
        if (statusFilter && order.status !== statusFilter) return false;
        if (cityFilter && order.city !== cityFilter) return false;
        if (searchFilter) {
            const searchStr = `${order.orderNo} ${order.userId}`.toLowerCase();
            if (!searchStr.includes(searchFilter)) return false;
        }
        return true;
    });

    currentPage = 1;
    renderTable();
}

// 渲染表格
function renderTable() {
    const tbody = document.getElementById('order-table-body');
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageOrders = filteredOrders.slice(start, end);

    tbody.innerHTML = pageOrders.map(order => `
        <tr>
            <td>${order.orderNo}</td>
            <td>${order.userId || '-'}</td>
            <td>${ITEM_TYPE_MAP[order.itemType] || order.itemType}</td>
            <td>${order.city}<br><small>${order.warehouseId}</small></td>
            <td><span class="status-tag ${STATUS_MAP[order.status]?.class || ''}">${STATUS_MAP[order.status]?.text || order.status}</span></td>
            <td>${formatTime(order.createTime)}</td>
            <td>
                <div class="action-btns">
                    <button class="btn btn-sm btn-primary" onclick="showDetail('${order._id}')">详情</button>
                    <button class="btn btn-sm btn-default" onclick="showStatusModal('${order._id}')">变更</button>
                </div>
            </td>
        </tr>
    `).join('');

    document.getElementById('current-page').textContent = currentPage;
}

// ========== 仓库管理 ==========

// 加载仓库数据
async function loadWarehouses() {
    try {
        const response = await fetch(`${API_BASE_URL}/warehouses`, {
            headers: {
                'X-OpenId': 'admin'
            }
        });
        const result = await response.json();

        if (result.code === 0) {
            allWarehouses = result.data;
            applyWarehouseFilters();
            updateWarehouseStats();
        }
    } catch (error) {
        console.error('加载仓库失败:', error);
        showToast('加载仓库失败', 'error');
    }
}

// 刷新仓库
function refreshWarehouses() {
    loadWarehouses();
    showToast('数据已刷新', 'success');
}

// 更新仓库统计
function updateWarehouseStats() {
    const total = allWarehouses.length;
    const active = allWarehouses.filter(w => w.status === 'ACTIVE').length;

    // 计算平均使用率
    let totalUsage = 0;
    let warningCount = 0;
    allWarehouses.forEach(w => {
        if (w.capacity > 0) {
            const usage = (w.usedCapacity / w.capacity) * 100;
            totalUsage += usage;
            if (usage >= 80) warningCount++;
        }
    });
    const avgUsage = total > 0 ? Math.round(totalUsage / total) : 0;

    document.getElementById('wh-stat-total').textContent = total;
    document.getElementById('wh-stat-active').textContent = active;
    document.getElementById('wh-stat-used').textContent = avgUsage + '%';
    document.getElementById('wh-stat-warning').textContent = warningCount;
}

// 应用仓库筛选
function applyWarehouseFilters() {
    const cityFilter = document.getElementById('wh-filter-city').value;
    const statusFilter = document.getElementById('wh-filter-status').value;

    filteredWarehouses = allWarehouses.filter(wh => {
        if (cityFilter && wh.city !== cityFilter) return false;
        if (statusFilter && wh.status !== statusFilter) return false;
        return true;
    });

    renderWarehouseTable();
}

// 渲染仓库表格
function renderWarehouseTable() {
    const tbody = document.getElementById('warehouse-table-body');

    tbody.innerHTML = filteredWarehouses.map(wh => {
        const usage = wh.capacity > 0 ? Math.round((wh.usedCapacity / wh.capacity) * 100) : 0;
        const usageClass = usage >= 90 ? 'danger' : usage >= 80 ? 'warning' : 'normal';

        return `
            <tr>
                <td>${wh._id}</td>
                <td>${wh.name}</td>
                <td>${wh.city}</td>
                <td>${wh.address}</td>
                <td>${wh.capacity}</td>
                <td>${wh.usedCapacity}</td>
                <td><span class="usage-badge ${usageClass}">${usage}%</span></td>
                <td><span class="status-tag ${WAREHOUSE_STATUS_MAP[wh.status]?.class || ''}">${WAREHOUSE_STATUS_MAP[wh.status]?.text || wh.status}</span></td>
            </tr>
        `;
    }).join('');
}

// ========== 通用函数 ==========

// 格式化时间
function formatTime(timeStr) {
    if (!timeStr) return '-';
    return timeStr.replace('T', ' ').split('.')[0];
}

// 分页
function changePage(delta) {
    const maxPage = Math.ceil(filteredOrders.length / pageSize);
    const newPage = currentPage + delta;

    if (newPage >= 1 && newPage <= maxPage) {
        currentPage = newPage;
        renderTable();
    }
}

// 显示状态变更弹窗
function showStatusModal(orderId) {
    currentOrderId = orderId;
    const order = allOrders.find(o => o._id === orderId);

    document.getElementById('modal-order-no').textContent = order?.orderNo || '';
    document.getElementById('new-status').value = order?.status || 'PENDING';
    document.getElementById('status-remark').value = '';

    document.getElementById('status-modal').classList.add('active');
}

// 关闭弹窗
function closeModal() {
    document.getElementById('status-modal').classList.remove('active');
    currentOrderId = null;
}

// 确认状态变更
async function confirmStatusChange() {
    if (!currentOrderId) return;

    const newStatus = document.getElementById('new-status').value;
    const remark = document.getElementById('status-remark').value;

    try {
        const response = await fetch(`${API_BASE_URL}/orders/${currentOrderId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-OpenId': 'admin'
            },
            body: JSON.stringify({
                newStatus: newStatus,
                operatorType: 'ADMIN',
                reason: remark || 'ADMIN_OPERATION'
            })
        });

        const result = await response.json();

        if (result.code === 0) {
            showToast('状态变更成功', 'success');
            closeModal();
            loadOrders();
        } else {
            showToast(result.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('状态变更失败:', error);
        showToast('操作失败', 'error');
    }
}

// 显示订单详情
function showDetail(orderId) {
    const order = allOrders.find(o => o._id === orderId);
    if (!order) return;

    const statusHistory = order.statusHistory || [];
    const historyHtml = statusHistory.map(h => `
        <div class="detail-row">
            <span class="detail-label">${h.from || '-'} → ${h.to}</span>
            <span class="detail-value">${h.operatorType || 'SYSTEM'} | ${formatTime(h.time || h.timestamp)}</span>
            ${h.reason ? `<span class="detail-reason">${h.reason}</span>` : ''}
        </div>
    `).join('') || '<p class="no-data">暂无状态变更记录</p>';

    document.getElementById('detail-content').innerHTML = `
        <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-row">
                <span class="detail-label">订单号</span>
                <span class="detail-value">${order.orderNo}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">用户ID</span>
                <span class="detail-value">${order.userId || '-'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">当前状态</span>
                <span class="detail-value"><span class="status-tag ${STATUS_MAP[order.status]?.class || ''}">${STATUS_MAP[order.status]?.text || order.status}</span></span>
            </div>
            <div class="detail-row">
                <span class="detail-label">物品类型</span>
                <span class="detail-value">${ITEM_TYPE_MAP[order.itemType] || order.itemType}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">所在城市</span>
                <span class="detail-value">${order.city}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">存放仓库</span>
                <span class="detail-value">${order.warehouseId}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">${formatTime(order.createTime)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">是否支付</span>
                <span class="detail-value">${order.isPaid ? '已支付' : '未支付'}</span>
            </div>
        </div>

        <div class="detail-section">
            <h4>费用信息</h4>
            <div class="detail-row">
                <span class="detail-label">存储费</span>
                <span class="detail-value">¥${order.amount?.storageFee ?? 0}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">配送费</span>
                <span class="detail-value">¥${order.amount?.deliveryFee ?? 0}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">保险费</span>
                <span class="detail-value">¥${order.amount?.insuranceFee ?? 0}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">合计</span>
                <span class="detail-value highlight">¥${order.amount?.totalFee ?? 0}</span>
            </div>
        </div>

        <div class="detail-section">
            <h4>状态变更记录</h4>
            ${historyHtml}
        </div>
    `;

    document.getElementById('detail-modal').classList.add('active');
}

// 关闭详情弹窗
function closeDetailModal() {
    document.getElementById('detail-modal').classList.remove('active');
}

// 退出登录
function logout() {
    if (confirm('确定要退出登录吗？')) {
        showToast('已退出登录', 'success');
    }
}

// Toast 提示
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    document.body.appendChild(toast);

    // 触发动画
    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 4px;
        color: #fff;
        font-size: 14px;
        z-index: 9999;
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s ease;
    }
    .toast.show {
        transform: translateX(0);
        opacity: 1;
    }
    .toast-success { background: #52C41A; }
    .toast-error { background: #F5222D; }
    .toast-info { background: #1890FF; }
    .panel { animation: fadeIn 0.3s ease; }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .usage-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    .usage-badge.normal { background: #F6FFED; color: #52C41A; }
    .usage-badge.warning { background: #FFF7E6; color: #FA8C16; }
    .usage-badge.danger { background: #FFF1F0; color: #F5222D; }
    .status-active { background: #F6FFED; color: #52C41A; }
    .status-inactive { background: #F5F5F5; color: #8C8C8C; }
    .status-transit { background: #E6F7FF; color: #1890FF; }
    .status-exception { background: #FFF1F0; color: #F5222D; }
    .no-data { color: #8C8C8C; padding: 16px 0; }
    .detail-row { flex-wrap: wrap; }
    .detail-reason { width: 100%; padding-left: 120px; color: #8C8C8C; font-size: 12px; margin-top: 4px; }
    .detail-value.highlight { color: #1890FF; font-weight: bold; }
`;
document.head.appendChild(style);
