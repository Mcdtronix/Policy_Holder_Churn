import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { StatCard } from '@/components/StatCard';
import { apiService } from '@/lib/api';
import { Users, FileText, AlertTriangle, DollarSign, TrendingUp, ClipboardList, CalendarCheck, UserPlus, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

interface DashboardStats {
  totalPolicies: number;
  activePolicies: number;
  pendingClaims: number;
  totalPremiumRevenue: number;
  avgChurnRate: number;
  newPoliciesThisMonth: number;
  claimsProcessed: number;
  maturedPolicies: number;
  highRiskCustomers: number;
}

interface MonthlyData {
  month: string;
  newPolicies: number;
  claims: number;
  revenue: number;
  churnRate: number;
}

interface RecentActivity {
  id: string;
  type: string;
  description: string;
  time: string;
  status: string;
}

export default function DashboardPage() {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch dashboard stats
        const statsResponse = await apiService.getDashboardStats();
        setDashboardStats(statsResponse);

        // Fetch monthly trends
        const trendsResponse = await apiService.get('/api/v1/analytics/monthly_trends/');
        setMonthlyData(trendsResponse);

        // Fetch recent activities
        const activitiesResponse = await apiService.get('/api/v1/analytics/recent_activities/');
        setRecentActivities(activitiesResponse);

      } catch (err: any) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err.message || 'Failed to load dashboard data');
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading dashboard data...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !dashboardStats) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-destructive" />
            <p className="text-destructive mb-2">Error loading dashboard</p>
            <p className="text-sm text-muted-foreground">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1>Dashboard Overview</h1>
        <p>Welcome back, Admin. Here's your policy management summary.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard title="Total Policies" value={dashboardStats.totalPolicies.toLocaleString()} change="+12% from last month" changeType="up" icon={FileText} />
        <StatCard title="Active Policies" value={dashboardStats.activePolicies.toLocaleString()} change={`${((dashboardStats.activePolicies / dashboardStats.totalPolicies) * 100).toFixed(1)}% active rate`} changeType="up" icon={Users} iconColor="bg-success/10 text-success" />
        <StatCard title="Pending Claims" value={dashboardStats.pendingClaims} change="5 urgent" changeType="down" icon={ClipboardList} iconColor="bg-warning/10 text-warning" />
        <StatCard title="Avg Churn Rate" value={`${dashboardStats.avgChurnRate.toFixed(1)}%`} change="-2.1% from last month" changeType="down" icon={AlertTriangle} iconColor="bg-destructive/10 text-destructive" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard title="Premium Revenue" value={`$${dashboardStats.totalPremiumRevenue.toLocaleString()}`} change="+8.5% this month" changeType="up" icon={DollarSign} iconColor="bg-accent/20 text-accent-foreground" />
        <StatCard title="New This Month" value={dashboardStats.newPoliciesThisMonth} change="+18 from last week" changeType="up" icon={UserPlus} iconColor="bg-info/10 text-info" />
        <StatCard title="Claims Processed" value={dashboardStats.claimsProcessed} change="87% approval rate" changeType="neutral" icon={TrendingUp} iconColor="bg-success/10 text-success" />
        <StatCard title="Matured Policies" value={dashboardStats.maturedPolicies} change="Pending payout" changeType="neutral" icon={CalendarCheck} iconColor="bg-primary/10 text-primary" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="stat-card">
          <h3 className="text-sm font-semibold text-foreground mb-4 font-sans">New Policies & Claims (Monthly)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid hsl(var(--border))' }} />
              <Bar dataKey="newPolicies" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="New Policies" />
              <Bar dataKey="claims" fill="hsl(var(--accent))" radius={[4, 4, 0, 0]} name="Claims" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="stat-card">
          <h3 className="text-sm font-semibold text-foreground mb-4 font-sans">Churn Rate Trend (%)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid hsl(var(--border))' }} />
              <Line type="monotone" dataKey="churnRate" stroke="hsl(var(--destructive))" strokeWidth={2.5} dot={{ r: 4, fill: 'hsl(var(--destructive))' }} name="Churn %" />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="data-table-container">
        <div className="p-4 border-b">
          <h3 className="text-sm font-semibold text-foreground font-sans">Recent Activity</h3>
        </div>
        <div className="divide-y">
          {recentActivities.map(activity => (
            <div key={activity.id} className="px-4 py-3 flex items-center justify-between hover:bg-muted/30 transition-colors">
              <div>
                <p className="text-sm text-foreground">{activity.description}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{activity.time}</p>
              </div>
              <span className={
                activity.status === 'pending' ? 'badge-warning' :
                activity.status === 'active' || activity.status === 'completed' || activity.status === 'approved' ? 'badge-success' :
                activity.status === 'matured' ? 'badge-info' : 'badge-danger'
              }>
                {activity.status}
              </span>
            </div>
          ))}
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
