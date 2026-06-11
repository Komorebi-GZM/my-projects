// pages/order/list.js
const { get } = require('../../utils/request')

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
  'LUGGAGE': '行李箱',
  'DOCUMENT': '文件',
  'PACKAGE': '包裹'
}

Page({
  data: {
    activeTab: 'all', // all, active, completed
    orders: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    loadingMore: false,
    refreshing: false
  },

  onLoad() {
    this.loadOrders()
  },

  onShow() {
    // 刷新列表
    this.refreshOrders()
  },

  // 切换Tab
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      activeTab: tab,
      orders: [],
      page: 1,
      hasMore: true
    })
    this.loadOrders()
  },

  // 加载订单列表
  async loadOrders(isLoadMore = false) {
    if (this.data.loading || (isLoadMore && !this.data.hasMore)) {
      return
    }

    this.setData({
      loading: !isLoadMore,
      loadingMore: isLoadMore
    })

    try {
      // 根据Tab构建查询参数
      let status = ''
      if (this.data.activeTab === 'active') {
        status = '' // 后端会过滤非终态
      } else if (this.data.activeTab === 'completed') {
        status = 'COMPLETED'
      }

      const res = await get('/orders', {
        page: this.data.page,
        pageSize: this.data.pageSize,
        status: status
      })

      if (res.code === 0) {
        const newOrders = res.data.list.map(order => this.formatOrder(order))
        const orders = isLoadMore ? [...this.data.orders, ...newOrders] : newOrders

        this.setData({
          orders: orders,
          hasMore: orders.length < res.data.total,
          page: this.data.page + 1,
          loading: false,
          loadingMore: false,
          refreshing: false
        })
      }
    } catch (err) {
      console.error('加载订单失败:', err)
      this.setData({
        loading: false,
        loadingMore: false,
        refreshing: false
      })
    }
  },

  // 刷新订单
  refreshOrders() {
    this.setData({
      orders: [],
      page: 1,
      hasMore: true
    })
    this.loadOrders()
  },

  // 下拉刷新
  onRefresh() {
    this.setData({ refreshing: true })
    this.refreshOrders()
  },

  // 加载更多
  onLoadMore() {
    this.loadOrders(true)
  },

  // 格式化订单数据
  formatOrder(order) {
    const statusConfig = STATUS_CONFIG[order.status] || { text: order.status, style: 'default' }
    const itemTypeText = ITEM_TYPE_CONFIG[order.itemType] || order.itemType

    // 判断是否需要显示操作按钮
    const showAction = ['PENDING', 'STORED'].includes(order.status)
    const actionText = order.status === 'PENDING' ? '去支付' : '发起配送'

    // 格式化时间
    const createTime = order.createTime ? order.createTime.split('T')[0] : ''

    return {
      ...order,
      statusText: statusConfig.text,
      statusStyle: statusConfig.style,
      itemTypeText: itemTypeText,
      createTime: createTime,
      showAction: showAction,
      actionText: actionText
    }
  },

  // 跳转到订单详情
  goToDetail(e) {
    const orderId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/order/detail?id=${orderId}`
    })
  },

  // 操作按钮点击
  onAction(e) {
    e.stopPropagation()
    const item = e.currentTarget.dataset.item

    if (item.status === 'PENDING') {
      // 去支付
      wx.showToast({
        title: '支付功能开发中',
        icon: 'none'
      })
    } else if (item.status === 'STORED') {
      // 发起配送
      wx.navigateTo({
        url: `/pages/delivery/create?orderId=${item._id}`
      })
    }
  },

  // 去下单
  goToCreate() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
