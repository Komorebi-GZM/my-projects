/**
 * 小程序配置文件
 * 根据环境自动切换API地址
 */

const ENV = {
  // 开发环境
  development: {
    API_BASE_URL: 'http://localhost:5001/api',
    DEBUG: true
  },
  // 生产环境
  production: {
    // 替换为实际的CloudBase环境ID
    API_BASE_URL: 'https://<YOUR_ENV_ID>.service.tcloudbase.com',
    DEBUG: false
  }
};

// 当前环境
const CURRENT_ENV = 'development'; // 发布前改为 'production'

module.exports = {
  ...ENV[CURRENT_ENV],
  ENV: CURRENT_ENV
};
