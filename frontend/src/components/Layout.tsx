import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ClipboardList, Home, PlusCircle } from 'lucide-react'

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()

  const navItems = [
    { to: '/', label: 'Dashboard', icon: Home },
    { to: '/inspections/new', label: 'Nova Inspeção', icon: PlusCircle },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-slate-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold">
            <ClipboardList size={28} />
            MSBD-360
          </Link>
          <nav className="flex gap-4">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.to
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-1 px-3 py-2 rounded text-sm transition-colors ${
                    isActive
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <Icon size={16} />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        {children}
      </main>
    </div>
  )
}
