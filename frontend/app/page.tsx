'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Loader2 } from 'lucide-react'

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    console.log('Home page effect:', { isAuthenticated, isLoading, pathname })
    
    if (!isLoading) {
      if (isAuthenticated) {
        router.push('/dashboard')
      } else {
        if (pathname !== '/login' && pathname !== '/signup') {
          router.push('/login')
        }
      }
    }
  }, [isAuthenticated, isLoading, router, pathname])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="text-gray-600">Loading Socivio...</p>
      </div>
    </div>
  )
}
