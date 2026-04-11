import { useState, useEffect, useMemo } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { apiService } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Search, Eye, ChevronLeft, ChevronRight, Loader2, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

/**
 * Policy Holder data interface
 * Represents a customer with their policy and engagement details
 */
interface LatestPolicy {
  id: number;
  policy_number: string;
  policy_type: string;
  status: string;
  premium_amount: string;
  created_at: string;
}

interface CustomerEngagement {
  service_satisfaction: number;
  number_of_complaints: number;
  claims_filed: number;
}

interface Customer {
  id: number;
  customer_number: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  age: number;
  location: {
    city: string;
  };
  latest_policy?: LatestPolicy;
  engagement?: CustomerEngagement;
}

const PAGE_SIZE = 15;

/**
 * Calculate tenure in years from policy creation date
 * Returns whole years only, accounting for months/days
 */
function calculateTenure(createdAt: string): number {
  const created = new Date(createdAt);
  const today = new Date();
  
  let years = today.getFullYear() - created.getFullYear();
  const monthDiff = today.getMonth() - created.getMonth();
  
  // Adjust if birthday hasn't occurred this year
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < created.getDate())) {
    years--;
  }
  
  return Math.max(0, years);
}

/**
 * Format satisfaction score as star rating with numeric value
 * Converts 0-10 scale to 0-5 stars
 */
function formatSatisfaction(score: number): string {
  if (!score || isNaN(score)) return '0/10';
  const numScore = parseFloat(score.toString());
  const stars = Math.round(numScore / 2);
  return `${'⭐'.repeat(Math.min(stars, 5))} ${numScore}/10`;
}

/**
 * Format currency amount with proper locale and symbol
 */
function formatCurrency(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '$0.00';
  return `$${num.toFixed(2)}`;
}

export default function PolicyHoldersPage() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [locationFilter, setLocationFilter] = useState('all');
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getCustomers({
          page_size: 1000, // Get all for now, implement pagination later
        });
        setCustomers(response.results || response);
      } catch (err: any) {
        console.error('Failed to fetch customers:', err);
        setError(err.message || 'Failed to load customers');
        toast.error('Failed to load customers');
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, []);

  const locations = useMemo(() => {
    const uniqueLocations = [...new Set(customers.map(c => c.location?.city).filter(Boolean))];
    return uniqueLocations.sort();
  }, [customers]);

  const filtered = useMemo(() => {
    return customers.filter(c => {
      const fullName = `${c.first_name} ${c.last_name}`.toLowerCase();
      const matchSearch = fullName.includes(search.toLowerCase()) ||
        c.customer_number.toLowerCase().includes(search.toLowerCase()) ||
        c.id.toString().includes(search);

      const matchLocation = locationFilter === 'all' || c.location?.city === locationFilter;

      return matchSearch && matchLocation;
    });
  }, [customers, search, locationFilter]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading policy holders...</p>
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
            <p className="text-destructive mb-2">Error loading policy holders</p>
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
          <h1>Policy Holders</h1>
          <p>{filtered.length} policy holders found</p>
        </div>
        <Button onClick={() => navigate('/register-policy')} className="bg-primary text-primary-foreground hover:bg-primary/90">
          + Register New Policy
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search by name or ID..." 
            value={search} 
            onChange={e => { setSearch(e.target.value); setPage(1); }} 
            className="pl-9" 
          />
        </div>
        <Select value={locationFilter} onValueChange={v => { setLocationFilter(v); setPage(1); }}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Location" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Locations</SelectItem>
            {locations.map(l => <SelectItem key={l} value={l}>{l}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="data-table-container overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/30">
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Customer ID</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Age</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Location</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Policy Number</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Policy Type</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Premium</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Tenure</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Satisfaction</th>
              <th className="text-center px-4 py-3 font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {paginated.map(c => {
              const policy = c.latest_policy;
              const satisfaction = c.engagement?.service_satisfaction ?? 0;
              const tenure = policy ? calculateTenure(policy.created_at) : 0;

              return (
                <tr key={c.id} className="hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{c.customer_number}</td>
                  <td className="px-4 py-3 font-medium text-foreground">{c.first_name} {c.last_name}</td>
                  <td className="px-4 py-3 text-foreground">{c.age} yrs</td>
                  <td className="px-4 py-3 text-foreground">{c.location?.city || '—'}</td>
                  <td className="px-4 py-3 font-mono text-xs text-foreground">{policy?.policy_number || '—'}</td>
                  <td className="px-4 py-3 text-foreground">{policy?.policy_type || '—'}</td>
                  <td className="px-4 py-3 font-semibold text-foreground">{formatCurrency(policy?.premium_amount || '0')}</td>
                  <td className="px-4 py-3 text-foreground">{tenure} yrs</td>
                  <td className="px-4 py-3 text-sm">{formatSatisfaction(satisfaction)}</td>
                  <td className="px-4 py-3 text-center">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 hover:bg-primary/10"
                      title="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <p className="text-sm text-muted-foreground">Page {page} of {totalPages}</p>
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
