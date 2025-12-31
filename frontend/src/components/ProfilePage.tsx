import { useState, useEffect } from 'react';
import { Database, BarChart3, Lightbulb, Loader2 } from 'lucide-react';
import Navbar from './Navbar';
import { useAuth } from '../lib/auth-context';
import { getToken, userAPI } from '../lib/api-client';
import type { UserProfileResponse } from '../lib/api-types';

export default function ProfilePage() {
  const { logout } = useAuth();
  const [profile, setProfile] = useState<UserProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = getToken() || "";
        const data = await userAPI.getProfile(token);
        setProfile(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-6 py-12 text-center">
          <Loader2 className="w-8 h-8 text-neutral-400 animate-spin mx-auto" />
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
            {error || 'Failed to load profile'}
          </div>
        </div>
      </div>
    );
  }

  const userInitial = profile.name ? profile.name.charAt(0).toUpperCase() : profile.email.charAt(0).toUpperCase();

  return (
    <div className="min-h-screen bg-neutral-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-neutral-900 mb-8">Profile</h1>

        <div className="bg-white border border-neutral-200 rounded-lg p-8 mb-8">
          <h2 className="text-neutral-900 mb-6">Profile Information</h2>

          <div className="flex items-start gap-6 mb-8">
            <div className="w-20 h-20 rounded-full bg-neutral-900 text-white flex items-center justify-center flex-shrink-0">
              <span className="text-2xl">{userInitial}</span>
            </div>

            <div className="flex-1">
              <div className="mb-4">
                <label className="block text-neutral-600 mb-1">Name</label>
                <p className="text-neutral-900">{profile.name || 'Not set'}</p>
              </div>

              <div className="mb-4">
                <label className="block text-neutral-600 mb-1">Email</label>
                <p className="text-neutral-900">{profile.email}</p>
              </div>

              <div className="mb-4">
                <label className="block text-neutral-600 mb-1">Account Status</label>
                <p className="text-neutral-900">
                  {profile.is_active ? (
                    <span className="text-green-600">Active</span>
                  ) : (
                    <span className="text-red-600">Inactive</span>
                  )}
                </p>
              </div>

              <div>
                <label className="block text-neutral-600 mb-1">Account Created</label>
                <p className="text-neutral-900">
                  {new Date(profile.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-neutral-200 rounded-lg p-8 mb-8">
          <h2 className="text-neutral-900 mb-6">Usage Statistics</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-neutral-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-2">
                <Database className="w-5 h-5 text-neutral-600" />
                <p className="text-neutral-600">Datasets Uploaded</p>
              </div>
              <p className="text-neutral-900">{profile.stats.datasets_uploaded}</p>
            </div>

            <div className="border border-neutral-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="w-5 h-5 text-neutral-600" />
                <p className="text-neutral-600">Dashboards Created</p>
              </div>
              <p className="text-neutral-900">{profile.stats.dashboards_created}</p>
            </div>

            <div className="border border-neutral-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-2">
                <Lightbulb className="w-5 h-5 text-neutral-600" />
                <p className="text-neutral-600">Insights Generated</p>
              </div>
              <p className="text-neutral-900">{profile.stats.insights_generated}</p>
            </div>
          </div>
        </div>

        <div className="bg-white border border-neutral-200 rounded-lg p-8">
          <h2 className="text-neutral-900 mb-6">Account Actions</h2>

          <button
            onClick={logout}
            className="bg-neutral-900 text-white py-2 px-6 rounded-md hover:bg-neutral-800 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
