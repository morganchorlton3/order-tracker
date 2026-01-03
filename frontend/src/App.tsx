import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SessionAuth } from "supertokens-auth-react/recipe/session"
import { useEffect } from 'react'
import './config/supertokens'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Orders from './pages/Orders'
import Products from './pages/Products'
import Settings from './pages/Settings'
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
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            {/* Public landing page */}
            <Route path="/" element={<Landing />} />
            
            {/* Auth routes */}
            <Route path="/auth/signin" element={<SignIn />} />
            <Route path="/auth/signup" element={<SignUp />} />
            
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
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/auth/etsy/callback" element={<EtsyCallback />} />
                    </Routes>
                  </Layout>
                </SessionAuth>
              }
            />
          </Routes>
        </Router>
      </QueryClientProvider>
    </ThemeProvider>
  )
}

export default App

