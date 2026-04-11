# Customer Data Import Scripts

## Overview
Two professional import utilities for loading the Nyaradzo churn dataset into your Django database.

## Files

### 1. `import_customers.py` (Production-Grade)
- **Purpose**: Comprehensive, production-ready import with full validation
- **Features**:
  - Transactional integrity
  - Comprehensive error handling and logging
  - Progress tracking
  - Dry-run mode
  - Batch processing
  - Duplicate detection
  - Detailed statistics

### 2. `quick_import.py` (Quick & Simple)
- **Purpose**: Fast, simple import for immediate data loading
- **Features**:
  - Minimal setup
  - Basic error handling
  - Progress indicators
  - Reference data creation

## Data Mapping

| CSV Column | Django Model | Field |
|------------|--------------|-------|
| Customer_ID | Customer | customer_number (NYC-XXXXXX) |
| Name_and_Surname | Customer | first_name, last_name |
| Age | Customer | date_of_birth (calculated) |
| Gender | Customer | gender (FK to Gender) |
| Location | Customer | location (FK to Location) |
| Income_Level | Customer | income_level (FK to IncomeLevel) |
| Policy_Type | Policy | policy_type |
| Premium_Amount | Policy | premium_amount |
| Dependents | CustomerEngagement | dependents_count |
| Payment_Method | Policy | payment_method |
| Late_Payments | CustomerEngagement | late_payments_count |
| Missed_Payments | CustomerEngagement | missed_payments_count |
| Number_of_Complaints | CustomerEngagement | complaints_count |
| Claims_Filed | CustomerEngagement | claims_filed_count |
| Customer_Tenure | CustomerEngagement | customer_tenure_months |
| Service_Satisfaction | CustomerEngagement | service_satisfaction_score |
| Churn_Percentage | ChurnPrediction | churn_percentage |

## Usage

### Quick Import (Recommended for immediate use)

```bash
cd /home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend
python quick_import.py
```

### Production Import

```bash
# Dry run (validation only)
python manage.py import_customers nyaradzo_churn_dataset_5000_customers.csv --dry-run

# Live import
python manage.py import_customers nyaradzo_churn_dataset_5000_customers.csv

# Custom batch size
python manage.py import_customers nyaradzo_churn_dataset_5000_customers.csv --batch-size 500
```

## Generated Data

### Customer Identifiers
- **Customer Number**: `NYC-XXXXXX` (6-digit format)
- **National ID**: `YY-XXXXXXAXX` (Zimbabwe format)
- **Email**: `customerXXXXX@nyaradzo.co.zw`
- **Phone**: `263XXXXXXXXX` (9-digit format)

### Reference Data Created
- **Genders**: Male, Female, Other
- **Income Levels**: Low, Medium, High
- **Locations**: All unique locations from CSV

### Risk Level Calculation
- **HIGH**: Churn % ≥ 80
- **MEDIUM**: Churn % ≥ 50 and < 80
- **LOW**: Churn % < 50

## Post-Import Verification

```sql
-- Check customer count
SELECT COUNT(*) FROM customers;

-- Check data distribution
SELECT 
    g.label as gender,
    COUNT(*) as count
FROM customers c
JOIN genders g ON c.gender_id = g.id
GROUP BY g.label;

-- Check churn risk distribution
SELECT 
    risk_level,
    COUNT(*) as count,
    AVG(churn_percentage) as avg_churn
FROM churn_predictions
GROUP BY risk_level;
```

## Notes

1. **Data Generation**: Missing fields (email, phone, national_id) are generated systematically
2. **Duplicate Handling**: Existing customers (by customer_number) are skipped
3. **Transaction Safety**: Production script uses database transactions
4. **Logging**: Comprehensive logs saved to `customer_import.log`
5. **Performance**: Batch processing optimized for 5,000 records

## Error Handling

- Invalid data formats are logged and skipped
- Database constraints are enforced
- Progress continues on individual record failures
- Comprehensive error reporting provided
