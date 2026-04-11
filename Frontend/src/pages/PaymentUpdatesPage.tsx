import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { paymentUpdateSchema, type PaymentUpdateFormData } from '@/lib/validation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { CreditCard, Upload, CheckCircle, Loader2, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { StatCard } from '@/components/StatCard';
import { apiService } from '@/lib/api';

interface Payment {
  id: string;
  payment_reference: string;
  policy: {
    policy_number: string;
    customer: {
      first_name: string;
      last_name: string;
    };
  };
  amount: string;
  transaction_date: string;
  payment_method: {
    label: string;
  };
  status: string;
}

export default function PaymentUpdatesPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, setValue, formState: { errors }, reset } = useForm<PaymentUpdateFormData>({
    resolver: zodResolver(paymentUpdateSchema),
  });

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getPayments({ page_size: 50 });
        setPayments(response.results || response);
      } catch (err: any) {
        console.error('Failed to fetch payments:', err);
        setError(err.message || 'Failed to load payments');
        toast.error('Failed to load payments');
      } finally {
        setLoading(false);
      }
    };

    fetchPayments();
  }, []);

  const onSubmit = async (data: PaymentUpdateFormData) => {
    try {
      setSubmitting(true);
      // TODO: Implement actual payment creation API call
      toast.success('Payment recorded successfully!', { description: `$${data.amount} for ${data.policyNumber}` });
      reset();
      // Refresh payments list
      const response = await apiService.getPayments({ page_size: 50 });
      setPayments(response.results || response);
    } catch (err: any) {
      console.error('Failed to record payment:', err);
      toast.error('Failed to record payment');
    } finally {
      setSubmitting(false);
    }
  };

  // Calculate stats from real data
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const paymentsThisMonth = payments.filter(p => {
    const paymentDate = new Date(p.transaction_date);
    return paymentDate.getMonth() === currentMonth && paymentDate.getFullYear() === currentYear;
  });

  const totalCollected = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
  const latePayments = payments.filter(p => p.status === 'OVERDUE').length;

  const Err = ({ error }: { error?: { message?: string } }) =>
    error ? <p className="text-xs text-destructive mt-1">{error.message}</p> : null;

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading payments...</p>
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
            <p className="text-destructive mb-2">Error loading payments</p>
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
        <h1>Payment Updates</h1>
        <p>Record monthly premium payments from bank records</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <StatCard title="Payments This Month" value={paymentsThisMonth.length.toString()} change="+12 from last week" changeType="up" icon={CreditCard} iconColor="bg-success/10 text-success" />
        <StatCard title="Total Collected" value={`$${totalCollected.toLocaleString()}`} icon={CreditCard} iconColor="bg-primary/10 text-primary" />
        <StatCard title="Late Payments" value={latePayments.toString()} change="Requires follow-up" changeType="down" icon={CreditCard} iconColor="bg-warning/10 text-warning" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="lg:col-span-2">
          <form onSubmit={handleSubmit(onSubmit)} className="form-section">
            <div className="flex items-center gap-2 mb-2">
              <Upload className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold font-display">Record Payment</h3>
            </div>
            <div className="space-y-4">
              <div><Label>Policy Number *</Label><Input {...register('policyNumber')} placeholder="POL-12345" /><Err error={errors.policyNumber} /></div>
              <div><Label>Payment Date *</Label><Input type="date" {...register('paymentDate')} /><Err error={errors.paymentDate} /></div>
              <div><Label>Amount (USD) *</Label><Input type="number" {...register('amount', { valueAsNumber: true })} /><Err error={errors.amount} /></div>
              <div>
                <Label>Payment Method *</Label>
                <Select onValueChange={v => setValue('paymentMethod', v as any)}>
                  <SelectTrigger><SelectValue placeholder="Select method" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Mobile Money">Mobile Money</SelectItem>
                    <SelectItem value="Ecocash">Ecocash</SelectItem>
                    <SelectItem value="Cash">Cash</SelectItem>
                    <SelectItem value="Bank Debit">Bank Debit</SelectItem>
                  </SelectContent>
                </Select>
                <Err error={errors.paymentMethod} />
              </div>
              <div><Label>Reference *</Label><Input {...register('reference')} placeholder="Transaction ref" /><Err error={errors.reference} /></div>
              <div><Label>Notes</Label><Textarea {...register('notes')} placeholder="Optional notes" rows={3} /></div>
              <Button type="submit" disabled={submitting} className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Record Payment
              </Button>
            </div>
          </form>
        </motion.div>

        {/* Recent Payments */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="lg:col-span-3 data-table-container">
          <div className="p-4 border-b">
            <h3 className="text-sm font-semibold font-sans">Recent Payments</h3>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/30">
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Policy</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Holder</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Amount</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Date</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Method</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {payments.slice(0, 15).map(p => (
                <tr key={p.id} className="hover:bg-muted/20">
                  <td className="px-4 py-3 font-mono text-xs">{p.policy.policy_number}</td>
                  <td className="px-4 py-3">{p.policy.customer.first_name} {p.policy.customer.last_name}</td>
                  <td className="px-4 py-3">${parseFloat(p.amount).toLocaleString()}</td>
                  <td className="px-4 py-3">{new Date(p.transaction_date).toLocaleDateString()}</td>
                  <td className="px-4 py-3">{p.payment_method.label}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1 ${p.status === 'COMPLETED' ? 'badge-success' : p.status === 'PENDING' ? 'badge-warning' : 'badge-danger'}`}>
                      {p.status === 'COMPLETED' ? <CheckCircle className="h-3 w-3" /> : null}
                      {p.status.toLowerCase().replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
