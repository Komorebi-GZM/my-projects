// pages/index/index.js
const { get, post } = require('../../utils/request')

// 状态映射配置
const STATUS_CONFIG = {
  'PENDING': { text: '待处理', style: 'warning' },
  'COLLECTED': { text: '已揽收', style: 'primary' },
  'STORED': { text: '已入库', style: 'success' },
  'DELIVERING': { text: '配送中', style: 'transit' },
  'COMPLETED': { text: '已完成', style: 'disabled' },
  'CANCELLED': { text: '已取消', style: 'disabled' }
}

// 物品类型映射
const ITEM_TYPE_CONFIG = {
  'LUGGAGE': { text: '行李箱', icon: '🧳' },
  'DOCUMENT': { text: '文件', icon: '📄' },
  'PACKAGE': { text: '包裹', icon: '📦' }
}

Page({
  data: {
    banners: [],
    activeOrders: [],
    loading: false
  },

  onLoad() {
    this.loadActiveOrders()
  },

  onShow() {
    // 每次显示页面时刷新订单列表
    this.loadActiveOrders()
  },

  onPullDownRefresh() {
    this.loadActiveOrders().finally(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载进行中订单
  async loadActiveOrders() {
    this.setData({ loading: true })
    
    try {
      const res = await get('/orders', { page: 1, pageSize: 5 })
      
      if (res.code === 0) {
        // 过滤非终态订单（PENDING, COLLECTED, STORED, DELIVERING）
        const activeStatuses = ['PENDING', 'COLLECTED', 'STORED', 'DELIVERING']
        const orders = res.data.list
          .filter(order => activeStatuses.includes(order.status))
          .map(order => this.formatOrder(order))
        
        this.setData({
          activeOrders: orders,
          loading: false
        })
      }
    } catch (err) {
      console.error('加载订单失败:', err)
      this.setData({ loading: false })
    }
  },

  // 格式化订单数据
  formatOrder(order) {
    const statusConfig = STATUS_CONFIG[order.status] || { text: order.status, style: 'default' }
    const itemConfig = ITEM_TYPE_CONFIG[order.itemType] || { text: order.itemType, icon: '📦' }
    
    // 格式化时间
    const createTime = new Date(order.createTime)
    const now = new Date()
    const diffHours = Math.floor((now - createTime) / (1000 * 60 * 60))
    
    let timeText
    if (diffHours < 1) {
      timeText = '刚刚'
    } else if (diffHours < 24) {
      timeText = `${diffHours}小时前`
    } else {
      const diffDays = Math.floor(diffHours / 24)
      timeText = `${diffDays}天前`
    }
    
    return {
      ...order,
      statusText: statusConfig.text,
      statusStyle: statusConfig.style,
      itemTypeText: itemConfig.text,
      itemIcon: itemConfig.icon,
      createTimeText: timeText
    }
  },

  // Banner点击
  onBannerTap(e) {
    const item = e.currentTarget.dataset.item
    console.log('Banner点击:', item)
    // 可扩展跳转逻辑
  },

  // 跳转到创建订单页
  goToCreateOrder() {
    wx.navigateTo({
      url: '/pages/order/create'
    })
  },

  // 跳转到订单列表页
  goToOrderList() {
    wx.switchTab({
      url: '/pages/order/list'
    })
  },

  // 跳转到订单详情页
  goToOrderDetail(e) {
    const orderId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/order/detail?id=${orderId}`
    })
  }
})
