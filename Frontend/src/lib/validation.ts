import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().trim().email('Please enter a valid email address').max(255),
  password: z.string().min(6, 'Password must be at least 6 characters').max(128),
});

/**
 * Dynamic policy registration schema factory.
 * Creates schema with actual policy types from database instead of hardcoded enums.
 */
export const createPolicyRegistrationSchema = (policyTypeNames: string[]) => {
  return z.object({
    firstName: z.string()
      .trim()
      .min(2, 'First name required (min 2 chars)')
      .max(50, 'First name cannot exceed 50 chars'),
    
    lastName: z.string()
      .trim()
      .min(2, 'Last name required (min 2 chars)')
      .max(50, 'Last name cannot exceed 50 chars'),
    
    idNumber: z.string()
      .trim()
      .regex(
        /^[0-9]{2}-[0-9]{6,7}[A-Z][0-9]{2}$/,
        'Invalid Zimbabwe National ID format (e.g., 63-123456A78)'
      ),
    
    dateOfBirth: z.string()
      .min(1, 'Date of birth is required')
      .refine(
        (date) => new Date(date) < new Date(),
        'Date of birth must be in the past'
      ),
    
    gender: z.enum(['Male', 'Female'], { 
      required_error: 'Gender is required',
      invalid_enum_value: 'Please select a valid gender'
    }),
    
    phone: z.string()
      .trim()
      .regex(
        /^(\+263|0)[7][1-9][0-9]{7}$/,
        'Invalid phone number (e.g., +263771234567 or 0771234567)'
      ),
    
    email: z.string()
      .trim()
      .email('Invalid email address')
      .max(255, 'Email cannot exceed 255 chars'),
    
    address: z.string()
      .trim()
      .min(5, 'Address required (min 5 chars)')
      .max(200, 'Address cannot exceed 200 chars'),
    
    city: z.string()
      .trim()
      .min(2, 'City required (min 2 chars)')
      .max(50, 'City cannot exceed 50 chars'),
    
    incomeLevel: z.enum(['Low', 'Medium', 'High'], {
      required_error: 'Income level is required'
    }),
    
    policyType: z.string()
      .min(1, 'Policy type is required')
      .refine(
        (val) => policyTypeNames.length === 0 || policyTypeNames.some(pt => 
          pt.toLowerCase().includes(val.toLowerCase()) || val.toLowerCase().includes(pt.toLowerCase())
        ),
        'Policy type is not available'
      ),
    
    policyFor: z.enum(['Self', 'Other'], {
      required_error: 'Please specify if policy is for yourself or another person'
    }),
    
    premiumAmount: z.number()
      .min(10, 'Minimum premium is $10')
      .max(500, 'Maximum premium is $500'),
    
    paymentMethod: z.enum(['Mobile Money', 'Ecocash', 'Cash', 'Bank Debit'], {
      required_error: 'Payment method is required'
    }),
    
    beneficiaryName: z.string()
      .trim()
      .min(2, 'Beneficiary name required (min 2 chars)')
      .max(100, 'Beneficiary name cannot exceed 100 chars')
      .optional(),
    
    beneficiaryRelation: z.string()
      .trim()
      .min(2, 'Relationship required (min 2 chars)')
      .max(50, 'Relationship cannot exceed 50 chars')
      .optional(),
    
    beneficiaryPhone: z.string()
      .trim()
      .regex(
        /^(\+263|0)[7][1-9][0-9]{7}$/,
        'Invalid beneficiary phone number'
      )
      .optional(),
  });
};

// Default schema for backwards compatibility
export const policyRegistrationSchema = createPolicyRegistrationSchema(['Individual', 'Family', 'Family Policy', 'Individual Policy']);

export const dependentSchema = z.object({
  name: z.string().trim().min(2, 'Name is required').max(100),
  relationship: z.string().trim().min(2, 'Relationship is required').max(50),
  dateOfBirth: z.string().min(1, 'Date of birth is required'),
  idNumber: z.string().trim().min(1, 'ID number is required').max(20),
});

