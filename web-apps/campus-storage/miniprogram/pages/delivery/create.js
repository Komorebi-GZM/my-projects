// pages/delivery/create.js
const { get, patch } = require('../../utils/request')

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
    deliveryInfo: {
      contactName: '',
      contactPhone: '',
      address: '',
      deliveryTime: '',
      remark: ''
    },
    timeOptions: [
      { value: 'morning', label: '上午配送', desc: '09:00 - 12:00' },
      { value: 'afternoon', label: '下午配送', desc: '13:00 - 18:00' },
      { value: 'evening', label: '晚间配送', desc: '18:00 - 21:00' },
      { value: 'anytime', label: '任意时间', desc: '配送员将尽快送达' }
    ],
    deliveryFee: 15,
    canSubmit: false,
    submitting: false
  },

  onLoad(options) {
    const orderId = options.orderId
    if (!orderId) {
      wx.showToast({
        title: '订单ID缺失',
        icon: 'none'
      })
      wx.navigateBack()
      return
    }

    this.setData({ orderId })
    this.loadOrderDetail(orderId)
  },

  // 加载订单详情
  async loadOrderDetail(orderId) {
    try {
      const res = await get(`/orders/${orderId}`)

      if (res.code === 0) {
        const order = res.data
        this.setData({
          order: {
            ...order,
            itemTypeText: ITEM_TYPE_CONFIG[order.itemType] || order.itemType
          }
        })
      }
    } catch (err) {
      console.error('加载订单详情失败:', err)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 输入框变化
  onInputChange(e) {
    const field = e.currentTarget.dataset.field
    const value = e.detail.value
    
    this.setData({
      [`deliveryInfo.${field}`]: value
    }, () => {
      this.checkCanSubmit()
    })
  },

  // 选择配送时间
  selectTime(e) {
    const value = e.currentTarget.dataset.value
    this.setData({
      'deliveryInfo.deliveryTime': value
    }, () => {
      this.checkCanSubmit()
    })
  },

  // 检查是否可以提交
  checkCanSubmit() {
    const { contactName, contactPhone, address, deliveryTime } = this.data.deliveryInfo
    const canSubmit = contactName && contactPhone && address && deliveryTime
    
    this.setData({ canSubmit })
  },

  // 提交配送请求
  async submitDelivery() {
    if (!this.data.canSubmit || this.data.submitting) {
      return
    }

    // 验证手机号
    const phone = this.data.deliveryInfo.contactPhone
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    this.setData({ submitting: true })

    try {
      // 更新订单状态为DELIVERING
      const res = await patch(`/orders/${this.data.orderId}/status`, {
        newStatus: 'DELIVERING',
        operatorType: 'USER',
        reason: 'USER_REQUEST_DELIVERY'
      })

      if (res.code === 0) {
        wx.showToast({
          title: '配送申请已提交',
          icon: 'success'
        })

        // 跳转到订单详情页
        setTimeout(() => {
          wx.redirectTo({
            url: `/pages/order/detail?id=${this.data.orderId}`
          })
        }, 1500)
      }
    } catch (err) {
      console.error('提交配送失败:', err)
      wx.showToast({
        title: err.message || '提交失败',
        icon: 'none'
      })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
