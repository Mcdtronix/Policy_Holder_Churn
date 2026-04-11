import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { apiService } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, AreaChart, Area } from 'recharts';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Download, Printer, Loader2, AlertTriangle } from 'lucide-react';
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

interface ChurnByLocation {
  location: string;
  churnRate: number;
  policyCount: number;
}

interface ChurnByAge {
  group: string;
  churnRate: number;
  count: number;
}

export default function ReportsPage() {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [churnByLocation, setChurnByLocation] = useState<ChurnByLocation[]>([]);
  const [churnByAge, setChurnByAge] = useState<ChurnByAge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReportsData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [statsRes, trendsRes, locationRes, ageRes] = await Promise.all([
          apiService.getDashboardStats(),
          apiService.getMonthlyTrends(),
          apiService.getChurnByLocation(),
          apiService.getChurnByAge()
        ]);

        setDashboardStats(statsRes);
        setMonthlyData(trendsRes);
        setChurnByLocation(locationRes);
        setChurnByAge(ageRes);

      } catch (err: any) {
        console.error('Failed to fetch reports data:', err);
        setError(err.message || 'Failed to load reports data');
        toast.error('Failed to load reports data');
      } finally {
        setLoading(false);
      }
    };

    fetchReportsData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading reports data...</p>
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
            <p className="text-destructive mb-2">Error loading reports</p>
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
      <div className="page-header flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1>Reports & Analytics</h1>
          <p>Comprehensive business intelligence reports</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm"><Printer className="h-4 w-4 mr-2" />Print</Button>
          <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" />Export CSV</Button>
        </div>
      </div>

      {/* KPI Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Policies', value: dashboardStats.totalPolicies.toLocaleString() },
          { label: 'Active Rate', value: `${((dashboardStats.activePolicies / dashboardStats.totalPolicies) * 100).toFixed(1)}%` },
          { label: 'Churn Rate', value: `${dashboardStats.avgChurnRate.toFixed(1)}%` },
          { label: 'Monthly Revenue', value: `$${dashboardStats.totalPremiumRevenue.toLocaleString()}` },
          { label: 'Claims Processed', value: dashboardStats.claimsProcessed.toString() },
        ].map((kpi, i) => (
          <div key={i} className="stat-card text-center">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">{kpi.label}</p>
            <p className="text-xl font-bold mt-1 font-sans">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Revenue Trend */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="stat-card mb-6">
        <h3 className="text-sm font-semibold mb-4 font-sans">Revenue Trend (Monthly)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
            <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
            <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
            <Area type="monotone" dataKey="revenue" stroke="hsl(var(--accent))" fill="hsl(var(--accent))" fillOpacity={0.15} strokeWidth={2.5} name="Revenue ($)" />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="stat-card">
          <h3 className="text-sm font-semibold mb-4 font-sans">Policy Growth vs Claims</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Line type="monotone" dataKey="newPolicies" stroke="hsl(var(--primary))" strokeWidth={2} name="New Policies" />
              <Line type="monotone" dataKey="claims" stroke="hsl(var(--destructive))" strokeWidth={2} name="Claims" />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="stat-card">
          <h3 className="text-sm font-semibold mb-4 font-sans">Churn by Age Demographics</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={churnByAge}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="group" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Policy Count" />
              <Bar dataKey="churnRate" fill="hsl(var(--destructive))" radius={[4, 4, 0, 0]} name="Churn %" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Location Report Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="data-table-container">
        <div className="p-4 border-b">
          <h3 className="text-sm font-semibold font-sans">Regional Performance Report</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/30">
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Location</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Policy Count</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Churn Rate</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Est. Revenue</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Risk Level</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {churnByLocation.map(loc => (
              <tr key={loc.location} className="hover:bg-muted/20">
                <td className="px-4 py-3 font-medium">{loc.location}</td>
                <td className="px-4 py-3">{loc.policyCount}</td>
                <td className="px-4 py-3">{loc.churnRate.toFixed(1)}%</td>
                <td className="px-4 py-3">${(loc.policyCount * 48).toLocaleString()}</td>
                <td className="px-4 py-3">
                  <span className={loc.churnRate > 70 ? 'badge-danger' : loc.churnRate > 50 ? 'badge-warning' : 'badge-success'}>
                    {loc.churnRate > 70 ? 'High' : loc.churnRate > 50 ? 'Medium' : 'Low'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </DashboardLayout>
  );
}
