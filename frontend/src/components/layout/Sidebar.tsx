import { Link, useLocation } from 'react-router-dom'
import { 
  ChartBarIcon, 
  PhoneIcon, 
  DocumentTextIcon, 
  CogIcon,
  PhoneArrowUpRightIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/app/dashboard', icon: ChartBarIcon },
  { name: 'Leads', href: '/app/leads', icon: UserGroupIcon },
  { name: 'Call History', href: '/app/calls', icon: PhoneIcon },
  { name: 'Knowledge Base', href: '/app/knowledge', icon: DocumentTextIcon },
  { name: 'Test Call', href: '/app/test-call', icon: PhoneArrowUpRightIcon },
  { name: 'Settings', href: '/app/settings', icon: CogIcon },
]

function Sidebar() {
  const location = useLocation()

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold text-primary-600">VocalIQ</h1>
      </div>
      
      <nav className="mt-8 px-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                    ${isActive 
                      ? 'bg-primary-50 text-primary-700' 
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </div>
  )
}

export default Sidebar