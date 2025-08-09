import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '../components/layout/DashboardLayout'
import Dashboard from '../pages/Dashboard'
import CallHistory from '../pages/CallHistory'
import KnowledgeBase from '../pages/KnowledgeBase'
import Settings from '../pages/Settings'
import Debug from '../pages/Debug'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/" element={<DashboardLayout />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="calls" element={<CallHistory />} />
        <Route path="knowledge" element={<KnowledgeBase />} />
        <Route path="settings" element={<Settings />} />
        <Route path="debug" element={<Debug />} />
      </Route>
    </Routes>
  )
}

export default AppRoutes