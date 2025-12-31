import { useParams } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { TrendingUp, AlertCircle, Database, Loader2 } from 'lucide-react';
import Navbar from './Navbar';
import WidgetRenderer from './widgets/WidgetRenderer';
import { dashboardAPI, getToken, insightAPI } from '../lib/api-client';
import type { DashboardResponse, InsightResponse } from '../lib/api-types';

const INSIGHTS_POLL_INTERVAL = 5000; // 5 seconds

export default function DashboardPage() {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [insights, setInsights] = useState<InsightResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [error, setError] = useState('');
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const insightsGeneratedRef = useRef(false);

  useEffect(() => {
    const fetchDashboard = async () => {
      if (!datasetId) return;

      try {
        const token = getToken();
        if (!token) throw new Error('User not authenticated');
        const data = await dashboardAPI.getByDataset(datasetId,token);
        console.log('Fetched dashboard:', data);
        setDashboard(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [datasetId]);

  // Generate insights once when dashboard loads
  useEffect(() => {
    const generateInsights = async () => {
      if (!datasetId || !dashboard || insightsGeneratedRef.current) return;

      insightsGeneratedRef.current = true;
      try {
        const token = getToken();
        if (!token) throw new Error('User not authenticated');
        await insightAPI.generate(datasetId,token);
      } catch (err) {
        console.error('Failed to generate insights:', err);
      }
    };

    generateInsights();
  }, [datasetId, dashboard]);

  // Poll for insights
  useEffect(() => {
    const fetchInsights = async () => {
      if (!datasetId) return;

      try {
        const token = getToken();
        if (!token) throw new Error('User not authenticated');
        const data = await insightAPI.get(datasetId,token);
        setInsights(data);
        setInsightsLoading(false);
        
        // Stop polling once we have insights
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
      } catch (err) {
        // Insights might not be ready yet, keep polling
        console.log('Insights not ready yet');
      }
    };

    if (dashboard && !insights) {
      fetchInsights();
      pollIntervalRef.current = setInterval(fetchInsights, INSIGHTS_POLL_INTERVAL);
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [datasetId, dashboard, insights]);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend':
        return <TrendingUp className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />;
      case 'anomaly':
        return <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />;
      case 'data_quality':
        return <Database className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />;
      default:
        return <AlertCircle className="w-5 h-5 text-neutral-600 flex-shrink-0 mt-0.5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-6 py-12 text-center">
          <Loader2 className="w-8 h-8 text-neutral-400 animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-6 py-12">
          <p className="text-neutral-600">Dashboard not found</p>
        </div>
      </div>
    );
  }

  // Separate KPI and chart widgets
  const kpiWidgets = dashboard.widgets.filter(w => w.type === 'kpi');
  const chartWidgets = dashboard.widgets.filter(w => w.type === 'chart');

  return (
    <div className="min-h-screen bg-neutral-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-neutral-900 mb-2">{dashboard.title}</h1>
          <p className="text-neutral-600">Dataset ID: {dashboard.dataset_id}</p>
        </div>

        {/* KPI Section */}
        {kpiWidgets.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {kpiWidgets.map(widget => (
              <WidgetRenderer key={widget.widget_id} widget={widget} />
            ))}
          </div>
        )}

        {/* Charts Section */}
        {chartWidgets.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {chartWidgets.map(widget => (
              <WidgetRenderer key={widget.widget_id} widget={widget} />
            ))}
          </div>
        )}

        {/* Insights Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-neutral-200 rounded-lg p-6">
            <h3 className="text-neutral-900 mb-4">Key Insights</h3>
            
            {insightsLoading ? (
              <div className="flex items-center gap-2 text-neutral-600">
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating insights...
              </div>
            ) : insights && insights.insights.length > 0 ? (
              <ul className="space-y-3">
                {insights.insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-2">
                    {getInsightIcon(insight.type)}
                    <span className="text-neutral-700">{insight.message}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-neutral-500">No insights available yet.</p>
            )}
          </div>

          <div className="bg-neutral-900 text-white rounded-lg p-6">
            <h3 className="mb-4">Summary</h3>
            
            {insightsLoading ? (
              <div className="flex items-center gap-2 text-neutral-300">
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating summary...
              </div>
            ) : insights && insights.summary ? (
              <>
                <p className="text-neutral-300 mb-4">{insights.summary}</p>
                <p className="text-neutral-500">Generated automatically</p>
              </>
            ) : (
              <p className="text-neutral-400">Summary will appear once insights are generated.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
