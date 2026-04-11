import { useState, useEffect, useMemo } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { claimSchema, type ClaimFormData } from '@/lib/validation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ClipboardList, Loader2, AlertTriangle, Upload, Check, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { apiService } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

interface Policy {
  id: number;
  policy_number: string;
  customer: {
    first_name: string;
    last_name: string;
  };
}

export default function ClaimFormPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [policiesLoading, setPoliciesLoading] = useState(true);
  const [policySearch, setPolicySearch] = useState('');
  const [showPolicyDropdown, setShowPolicyDropdown] = useState(false);
  
  // File upload states
  const [claimDocFile, setClaimDocFile] = useState<File | null>(null);
  const [deceasedIdFile, setDeceasedIdFile] = useState<File | null>(null);
  const [relationshipDocFile, setRelationshipDocFile] = useState<File | null>(null);
  
  const { register, handleSubmit, formState: { errors }, reset, setValue, watch } = useForm<ClaimFormData>({
    resolver: zodResolver(claimSchema),
    defaultValues: { claimAmount: 5000 },
  });

  const selectedPolicyNumber = watch('policyNumber');

  // Fetch policies on mount
  useEffect(() => {
    const fetchPolicies = async () => {
      try {
        setPoliciesLoading(true);
        const response = await apiService.getPolicies({ page_size: 1000 });
        setPolicies(response.results || response);
      } catch (err) {
        console.error('Failed to fetch policies:', err);
        toast.error('Failed to load policies');
      } finally {
        setPoliciesLoading(false);
      }
    };
    fetchPolicies();
  }, []);

  // Filter policies based on search
  const filteredPolicies = useMemo(() => {
    if (!policySearch) return policies;
    const search = policySearch.toLowerCase();
    return policies.filter(p => 
      p.policy_number.toLowerCase().includes(search) ||
      `${p.customer.first_name} ${p.customer.last_name}`.toLowerCase().includes(search)
    );
  }, [policies, policySearch]);

  // Document type labels
  const claimDocTypes = {
    death_certificate: 'Original Death Certificate',
    medical_report: 'Medical Report',
    cause_of_death_report: 'Cause of Death Report',
    postmortem_report: 'Post Mortem Report'
  };

  const deceasedIdTypes = {
    id: 'National ID',
    passport: 'Passport'
  };

  const relationshipDocTypes = {
    birth_certificate: 'Birth Certificate (for children/parents)',
    marriage_certificate: 'Marriage Certificate (for spouse)',
    affidavit: 'Affidavit (if formal documents unavailable)'
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, fileType: 'claim' | 'deceased' | 'relationship') => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File too large', { description: 'Maximum file size is 5MB' });
      return;
    }

    // Validate file type (PDFs and images only)
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      toast.error('Invalid file type', { description: 'Please upload a PDF or image file' });
      return;
    }

    if (fileType === 'claim') setClaimDocFile(file);
    else if (fileType === 'deceased') setDeceasedIdFile(file);
    else setRelationshipDocFile(file);
  };

  const onSubmit = async (data: ClaimFormData) => {
    try {
      setError(null);

      // Validate file uploads
      if (!claimDocFile) {
        toast.error('Missing documents', { description: 'Please upload a claim document' });
        return;
      }
      if (!deceasedIdFile) {
        toast.error('Missing documents', { description: 'Please upload the deceased\'s ID/Passport' });
        return;
      }
      if (!relationshipDocFile) {
        toast.error('Missing documents', { description: 'Please upload a relationship document' });
        return;
      }

      setSubmitting(true);

      // Create comprehensive claim payload (JSON, not FormData)
      const claimPayload = {
        policy_number: data.policyNumber.trim(),
        claim_type: 'DEATH',
        amount_claimed: data.claimAmount.toString(),
        description: `Death claim - Deceased: ${data.deceasedName}. Cause: ${data.causeOfDeath}`,
        event_date: data.dateOfDeath,
        claimant_name: data.claimantName.trim(),
        claimant_relation: data.claimantRelation.trim(),
        claimant_phone: data.claimantPhone.trim(),
        claimant_email: data.claimantEmail.trim().toLowerCase(),
        deceased_name: data.deceasedName.trim(),
        date_of_death: data.dateOfDeath,
        cause_of_death: data.causeOfDeath.trim(),
        place_of_death: data.placeOfDeath.trim(),
        burial_date: data.burialDate || null,
        burial_place: data.burialPlace.trim(),
        bank_name: data.bankName.trim(),
        account_number: data.accountNumber.trim(),
        branch_code: data.branchCode.trim(),
      };

      console.log('[ClaimForm] Submitting claim:', claimPayload);
      const response = await apiService.createClaim(claimPayload);
      console.log('[ClaimForm] Claim created successfully:', response);
      
      // Upload documents asynchronously (don't block on failure)
      if (response.id) {
        uploadClaimDocuments(response.id, data);
      }
      
      toast.success('Claim submitted successfully!', { 
        description: `Claim ${response.claim_number} has been created and is pending review.` 
      });
      
      reset();
      setClaimDocFile(null);
      setDeceasedIdFile(null);
      setRelationshipDocFile(null);
      setTimeout(() => navigate('/claims'), 2000);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to submit claim';
      console.error('Claim submission error:', err);
      setError(errorMessage);
      toast.error('Failed to submit claim', { description: errorMessage });
    } finally {
      setSubmitting(false);
    }
  };

  const uploadClaimDocuments = async (claimId: string, data: ClaimFormData) => {
    try {
      console.log('[ClaimForm] Uploading documents for claim:', claimId);
      
      // Upload all documents
      const documentsToUpload = [
        { file: claimDocFile, docType: 'DEATH_CERT', title: 'Claim Document' },
        { file: deceasedIdFile, docType: 'MEDICAL_CERT', title: 'Deceased ID Document' },
        { file: relationshipDocFile, docType: 'AFFIDAVIT', title: 'Relationship Document' }
      ];

      for (const doc of documentsToUpload) {
        if (doc.file) {
          const formData = new FormData();
          formData.append('doc_type', doc.docType);
          formData.append('title', doc.title);
          formData.append('file', doc.file);
          
          try {
            await apiService.uploadClaimDocument(claimId, formData);
            console.log('[ClaimForm] Document uploaded:', doc.title);
          } catch (err) {
            console.warn('[ClaimForm] Document upload failed:', doc.title, err);
            // Don't fail the claim if documents fail - they can be uploaded later
          }
        }
      }
      
      console.log('[ClaimForm] All documents uploaded successfully');
    } catch (err) {
      console.error('[ClaimForm] Error uploading documents:', err);
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
    <div>{children}<FieldError error={error} /></div>
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
                <h3 className="font-semibold text-destructive mb-1">Error Submitting Claim</h3>
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
        <h1>File a Claim</h1>
        <p>Submit a funeral assurance claim for processing</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="max-w-4xl space-y-6">
        {/* Claim Info */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="form-section">
          <div className="flex items-center gap-2 mb-4">
            <ClipboardList className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold font-display">Claim Information</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Searchable Policy Number */}
            <FormFieldWrapper error={errors.policyNumber}>
              <Label>Policy Number *</Label>
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Search by policy number or customer name"
                  value={policySearch}
                  onChange={(e) => {
                    setPolicySearch(e.target.value);
                    setShowPolicyDropdown(true);
                  }}
                  onFocus={() => setShowPolicyDropdown(true)}
                  className={errors.policyNumber ? 'border-destructive focus-visible:ring-destructive' : ''}
                />
                {showPolicyDropdown && (
                  <div className="absolute top-full left-0 right-0 mt-2 max-h-48 overflow-y-auto bg-background border rounded-md shadow-md z-10">
                    {policiesLoading ? (
                      <div className="p-2 text-sm text-muted-foreground text-center">Loading policies...</div>
                    ) : filteredPolicies.length > 0 ? (
                      filteredPolicies.map(policy => (
                        <button
                          key={policy.id}
                          type="button"
                          onClick={() => {
                            setValue('policyNumber', policy.policy_number);
                            setPolicySearch(policy.policy_number);
                            setShowPolicyDropdown(false);
                          }}
                          className="w-full text-left px-3 py-2 hover:bg-muted transition-colors text-sm"
                        >
                          <div className="font-medium">{policy.policy_number}</div>
                          <div className="text-xs text-muted-foreground">
                            {policy.customer.first_name} {policy.customer.last_name}
                          </div>
                        </button>
                      ))
                    ) : (
                      <div className="p-2 text-sm text-muted-foreground text-center">No policies found</div>
                    )}
                  </div>
                )}
              </div>
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.claimAmount}>
              <Label>Claim Amount (USD) *</Label>
              <Input type="number" {...register('claimAmount', { valueAsNumber: true })} min={100} max={50000} className={errors.claimAmount ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
          </div>
        </motion.div>

        {/* Claimant */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-4">Claimant Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormFieldWrapper error={errors.claimantName}>
              <Label>Full Name *</Label>
              <Input {...register('claimantName')} className={errors.claimantName ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.claimantRelation}>
              <Label>Relationship to Deceased *</Label>
              <Input {...register('claimantRelation')} placeholder="e.g. Spouse" className={errors.claimantRelation ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.claimantPhone}>
              <Label>Phone *</Label>
              <Input {...register('claimantPhone')} placeholder="+263771234567" className={errors.claimantPhone ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.claimantEmail}>
              <Label>Email *</Label>
              <Input type="email" {...register('claimantEmail')} className={errors.claimantEmail ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
          </div>
        </motion.div>

        {/* Deceased */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-4">Deceased Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormFieldWrapper error={errors.deceasedName}>
              <Label>Name of Deceased *</Label>
              <Input {...register('deceasedName')} className={errors.deceasedName ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.dateOfDeath}>
              <Label>Date of Death *</Label>
              <Input type="date" {...register('dateOfDeath')} className={errors.dateOfDeath ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.causeOfDeath}>
              <Label>Cause of Death *</Label>
              <Input {...register('causeOfDeath')} className={errors.causeOfDeath ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.placeOfDeath}>
              <Label>Place of Death *</Label>
              <Input {...register('placeOfDeath')} className={errors.placeOfDeath ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.burialDate}>
              <Label>Burial Date *</Label>
              <Input type="date" {...register('burialDate')} className={errors.burialDate ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.burialPlace}>
              <Label>Burial Place *</Label>
              <Input {...register('burialPlace')} className={errors.burialPlace ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
          </div>

          {/* Deceased ID Upload */}
          <div className="mt-6 pt-6 border-t">
            <h4 className="font-semibold mb-4">Deceased Identification Document *</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormFieldWrapper error={errors.deceasedIdType}>
                <Label>Document Type *</Label>
                <Select onValueChange={v => setValue('deceasedIdType', v as any)}>
                  <SelectTrigger className={errors.deceasedIdType ? 'border-destructive' : ''}><SelectValue placeholder="Select document type" /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(deceasedIdTypes).map(([key, label]) => (
                      <SelectItem key={key} value={key}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormFieldWrapper>
              <div>
                <Label>Upload Document *</Label>
                <div className="relative">
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.webp"
                    onChange={(e) => handleFileChange(e, 'deceased')}
                    className="hidden"
                    id="deceased-id-upload"
                  />
                  <label htmlFor="deceased-id-upload" className={`flex items-center justify-center px-4 py-3 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${deceasedIdFile ? 'border-green-500 bg-green-50' : 'border-muted-foreground hover:border-primary'}`}>
                    <div className="text-center">
                      {deceasedIdFile ? (
                        <>
                          <Check className="h-5 w-5 text-green-600 mx-auto mb-1" />
                          <p className="text-sm font-medium text-green-600">{deceasedIdFile.name}</p>
                        </>
                      ) : (
                        <>
                          <Upload className="h-5 w-5 text-muted-foreground mx-auto mb-1" />
                          <p className="text-sm text-muted-foreground">Click to upload (PDF or image, max 5MB)</p>
                        </>
                      )}
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Claim Documents */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-4">Claim Documents</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormFieldWrapper error={errors.claimDocumentType}>
              <Label>Document Type *</Label>
              <Select onValueChange={v => setValue('claimDocumentType', v as any)}>
                <SelectTrigger className={errors.claimDocumentType ? 'border-destructive' : ''}><SelectValue placeholder="Select document type" /></SelectTrigger>
                <SelectContent>
                  {Object.entries(claimDocTypes).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormFieldWrapper>
            <div>
              <Label>Upload Document *</Label>
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.webp"
                  onChange={(e) => handleFileChange(e, 'claim')}
                  className="hidden"
                  id="claim-doc-upload"
                />
                <label htmlFor="claim-doc-upload" className={`flex items-center justify-center px-4 py-3 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${claimDocFile ? 'border-green-500 bg-green-50' : 'border-muted-foreground hover:border-primary'}`}>
                  <div className="text-center">
                    {claimDocFile ? (
                      <>
                        <Check className="h-5 w-5 text-green-600 mx-auto mb-1" />
                        <p className="text-sm font-medium text-green-600">{claimDocFile.name}</p>
                      </>
                    ) : (
                      <>
                        <Upload className="h-5 w-5 text-muted-foreground mx-auto mb-1" />
                        <p className="text-sm text-muted-foreground">Click to upload (PDF or image, max 5MB)</p>
                      </>
                    )}
                  </div>
                </label>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Relationship Documents */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-4">Proof of Relationship Document</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormFieldWrapper error={errors.relationshipDocumentType}>
              <Label>Document Type *</Label>
              <Select onValueChange={v => setValue('relationshipDocumentType', v as any)}>
                <SelectTrigger className={errors.relationshipDocumentType ? 'border-destructive' : ''}><SelectValue placeholder="Select document type" /></SelectTrigger>
                <SelectContent>
                  {Object.entries(relationshipDocTypes).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormFieldWrapper>
            <div>
              <Label>Upload Document *</Label>
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.webp"
                  onChange={(e) => handleFileChange(e, 'relationship')}
                  className="hidden"
                  id="relationship-doc-upload"
                />
                <label htmlFor="relationship-doc-upload" className={`flex items-center justify-center px-4 py-3 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${relationshipDocFile ? 'border-green-500 bg-green-50' : 'border-muted-foreground hover:border-primary'}`}>
                  <div className="text-center">
                    {relationshipDocFile ? (
                      <>
                        <Check className="h-5 w-5 text-green-600 mx-auto mb-1" />
                        <p className="text-sm font-medium text-green-600">{relationshipDocFile.name}</p>
                      </>
                    ) : (
                      <>
                        <Upload className="h-5 w-5 text-muted-foreground mx-auto mb-1" />
                        <p className="text-sm text-muted-foreground">Click to upload (PDF or image, max 5MB)</p>
                      </>
                    )}
                  </div>
                </label>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Banking */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="form-section">
          <h3 className="text-lg font-semibold font-display mb-4">Banking Details for Payout</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormFieldWrapper error={errors.bankName}>
              <Label>Bank Name *</Label>
              <Input {...register('bankName')} placeholder="e.g. CBZ Bank" className={errors.bankName ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.accountNumber}>
              <Label>Account Number *</Label>
              <Input {...register('accountNumber')} className={errors.accountNumber ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
            <FormFieldWrapper error={errors.branchCode}>
              <Label>Branch Code *</Label>
              <Input {...register('branchCode')} className={errors.branchCode ? 'border-destructive focus-visible:ring-destructive' : ''} />
            </FormFieldWrapper>
          </div>
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
                Submitting...
              </>
            ) : (
              'Submit Claim'
            )}
          </Button>
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => {
              reset();
              setClaimDocFile(null);
              setDeceasedIdFile(null);
              setRelationshipDocFile(null);
            }}
            disabled={submitting}
          >
            Clear Form
          </Button>
        </div>
      </form>
    </DashboardLayout>
  );
}
