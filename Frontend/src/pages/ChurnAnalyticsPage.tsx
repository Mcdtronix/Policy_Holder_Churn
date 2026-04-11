import { useState, useEffect, useMemo } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { StatCard } from '@/components/StatCard';
import { apiService } from '@/lib/api';
import { getChurnRisk, getChurnRiskColor } from '@/lib/types';
import { TrendingDown, AlertTriangle, Users, ShieldAlert, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, ScatterChart, Scatter, CartesianGrid, Legend } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const COLORS = ['hsl(152, 60%, 40%)', 'hsl(210, 80%, 52%)', 'hsl(38, 92%, 50%)', 'hsl(0, 72%, 51%)'];

interface Customer {
  id: number;
  customer_number: string;
  first_name: string;
  last_name: string;
  location: {
    city: string;
  };
  churn_predictions?: Array<{
    churn_percentage: number;
  }>;
  engagement?: {
    service_satisfaction: number;
    number_of_complaints: number;
  };
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

export default function ChurnAnalyticsPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [churnByLocation, setChurnByLocation] = useState<ChurnByLocation[]>([]);
  const [churnByAge, setChurnByAge] = useState<ChurnByAge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [customersRes, locationRes, ageRes] = await Promise.all([
          apiService.getCustomers({ page_size: 1000 }),
          apiService.getChurnByLocation(),
          apiService.getChurnByAge()
        ]);

        setCustomers(customersRes.results || customersRes);
        setChurnByLocation(locationRes);
        setChurnByAge(ageRes);

      } catch (err: any) {
        console.error('Failed to fetch analytics data:', err);
        setError(err.message || 'Failed to load analytics data');
        toast.error('Failed to load analytics data');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  const riskDistribution = useMemo(() => {
    const counts = { low: 0, medium: 0, high: 0, critical: 0 };
    customers.forEach(c => {
      const churnPercentage = c.churn_predictions?.[0]?.churn_percentage || 0;
      counts[getChurnRisk(churnPercentage)]++;
    });
    return [
      { name: 'Low Risk', value: counts.low, risk: 'low' as const },
      { name: 'Medium Risk', value: counts.medium, risk: 'medium' as const },
      { name: 'High Risk', value: counts.high, risk: 'high' as const },
      { name: 'Critical', value: counts.critical, risk: 'critical' as const },
    ];
  }, [customers]);

  const highRisk = useMemo(() => {
    return customers
      .filter(c => (c.churn_predictions?.[0]?.churn_percentage || 0) >= 80)
      .slice(0, 10);
  }, [customers]);

  const avgChurn = useMemo(() => {
    if (customers.length === 0) return '0.0';
    const total = customers.reduce((s, c) => s + (c.churn_predictions?.[0]?.churn_percentage || 0), 0);
    return (total / customers.length).toFixed(1);
  }, [customers]);

  const criticalCount = riskDistribution.find(r => r.risk === 'critical')?.value || 0;

  const scatterData = useMemo(() => {
    return customers.slice(0, 100).map(c => ({
      tenure: 1, // Placeholder - would need policy tenure data
      churn: c.churn_predictions?.[0]?.churn_percentage || 0,
      satisfaction: c.engagement?.service_satisfaction || 0,
      name: `${c.first_name} ${c.last_name}`,
    }));
  }, [customers]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading churn analytics...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-destructive" />
            <p className="text-destructive mb-2">Error loading analytics</p>
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
        <h1>Churn Analytics</h1>
        <p>AI-powered policyholder churn prediction insights from {customers.length}+ customer records</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard title="Average Churn Rate" value={`${avgChurn}%`} change="Based on ML prediction" icon={TrendingDown} iconColor="bg-destructive/10 text-destructive" />
        <StatCard title="Critical Risk" value={criticalCount} change="Immediate attention needed" changeType="down" icon={AlertTriangle} iconColor="bg-warning/10 text-warning" />
        <StatCard title="At-Risk Revenue" value={`$${(criticalCount * 52).toLocaleString()}`} change="Monthly premium at risk" icon={ShieldAlert} iconColor="bg-destructive/10 text-destructive" />
        <StatCard title="Total Analysed" value={customers.length} change="From database" icon={Users} iconColor="bg-primary/10 text-primary" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Risk Distribution Pie */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="stat-card">
          <h3 className="text-sm font-semibold mb-4 font-sans">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={riskDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {riskDistribution.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Churn by Age Group */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="stat-card">
          <h3 className="text-sm font-semibold mb-4 font-sans">Churn Rate by Age Group</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={churnByAge}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="group" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Bar dataKey="churnRate" fill="hsl(var(--accent))" radius={[4, 4, 0, 0]} name="Churn %" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Churn by Location */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="stat-card">
          <h3 className="text-sm font-semibold mb-4 font-sans">Churn Rate by Location</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={churnByLocation} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis type="category" dataKey="location" tick={{ fontSize: 11 }} width={90} stroke="hsl(var(--muted-foreground))" />
              <Tooltip />
              <Bar dataKey="churnRate" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} name="Churn %" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Tenure vs Churn scatter */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="stat-card">
          <h3 className="text-sm font-semibold mb-4 font-sans">Tenure vs Churn Probability</h3>
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" dataKey="tenure" name="Tenure (yrs)" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis type="number" dataKey="churn" name="Churn %" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={scatterData} fill="hsl(var(--destructive))" fillOpacity={0.6} />
            </ScatterChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* High Risk Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="data-table-container">
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="text-sm font-semibold font-sans">Top At-Risk Policy Holders</h3>
          <span className="badge-danger">Requires Immediate Attention</span>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/30">
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Location</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Satisfaction</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Churn %</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {highRisk.map(c => (
              <tr key={c.id} className="hover:bg-muted/20">
                <td className="px-4 py-3 font-medium">{c.first_name} {c.last_name}</td>
                <td className="px-4 py-3">{c.location?.city || 'N/A'}</td>
                <td className="px-4 py-3">{'⭐'.repeat(c.engagement?.service_satisfaction || 0)}</td>
                <td className="px-4 py-3"><span className="badge-danger">{(c.churn_predictions?.[0]?.churn_percentage || 0).toFixed(1)}%</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </DashboardLayout>
  );
}
