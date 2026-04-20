import { Sidebar } from "./Sidebar"

interface DashboardLayoutProps {
    children: React.ReactNode
}

export const DashboardLayout = ({children}: DashboardLayoutProps) => {
    return (
        <div className="flex h-screen bg-gray-950">
            <Sidebar />
            <main className="flex-1 ml-64 overflow-y-auto">
                {children}
            </main>
        </div>
    )
}