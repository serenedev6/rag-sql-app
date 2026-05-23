import { Sidebar } from './Sidebar'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
      <Sidebar />
      
      {/* Main Content - Full height, proper mobile handling */}
      <main className="flex-1 overflow-auto lg:ml-64 w-full">
        <div className="min-h-full">
          {children}
        </div>
      </main>
    </div>
  )
}