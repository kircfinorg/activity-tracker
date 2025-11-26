import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import ConnectionStatus from '@/components/ConnectionStatus'

export const metadata: Metadata = {
  title: 'Gamified Activity Tracker',
  description: 'Track activities and earn rewards',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <ThemeProvider>
            <ConnectionStatus />
            {children}
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
