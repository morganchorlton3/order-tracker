import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Order {
  id: number
  external_id: string
  source: 'etsy' | 'tiktok_shop'
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled'
  customer_name: string
  customer_email?: string
  shipping_address?: any
  total_amount: number
  currency: string
  items?: any[]
  order_date: string
  created_at: string
  updated_at: string
}

export interface OrdersCount {
  count: number
}

export interface Product {
  id: number
  name: string
  description?: string
  sku?: string
  price: number
  currency: string
  quantity: number
  images?: string[]
  tags?: string[]
  variants?: any
  status: 'draft' | 'active' | 'inactive' | 'archived'
  etsy_listing_id?: string
  tiktok_shop_product_id?: string
  created_at: string
  updated_at: string
}

export interface SyncLog {
  id: number
  sync_type: 'order_import' | 'order_export' | 'product_import' | 'product_export'
  status: 'pending' | 'in_progress' | 'success' | 'failed'
  source: string
  order_id?: number
  records_processed: number
  records_successful: number
  records_failed: number
  error_message?: string
  started_at: string
  completed_at?: string
}

export const getOrders = async (params?: { skip?: number; limit?: number; source?: string; status?: string }) => {
  const response = await api.get<Order[]>('/orders', { params })
  return response.data
}

export const getOrdersCount = async () => {
  const response = await api.get<OrdersCount>('/orders/count')
  return response.data
}

export const getOrder = async (id: number) => {
  const response = await api.get<Order>(`/orders/${id}`)
  return response.data
}

export const createOrder = async (order: Partial<Order>) => {
  const response = await api.post<Order>('/orders', order)
  return response.data
}

export const updateOrder = async (id: number, order: Partial<Order>) => {
  const response = await api.put<Order>(`/orders/${id}`, order)
  return response.data
}

export const deleteOrder = async (id: number) => {
  await api.delete(`/orders/${id}`)
}

export const getProducts = async (params?: { skip?: number; limit?: number; status?: string }) => {
  const response = await api.get<Product[]>('/products', { params })
  return response.data
}

export const getProduct = async (id: number) => {
  const response = await api.get<Product>(`/products/${id}`)
  return response.data
}

export const createProduct = async (product: Partial<Product>) => {
  const response = await api.post<Product>('/products', product)
  return response.data
}

export const updateProduct = async (id: number, product: Partial<Product>) => {
  const response = await api.put<Product>(`/products/${id}`, product)
  return response.data
}

export const deleteProduct = async (id: number) => {
  await api.delete(`/products/${id}`)
}

export const syncOrdersImport = async (data: { source: string }) => {
  const response = await api.post<SyncLog>('/sync/orders/import', data)
  return response.data
}

export const syncProductsExport = async (data: { source: string }) => {
  const response = await api.post<SyncLog>('/sync/products/export', data)
  return response.data
}

export const getSyncLogs = async () => {
  const response = await api.get<SyncLog[]>('/sync/logs')
  return response.data
}

export const getSyncLog = async (id: number) => {
  const response = await api.get<SyncLog>(`/sync/logs/${id}`)
  return response.data
}

export interface EtsyAuthStatus {
  authenticated: boolean
  expired?: boolean
  shop_name?: string
  shop_id?: string
  expires_at?: string
  message?: string
}

export const getEtsyAuthStatus = async () => {
  const response = await api.get<EtsyAuthStatus>('/auth/etsy/status')
  return response.data
}

export const getEtsyAuthUrl = async () => {
  const response = await api.get<{ authorization_url: string; state: string; message: string }>('/auth/etsy/authorize')
  return response.data
}

