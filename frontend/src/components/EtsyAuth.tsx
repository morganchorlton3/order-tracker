import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getEtsyAuthStatus, getEtsyAuthUrl } from '../services/api'

export default function EtsyAuth() {
  const queryClient = useQueryClient()
  const [authWindow, setAuthWindow] = useState<Window | null>(null)

  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['etsyAuthStatus'],
    queryFn: getEtsyAuthStatus,
    refetchInterval: 5000, // Check every 5 seconds
  })

  const authorizeMutation = useMutation({
    mutationFn: getEtsyAuthUrl,
    onSuccess: (data) => {
      // Open the authorization URL in a popup window
      const width = 600
      const height = 700
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2

      const popup = window.open(
        data.authorization_url,
        'Etsy Authorization',
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no,scrollbars=yes,resizable=yes`
      )

      if (popup) {
        setAuthWindow(popup)

        // Listen for messages from the popup (callback page sends them)
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
            
            if (event.data.type === 'ETSY_AUTH_SUCCESS') {
              // Show success message or update UI
              console.log('Etsy authentication successful!', event.data)
            }
          }
        }
        window.addEventListener('message', messageHandler)
        
        // Check if popup was closed manually
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed)
            setAuthWindow(null)
            window.removeEventListener('message', messageHandler)
            // Refetch auth status when popup closes
            queryClient.invalidateQueries({ queryKey: ['etsyAuthStatus'] })
          }
        }, 1000)
      }
    },
  })

  const handleAuthorize = () => {
    authorizeMutation.mutate()
  }

  if (isLoading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">Checking authentication status...</p>
      </div>
    )
  }

  const isAuthenticated = authStatus?.authenticated === true

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Etsy Authentication</h3>
          <p className="mt-1 text-sm text-gray-500">
            {isAuthenticated
              ? `Connected to ${authStatus.shop_name || 'your Etsy shop'}`
              : 'Connect your Etsy account to sync orders'}
          </p>
          {isAuthenticated && authStatus.expires_at && (
            <p className="mt-1 text-xs text-gray-400">
              Expires: {new Date(authStatus.expires_at).toLocaleString()}
            </p>
          )}
        </div>
        <div>
          {isAuthenticated ? (
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                Connected
              </span>
            </div>
          ) : (
            <button
              onClick={handleAuthorize}
              disabled={authorizeMutation.isPending || authWindow !== null}
              className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {authorizeMutation.isPending || authWindow !== null
                ? 'Opening...'
                : 'Connect Etsy'}
            </button>
          )}
        </div>
      </div>
      {authWindow && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            Please complete the authorization in the popup window. If the popup was blocked, please allow popups for this site.
          </p>
        </div>
      )}
    </div>
  )
}

