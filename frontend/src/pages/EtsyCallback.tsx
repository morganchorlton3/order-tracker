import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'

export default function EtsyCallback() {
  const [searchParams] = useSearchParams()
  const code = searchParams.get('code')
  const error = searchParams.get('error')
  const errorDescription = searchParams.get('error_description')

  useEffect(() => {
    // Notify parent window of the result
    if (window.opener) {
      if (error) {
        window.opener.postMessage(
          {
            type: 'ETSY_AUTH_ERROR',
            error,
            errorDescription,
          },
          window.location.origin
        )
      } else if (code) {
        window.opener.postMessage(
          {
            type: 'ETSY_AUTH_SUCCESS',
            code,
          },
          window.location.origin
        )
      }
      // Close the popup
      window.close()
    } else {
      // If not in a popup, redirect to sync page
      window.location.href = '/sync'
    }
  }, [code, error, errorDescription])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        {error ? (
          <>
            <h1 className="text-2xl font-bold text-red-600 mb-4">Authentication Failed</h1>
            <p className="text-gray-600">{errorDescription || error}</p>
          </>
        ) : (
          <>
            <h1 className="text-2xl font-bold text-green-600 mb-4">Authentication Successful!</h1>
            <p className="text-gray-600">You can close this window.</p>
          </>
        )}
      </div>
    </div>
  )
}

