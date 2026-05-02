export interface PolicyHolder {
  Customer_ID: number;
  Name_and_Surname: string;
  Age: number;
  Gender: string;
  Location: string;
  Income_Level: string;
  Policy_Type: string;
  Premium_Amount: number;
  Dependents: number;
  Payment_Method: string;
  Late_Payments: number;
  Missed_Payments: number;
  Number_of_Complaints: number;
  Claims_Filed: number;
  Customer_Tenure: number;
  Service_Satisfaction: number;
  Churn_Percentage: number;
}

export interface PolicyRegistration {
  firstName: string;
  lastName: string;
  idNumber: string;
  dateOfBirth: string;
  gender: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  incomeLevel: string;
  policyType: string;
  premiumAmount: number;
  paymentMethod: string;
  dependents: Dependent[];
  beneficiaryName: string;
  beneficiaryRelation: string;
  beneficiaryPhone: string;
}

export interface Dependent {
  name: string;
  relationship: string;
  dateOfBirth: string;
  idNumber: string;
}

export interface ClaimForm {
  policyNumber: string;
  claimantName: string;
  claimantRelation: string;
  claimantPhone: string;
  claimantEmail: string;
  deceasedName: string;
  dateOfDeath: string;
  causeOfDeath: string;
  placeOfDeath: string;
  burialDate: string;
  burialPlace: string;
  claimAmount: number;
  bankName: string;
  accountNumber: string;
  branchCode: string;
  documents: string[];
}

export type ChurnRisk = 'low' | 'medium' | 'high' | 'critical';

export function getChurnRisk(churnPct: number): ChurnRisk {
  if (churnPct <= 30) return 'low';
  if (churnPct <= 60) return 'medium';
  if (churnPct <= 80) return 'high';
  return 'critical';
}

export function getChurnRiskColor(risk: ChurnRisk): string {
  switch (risk) {
    case 'low': return 'badge-success';
    case 'medium': return 'badge-info';
    case 'high': return 'badge-warning';
    case 'critical': return 'badge-danger';
  }
}
