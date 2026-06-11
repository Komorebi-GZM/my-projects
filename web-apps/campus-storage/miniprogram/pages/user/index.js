Page({
  data: {},

  onLoad() {},

  goToOrders() {
    wx.switchTab({
      url: '/pages/order/list'
    })
  },

  goToHelp() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  goToAbout() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  }
})