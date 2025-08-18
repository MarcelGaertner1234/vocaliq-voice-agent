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
import LeadDashboard from '../pages/LeadDashboard'

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
import AdminLeadDashboard from '../pages/AdminLeadDashboard'

// Legal Pages
import Datenschutz from '../pages/Datenschutz'
import Impressum from '../pages/Impressum'
import AGB from '../pages/AGB'
import Kontakt from '../pages/Kontakt'
import Preise from '../pages/Preise'

// Landing Page
import ProfessionalLanding from '../pages/ProfessionalLanding'

function AppRoutes() {
  return (
    <Routes>
      {/* Root redirect to landing page */}
      <Route path="/" element={<ProfessionalLanding />} />
      
      {/* Legal Pages */}
      <Route path="/datenschutz" element={<Datenschutz />} />
      <Route path="/impressum" element={<Impressum />} />
      <Route path="/agb" element={<AGB />} />
      <Route path="/kontakt" element={<Kontakt />} />
      <Route path="/preise" element={<Preise />} />
      
      {/* Auth Routes */}
      <Route path="/login" element={<CustomerLogin />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      
      {/* Customer Routes */}
      <Route path="/app" element={<DashboardLayout />}>
        <Route index element={<Navigate to="/app/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="calls" element={<CallHistory />} />
        <Route path="knowledge" element={<KnowledgeBase />} />
        <Route path="leads" element={<LeadDashboard />} />
        <Route path="leads/:id" element={<LeadDashboard />} />
        <Route path="test-call" element={<TestCall />} />
        <Route path="settings" element={<Settings />} />
        <Route path="debug" element={<Debug />} />
      </Route>
      
      {/* Admin Routes */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="leads" element={<AdminLeadDashboard />} />
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