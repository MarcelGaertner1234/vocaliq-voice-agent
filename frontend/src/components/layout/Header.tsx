import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline'

function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Dashboard</h2>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <BellIcon className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Admin User</p>
                <p className="text-xs text-gray-500">admin@vocaliq.ai</p>
              </div>
              <UserCircleIcon className="h-8 w-8 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header