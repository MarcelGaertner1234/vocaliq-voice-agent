import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '../components/layout/DashboardLayout'
import AdminLayout from '../layouts/AdminLayout'

// Customer Pages
import Dashboard from '../pages/Dashboard'
import CallHistory from '../pages/CallHistory'
import KnowledgeBase from '../pages/KnowledgeBase'
import Settings from '../pages/Settings'
import Debug from '../pages/Debug'
import TestCall from '../pages/TestCall'

// Auth Pages
import AdminLogin from '../pages/auth/AdminLogin'
import CustomerLogin from '../pages/auth/CustomerLogin'

// Admin Pages
import AdminDashboard from '../pages/admin/AdminDashboard'
import ApiConfiguration from '../pages/admin/ApiConfiguration'
import PhoneNumbers from '../pages/admin/PhoneNumbers'
import Companies from '../pages/admin/Companies'
import Users from '../pages/admin/Users'
import Analytics from '../pages/admin/Analytics'
import SystemSettings from '../pages/admin/SystemSettings'
import Logs from '../pages/admin/Logs'
import Webhooks from '../pages/admin/Webhooks'

function AppRoutes() {
  return (
    <Routes>
      {/* Root redirect */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      
      {/* Auth Routes */}
      <Route path="/login" element={<CustomerLogin />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      
      {/* Customer Routes */}
      <Route path="/" element={<DashboardLayout />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="calls" element={<CallHistory />} />
        <Route path="knowledge" element={<KnowledgeBase />} />
        <Route path="test-call" element={<TestCall />} />
        <Route path="settings" element={<Settings />} />
        <Route path="debug" element={<Debug />} />
      </Route>
      
      {/* Admin Routes */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="api-config" element={<ApiConfiguration />} />
        <Route path="phone-numbers" element={<PhoneNumbers />} />
        <Route path="companies" element={<Companies />} />
        <Route path="users" element={<Users />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="settings" element={<SystemSettings />} />
        <Route path="logs" element={<Logs />} />
        <Route path="webhooks" element={<Webhooks />} />
      </Route>
    </Routes>
  )
}

export default AppRoutes