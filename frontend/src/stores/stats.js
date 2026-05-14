import axios from 'axios';
import { defineStore } from 'pinia';

export const useStatsStore = defineStore('stats', {
  state: () => ({
    kpiSummary: {},
    stockAlerts: [],
    salesTrend: [],
    popularItems: [],
    perUserSpend: [],
    vendorTrend: [],
  }),

  actions: {
    async fetchKpiSummary(vendorId) {
      try {
        const res = await axios.get('/api/statistics/summary', { params: { vendor_id: vendorId } });
        this.kpiSummary = res.data.data;
        return res.data.data;
      } catch (error) {
        console.error('Failed to fetch KPI summary:', error.response?.data?.error);
        throw error;
      }
    },

    async fetchStockAlerts(vendorId) {
      try {
        const res = await axios.get('/api/statistics/stock-alerts', { params: { vendor_id: vendorId } });
        this.stockAlerts = res.data.data.alerts;
        return res.data.data.alerts;
      } catch (error) {
        console.error('Failed to fetch stock alerts:', error.response?.data?.error);
        throw error;
      }
    },

    async fetchSalesTrend(vendorId, days = 30) {
      try {
        const res = await axios.get('/api/statistics/sales-trend', {
          params: { vendor_id: vendorId, days },
        });
        this.salesTrend = res.data.data.sales;
        return res.data.data.sales;
      } catch (error) {
        console.error('Failed to fetch sales trend:', error.response?.data?.error);
        throw error;
      }
    },

    async fetchPopularItems(vendorId, params = {}) {
      try {
        const res = await axios.get('/api/statistics/popular-items', {
          params: { vendor_id: vendorId, ...params },
        });
        this.popularItems = res.data.data.items;
        return res.data.data.items;
      } catch (error) {
        console.error('Failed to fetch popular items:', error.response?.data?.error);
        throw error;
      }
    },

    async fetchPerUserSpend(vendorId, params = {}) {
      try {
        const res = await axios.get('/api/statistics/user-spend', {
          params: { vendor_id: vendorId, ...params },
        });
        this.perUserSpend = res.data.data.users;
        return res.data.data.users;
      } catch (error) {
        console.error('Failed to fetch per-user spend:', error.response?.data?.error);
        throw error;
      }
    },

    async fetchVendorTrend(vendorId, params = {}) {
      try {
        const res = await axios.get('/api/statistics/vendor-trend', {
          params: { vendor_id: vendorId, ...params },
        });
        this.vendorTrend = res.data.data.trend;
        return res.data.data.trend;
      } catch (error) {
        console.error('Failed to fetch vendor trend:', error.response?.data?.error);
        throw error;
      }
    },

    async fetchStockHistory(sizeId, params = {}) {
      try {
        const res = await axios.get(`/api/size/${sizeId}/stock/history`, { params });
        return res.data.data;
      } catch (error) {
        console.error('Failed to fetch stock history:', error.response?.data?.error);
        throw error;
      }
    },

    async topUpStock(sizeId, quantity, note = '') {
      try {
        const res = await axios.post(`/api/size/${sizeId}/topup`, { quantity, note });
        return res.data;
      } catch (error) {
        console.error('Failed to top up stock:', error.response?.data?.error);
        throw error;
      }
    },
  },
});
