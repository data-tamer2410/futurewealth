# Report: Computing Advanced Financial Indicators for Banks

## Project Objective

Develop a system for automatic computation of advanced financial indicators for banks based on their financial statements, with the capability to use proxy methods when direct data is unavailable.

## What Was Accomplished

### 1. Developed the Main Function 
`compute_advanced_indicators()`

The function automatically analyzes available data and computes 7 key financial indicators, using direct calculation or proxy methods depending on data availability.

### 2. Created Proxy Functions for Each Indicator
- `proxy_duration_gap()` - for duration gap calculation
- `proxy_fx_mismatch()` - for foreign exchange mismatch
- `proxy_loan_to_deposit()` - for loan-to-deposit ratio
- `proxy_cash_shortage()` - for cash shortage proxy
- `proxy_core_deposit_mix()` - for core deposit mix ratio
- `proxy_oci_losses()` - for OCI unrealized losses

### 3. Implemented Quality Control System
Each indicator is marked as "direct" (direct calculation) or "proxy" (proxy calculation) to track reliability of results.

### 4. Processed Data for 9 Banks
Analyzed financial data for: Bank of China, Nord LB Luxembourg, KBC Group, Standard Chartered, Barclays, Lloyds TSB Bank, Royal Bank of Canada, First Abu Dhabi Bank, Basler Kantonalbank.

## Calculated Financial Indicators

### 1. Loan-to-Deposit Ratio (LDR)
**Direct Calculation:**
```
LDR = Gross Total Loans / Retail Customer Deposits
```

**Proxy Calculation:**
```
LDR = Gross Total Loans / Gross Total Deposits
```

**Purpose:** Assess bank liquidity and lending intensity

### 2. Cash Shortage Proxy
**Calculation:**
```
Cash Shortage = (Cash + Interbank Loans) / Short-term Liabilities
```

where: 
- Short-term Liabilities = Central Bank Deposits + Bank Deposits

**Purpose:** Evaluate bank's ability to cover short-term obligations

### 3. Duration Gap
**Direct Calculation:**
```
Duration Gap = Average Duration of Assets - Average Duration of Liabilities
```

**Proxy Calculation:**
```
Duration Gap = (Long-term Liabilities - Short-term Liabilities) / Total Liabilities
```

where:
- Long-term = Senior Debt + Subordinated Liabilities
- Short-term = Central Bank Deposits + Bank Deposits

**Purpose:** Assess interest rate risk exposure

### 4. Core Deposit Mix Ratio
**Calculation:**
```
Core Deposit Mix = Retail Customer Deposits / Gross Total Deposits
```

**Purpose:** Evaluate funding stability

### 5. Net Stable Funding Ratio (NSFR)
**Calculation:**
```
NSFR = Reported Value (%) / 100
```

**Purpose:** Regulatory long-term liquidity measure

### 6. OCI-based Unrealized Losses
**Calculation (two indicators):**
```
OCI to Equity = (AFS Securities + HTM Securities) / Total Equity
OCI to Assets = (AFS Securities + HTM Securities) / Total Assets
```

**Purpose:** Assess hidden risks from interest rate changes

### 7. Foreign Exchange Mismatch
**Direct Calculation:**
```
FX Mismatch = |FX Assets - FX Liabilities| / Total Equity
```

**Proxy Calculation:**
```
FX Mismatch = |Derivatives (Assets) - Derivatives (Liabilities)| / Total Equity
```

**Purpose:** Evaluate foreign exchange risk exposure

## Technical Implementation

### Missing Data Handling
- Zeros are automatically replaced with NaN for correct calculations
- Proxy methods are used when direct calculation data is unavailable
- Indicators that cannot be calculated are marked as `null`

### Quality Control
The `cols_exist_and_not_na()` function checks:
- Presence of required columns in the data
- Whether all values are NaN

### Average Value Calculation
All indicators are calculated as arithmetic means over the available period to smooth seasonal fluctuations.

## Results

### Output Data Structure
```json
{
    "meta": {
        "bank_name": "Bank Name",
        "period": "Analysis Period",
        "source_file": "Input File Name"
    },
    "indicators": {
        "Indicator 1": value,
        "Indicator 2": value,
        ...
    },
    "quality": {
        "Indicator 1": "direct/proxy",
        "Indicator 2": "direct/proxy",
        ...
    }
}
```

## Conclusions

The developed system successfully computes a comprehensive set of advanced financial indicators for bank risk assessment, automatically adapting to available data and ensuring transparency of calculation methods through a quality marking system.