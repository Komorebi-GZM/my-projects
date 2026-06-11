// app.js
const config = require('./config.js')

App({
  globalData: {
    userInfo: null,
    apiBaseUrl: config.API_BASE_URL,
    isDev: config.DEBUG
  },

  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    this.login()
  },

  // 微信登录
  login() {
    const that = this
    wx.request({
      url: `${this.globalData.apiBaseUrl}/login`,
      method: 'POST',
      header: {
        'X-OpenId': 'test_user_123' // 开发测试用：固定用户ID
      },
      success: (res) => {
        if (res.data.code === 0) {
          that.globalData.userInfo = res.data.data
          wx.setStorageSync('userInfo', res.data.data)
          console.log('登录成功:', res.data.data)
        } else {
          console.error('登录失败:', res.data.message)
        }
      },
      fail: (err) => {
        console.error('登录请求失败:', err)
      }
    })
  },

  // 获取用户信息
  getUserInfo() {
    return this.globalData.userInfo || wx.getStorageSync('userInfo')
  }
})
