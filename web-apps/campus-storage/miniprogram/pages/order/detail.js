// pages/order/detail.js
const { get, patch, post } = require('../../utils/request')

// 状态配置
const STATUS_CONFIG = {
  'PENDING': { text: '待处理', icon: '⏳', desc: '等待工作人员揽收', gradient: '#FF9800' },
  'COLLECTED': { text: '已揽收', icon: '📦', desc: '物品已被揽收，即将入库', gradient: '#1890FF' },
  'TRANSIT': { text: '运输中', icon: '🚚', desc: '物品正在运输途中', gradient: '#1890FF' },
  'STORED': { text: '已入库', icon: '🏪', desc: '物品已安全存放', gradient: '#52C41A' },
  'DELIVERING': { text: '配送中', icon: '🚚', desc: '物品正在配送中', gradient: '#1890FF' },
  'COMPLETED': { text: '已完成', icon: '✅', desc: '订单已完成', gradient: '#8C8C8C' },
  'CANCELLED': { text: '已取消', icon: '❌', desc: '订单已取消', gradient: '#8C8C8C' },
  'EXCEPTION': { text: '异常', icon: '⚠️', desc: '订单异常', gradient: '#F5222D' }
}

// 时间轴配置
const TIMELINE_CONFIG = [
  { status: 'PENDING', text: '提交订单' },
  { status: 'COLLECTED', text: '已揽收' },
  { status: 'TRANSIT', text: '运输中' },
  { status: 'STORED', text: '已入库' },
  { status: 'DELIVERING', text: '配送中' },
  { status: 'COMPLETED', text: '已完成' }
]

// 物品类型映射
const ITEM_TYPE_CONFIG = {
  'LUGGAGE': '行李箱',
  'DOCUMENT': '文件',
  'PACKAGE': '包裹'
}

