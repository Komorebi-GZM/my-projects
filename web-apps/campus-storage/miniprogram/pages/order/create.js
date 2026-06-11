// pages/order/create.js
const { post, get } = require('../../utils/request')

Page({
  data: {
    // 城市列表
    cities: ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安'],
    selectedCity: '',

    // 物品类型
    itemTypes: [
      { value: 'LUGGAGE', label: '行李箱', icon: '🧳' },
      { value: 'DOCUMENT', label: '文件', icon: '📄' },
      { value: 'PACKAGE', label: '包裹', icon: '📦' }
    ],
    selectedType: '',

    // 仓库列表（根据城市动态加载）
    warehouses: [],
    warehouseLoading: false,
    selectedWarehouse: '',

    // 费用预估
    fee: {
      storage: 0,
      delivery: 0,
      insurance: 0,
      total: 0
    },

    // 提交状态
    submitting: false
  },

  onLoad() {
    // 默认选择第一个城市
    this.selectCity({ currentTarget: { dataset: { city: this.data.cities[0] } } })
  },

  // 计算是否可以提交
  computeCanSubmit() {
    const { selectedCity, selectedType, selectedWarehouse } = this.data
    return !!(selectedCity && selectedType && selectedWarehouse)
  },

  // 选择城市
  selectCity(e) {
    const city = e.currentTarget.dataset.city
    this.setData({
      selectedCity: city,
      selectedWarehouse: '',
      warehouses: [],
      warehouseLoading: true
    })
    this.calculateFee()
    this.loadWarehouses(city)
  },

  // 从API加载仓库列表
  async loadWarehouses(city) {
    try {
      const res = await get('/warehouses', { city: city })
      if (res.code === 0) {
        this.setData({
          warehouses: res.data.map(w => ({
            id: w._id,
            name: w.name,
            address: w.address
          })),
          warehouseLoading: false
        })
      }
    } catch (err) {
      console.error('加载仓库失败:', err)
      this.setData({ warehouseLoading: false })
      // 降级到本地数据
      this.setData({
        warehouses: this.getWarehousesByCity(city)
      })
    }
  },

  // 选择物品类型
  selectType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ selectedType: type })
    this.calculateFee()
    this.updateSubmitButton()
  },

  // 选择仓库
  selectWarehouse(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ selectedWarehouse: id })
    this.calculateFee()
    this.updateSubmitButton()
  },

  // 更新提交按钮状态
  updateSubmitButton() {
    this.setData({ canSubmit: this.computeCanSubmit() })
  },

  // 根据城市获取仓库列表（本地降级数据）
  getWarehousesByCity(city) {
    const warehouseMap = {
      '北京': [
        { id: 'wh_bj_central', name: '北京中央仓库', address: '北京市朝阳区建国路88号' },
        { id: 'wh_bj_haidian', name: '北京海淀仓库', address: '北京市海淀区中关村大街1号' }
      ],
      '上海': [
        { id: 'wh_sh_pudong', name: '上海浦东仓库', address: '上海市浦东新区陆家嘴环路1000号' },
        { id: 'wh_sh_xuhui', name: '上海徐汇仓库', address: '上海市徐汇区漕溪北路595号' }
      ],
      '广州': [
        { id: 'wh_gz_uc_north', name: '广州大学城北区仓库', address: '广州市番禺区大学城北区' },
        { id: 'wh_gz_uc_south', name: '广州大学城南区仓库', address: '广州市番禺区大学城南区' }
      ],
      '深圳': [
        { id: 'wh_sz_nanshan', name: '深圳南山仓库', address: '深圳市南山区科技园' },
        { id: 'wh_sz_futian', name: '深圳福田仓库', address: '深圳市福田区中心城' }
      ],
      '杭州': [
        { id: 'wh_hz_xihu', name: '杭州西湖仓库', address: '杭州市西湖区文三路' }
      ],
      '成都': [
        { id: 'wh_cd_wuhou', name: '成都武侯仓库', address: '成都市武侯区人民南路' }
      ],
      '武汉': [
        { id: 'wh_wh_wuchang', name: '武汉武昌仓库', address: '武汉市武昌区中南路' }
      ],
      '西安': [
        { id: 'wh_wa_yanta', name: '西安雁塔仓库', address: '西安市雁塔区长安南路' }
      ]
    }
    return warehouseMap[city] || []
  },

  // 计算费用
  calculateFee() {
    const { selectedCity, selectedType, selectedWarehouse } = this.data

    if (!selectedCity || !selectedType || !selectedWarehouse) {
      this.setData({
        fee: { storage: 0, delivery: 0, insurance: 0, total: 0 }
      })
      return
    }

    // 基础费用计算（Demo阶段简化逻辑）
    const baseStorage = 10  // 基础存储费
    const baseDelivery = 15  // 基础配送费
    const insurance = 5  // 保险费

    // 根据物品类型调整
    const typeMultiplier = {
      'LUGGAGE': 1.5,
      'DOCUMENT': 0.8,
      'PACKAGE': 1.2
    }

    const multiplier = typeMultiplier[selectedType] || 1.0
    const storageFee = Math.round(baseStorage * multiplier)
    const deliveryFee = baseDelivery
    const insuranceFee = insurance
    const total = storageFee + deliveryFee + insuranceFee

    this.setData({
      fee: {
        storage: storageFee,
        delivery: deliveryFee,
        insurance: insuranceFee,
        total: total
      }
    })
  },

  // 提交订单
  async submitOrder() {
    if (!this.computeCanSubmit() || this.data.submitting) {
      return
    }

    this.setData({ submitting: true })

    try {
      const res = await post('/orders', {
        city: this.data.selectedCity,
        itemType: this.data.selectedType,
        warehouseId: this.data.selectedWarehouse
      })

      if (res.code === 0) {
        wx.showToast({
          title: '下单成功',
          icon: 'success'
        })

        // 跳转到订单详情页
        setTimeout(() => {
          wx.redirectTo({
            url: `/pages/order/detail?id=${res.data._id}`
          })
        }, 1500)
      }
    } catch (err) {
      console.error('下单失败:', err)
      wx.showToast({
        title: err.message || '下单失败',
        icon: 'none'
      })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
