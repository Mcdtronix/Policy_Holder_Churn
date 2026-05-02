import type { PolicyHolder } from './types';

// Generate mock data matching the CSV structure
const locations = ['Harare', 'Bulawayo', 'Mutare', 'Gweru', 'Masvingo', 'Chitungwiza', 'Kadoma', 'Kwekwe', 'Kariba', 'Victoria Falls'];
const names = ['Tatenda Moyo', 'Rudo Chipanga', 'Blessing Mutsvangwa', 'Tapiwa Ncube', 'Fadzai Mupfudze', 'Kudzai Chikore', 'Memory Chiweshe', 'Tinotenda Munyoro', 'Rumbidzai Mupinga', 'Prince Chibanda'];
const paymentMethods = ['Mobile Money', 'Ecocash', 'Cash', 'Bank Debit'];
const incomes = ['Low', 'Medium', 'High'];
const policyTypes = ['Individual', 'Family'];

function rand(min: number, max: number) { return Math.floor(Math.random() * (max - min + 1)) + min; }

export function generateMockPolicyHolders(count: number = 200): PolicyHolder[] {
  return Array.from({ length: count }, (_, i) => ({
    Customer_ID: i + 1,
    Name_and_Surname: names[rand(0, names.length - 1)] + (i > 9 ? ` ${i}` : ''),
    Age: rand(18, 75),
    Gender: Math.random() > 0.5 ? 'Male' : 'Female',
    Location: locations[rand(0, locations.length - 1)],
    Income_Level: incomes[rand(0, 2)],
    Policy_Type: policyTypes[rand(0, 1)],
    Premium_Amount: rand(15, 120),
    Dependents: rand(0, 6),
    Payment_Method: paymentMethods[rand(0, 3)],
    Late_Payments: rand(0, 10),
    Missed_Payments: rand(0, 5),
    Number_of_Complaints: rand(0, 5),
    Claims_Filed: rand(0, 4),
    Customer_Tenure: rand(1, 10),
    Service_Satisfaction: rand(1, 5),
    Churn_Percentage: rand(0, 100),
  }));
}

export const mockPolicyHolders = generateMockPolicyHolders(200);

export const dashboardStats = {
  totalPolicies: 5243,
  activePolicies: 4102,
  pendingClaims: 87,
  totalPremiumRevenue: 482600,
  avgChurnRate: 64.2,
  newPoliciesThisMonth: 142,
  claimsProcessed: 56,
  maturedPolicies: 23,
};

export const monthlyData = [
  { month: 'Jul', newPolicies: 98, claims: 34, churnRate: 62, revenue: 38200 },
  { month: 'Aug', newPolicies: 112, claims: 41, churnRate: 58, revenue: 41500 },
  { month: 'Sep', newPolicies: 89, claims: 28, churnRate: 65, revenue: 36800 },
  { month: 'Oct', newPolicies: 134, claims: 52, churnRate: 61, revenue: 45200 },
  { month: 'Nov', newPolicies: 121, claims: 38, churnRate: 59, revenue: 43100 },
  { month: 'Dec', newPolicies: 156, claims: 45, churnRate: 55, revenue: 48900 },
  { month: 'Jan', newPolicies: 142, claims: 56, churnRate: 64, revenue: 48260 },
];

export const churnByLocation = locations.map(loc => ({
  location: loc,
  churnRate: rand(35, 85),
  policyCount: rand(200, 800),
}));

export const churnByAge = [
  { group: '18-25', churnRate: 72, count: 620 },
  { group: '26-35', churnRate: 58, count: 1240 },
  { group: '36-45', churnRate: 45, count: 1450 },
  { group: '46-55', churnRate: 52, count: 980 },
  { group: '56-65', churnRate: 61, count: 640 },
  { group: '65+', churnRate: 68, count: 313 },
];

export const recentActivities = [
  { id: 1, type: 'claim', description: 'Claim #CLM-2024-087 submitted by Rudo Chipanga', time: '2 hours ago', status: 'pending' },
  { id: 2, type: 'policy', description: 'New family policy registered - Tatenda Moyo', time: '3 hours ago', status: 'active' },
  { id: 3, type: 'payment', description: 'Premium payment received - $48.00 from Blessing Mutsvangwa', time: '5 hours ago', status: 'completed' },
  { id: 4, type: 'maturity', description: 'Policy #POL-3421 matured - Kudzai Chikore', time: '6 hours ago', status: 'matured' },
  { id: 5, type: 'churn', description: 'High churn risk alert - 12 policies flagged', time: '8 hours ago', status: 'alert' },
  { id: 6, type: 'claim', description: 'Claim #CLM-2024-086 approved - Fadzai Mupfudze', time: '1 day ago', status: 'approved' },
];