export const claimSchema = z.object({
  policyNumber: z.string().trim().min(1, 'Policy number is required'),
  claimantName: z.string().trim().min(2, 'Claimant name is required (min 2 chars)').max(100, 'Claimant name cannot exceed 100 chars'),
  claimantRelation: z.string().trim().min(2, 'Relationship is required (min 2 chars)').max(50, 'Relationship cannot exceed 50 chars'),
  claimantPhone: z.string().trim().regex(/^(\+263|0)[7][1-9][0-9]{7}$/, 'Invalid phone number (e.g., +263771234567 or 0771234567)'),
  claimantEmail: z.string().trim().email('Invalid email address').max(255, 'Email cannot exceed 255 chars'),
  deceasedName: z.string().trim().min(2, 'Deceased name is required (min 2 chars)').max(100, 'Deceased name cannot exceed 100 chars'),
  dateOfDeath: z.string().min(1, 'Date of death is required'),
  causeOfDeath: z.string().trim().min(3, 'Cause of death is required (min 3 chars)').max(200, 'Cause of death cannot exceed 200 chars'),
  placeOfDeath: z.string().trim().min(2, 'Place of death is required (min 2 chars)').max(100, 'Place of death cannot exceed 100 chars'),
  burialDate: z.string().min(1, 'Burial date is required'),
  burialPlace: z.string().trim().min(2, 'Burial place is required (min 2 chars)').max(100, 'Burial place cannot exceed 100 chars'),
  claimAmount: z.number().min(100, 'Minimum claim is $100').max(50000, 'Maximum claim is $50,000'),
  bankName: z.string().trim().min(2, 'Bank name is required (min 2 chars)').max(100, 'Bank name cannot exceed 100 chars'),
  accountNumber: z.string().trim().min(5, 'Account number is required (min 5 chars)').max(20, 'Account number cannot exceed 20 chars'),
  branchCode: z.string().trim().min(3, 'Branch code is required (min 3 chars)').max(10, 'Branch code cannot exceed 10 chars'),
  claimDocumentType: z.enum(['death_certificate', 'medical_report', 'cause_of_death_report', 'postmortem_report'], {
    required_error: 'Please select a claim document type'
  }),
  deceasedIdType: z.enum(['id', 'passport'], {
    required_error: 'Please select a deceased ID document type'
  }),
  relationshipDocumentType: z.enum(['birth_certificate', 'marriage_certificate', 'affidavit'], {
    required_error: 'Please select a relationship document type'
  }),
});

export const paymentUpdateSchema = z.object({
  policyNumber: z.string().trim().regex(/^POL-[0-9]{4,6}$/, 'Invalid policy number'),
  paymentDate: z.string().min(1, 'Payment date is required'),
  amount: z.number().min(1, 'Amount must be greater than 0').max(10000),
  paymentMethod: z.enum(['Mobile Money', 'Ecocash', 'Cash', 'Bank Debit']),
  reference: z.string().trim().min(3, 'Reference is required').max(50),
  notes: z.string().max(500).optional(),
});

export const churnPredictionSchema = z.object({
  customerId: z.string().optional(),
  age: z.number().min(18).max(120),
  gender: z.enum(['Male', 'Female']),
  location: z.string().min(2),
  incomeLevel: z.enum(['Low Income', 'Medium Income', 'High Income']),
  policyCount: z.number().min(0),
  averagePremium: z.number().min(0),
  paymentMethod: z.enum(['Mobile Money', 'Ecocash', 'Cash', 'Bank Debit']),
  dependents: z.number().min(0),
  latePayments: z.number().min(0),
  missedPayments: z.number().min(0),
  numberOfComplaints: z.number().min(0),
  claimsFiled: z.number().min(0),
  customerTenure: z.number().min(0),
  serviceSatisfaction: z.number().min(0).max(10),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type PolicyFormData = z.infer<typeof policyRegistrationSchema>;
export type ClaimFormData = z.infer<typeof claimSchema>;
export type PaymentUpdateFormData = z.infer<typeof paymentUpdateSchema>;
export type ChurnPredictionFormData = z.infer<typeof churnPredictionSchema>;
