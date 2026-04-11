import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Button } from '@/components/ui/button';
import { CalendarCheck, DollarSign, Eye, Download, Loader2, AlertTriangle } from 'lucide-react';
import { StatCard } from '@/components/StatCard';
import { apiService } from '@/lib/api';
import { toast } from 'sonner';

interface MaturedPolicy {
  id: string;
  policy_number: string;
  customer: {
    first_name: string;
    last_name: string;
  };
  policy_type: {
    name: string;
  };
  start_date: string;
  end_date: string;
  premium_amount: string;
  sum_assured: string;
  status: string;
}

export default function MaturedPoliciesPage() {
  const [policies, setPolicies] = useState<MaturedPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMaturedPolicies = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getPolicies({ status: 'MATURED', page_size: 100 });
        setPolicies(response.results || response);
      } catch (err: any) {
        console.error('Failed to fetch matured policies:', err);
        setError(err.message || 'Failed to load matured policies');
        toast.error('Failed to load matured policies');
      } finally {
        setLoading(false);
      }
    };

    fetchMaturedPolicies();
  }, []);

  const pendingCount = policies.filter(p => p.status === 'MATURED').length;
  const totalPayout = policies.reduce((sum, p) => sum + parseFloat(p.sum_assured), 0);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading matured policies...</p>
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
            <p className="text-destructive mb-2">Error loading matured policies</p>
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
          <h1>Matured Policies</h1>
          <p>Policies that have reached maturity and are eligible for payout</p>
        </div>
        <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" />Export</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <StatCard title="Total Matured" value={policies.length} icon={CalendarCheck} iconColor="bg-primary/10 text-primary" />
        <StatCard title="Pending Payout" value={pendingCount} change="Requires processing" changeType="down" icon={CalendarCheck} iconColor="bg-warning/10 text-warning" />
        <StatCard title="Total Payout Due" value={`$${totalPayout.toLocaleString()}`} icon={DollarSign} iconColor="bg-accent/20 text-accent-foreground" />
      </div>

      <div className="data-table-container overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/30">
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Policy #</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Holder</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Type</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Start Date</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Maturity Date</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Premium</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Payout</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {policies.map(p => (
              <tr key={p.id} className="hover:bg-muted/20">
                <td className="px-4 py-3 font-mono text-xs">{p.policy_number}</td>
                <td className="px-4 py-3 font-medium">{p.customer.first_name} {p.customer.last_name}</td>
                <td className="px-4 py-3">{p.policy_type.name}</td>
                <td className="px-4 py-3">{new Date(p.start_date).toLocaleDateString()}</td>
                <td className="px-4 py-3">{p.end_date ? new Date(p.end_date).toLocaleDateString() : 'N/A'}</td>
                <td className="px-4 py-3">${parseFloat(p.premium_amount).toLocaleString()}</td>
                <td className="px-4 py-3 font-semibold">${parseFloat(p.sum_assured).toLocaleString()}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 badge-success">
                    <CalendarCheck className="h-3 w-3" />
                    Matured
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Button variant="ghost" size="icon" className="h-7 w-7"><Eye className="h-3.5 w-3.5" /></Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
