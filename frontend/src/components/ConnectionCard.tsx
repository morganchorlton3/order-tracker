import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getEtsyAuthStatus, getEtsyAuthUrl } from '../services/api'

interface ConnectionCardProps {
  name: string
  description: string
  icon: React.ReactNode
  source: 'etsy' | 'tiktok_shop'
  color: string
  darkColor: string
}

export default function ConnectionCard({ name, description, icon, source, color, darkColor }: ConnectionCardProps) {
  const queryClient = useQueryClient()
  const [authWindow, setAuthWindow] = useState<Window | null>(null)

  // Only fetch Etsy auth status for now
  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['etsyAuthStatus'],
    queryFn: getEtsyAuthStatus,
    refetchInterval: 5000,
    enabled: source === 'etsy',
  })

  const authorizeMutation = useMutation({
    mutationFn: getEtsyAuthUrl,
    onSuccess: (data) => {
      const width = 600
      const height = 700
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2

      const popup = window.open(
        data.authorization_url,
        `${name} Authorization`,
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no,scrollbars=yes,resizable=yes`
      )

      if (popup) {
        setAuthWindow(popup)

        const messageHandler = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return
          if (event.data.type === 'ETSY_AUTH_SUCCESS' || event.data.type === 'ETSY_AUTH_ERROR') {
            if (popup && !popup.closed) {
              popup.close()
            }
            clearInterval(checkClosed)
            setAuthWindow(null)
            queryClient.invalidateQueries({ queryKey: ['etsyAuthStatus'] })
            window.removeEventListener('message', messageHandler)
          }
        }
        window.addEventListener('message', messageHandler)
        
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed)
            setAuthWindow(null)
            window.removeEventListener('message', messageHandler)
            queryClient.invalidateQueries({ queryKey: ['etsyAuthStatus'] })
          }
        }, 1000)
      }
    },
  })

  const handleAuthorize = () => {
    if (source === 'etsy') {
      authorizeMutation.mutate()
    } else {
      // TODO: Implement TikTok Shop auth
      alert('TikTok Shop authentication coming soon!')
    }
  }

  const isAuthenticated = source === 'etsy' && authStatus?.authenticated === true
  const isConnecting = source === 'etsy' && (authorizeMutation.isPending || authWindow !== null)

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          <div className={`flex-shrink-0 p-3 rounded-lg ${color} ${darkColor}`}>
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{name}</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>
            {isAuthenticated && authStatus?.shop_name && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Connected to: <span className="font-medium">{authStatus.shop_name}</span>
              </p>
            )}
            {isAuthenticated && authStatus?.expires_at && (
              <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                Expires: {new Date(authStatus.expires_at).toLocaleString()}
              </p>
            )}
          </div>
        </div>
        <div className="ml-4 flex-shrink-0">
          {isAuthenticated ? (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
              Connected
            </span>
          ) : (
            <button
              onClick={handleAuthorize}
              disabled={isConnecting}
              className={`${color} ${darkColor} text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium`}
            >
              {isConnecting ? 'Connecting...' : 'Connect'}
            </button>
          )}
        </div>
      </div>
      {authWindow && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-md">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            Please complete the authorization in the popup window. If the popup was blocked, please allow popups for this site.
          </p>
        </div>
      )}
    </div>
  )
}

