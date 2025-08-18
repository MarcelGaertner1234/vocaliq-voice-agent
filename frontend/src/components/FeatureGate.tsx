import React from 'react'
import { useAuthStore } from '../stores/authStore'
import { LockClosedIcon } from '@heroicons/react/24/outline'

interface FeatureGateProps {
  feature: string
  children: React.ReactNode
  showLocked?: boolean
  fallback?: React.ReactNode
}

export default function FeatureGate({ 
  feature, 
  children, 
  showLocked = false,
  fallback = null 
}: FeatureGateProps) {
  const { user } = useAuthStore()
  
  // Map feature strings to actual feature flags
  const featureMap: Record<string, string[]> = {
    // Professional Features
    'lead_scoring': ['professional', 'enterprise'],
    'lead_dashboard': ['professional', 'enterprise'],
    'manual_follow_up': ['professional', 'enterprise'],
    'basic_analytics': ['professional', 'enterprise'],
    
    // Enterprise Features
    'auto_follow_up': ['enterprise'],
    'lead_reactivation': ['enterprise'],
    'lead_enrichment': ['enterprise'],
    'roi_analytics': ['enterprise'],
    'bulk_operations': ['enterprise'],
    'api_access': ['enterprise'],
    'custom_scripts': ['enterprise'],
  }
  
  // Get user's subscription plan (default to 'basic' if not set)
  const userPlan = user?.subscription_plan || 'basic'
  
  // Check if user has access to feature
  const allowedPlans = featureMap[feature] || []
  const hasAccess = allowedPlans.includes(userPlan)
  
  if (hasAccess) {
    return <>{children}</>
  }
  
  if (showLocked) {
    return (
      <div className="relative">
        <div className="opacity-50 pointer-events-none">
          {children}
        </div>
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-50">
          <div className="text-center">
            <LockClosedIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">
              {getPlanRequirement(feature)}
            </p>
          </div>
        </div>
      </div>
    )
  }
  
  return <>{fallback}</>
}

function getPlanRequirement(feature: string): string {
  const requirements: Record<string, string> = {
    'lead_scoring': 'Professional Plan erforderlich',
    'lead_dashboard': 'Professional Plan erforderlich',
    'manual_follow_up': 'Professional Plan erforderlich',
    'basic_analytics': 'Professional Plan erforderlich',
    'auto_follow_up': 'Enterprise Plan erforderlich',
    'lead_reactivation': 'Enterprise Plan erforderlich',
    'lead_enrichment': 'Enterprise Plan erforderlich',
    'roi_analytics': 'Enterprise Plan erforderlich',
    'bulk_operations': 'Enterprise Plan erforderlich',
    'api_access': 'Enterprise Plan erforderlich',
    'custom_scripts': 'Enterprise Plan erforderlich',
  }
  
  return requirements[feature] || 'Upgrade erforderlich'
}