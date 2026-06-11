// utils/request.js
// API请求封装

const app = getApp()

// 请求拦截器
const request = (options) => {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data, header = {} } = options
    
    // 获取用户openid
    const userInfo = wx.getStorageSync('userInfo') || {}
    const openId = userInfo.openId || userInfo.openid || ''
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'X-OpenId': openId,
        ...header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          if (res.data.code === 0) {
            resolve(res.data)
          } else {
            wx.showToast({
              title: res.data.message || '请求失败',
              icon: 'none'
            })
            reject(res.data)
          }
        } else if (res.statusCode === 401) {
          wx.showToast({
            title: '请先登录',
            icon: 'none'
          })
          app.login()
          reject(new Error('Unauthorized'))
        } else {
          wx.showToast({
            title: '服务器错误',
            icon: 'none'
          })
          reject(new Error(`HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络异常，请稍后重试',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// GET请求
const get = (url, params = {}) => {
  // 构建查询字符串
  const queryString = Object.keys(params)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')
  
  const fullUrl = queryString ? `${url}?${queryString}` : url
  
  return request({ url: fullUrl, method: 'GET' })
}

// POST请求
const post = (url, data = {}) => {
  return request({ url, method: 'POST', data })
}

// PUT请求
const put = (url, data = {}) => {
  return request({ url, method: 'PUT', data })
}

// PATCH请求
const patch = (url, data = {}) => {
  return request({ url, method: 'PATCH', data })
}

// DELETE请求
const del = (url) => {
  return request({ url, method: 'DELETE' })
}

module.exports = {
  request,
  get,
  post,
  put,
  patch,
  delete: del
}
