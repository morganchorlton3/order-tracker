import { useState } from 'react'
import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { getOrders } from '../services/api'
import { format } from 'date-fns'

export default function Orders() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [sourceFilter, setSourceFilter] = useState<'etsy' | 'tiktok_shop' | ''>('')
  const [statusFilter, setStatusFilter] = useState<'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | ''>('')
  const [currencyFilter, setCurrencyFilter] = useState('')
  const [minAmount, setMinAmount] = useState('')
  const [maxAmount, setMaxAmount] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const limit = 20

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ['orders', page, search, sourceFilter, statusFilter, currencyFilter, minAmount, maxAmount, dateFrom, dateTo],
    queryFn: () => getOrders({
      skip: (page - 1) * limit,
      limit,
      search: search || undefined,
      source: sourceFilter || undefined,
      status: statusFilter || undefined,
      currency: currencyFilter || undefined,
      min_amount: minAmount ? parseFloat(minAmount) : undefined,
      max_amount: maxAmount ? parseFloat(maxAmount) : undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    }),
    placeholderData: keepPreviousData,
  })

  const totalPages = data ? Math.ceil(data.total / limit) : 0

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
    setPage(1) // Reset to first page when searching
  }

  const handleSourceFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSourceFilter(e.target.value as 'etsy' | 'tiktok_shop' | '')
    setPage(1)
  }

  const handleStatusFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | '')
    setPage(1)
  }

  const clearFilters = () => {
    setSearch('')
    setSourceFilter('')
    setStatusFilter('')
    setCurrencyFilter('')
    setMinAmount('')
    setMaxAmount('')
    setDateFrom('')
    setDateTo('')
    setPage(1)
  }

  const hasActiveFilters = search || sourceFilter || statusFilter || currencyFilter || minAmount || maxAmount || dateFrom || dateTo

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'shipped':
        return 'bg-purple-100 text-purple-800'
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getCurrencySymbol = (currencyCode: string): string => {
    const currencyMap: Record<string, string> = {
      'GBP': '£',
      'USD': '$',
      'EUR': '€',
      'CAD': 'C$',
      'AUD': 'A$',
      'JPY': '¥',
      'CNY': '¥',
      'INR': '₹',
      'CHF': 'CHF',
      'NZD': 'NZ$',
      'SGD': 'S$',
      'HKD': 'HK$',
      'SEK': 'kr',
      'NOK': 'kr',
      'DKK': 'kr',
      'PLN': 'zł',
      'MXN': '$',
      'BRL': 'R$',
      'ZAR': 'R',
      'KRW': '₩',
      'TRY': '₺',
    }
    return currencyMap[currencyCode.toUpperCase()] || currencyCode
  }

  const formatCurrency = (amount: number, currencyCode: string): string => {
    const symbol = getCurrencySymbol(currencyCode)
    // For currencies like USD, EUR, GBP, put symbol before amount
    // For some currencies like JPY, no decimal places
    const isSymbolBefore = ['GBP', 'USD', 'EUR', 'CAD', 'AUD', 'NZD', 'SGD', 'HKD', 'MXN', 'BRL'].includes(currencyCode.toUpperCase())
    const isNoDecimal = ['JPY', 'KRW'].includes(currencyCode.toUpperCase())
    
    if (isNoDecimal) {
      return isSymbolBefore ? `${symbol}${Math.round(amount)}` : `${Math.round(amount)}${symbol}`
    }
    
    return isSymbolBefore ? `${symbol}${amount.toFixed(2)}` : `${amount.toFixed(2)} ${symbol}`
  }

  if (isLoading && !data) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center">Loading orders...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center text-red-600">Error loading orders</div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Orders</h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Manage and track your orders from Etsy and TikTok Shop
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-4 sm:space-y-0">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by customer name, email, or order ID..."
              value={search}
            onChange={handleSearchChange}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        <div className="sm:w-48">
          <select
            value={sourceFilter}
            onChange={handleSourceFilterChange}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
              <option value="">All Sources</option>
              <option value="etsy">Etsy</option>
              <option value="tiktok_shop">TikTok Shop</option>
            </select>
          </div>
        <div className="sm:w-48">
          <select
            value={statusFilter}
            onChange={handleStatusFilterChange}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="shipped">Shipped</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {showFilters ? 'Hide' : 'Show'} Filters
            </button>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Clear All
              </button>
            )}
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-md border border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Currency
                </label>
                <select
                  value={currencyFilter}
                  onChange={(e) => {
                    setCurrencyFilter(e.target.value)
                    setPage(1)
                  }}
                  className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">All Currencies</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="CAD">CAD (C$)</option>
                  <option value="AUD">AUD (A$)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Min Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={minAmount}
                  onChange={(e) => {
                    setMinAmount(e.target.value)
                    setPage(1)
                  }}
                  className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Max Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={maxAmount}
                  onChange={(e) => {
                    setMaxAmount(e.target.value)
                    setPage(1)
                  }}
                  className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Date From
                </label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => {
                    setDateFrom(e.target.value)
                    setPage(1)
                  }}
                  className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Date To
                </label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => {
                    setDateTo(e.target.value)
                    setPage(1)
                  }}
                  className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Orders Table */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md relative">
        {isFetching && (
          <div className="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-75 flex items-center justify-center z-10">
            <div className="text-sm text-gray-600 dark:text-gray-400">Updating...</div>
          </div>
        )}
        {data && data.items.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Order ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {data.items.map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {order.external_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        <div>{order.customer_name}</div>
                        {order.customer_email && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">{order.customer_email}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                          {order.source}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(order.status)}`}>
                          {order.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {formatCurrency(order.total_amount, order.currency)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {format(new Date(order.order_date), 'MMM d, yyyy')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to{' '}
                    <span className="font-medium">{Math.min(page * limit, data.total)}</span> of{' '}
                    <span className="font-medium">{data.total}</span> results
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum
                      if (totalPages <= 5) {
                        pageNum = i + 1
                      } else if (page <= 3) {
                        pageNum = i + 1
                      } else if (page >= totalPages - 2) {
                        pageNum = totalPages - 4 + i
                      } else {
                        pageNum = page - 2 + i
                      }
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setPage(pageNum)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === pageNum
                              ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                    <button
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page >= totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No orders found</p>
          </div>
        )}
      </div>
    </div>
  )
}
