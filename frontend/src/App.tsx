import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { getSuperTokensRoutesForReactRouterDom } from "supertokens-auth-react/ui"
import { EmailPasswordPreBuiltUI } from "supertokens-auth-react/recipe/emailpassword/prebuiltui"
import { SessionAuth } from "supertokens-auth-react/recipe/session"
import { useEffect } from 'react'
import * as reactRouterDom from "react-router-dom"
import './config/supertokens'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Orders from './pages/Orders'
import Products from './pages/Products'
import Sync from './pages/Sync'
import EtsyCallback from './pages/EtsyCallback'
import { syncUser } from './services/api'

const queryClient = new QueryClient()

// Component to sync user after authentication
function UserSync() {
  useEffect(() => {
    // Sync user in local database when component mounts (user is authenticated)
    syncUser().catch(err => {
      console.error('Failed to sync user:', err)
    })
  }, [])
  return null
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Public landing page */}
          <Route path="/" element={<Landing />} />
          
          {/* SuperTokens auth routes */}
          {getSuperTokensRoutesForReactRouterDom(reactRouterDom, [EmailPasswordPreBuiltUI])}
          
          {/* Protected routes */}
          <Route
            path="/*"
            element={
              <SessionAuth>
                <UserSync />
                <Layout>
                  <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/orders" element={<Orders />} />
                    <Route path="/products" element={<Products />} />
                    <Route path="/sync" element={<Sync />} />
                    <Route path="/auth/etsy/callback" element={<EtsyCallback />} />
                  </Routes>
                </Layout>
              </SessionAuth>
            }
          />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App

