import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { syncOrdersImport, syncProductsExport, getSyncLogs } from '../services/api'
import ConnectionCard from '../components/ConnectionCard'

export default function Settings() {
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

  const connections = [
    {
      name: 'Etsy',
      description: 'Connect your Etsy shop to sync orders and products',
      source: 'etsy' as const,
      icon: (
        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8.564 2.445c0 .325-.033.651-.107.975a5.866 5.866 0 0 1-3.17 4.09 5.866 5.866 0 0 1-4.17.59 10.1 10.1 0 0 1 7.447-5.655zm4.305 0a10.1 10.1 0 0 1 7.447 5.655 5.866 5.866 0 0 1-4.17-.59 5.866 5.866 0 0 1-3.17-4.09 5.866 5.866 0 0 1-.107-.975zm-4.305 19.11c0-.325-.033-.651-.107-.975a5.866 5.866 0 0 0-3.17-4.09 5.866 5.866 0 0 0-4.17-.59 10.1 10.1 0 0 0 7.447 5.655zm4.305 0a10.1 10.1 0 0 0 7.447-5.655 5.866 5.866 0 0 0-4.17.59 5.866 5.866 0 0 0-3.17 4.09 5.866 5.866 0 0 0-.107.975zM12 8.43a3.57 3.57 0 1 0 0 7.14 3.57 3.57 0 0 0 0-7.14z"/>
        </svg>
      ),
      color: 'bg-purple-600',
      darkColor: 'dark:bg-purple-500',
    },
    {
      name: 'TikTok Shop',
      description: 'Connect your TikTok Shop to sync orders and products',
      source: 'tiktok_shop' as const,
      icon: (
        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
        </svg>
      ),
      color: 'bg-black',
      darkColor: 'dark:bg-gray-700',
    },
  ]

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Manage your integrations and sync settings
        </p>
      </div>

      {/* Connections Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Connections</h2>
        <div className="space-y-4">
          {connections.map((connection) => (
            <ConnectionCard
              key={connection.source}
              name={connection.name}
              description={connection.description}
              icon={connection.icon}
              source={connection.source}
              color={connection.color}
              darkColor={connection.darkColor}
            />
          ))}
        </div>
      </div>

      {/* Quick Sync Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Sync</h2>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Import Orders
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Source
                </label>
                <select
                  value={selectedSource}
                  onChange={(e) =>
                    setSelectedSource(e.target.value as 'etsy' | 'tiktok_shop')
                  }
                  className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="etsy">Etsy</option>
                  <option value="tiktok_shop">TikTok Shop</option>
                </select>
              </div>
              <button
                onClick={handleImportOrders}
                disabled={importOrdersMutation.isPending}
                className="w-full bg-blue-600 dark:bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                {importOrdersMutation.isPending
                  ? 'Importing...'
                  : 'Import Orders'}
              </button>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Export Products
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Destination
                </label>
                <select
                  value={selectedSource}
                  onChange={(e) =>
                    setSelectedSource(e.target.value as 'etsy' | 'tiktok_shop')
                  }
                  className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="etsy">Etsy</option>
                  <option value="tiktok_shop">TikTok Shop</option>
                </select>
              </div>
              <button
                onClick={handleExportProducts}
                disabled={exportProductsMutation.isPending}
                className="w-full bg-green-600 dark:bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-700 dark:hover:bg-green-600 disabled:opacity-50"
              >
                {exportProductsMutation.isPending
                  ? 'Exporting...'
                  : 'Export Products'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Sync History */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Sync History</h2>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {syncLogs && syncLogs.length > 0 ? (
            syncLogs.map((log) => (
              <div key={log.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {log.sync_type.replace('_', ' ').toUpperCase()} - {log.source}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Started: {new Date(log.started_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        log.status === 'success'
                          ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                          : log.status === 'failed'
                          ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                          : log.status === 'in_progress'
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                          : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                      }`}
                    >
                      {log.status}
                    </span>
                    {log.records_processed > 0 && (
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {log.records_successful}/{log.records_processed} successful
                      </span>
                    )}
                  </div>
                </div>
                {log.error_message && (
                  <p className="mt-2 text-sm text-red-600 dark:text-red-400">{log.error_message}</p>
                )}
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
              No sync history yet. Start syncing to see logs here.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
