import { Link, useLocation } from 'react-router-dom'
import { FileText, Upload, Users, Activity } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Documents', icon: FileText },
  { path: '/upload', label: 'Upload', icon: Upload },
  { path: '/patients', label: 'Patients', icon: Users },
]

export default function Navbar() {
  const location = useLocation()
  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-clinical-600" />
            <span className="text-lg font-bold text-gray-900">Clinical Doc Hub</span>
          </Link>
          <div className="flex gap-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === path
                    ? 'bg-clinical-50 text-clinical-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
