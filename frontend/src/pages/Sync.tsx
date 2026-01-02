import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { syncOrdersImport, syncProductsExport, getSyncLogs } from '../services/api'
import EtsyAuth from '../components/EtsyAuth'

export default function Sync() {
  const queryClient = useQueryClient()
  const [selectedSource, setSelectedSource] = useState<'etsy' | 'tiktok_shop'>('etsy')

  const { data: syncLogs } = useQuery({
    queryKey: ['syncLogs'],
    queryFn: getSyncLogs,
  })

  const importOrdersMutation = useMutation({
    mutationFn: (source: string) => syncOrdersImport({ source }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncLogs'] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
  })

  const exportProductsMutation = useMutation({
    mutationFn: (source: string) => syncProductsExport({ source }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncLogs'] })
    },
  })

  const handleImportOrders = () => {
    importOrdersMutation.mutate(selectedSource)
  }

  const handleExportProducts = () => {
    exportProductsMutation.mutate(selectedSource)
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Sync</h1>
        <p className="mt-2 text-sm text-gray-600">
          Sync orders and products with Etsy and TikTok Shop
        </p>
      </div>

      <div className="mb-6">
        <EtsyAuth />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Import Orders
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Source
              </label>
              <select
                value={selectedSource}
                onChange={(e) =>
                  setSelectedSource(e.target.value as 'etsy' | 'tiktok_shop')
                }
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="etsy">Etsy</option>
                <option value="tiktok_shop">TikTok Shop</option>
              </select>
            </div>
            <button
              onClick={handleImportOrders}
              disabled={importOrdersMutation.isPending}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {importOrdersMutation.isPending
                ? 'Importing...'
                : 'Import Orders'}
            </button>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Export Products
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Destination
              </label>
              <select
                value={selectedSource}
                onChange={(e) =>
                  setSelectedSource(e.target.value as 'etsy' | 'tiktok_shop')
                }
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="etsy">Etsy</option>
                <option value="tiktok_shop">TikTok Shop</option>
              </select>
            </div>
            <button
              onClick={handleExportProducts}
              disabled={exportProductsMutation.isPending}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {exportProductsMutation.isPending
                ? 'Exporting...'
                : 'Export Products'}
            </button>
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Sync History</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {syncLogs && syncLogs.length > 0 ? (
            syncLogs.map((log) => (
              <div key={log.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {log.sync_type.replace('_', ' ').toUpperCase()} - {log.source}
                    </p>
                    <p className="text-sm text-gray-500">
                      Started: {new Date(log.started_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        log.status === 'success'
                          ? 'bg-green-100 text-green-800'
                          : log.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : log.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {log.status}
                    </span>
                    {log.records_processed > 0 && (
                      <span className="text-sm text-gray-500">
                        {log.records_successful}/{log.records_processed} successful
                      </span>
                    )}
                  </div>
                </div>
                {log.error_message && (
                  <p className="mt-2 text-sm text-red-600">{log.error_message}</p>
                )}
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center text-gray-500">
              No sync history yet. Start syncing to see logs here.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