Page({
  data: {
    orderId: '',
    order: {},
    statusIcon: '',
    statusDesc: '',
    statusGradient: '#1890FF',
    timeline: [],
    actions: [],
    loading: false
  },

  onLoad(options) {
    const orderId = options.id
    this.setData({ orderId })
    this.loadOrderDetail(orderId)
  },

  onShow() {
    // 刷新订单详情
    if (this.data.orderId) {
      this.loadOrderDetail(this.data.orderId)
    }
  },

  // 加载订单详情
  async loadOrderDetail(orderId) {
    this.setData({ loading: true })
    try {
      const res = await get(`/orders/${orderId}`)

      if (res.code === 0) {
        const order = this.formatOrder(res.data)
        const statusConfig = STATUS_CONFIG[order.status] || {}

        this.setData({
          order: order,
          statusIcon: statusConfig.icon || '📦',
          statusDesc: statusConfig.desc || '',
          statusGradient: statusConfig.gradient || '#1890FF',
          timeline: this.buildTimeline(order),
          actions: this.getActions(order),
          loading: false
        })
      }
    } catch (err) {
      console.error('加载订单详情失败:', err)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 格式化订单数据
  formatOrder(order) {
    const statusConfig = STATUS_CONFIG[order.status] || { text: order.status }
    const itemTypeText = ITEM_TYPE_CONFIG[order.itemType] || order.itemType

    // 格式化时间
    const createTime = order.createTime
      ? order.createTime.replace('T', ' ').split('.')[0]
      : ''

    return {
      ...order,
      statusText: statusConfig.text,
      itemTypeText: itemTypeText,
      createTime: createTime
    }
  },

  // 构建时间轴
  buildTimeline(order) {
    const statusHistory = order.statusHistory || []
    const currentStatus = order.status

    // 构建状态时间映射
    const statusTimeMap = {}
    statusHistory.forEach(record => {
      const toStatus = record.to || record.toStatus
      const time = record.time || record.timestamp
      if (toStatus && time) {
        statusTimeMap[toStatus] = time.replace('T', ' ').split('.')[0]
      }
    })

    // 如果是取消状态，特殊处理
    if (currentStatus === 'CANCELLED') {
      return [
        { status: 'PENDING', text: '提交订单', completed: true, time: statusTimeMap['PENDING'] },
        { status: 'CANCELLED', text: '已取消', isCurrent: true, time: statusTimeMap['CANCELLED'] }
      ]
    }

    // 异常状态特殊处理
    if (currentStatus === 'EXCEPTION') {
      const normalFlow = TIMELINE_CONFIG.findIndex(t => t.status === currentStatus)
      return TIMELINE_CONFIG.slice(0, normalFlow + 1).map((item, idx) => ({
        ...item,
        completed: idx < normalFlow,
        isCurrent: idx === normalFlow,
        time: statusTimeMap[item.status]
      }))
    }

    // 正常流程时间轴
    const currentIndex = TIMELINE_CONFIG.findIndex(t => t.status === currentStatus)
    return TIMELINE_CONFIG.map((item, idx) => ({
      ...item,
      completed: idx < currentIndex,
      isCurrent: idx === currentIndex,
      time: statusTimeMap[item.status]
    }))
  },

  // 获取操作按钮
  getActions(order) {
    const actions = []

    switch (order.status) {
      case 'PENDING':
        if (!order.isPaid) {
          actions.push({ type: 'primary', text: '去支付' })
        }
        actions.push({ type: 'danger', text: '取消订单' })
        break
      case 'COLLECTED':
      case 'TRANSIT':
      case 'STORED':
        actions.push({ type: 'default', text: '查看详情' })
        break
      case 'DELIVERING':
        actions.push({ type: 'primary', text: '确认收货' })
        break
      case 'COMPLETED':
      case 'CANCELLED':
        // 终态无操作
        break
    }

    return actions
  },

  // 操作按钮点击
  onAction(e) {
    const type = e.currentTarget.dataset.type
    const actionText = e.currentTarget.dataset.text

    switch (actionText) {
      case '去支付':
        this.handlePay()
        break
      case '取消订单':
        this.handleCancel()
        break
      case '发起配送':
        this.handleDelivery()
        break
      case '确认收货':
        this.handleConfirm()
        break
    }
  },

  // 支付
  async handlePay() {
    try {
      wx.showLoading({ title: '支付中...' })

      // 创建支付单
      const paymentRes = await post(`/orders/${this.data.orderId}/payment`, {
        amount: this.data.order.amount
      })

      // 执行支付
      const payRes = await post(`/orders/${this.data.orderId}/pay`, {
        paymentId: paymentRes.data._id,
        paymentMethod: 'WECHAT'
      })

      wx.hideLoading()

      if (payRes.code === 0) {
        wx.showToast({
          title: '支付成功',
          icon: 'success'
        })
        // 刷新订单详情
        this.loadOrderDetail(this.data.orderId)
      }
    } catch (err) {
      wx.hideLoading()
      wx.showToast({
        title: err.message || '支付失败',
        icon: 'none'
      })
    }
  },

  // 取消订单
  handleCancel() {
    wx.showModal({
      title: '确认取消',
      content: '取消后订单将无法恢复，是否确认取消？',
      confirmColor: '#F5222D',
      success: (res) => {
        if (res.confirm) {
          this.updateStatus('CANCELLED', 'USER_CANCEL')
        }
      }
    })
  },

  // 发起配送
  handleDelivery() {
    wx.navigateTo({
      url: `/pages/delivery/create?orderId=${this.data.orderId}`
    })
  },

  // 确认收货
  handleConfirm() {
    wx.showModal({
      title: '确认收货',
      content: '确认已收到物品？',
      success: (res) => {
        if (res.confirm) {
          this.updateStatus('COMPLETED', 'USER_CONFIRM')
        }
      }
    })
  },

  // 更新订单状态
  async updateStatus(newStatus, reason) {
    try {
      wx.showLoading({ title: '处理中...' })

      const res = await patch(`/orders/${this.data.orderId}/status`, {
        newStatus: newStatus,
        operatorType: 'USER',
        reason: reason
      })

      wx.hideLoading()

      if (res.code === 0) {
        wx.showToast({
          title: '操作成功',
          icon: 'success'
        })
        // 刷新订单详情
        this.loadOrderDetail(this.data.orderId)
      }
    } catch (err) {
      wx.hideLoading()
      wx.showToast({
        title: err.message || '操作失败',
        icon: 'none'
      })
    }
  }
})
