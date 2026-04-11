import { useState, useEffect, useMemo } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { apiService } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Search, Eye, CheckCircle, XCircle, Clock, Loader2, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

interface Claim {
  id: number;
  claim_number: string;
  policy?: {
    policy_number: string;
    customer?: {
      first_name: string;
      last_name: string;
    };
  };
  claim_type: string;
  amount_claimed: string;
  reported_date: string;
  status: string;
}

const PAGE_SIZE = 15;

export default function ClaimsManagementPage() {
  const navigate = useNavigate();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchClaims = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getClaims({ page_size: 100 });
        setClaims(response.results || response);
      } catch (err: any) {
        console.error('Failed to fetch claims:', err);
        setError(err.message || 'Failed to load claims');
        toast.error('Failed to load claims');
      } finally {
        setLoading(false);
      }
    };

    fetchClaims();
  }, []);

  const filtered = useMemo(() => {
    return claims.filter(c => {
      // Safely extract data with fallbacks
      const customer = c.policy?.customer;
      const firstName = customer?.first_name || 'Unknown';
      const lastName = customer?.last_name || 'Customer';
      const policyNumber = c.policy?.policy_number || 'N/A';
      
      const fullName = `${firstName} ${lastName}`.toLowerCase();
      const matchSearch = fullName.includes(search.toLowerCase()) ||
        c.claim_number.toLowerCase().includes(search.toLowerCase()) ||
        policyNumber.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'all' || c.status.toLowerCase() === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [claims, search, statusFilter]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const statusIcon = (status: string) => {
    const lowerStatus = status.toLowerCase();
    switch (lowerStatus) {
      case 'approved': return <CheckCircle className="h-3.5 w-3.5 text-success" />;
      case 'rejected': return <XCircle className="h-3.5 w-3.5 text-destructive" />;
      case 'processing': return <Clock className="h-3.5 w-3.5 text-info" />;
      default: return <Clock className="h-3.5 w-3.5 text-warning" />;
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading claims...</p>
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
            <p className="text-destructive mb-2">Error loading claims</p>
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
          <h1>Claims Management</h1>
          <p>Manage and process funeral assurance claims</p>
        </div>
        <Button onClick={() => navigate('/claims/new')} className="bg-primary text-primary-foreground hover:bg-primary/90">+ File New Claim</Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search claims..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9" />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="submitted">Pending</SelectItem>
            <SelectItem value="under_review">Processing</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="data-table-container overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/30">
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Claim ID</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Policy</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Claimant</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Type</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Amount</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Date</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {paginated.map(c => (
              <tr key={c.id} className="hover:bg-muted/20">
                <td className="px-4 py-3 font-mono text-xs">{c.claim_number}</td>
                <td className="px-4 py-3">{c.policy?.policy_number || 'N/A'}</td>
                <td className="px-4 py-3 font-medium">{c.policy?.customer?.first_name || 'Unknown'} {c.policy?.customer?.last_name || 'Customer'}</td>
                <td className="px-4 py-3">{c.claim_type}</td>
                <td className="px-4 py-3">${parseFloat(c.amount_claimed).toLocaleString()}</td>
                <td className="px-4 py-3">{new Date(c.reported_date).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 ${
                    c.status.toLowerCase() === 'approved' ? 'badge-success' :
                    c.status.toLowerCase() === 'rejected' ? 'badge-danger' :
                    c.status.toLowerCase() === 'under_review' ? 'badge-info' : 'badge-warning'
                  }`}>
                    {statusIcon(c.status)} {c.status.replace('_', ' ')}
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

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <p className="text-sm text-muted-foreground">Showing {Math.min((page - 1) * PAGE_SIZE + 1, filtered.length)}-{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length} claims • Page {page} of {totalPages || 1}</p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
            <ChevronLeft className="h-4 w-4" /> Prev
          </Button>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
            Next <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}
