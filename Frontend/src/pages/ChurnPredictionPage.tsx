import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { DashboardLayout } from '@/components/DashboardLayout';
import { apiService } from '@/lib/api';
import { churnPredictionSchema, type ChurnPredictionFormData } from '@/lib/validation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { CheckCircle2, Loader2, AlertTriangle, Brain, Zap, TrendingUp } from 'lucide-react';

interface CustomerSummary {
  id: string;
  customer_number: string;
  full_name: string;
  age: number;
  gender: { label: string };
  location: { city: string; province: string; district: string };
  income_level: { label: string };
}

interface PredictionResult {
  customer_name: string;
  churn_percentage: number;
  risk_level: { code: string; label: string; color_hex: string };
  is_churned: boolean;
  confidence_score: number;
  key_factors: string[];
  recommendations: string[];
}

/**
 * ChurnPredictionPage - ML-Powered Churn Risk Assessment
 * 
 * Professional implementation for customer churn prediction using trained ML model.
 * Users can either:
 * 1. Select an existing customer from database (auto-fill form)
 * 2. Manually enter customer features (custom analysis)
 * 
 * Both paths leverage the same GradientBoosting ML model with 19-feature vectors.
 */
export default function ChurnPredictionPage() {
  const [customers, setCustomers] = useState<CustomerSummary[]>([]);
  const [loadingCustomers, setLoadingCustomers] = useState(false);
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const [calculatorError, setCalculatorError] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [predictionMode, setPredictionMode] = useState<'database' | 'manual'>('database');

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors }
  } = useForm<ChurnPredictionFormData>({
    resolver: zodResolver(churnPredictionSchema),
    defaultValues: {
      customerId: undefined,
      age: 30,
      gender: 'Male',
      location: '',
      incomeLevel: 'Medium Income',
      policyCount: 1,
      averagePremium: 50,
      paymentMethod: 'Mobile Money',
      dependents: 0,
      latePayments: 0,
      missedPayments: 0,
      numberOfComplaints: 0,
      claimsFiled: 0,
      customerTenure: 12,
      serviceSatisfaction: 7,
    }
  });

  const selectedCustomerId = watch('customerId');

  // Load customers on component mount
  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoadingCustomers(true);
        const response = await apiService.getCustomers({ page_size: 1000 });
        const list = Array.isArray(response) ? response : response.results || [];
        setCustomers(list);
      } catch (err: any) {
        console.error('Customer list load failed:', err);
        toast.error('Unable to load customer database');
      } finally {
        setLoadingCustomers(false);
      }
    };

    fetchCustomers();
  }, []);

  const customerOptions = useMemo(() => {
    return customers.map(c => ({
      id: c.id,
      label: `${c.customer_number} - ${c.full_name}`
    }));
  }, [customers]);

  // Load selected customer profile and auto-fill form
  const loadCustomerProfile = async (custId: string) => {
    if (!custId) return;

    try {
      setSelectionError(null);
      const { customer_details } = await apiService.getChurnCalculationCustomerDetails(custId);
      const customerInfo = customer_details?.customer_info;
      const policySummary = customer_details?.policy_summary;
      const engagementMetrics = customer_details?.engagement_metrics;

      if (!customerInfo) {
        setSelectionError('Selected customer has no profile data');
        return;
      }

      setValue('age', customerInfo.age || 0);
      setValue('gender', customerInfo.gender?.label || 'Male');
      setValue('location', customerInfo.location?.city || '');
      setValue('incomeLevel', customerInfo.income_level?.label || 'Medium Income');
      setValue('policyCount', policySummary?.total_policies || 0);
      setValue('averagePremium', policySummary?.average_premium || 0);

      const firstPolicy = customer_details?.policies?.[0];
      setValue('paymentMethod', firstPolicy?.payment_method || 'Mobile Money');
      setValue('dependents', firstPolicy?.dependents ?? 0);

      setValue('latePayments', 0);
      setValue('missedPayments', 0);
      setValue('numberOfComplaints', engagementMetrics?.total_interactions ?? 0);
      setValue('claimsFiled', engagementMetrics?.total_interactions ?? 0);
      setValue('customerTenure', policySummary?.average_tenure_months || 0);
      setValue('serviceSatisfaction', customer_details?.engagement_metrics?.last_interaction ? 7 : 5);

      setPredictionMode('database');
      toast.success('Customer profile loaded - ready to predict');
    } catch (err: any) {
      console.error('Customer profile load error:', err);
      setSelectionError(err?.message || 'Failed to load customer details');
      toast.error('Could not load customer profile');
    }
  };

  useEffect(() => {
    if (selectedCustomerId) {
      void loadCustomerProfile(selectedCustomerId);
    }
  }, [selectedCustomerId]);

  // Handle form submission - uses ML model for prediction
  const onSubmit = async (values: ChurnPredictionFormData) => {
    try {
      setCalculatorError(null);
      setPredictionResult(null);
      setIsCalculating(true);

      let payload: any;
      const source = values.customerId ? 'database_customer' : 'manual_entry';

      if (values.customerId) {
        // Customer database mode: use ML model with database features
        payload = { customer_id: values.customerId, calculation_context: { source } };
      } else {
        // Manual entry mode: use ML model with user-provided features
        payload = {
          age: values.age,
          gender: values.gender,
          location: values.location,
          income_level: values.incomeLevel,
          policy_count: values.policyCount,
          average_premium: values.averagePremium,
          payment_method: values.paymentMethod,
          dependents: values.dependents,
          late_payments: values.latePayments,
          missed_payments: values.missedPayments,
          number_of_complaints: values.numberOfComplaints,
          claims_filed: values.claimsFiled,
          customer_tenure: values.customerTenure,
          service_satisfaction: values.serviceSatisfaction,
        };
      }

      const response = await apiService.calculateChurn(payload);
      if (response.success) {
        setPredictionResult(response.churn_prediction);
        toast.success(`ML prediction: ${response.churn_prediction.churn_percentage}% churn risk`);
      } else {
        setCalculatorError(response.message || 'Prediction failed');
        toast.error('ML model prediction error');
      }
    } catch (err: any) {
      console.error('Churn calculation error:', err);
      setCalculatorError(err?.message ?? 'Unexpected error during prediction');
      toast.error('Churn prediction failed');
    } finally {
      setIsCalculating(false);
    }
  };

  const resetForm = () => {
    reset({
      customerId: undefined,
      age: 30,
      gender: 'Male',
      location: '',
      incomeLevel: 'Medium Income',
      policyCount: 1,
      averagePremium: 50,
      paymentMethod: 'Mobile Money',
      dependents: 0,
      latePayments: 0,
      missedPayments: 0,
      numberOfComplaints: 0,
      claimsFiled: 0,
      customerTenure: 12,
      serviceSatisfaction: 7,
    });
    setPredictionResult(null);
    setCalculatorError(null);
    setSelectionError(null);
    setPredictionMode('database');
  };

  // Get risk badge color based on churn percentage
  const getRiskColor = (riskCode: string, churnPct: number) => {
    if (churnPct >= 70) return 'bg-red-100 text-red-800 border-red-300';
    if (churnPct >= 50) return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-green-100 text-green-800 border-green-300';
  };

  const getRiskIcon = (churnPct: number) => {
    if (churnPct >= 70) return '🔴';
    if (churnPct >= 50) return '🟡';
    return '✅';
  };

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="page-header mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Brain className="h-6 w-6 text-blue-600" />
              <h1 className="text-3xl font-bold">ML Churn Prediction</h1>
            </div>
            <p className="text-muted-foreground">
              GradientBoosting ML model analyzing 19 customer features for accurate churn risk prediction
            </p>
          </div>
        </div>
      </div>

      {/* Mode Selection */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          onClick={() => {
            setPredictionMode('database');
            reset({ ...reset(), customerId: undefined });
          }}
          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
            predictionMode === 'database'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold">Database Customer</h3>
          </div>
          <p className="text-sm text-gray-600">
            Select an existing customer from database. ML model extracts features from customer records.
          </p>
        </div>

        <div
          onClick={() => {
            setPredictionMode('manual');
            reset({ ...reset(), customerId: undefined });
          }}
          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
            predictionMode === 'manual'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="flex items-center gap-3 mb-2">
            <Zap className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold">Manual Entry</h3>
          </div>
          <p className="text-sm text-gray-600">
            Manually enter customer features. ML model processes your input for prediction.
          </p>
        </div>
      </div>

      {/* Prediction Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-card rounded-lg border p-6 shadow-sm">
        {/* Customer Selection (Database Mode) */}
        {predictionMode === 'database' && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Select Customer from Database</h3>
              <p className="text-sm text-blue-800">
                This mode automatically extracts 19 features from your customer's database records using the ML model.
              </p>
            </div>

            <div>
              <Label htmlFor="customerId" className="text-base font-semibold">
                Customer Selection
              </Label>
              <select
                id="customerId"
                {...register('customerId')}
                className="mt-2 block w-full rounded-md border border-input bg-background px-3 py-2 text-base"
                disabled={loadingCustomers}
              >
                <option value="">
                  {loadingCustomers ? 'Loading customers...' : '-- Select a customer --'}
                </option>
                {customerOptions.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
              {selectionError && (
                <p className="text-sm text-destructive mt-2 flex items-center gap-1">
                  <AlertTriangle className="h-4 w-4" /> {selectionError}
                </p>
              )}
            </div>

            {selectedCustomerId && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800">
                  ✓ Customer selected. Form will auto-populate with database features.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Feature Grid */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Customer Features (19-Feature Vector)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Demographics */}
            <div>
              <Label htmlFor="age" className="text-sm">
                Age
              </Label>
              <Input id="age" type="number" {...register('age', { valueAsNumber: true })} className="mt-1" />
              {errors.age && <p className="text-destructive text-xs mt-1">{errors.age.message}</p>}
            </div>

            <div>
              <Label htmlFor="gender" className="text-sm">
                Gender
              </Label>
              <select id="gender" {...register('gender')} className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Male</option>
                <option>Female</option>
              </select>
              {errors.gender && <p className="text-destructive text-xs mt-1">{errors.gender.message}</p>}
            </div>

            <div>
              <Label htmlFor="location" className="text-sm">
                Location
              </Label>
              <Input id="location" {...register('location')} className="mt-1" placeholder="City" />
              {errors.location && <p className="text-destructive text-xs mt-1">{errors.location.message}</p>}
            </div>

            <div>
              <Label htmlFor="incomeLevel" className="text-sm">
                Income Level
              </Label>
              <select id="incomeLevel" {...register('incomeLevel')} className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Low Income</option>
                <option>Medium Income</option>
                <option>High Income</option>
              </select>
              {errors.incomeLevel && <p className="text-destructive text-xs mt-1">{errors.incomeLevel.message}</p>}
            </div>

            {/* Policy */}
            <div>
              <Label htmlFor="policyCount" className="text-sm">
                Policy Count
              </Label>
              <Input id="policyCount" type="number" {...register('policyCount', { valueAsNumber: true })} className="mt-1" />
              {errors.policyCount && <p className="text-destructive text-xs mt-1">{errors.policyCount.message}</p>}
            </div>

            <div>
              <Label htmlFor="averagePremium" className="text-sm">
                Average Premium ($)
              </Label>
              <Input id="averagePremium" type="number" step="0.01" {...register('averagePremium', { valueAsNumber: true })} className="mt-1" />
              {errors.averagePremium && <p className="text-destructive text-xs mt-1">{errors.averagePremium.message}</p>}
            </div>

            <div>
              <Label htmlFor="paymentMethod" className="text-sm">
                Payment Method
              </Label>
              <select id="paymentMethod" {...register('paymentMethod')} className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option>Mobile Money</option>
                <option>Ecocash</option>
                <option>Cash</option>
                <option>Bank Debit</option>
              </select>
              {errors.paymentMethod && <p className="text-destructive text-xs mt-1">{errors.paymentMethod.message}</p>}
            </div>

            <div>
              <Label htmlFor="dependents" className="text-sm">
                Dependents
              </Label>
              <Input id="dependents" type="number" {...register('dependents', { valueAsNumber: true })} className="mt-1" />
              {errors.dependents && <p className="text-destructive text-xs mt-1">{errors.dependents.message}</p>}
            </div>

            {/* Payment Behavior */}
            <div>
              <Label htmlFor="latePayments" className="text-sm">
                Late Payments
              </Label>
              <Input id="latePayments" type="number" {...register('latePayments', { valueAsNumber: true })} className="mt-1" />
              {errors.latePayments && <p className="text-destructive text-xs mt-1">{errors.latePayments.message}</p>}
            </div>

            <div>
              <Label htmlFor="missedPayments" className="text-sm">
                Missed Payments
              </Label>
              <Input id="missedPayments" type="number" {...register('missedPayments', { valueAsNumber: true })} className="mt-1" />
              {errors.missedPayments && <p className="text-destructive text-xs mt-1">{errors.missedPayments.message}</p>}
            </div>

            {/* Engagement */}
            <div>
              <Label htmlFor="numberOfComplaints" className="text-sm">
                Complaints
              </Label>
              <Input id="numberOfComplaints" type="number" {...register('numberOfComplaints', { valueAsNumber: true })} className="mt-1" />
              {errors.numberOfComplaints && <p className="text-destructive text-xs mt-1">{errors.numberOfComplaints.message}</p>}
            </div>

            <div>
              <Label htmlFor="claimsFiled" className="text-sm">
                Claims Filed
              </Label>
              <Input id="claimsFiled" type="number" {...register('claimsFiled', { valueAsNumber: true })} className="mt-1" />
              {errors.claimsFiled && <p className="text-destructive text-xs mt-1">{errors.claimsFiled.message}</p>}
            </div>

            {/* Tenure & Satisfaction */}
            <div>
              <Label htmlFor="customerTenure" className="text-sm">
                Tenure (months)
              </Label>
              <Input id="customerTenure" type="number" {...register('customerTenure', { valueAsNumber: true })} className="mt-1" />
              {errors.customerTenure && <p className="text-destructive text-xs mt-1">{errors.customerTenure.message}</p>}
            </div>

            <div>
              <Label htmlFor="serviceSatisfaction" className="text-sm">
                Satisfaction (0-10)
              </Label>
              <Input id="serviceSatisfaction" type="number" step="0.1" {...register('serviceSatisfaction', { valueAsNumber: true })} className="mt-1" />
              {errors.serviceSatisfaction && <p className="text-destructive text-xs mt-1">{errors.serviceSatisfaction.message}</p>}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 pt-4 border-t">
          <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={isCalculating}>
            {isCalculating ? (
              <span className="inline-flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" /> Running ML Model...
              </span>
            ) : (
              <span className="inline-flex items-center gap-2">
                <Brain className="h-4 w-4" /> Calculate Churn Risk
              </span>
            )}
          </Button>

          <Button type="button" variant="outline" onClick={resetForm} disabled={isCalculating}>
            Reset
          </Button>

          {calculatorError && (
            <div className="flex items-center gap-2 text-destructive text-sm">
              <AlertTriangle className="h-4 w-4" /> {calculatorError}
            </div>
          )}
        </div>
      </form>

      {/* ML Prediction Result */}
      {predictionResult && (
        <section className="mt-8 space-y-6">
          {/* Risk Summary Card */}
          <div
            className={`rounded-lg border-2 p-6 ${getRiskColor(
              predictionResult.risk_level.code,
              predictionResult.churn_percentage
            )}`}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">
                {getRiskIcon(predictionResult.churn_percentage)} Churn Risk Assessment
              </h2>
              <div className="text-right">
                <div className="text-4xl font-bold">{predictionResult.churn_percentage}%</div>
                <div className="text-sm font-semibold">{predictionResult.risk_level.label} Risk</div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-current border-opacity-20">
              <p className="text-sm font-semibold">
                Status: {predictionResult.is_churned ? 'High likelihood of churn' : 'Low likelihood of churn'}
              </p>
              <p className="text-sm mt-1">Confidence: {(predictionResult.confidence_score * 100).toFixed(0)}%</p>
            </div>
          </div>

          {/* Customer & Prediction Info */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-card rounded-lg border p-4">
              <h3 className="font-semibold text-sm text-gray-600 mb-2">CUSTOMER</h3>
              <p className="text-lg font-bold">{predictionResult.customer_name}</p>
            </div>
            <div className="bg-card rounded-lg border p-4">
              <h3 className="font-semibold text-sm text-gray-600 mb-2">PREDICTION MODEL</h3>
              <p className="text-lg font-bold">GradientBoosting</p>
              <p className="text-xs text-gray-600 mt-1">19-feature vector</p>
            </div>
            <div className="bg-card rounded-lg border p-4">
              <h3 className="font-semibold text-sm text-gray-600 mb-2">DATA POINTS</h3>
              <p className="text-lg font-bold">19</p>
              <p className="text-xs text-gray-600 mt-1">features analyzed</p>
            </div>
          </div>

          {/* Key Factors */}
          {predictionResult.key_factors && predictionResult.key_factors.length > 0 && (
            <div className="bg-card rounded-lg border p-6">
              <h3 className="font-bold text-lg mb-4">Key Churn Factors</h3>
              <ul className="space-y-2">
                {predictionResult.key_factors.map((factor, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="inline-block w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {predictionResult.recommendations && predictionResult.recommendations.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-bold text-lg text-blue-900 mb-4">Recommended Actions</h3>
              <ul className="space-y-2">
                {predictionResult.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-blue-800">
                    <span className="inline-block w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </DashboardLayout>
  );
}
