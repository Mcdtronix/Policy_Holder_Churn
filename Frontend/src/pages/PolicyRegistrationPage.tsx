import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createPolicyRegistrationSchema, type PolicyFormData } from '@/lib/validation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { UserPlus, Trash2, Plus, Loader2, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { apiService } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

interface DependentForm {
  name: string;
  relationship: string;
  dateOfBirth: string;
  idNumber: string;
}

interface PolicyType {
  id: number;
  name: string;
  code: string;
}

interface PolicyForOption {
  value: 'Self' | 'Other';
  label: string;
}

export default function PolicyRegistrationPage() {
  const navigate = useNavigate();
  const [dependents, setDependents] = useState<DependentForm[]>([]);
  const [policyTypes, setPolicyTypes] = useState<PolicyType[]>([]);
  // Initialize with fallback data to prevent rendering errors during loading
  const [genders, setGenders] = useState<{ id: number; label: string }[]>([
    { id: 1, label: 'Male' },
    { id: 2, label: 'Female' }
  ]);
  const [incomeLevels, setIncomeLevels] = useState<{ id: number; label: string }[]>([
    { id: 1, label: 'Low' },
    { id: 2, label: 'Medium' },
    { id: 3, label: 'High' }
  ]);
  const [locations, setLocations] = useState<{ id: number; city: string }[]>([
    { id: 1, city: 'Harare' },
    { id: 2, city: 'Bulawayo' },
    { id: 3, city: 'Mutare' }
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Create schema dynamically based on fetched policy types
  const [validationSchema, setValidationSchema] = useState(() => 
    createPolicyRegistrationSchema(['Individual', 'Family', 'Family Policy', 'Individual Policy'])
  );

  const { register, handleSubmit, setValue, formState: { errors }, reset, watch } = useForm<PolicyFormData>({
    resolver: zodResolver(validationSchema),
    defaultValues: { policyFor: 'Self', premiumAmount: 30 },
  });

  const policyType = watch('policyType');
  const policyFor = watch('policyFor');

  useEffect(() => {
    const fetchReferenceData = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log('[PolicyRegistration] Fetching reference data from API...');
        
        const [policyTypesRes, gendersRes, incomeRes, locationsRes] = await Promise.all([
          apiService.getPolicyTypes(),
          apiService.getGenders(),
          apiService.getIncomeLevels(),
          apiService.getLocations()
        ]);

        console.log('[PolicyRegistration] Raw API responses:', {
          policyTypesRes,
          gendersRes,
          incomeRes,
          locationsRes
        });

        // Robust data extraction - handle multiple response formats for all endpoints
        const extractArrayData = (response: any): any[] => {
          if (Array.isArray(response)) return response;
          if (response?.data && Array.isArray(response.data)) return response.data;
          if (response?.results && Array.isArray(response.results)) return response.results;
          return [];
        };
        
        const fetchedPolicyTypes = extractArrayData(policyTypesRes);
        let fetchedGenders = extractArrayData(gendersRes);
        let fetchedIncome = extractArrayData(incomeRes);
        let fetchedLocations = extractArrayData(locationsRes);
        
        // Normalize API responses to match expected interfaces
        // Genders: expect {id, label} but API might return {id, name}
        fetchedGenders = fetchedGenders.map((g: any) => ({
          id: g.id,
          label: g.label || g.name || g.value || ''
        })).filter((g: any) => g.label); // Filter out empty labels
        
        // Income Levels: expect {id, label} but API might return {id, name}
        // Extract just the first word from the label (e.g., "Low Income" -> "Low")
        fetchedIncome = fetchedIncome.map((inc: any) => {
          const label = inc.label || inc.name || inc.value || '';
          return {
            id: inc.id,
            label: label.split(' ')[0] // Extract first word to match validation schema
          };
        }).filter((inc: any) => inc.label); // Filter out empty labels
        
        // Locations: expect {id, city} but API might return {id, name}
        fetchedLocations = fetchedLocations.map((loc: any) => ({
          id: loc.id,
          city: loc.city || loc.name || loc.value || ''
        })).filter((loc: any) => loc.city); // Filter out empty cities

        // Only warn if policy types are empty, but use fallback instead of throwing
        if (!Array.isArray(fetchedPolicyTypes) || fetchedPolicyTypes.length === 0) {
          console.warn('[PolicyRegistration] No policy types from API, using fallback data');
          throw new Error('API returned no policy types, will use fallback');
        }

        setPolicyTypes(fetchedPolicyTypes);
        setGenders(fetchedGenders);
        setIncomeLevels(fetchedIncome);
        setLocations(fetchedLocations);

        // Update validation schema with actual policy type names
        const policyTypeNames = fetchedPolicyTypes.map(pt => pt.name);
        setValidationSchema(createPolicyRegistrationSchema(policyTypeNames));

        console.log('✅ [PolicyRegistration] Reference data loaded successfully:', {
          policyTypes: policyTypeNames,
          genders: fetchedGenders.length,
          incomeLevels: fetchedIncome.length,
          locations: fetchedLocations.length,
        });
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to load policy types';
        console.error('⚠️ [PolicyRegistration] Failed to fetch reference data:', errorMsg);
        console.warn('Using fallback data - API may be unavailable');
        
        // Use sensible fallbacks WITHOUT setting error state (since fallback is valid)
        const fallbackPolicyTypes = [
          { id: 1, name: 'Business Policy', code: 'BUSINESS' },
          { id: 2, name: 'Family Policy', code: 'FAMILY' },
          { id: 3, name: 'Individual Policy', code: 'INDIVIDUAL' },
          { id: 4, name: 'Special Policy', code: 'SPECIAL' }
        ];
        
        setPolicyTypes(fallbackPolicyTypes);
        setGenders([{ id: 1, label: 'Male' }, { id: 2, label: 'Female' }]);
        setIncomeLevels([{ id: 1, label: 'Low' }, { id: 2, label: 'Medium' }, { id: 3, label: 'High' }]);
        setLocations([{ id: 1, city: 'Harare' }, { id: 2, city: 'Bulawayo' }, { id: 3, city: 'Mutare' }]);
        
        setValidationSchema(createPolicyRegistrationSchema(fallbackPolicyTypes.map(pt => pt.name)));
        
        // Only show toast if it's a real error (network issue), not just missing data
        toast.error('Using cached data', { 
          description: 'Some form data may be outdated. Try refreshing the page.' 
        });
      } finally {
        setLoading(false);
      }
    };

    fetchReferenceData();
  }, []);

  const addDependent = () => {
    if (dependents.length >= 6) { toast.error('Maximum 6 dependents allowed'); return; }
    setDependents([...dependents, { name: '', relationship: '', dateOfBirth: '', idNumber: '' }]);
  };

  const removeDependent = (i: number) => setDependents(dependents.filter((_, idx) => idx !== i));

  const updateDependent = (i: number, field: keyof DependentForm, value: string) => {
    const updated = [...dependents];
    updated[i] = { ...updated[i], [field]: value };
    setDependents(updated);
  };

  const onSubmit = async (data: PolicyFormData) => {
    try {
      setError(null);

      // ─────────────────────────────────────────
      // 1. VALIDATE DEPENDENTS (if any provided)
      // ─────────────────────────────────────────
      // Validate only the dependents that have been started (not partially filled)
      for (const dep of dependents) {
        const hasAnyData = dep.name?.trim() || dep.relationship?.trim() || dep.dateOfBirth?.trim() || dep.idNumber?.trim();
        if (hasAnyData) {
          // If any field is filled, all fields should be completed
          if (!dep.name?.trim() || !dep.relationship?.trim() || !dep.dateOfBirth?.trim()) {
            toast.error('All dependent information must be completed. Either fill all fields or remove the dependent.');
            return;
          }
        }
      }

      setSubmitting(true);

      // ─────────────────────────────────────────
      // 2. FIND SELECTED POLICY TYPE
      // ─────────────────────────────────────────
      const selectedPolicyType = policyTypes.find(pt => 
        pt.name.toLowerCase().includes(data.policyType.toLowerCase()) ||
        pt.code.toLowerCase() === data.policyType.toLowerCase() ||
        pt.name === data.policyType
      );

      if (!selectedPolicyType) {
        throw new Error(
          `Selected policy type "${data.policyType}" not found. Available types: ${policyTypes.map(pt => pt.name).join(', ')}`
        );
      }

      // ─────────────────────────────────────────
      // 3. CREATE OR GET CUSTOMER
      // ─────────────────────────────────────────
      const customerPayload = {
        first_name: data.firstName.trim(),
        last_name: data.lastName.trim(),
        national_id: data.idNumber.trim(),
        date_of_birth: data.dateOfBirth,
        gender: data.gender,
        email: data.email.trim().toLowerCase(),
        phone_primary: data.phone.trim(),
        address_line1: data.address.trim(),
        location: data.city.trim(),
        income_level: data.incomeLevel,
      };

      console.log('[PolicyRegistration] Creating customer:', customerPayload);
      const customerResponse = await apiService.createCustomer(customerPayload);
      const customerId = customerResponse.id;
      console.log('[PolicyRegistration] Customer created/retrieved:', { id: customerId });

      // ─────────────────────────────────────────
      // 4. PREPARE BENEFICIARY INFORMATION
      // ─────────────────────────────────────────
      const policyForSelf = data.policyFor === 'Self';
      
      let beneficiaryName = data.beneficiaryName?.trim() || '';
      let beneficiaryRelation = data.beneficiaryRelation?.trim() || '';
      let beneficiaryPhone = data.beneficiaryPhone?.trim() || '';

      if (policyForSelf) {
        // Auto-populate with customer details if not provided
        beneficiaryName = beneficiaryName || `${data.firstName.trim()} ${data.lastName.trim()}`;
        beneficiaryRelation = beneficiaryRelation || 'Self';
        beneficiaryPhone = beneficiaryPhone || data.phone;
      }

      // Strict validation for beneficiaries
      if (!beneficiaryName || !beneficiaryRelation || !beneficiaryPhone) {
        throw new Error(
          'Complete beneficiary information is required. ' +
          'Please provide beneficiary name, relationship, and phone number.'
        );
      }

      // ─────────────────────────────────────────
      // 5. VALIDATE BENEFICIARY PHONE
      // ─────────────────────────────────────────
      const phoneRegex = /^(\+263|0)[7][1-9][0-9]{7}$/;
      if (!phoneRegex.test(beneficiaryPhone)) {
        throw new Error('Beneficiary phone must be a valid Zimbabwe number (e.g., +263771234567)');
      }

      // ─────────────────────────────────────────
      // 6. CREATE POLICY WITH BENEFICIARIES
      // ─────────────────────────────────────────
      const sumAssured = data.premiumAmount * 100;

      const policyPayload = {
        customer: customerId,
        policy_type: selectedPolicyType.id,
        start_date: new Date().toISOString().split('T')[0],
        sum_assured: sumAssured.toString(),
        premium_amount: data.premiumAmount.toString(),
        premium_frequency: 'MONTHLY',
        dependents: dependents.length,
        status: 'ACTIVE',
        beneficiaries: [
          {
            full_name: beneficiaryName,
            relationship: beneficiaryRelation,
            phone: beneficiaryPhone,
            is_primary: true,
            share_percent: 100,
          },
        ],
      };

      console.log('[PolicyRegistration] Submitting policy:', policyPayload);
      const policyResponse = await apiService.createPolicy(policyPayload);

      toast.success('Policy registered successfully!', {
        description: `Policy ${policyResponse.data?.policy_number || 'created'} for ${data.firstName} ${data.lastName}`,
      });

      console.log('[PolicyRegistration] Policy created:', policyResponse.data);
      reset();
      setDependents([]);
      setTimeout(() => navigate('/policyholders'), 2000);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to register policy. Please try again.';
      console.error('[PolicyRegistration] Error:', err);
      setError(errorMessage);
      toast.error('Registration failed', { description: errorMessage });
    } finally {
      setSubmitting(false);
    }
  };

  const FieldError = ({ error }: { error?: { message?: string } }) => (
    error ? (
      <div className="flex items-start gap-1.5 mt-2">
        <div className="h-1.5 w-1.5 rounded-full bg-destructive flex-shrink-0 mt-1" />
        <p className="text-sm text-destructive font-medium">{error.message}</p>
      </div>
    ) : null
  );

  const FormFieldWrapper = ({ children, error }: { children: React.ReactNode; error?: { message?: string } }) => (
    <div className={error ? 'has-error' : ''}>
      {children}
      <FieldError error={error} />
    </div>
  );

  if (error && submitting === false) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-destructive/10 border border-destructive/30 rounded-lg p-6"
          >
            <div className="flex gap-3">
              <AlertTriangle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-destructive mb-1">Error Registering Policy</h3>
                <p className="text-sm text-destructive/80 mb-4">{error}</p>
                <Button
                  onClick={() => setError(null)}
                  variant="outline"
                  className="text-destructive border-destructive hover:bg-destructive/5"
                >
                  Try Again
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="page-header">
        <h1>Register New Policy</h1>
        <p>Complete the form below to register a new funeral assurance policy</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="max-w-4xl space-y-6">
        {/* Personal Information */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="form-section">
          <div className="flex items-center gap-2 mb-2">
            <UserPlus className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold font-display">Personal Information</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormFieldWrapper error={errors.firstName}>
              <Label>First Name *</Label>
              <Input {...register('firstName')} placeholder="e.g. Tatenda" className={errors.firstName ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.lastName}>
              <Label>Last Name *</Label>
              <Input {...register('lastName')} placeholder="e.g. Moyo" className={errors.lastName ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.idNumber}>
              <Label>National ID *</Label>
              <Input {...register('idNumber')} placeholder="63-123456A78" className={errors.idNumber ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.dateOfBirth}>
              <Label>Date of Birth *</Label>
              <Input type="date" {...register('dateOfBirth')} className={errors.dateOfBirth ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.gender}>
              <Label>Gender *</Label>
              <Select onValueChange={v => setValue('gender', v as 'Male' | 'Female')}>
                <SelectTrigger className={errors.gender ? 'border-destructive' : ''}><SelectValue placeholder="Select gender" /></SelectTrigger>
                <SelectContent>
                  {(genders.length ? genders : [{id:1,label:'Male'}, {id:2,label:'Female'}]).map((g) => (
                    <SelectItem key={g.id} value={g.label}>{g.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.phone}>
              <Label>Phone *</Label>
              <Input {...register('phone')} placeholder="+263771234567" className={errors.phone ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.email}>
              <Label>Email *</Label>
              <Input type="email" {...register('email')} placeholder="email@example.com" className={errors.email ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.incomeLevel}>
              <Label>Income Level *</Label>
              <Select onValueChange={v => setValue('incomeLevel', v as 'Low' | 'Medium' | 'High')}>
                <SelectTrigger className={errors.incomeLevel ? 'border-destructive' : ''}><SelectValue placeholder="Select income level" /></SelectTrigger>
                <SelectContent>
                  {(incomeLevels.length ? incomeLevels : [{id:1,label:'Low'}, {id:2,label:'Medium'}, {id:3,label:'High'}]).map((lvl) => (
                    <SelectItem key={lvl.id} value={lvl.label}>{lvl.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormFieldWrapper>
            <div className="md:col-span-2">
              <FormFieldWrapper error={errors.address}>
                <Label>Physical Address *</Label>
                <Input {...register('address')} placeholder="123 Main Street" className={errors.address ? 'border-destructive focus-visible:ring-destructive' : ''} />
              </FormFieldWrapper>
            </div>
            <FormFieldWrapper error={errors.city}>
              <Label>City/Location *</Label>
              <Input {...register('city')} placeholder="e.g. Harare, Bulawayo, or any other location" className={errors.city ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
          </div>
        </motion.div>

        {/* Policy Details */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-2">Policy Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormFieldWrapper error={errors.policyType}>
              <Label>Policy Type *</Label>
              <Select 
                value={policyType}
                onValueChange={v => setValue('policyType', v)}
                disabled={loading || !policyTypes.length}
              >
                <SelectTrigger className={`${!policyTypes.length ? 'opacity-50' : ''} ${errors.policyType ? 'border-destructive' : ''}`}>
                  <SelectValue placeholder={loading ? 'Loading policy types...' : 'Select policy type'} />
                </SelectTrigger>
                <SelectContent>
                  {policyTypes.length > 0 && policyTypes.map((pt) => (
                    <SelectItem key={pt.id} value={pt.name}>
                      <span className="flex items-center gap-2">
                        {pt.name}
                        <span className="text-xs text-muted-foreground">({pt.code})</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {!policyTypes.length && !loading && (
                <div className="flex items-start gap-1.5 mt-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-destructive flex-shrink-0 mt-1" />
                  <p className="text-sm text-destructive font-medium">Unable to load policy types. Please refresh the page.</p>
                </div>
              )}
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.policyFor}>
              <Label>Policy For *</Label>
              <Select onValueChange={v => setValue('policyFor', v as 'Self' | 'Other')}>
                <SelectTrigger className={errors.policyFor ? 'border-destructive' : ''}><SelectValue placeholder="Select policy beneficiary" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Self">For Self (self-beneficiary)</SelectItem>
                  <SelectItem value="Other">For Other (third party beneficiary)</SelectItem>
                </SelectContent>
              </Select>
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.premiumAmount}>
              <Label>Monthly Premium (USD) *</Label>
              <Input type="number" {...register('premiumAmount', { valueAsNumber: true })} min={10} max={500} className={errors.premiumAmount ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.paymentMethod}>
              <Label>Payment Method *</Label>
              <Select onValueChange={v => setValue('paymentMethod', v as any)}>
                <SelectTrigger className={errors.paymentMethod ? 'border-destructive' : ''}><SelectValue placeholder="Select payment method" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Mobile Money">Mobile Money</SelectItem>
                  <SelectItem value="Ecocash">Ecocash</SelectItem>
                  <SelectItem value="Cash">Cash</SelectItem>
                  <SelectItem value="Bank Debit">Bank Debit</SelectItem>
                </SelectContent>
              </Select>
            </FormFieldWrapper>
          </div>
        </motion.div>

        {/* Beneficiary */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-2">Beneficiary Information</h3>
          <p className="text-sm text-muted-foreground mb-3">
            {policyFor === 'Self'
              ? 'For self policies, you are automatically the primary beneficiary. You may override details below if needed.'
              : 'For third-party policies, please provide the beneficiary details explicitly.'}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormFieldWrapper error={errors.beneficiaryName}>
              <Label>Full Name {policyFor !== 'Self' && '*'}</Label>
              <Input {...register('beneficiaryName')} placeholder="Beneficiary name" className={errors.beneficiaryName ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.beneficiaryRelation}>
              <Label>Relationship {policyFor !== 'Self' && '*'}</Label>
              <Input {...register('beneficiaryRelation')} placeholder="e.g. Spouse" className={errors.beneficiaryRelation ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.beneficiaryPhone}>
              <Label>Phone {policyFor !== 'Self' && '*'}</Label>
              <Input {...register('beneficiaryPhone')} placeholder="+263771234567" className={errors.beneficiaryPhone ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
          </div>
        </motion.div>

        {/* Dependents - Always visible */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="form-section">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-lg font-semibold font-display">Dependents</h3>
              <p className="text-sm text-muted-foreground mt-1">Add dependents covered under this policy (optional - leave empty if not applicable)</p>
            </div>
            {dependents.length < 6 && (
              <Button type="button" variant="outline" size="sm" onClick={addDependent}>
                <Plus className="h-4 w-4 mr-1" />Add Dependent
              </Button>
            )}
          </div>
          
          {dependents.length === 0 ? (
            <div className="p-4 border border-dashed border-muted-foreground/30 rounded-lg bg-muted/20">
              <p className="text-sm text-muted-foreground text-center">No dependents added. You can add up to 6 dependents.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {dependents.map((dep, i) => (
                <div key={i} className="grid grid-cols-1 md:grid-cols-5 gap-3 p-4 bg-muted/40 border border-muted-foreground/20 rounded-lg items-end hover:bg-muted/50 transition-colors">
                  <div>
                    <Label className="text-xs">Name</Label>
                    <Input value={dep.name} onChange={e => updateDependent(i, 'name', e.target.value)} placeholder="Full name" size={30} />
                  </div>
                  <div>
                    <Label className="text-xs">Relationship</Label>
                    <Input value={dep.relationship} onChange={e => updateDependent(i, 'relationship', e.target.value)} placeholder="e.g. Child" />
                  </div>
                  <div>
                    <Label className="text-xs">Date of Birth</Label>
                    <Input type="date" value={dep.dateOfBirth} onChange={e => updateDependent(i, 'dateOfBirth', e.target.value)} />
                  </div>
                  <div>
                    <Label className="text-xs">ID Number</Label>
                    <Input value={dep.idNumber} onChange={e => updateDependent(i, 'idNumber', e.target.value)} placeholder="ID" />
                  </div>
                  <div className="flex gap-2">
                    {dependents.length < 6 && i === dependents.length - 1 && (
                      <Button type="button" variant="outline" size="sm" onClick={addDependent} title="Add another dependent" className="flex-1">
                        <Plus className="h-3.5 w-3.5" />
                      </Button>
                    )}
                    <Button type="button" variant="ghost" size="icon" onClick={() => removeDependent(i)} title="Remove dependent" className="text-destructive hover:text-destructive hover:bg-destructive/10">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <div className="flex gap-3">
          <Button 
            type="submit" 
            disabled={submitting}
            className="bg-primary text-primary-foreground hover:bg-primary/90 px-8"
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Registering...
              </>
            ) : (
              'Register Policy'
            )}
          </Button>
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => { reset(); setDependents([]); }}
            disabled={submitting}
          >
            Clear Form
          </Button>
        </div>
      </form>
    </DashboardLayout>
  );
}
