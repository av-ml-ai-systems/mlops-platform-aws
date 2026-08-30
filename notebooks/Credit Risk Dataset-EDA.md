# Credit Risk Dataset — Exploratory Data Analysis

## 1. Dataset Overview

The original Credit Risk dataset contains:

- **32,581 observations**
- **12 variables**

The dataset represents individual loan applications and contains information about:

- applicant demographics
- income
- employment
- home ownership
- loan characteristics
- credit history
- previous default history
- loan default status

### Dataset Structure

| Variable | Type | Description |
|---|---|---|
| `person_age` | Numerical | Applicant age |
| `person_income` | Numerical | Annual applicant income |
| `person_home_ownership` | Categorical | Housing status |
| `person_emp_length` | Numerical | Employment length |
| `loan_intent` | Categorical | Purpose of the loan |
| `loan_grade` | Categorical | Loan risk grade |
| `loan_amnt` | Numerical | Requested loan amount |
| `loan_int_rate` | Numerical | Loan interest rate |
| `loan_status` | Binary | Default indicator |
| `loan_percent_income` | Numerical | Loan amount as percentage of income |
| `cb_person_default_on_file` | Categorical | Previous default recorded by credit bureau |
| `cb_person_cred_hist_length` | Numerical | Credit history length |

---

# 2. Data Types

### Numerical Variables

The numerical variables identified were:

- `person_age`
- `person_income`
- `person_emp_length`
- `loan_amnt`
- `loan_int_rate`
- `loan_status`
- `loan_percent_income`
- `cb_person_cred_hist_length`

`loan_status` is technically stored as an integer but represents a binary target variable rather than a continuous numerical feature.

### Categorical Variables

The categorical variables identified were:

- `person_home_ownership`
- `loan_intent`
- `loan_grade`
- `cb_person_default_on_file`

---

# 3. Missing Values

Two variables contain missing observations.

| Variable | Missing Count | Missing Percentage |
|---|---:|---:|
| `loan_int_rate` | 3,116 | 9.56% |
| `person_emp_length` | 895 | 2.75% |

### Main Observation

`loan_int_rate` has the highest missingness and therefore requires an explicit preprocessing policy.

`person_emp_length` has substantially less missingness but still requires a defined treatment.

Missing values should **not automatically be replaced with arbitrary values**.

The preprocessing stage must determine the appropriate strategy based on:

- business meaning
- missingness mechanism
- relationship with other variables
- modeling requirements

---

# 4. Duplicate Records

The dataset contains:

**165 exact duplicate records.**

These duplicates represent a clear data-quality issue that requires a preprocessing decision.

The final preprocessing specification must explicitly define whether exact duplicates will be removed and why.

---

# 5. Target Variable

The target variable is:

`loan_status`

Its distribution is:

| `loan_status` | Count |
|---:|---:|
| 0 | 25,473 |
| 1 | 7,108 |

Where:

- `0` = non-default
- `1` = default

### Main Observation

The target is imbalanced.

The majority of observations belong to the non-default class, while the default class represents a smaller portion of the dataset.

This imbalance must be considered later during:

- model evaluation
- metric selection
- validation strategy
- threshold selection
- potential class-balancing strategies

The target distribution itself is **not a data-quality error**.

---

# 6. Numerical Distribution Analysis

## 6.1 `person_age`

The distribution is strongly right-skewed.

Most observations are concentrated among younger adults, with progressively fewer observations at higher ages.

The distribution contains a long upper tail.

### Main Characteristics

- strong right skew
- concentration around younger ages
- long upper tail
- presence of extreme ages

The maximum observed age is **144**.

This is a strong candidate for business-rule validation.

An unusual age is not automatically an error, but an age of 144 is highly suspicious in the context of a credit application dataset.

### ML Implications

Tree-based models such as:

- Decision Trees
- Random Forest
- XGBoost
- LightGBM

are generally less sensitive to skewness itself.

The more important issue is whether the extreme values are valid observations.

---

## 6.2 `person_income`

`person_income` is one of the most strongly right-skewed variables in the dataset.

Most observations are concentrated toward lower income values, while a small number of observations extend into extremely high income values.

The maximum observed income is:

**6,000,000**

Several additional observations have incomes above one million.

### Main Characteristics

- extremely right-skewed
- very long upper tail
- large difference between median and mean
- presence of extreme income observations

### Important Observation

Extreme income values should **not automatically be removed**.

Possible explanations include:

- legitimate high-income applicants
- different income scales
- unusual financial profiles
- data-entry errors
- encoding problems

Therefore, these observations require domain validation.

### ML Implications

Income transformations may be useful for some models, especially models sensitive to scale and distribution.

A logarithmic transformation could be considered later, but only after understanding the data and modeling objective.

For tree-based models, raw skewness is generally less problematic.

---

## 6.3 `person_emp_length`

`person_emp_length` is strongly right-skewed.

Most applicants have relatively short employment histories, while fewer observations have longer employment lengths.

The maximum observed value is:

**123 years**

This is clearly suspicious for applicants in their early twenties.

### Important Observation

Employment length should not be evaluated independently.

It should be validated against other variables, particularly:

- `person_age`
- potentially `cb_person_cred_hist_length`

An employment history that is impossible given the applicant's age represents a **business-rule violation**, not merely a statistical outlier.

---

## 6.4 `loan_amnt`

`loan_amnt` is not simply a smooth right-skewed distribution.

The distribution shows several noticeable peaks, suggesting **multimodality**.

There is also a right tail toward larger loan amounts.

### Main Characteristics

- multimodal
- several concentration points
- right tail
- possible standardized/common loan amounts

### Interpretation

The multiple peaks may reflect:

- common requested loan amounts
- predefined lending amounts
- different borrower segments
- different loan purposes
- the way loan amounts are generated or recorded

Therefore, this variable should not automatically receive a generic skewness treatment.

---

## 6.5 `loan_int_rate`

`loan_int_rate` appears to be multimodal.

Instead of one clean distribution, several peaks and valleys are visible.

### Possible Explanation

The multiple modes may reflect different interest-rate regimes associated with:

- loan grades
- borrower risk
- credit history
- income
- loan amount
- loan purpose
- lending policies

### Important Modeling Consideration

Interest rate may already incorporate information about borrower risk.

Therefore, depending on the exact prediction point and business problem, `loan_int_rate` must be investigated for:

- availability at prediction time
- temporal ordering
- potential target leakage
- whether it represents information already derived from the target-related risk assessment

The histogram alone cannot establish leakage, but it identifies the need for this investigation.

---

## 6.6 `loan_percent_income`

`loan_percent_income` is right-skewed.

Most observations are concentrated at relatively low values, while a smaller number of borrowers have substantially larger loan-to-income ratios.

### Important Interpretation

This feature is particularly meaningful from a credit-risk perspective.

`loan_amnt` represents the absolute loan size.

`loan_percent_income` represents the relative financial burden.

A large loan is not necessarily risky if the applicant has a sufficiently high income.

Therefore, the ratio can provide information that the absolute loan amount cannot provide by itself.

### Main Characteristics

- unimodal
- right-skewed
- concentrated at lower values
- upper tail containing potentially important observations

High values should not automatically be treated as errors.

They may represent genuine high-risk financial situations.

---

## 6.7 `cb_person_cred_hist_length`

This variable represents credit-history length.

The distribution appears discrete rather than truly continuous.

There are sharp peaks because the variable takes specific values rather than arbitrary continuous values.

### Main Characteristics

- discrete
- right-skewed
- concentration around shorter credit histories
- progressively fewer observations at longer histories

### Important Visualization Consideration

KDE is not necessarily the ideal visualization for this variable because KDE assumes an underlying continuous distribution.

For discrete variables, frequency-based plots may provide a more faithful representation.

### Potential Relationship

This feature should be investigated together with:

`person_age`

Older applicants generally have more opportunity to have longer credit histories.

This does not mean the variables are redundant, but their relationship should be investigated during feature analysis.

---

# 7. Numerical Distribution Summary

| Variable | Main Shape | Main Observation |
|---|---|---|
| `person_age` | Right-skewed | Younger applicants dominate; suspicious extreme ages |
| `person_income` | Extremely right-skewed | Very long upper tail and extreme incomes |
| `person_emp_length` | Right-skewed | Short employment histories dominate; suspicious extreme values |
| `loan_amnt` | Multimodal + right tail | Several common loan-size concentrations |
| `loan_int_rate` | Multimodal | Multiple interest-rate regimes may exist |
| `loan_percent_income` | Right-skewed | Most borrowers have lower ratios |
| `cb_person_cred_hist_length` | Discrete + right-skewed | Short credit histories dominate |

---

# 8. Categorical Distribution Analysis

## 8.1 `person_home_ownership`

| Category | Count |
|---|---:|
| RENT | 16,446 |
| MORTGAGE | 13,444 |
| OWN | 2,584 |
| OTHER | 107 |

The largest groups are:

- `RENT`
- `MORTGAGE`

`OTHER` has very few observations.

Therefore, the `OTHER` category should be interpreted carefully because estimates based on very small groups can be unstable.

---

## 8.2 `loan_intent`

| Category | Count |
|---|---:|
| EDUCATION | 6,453 |
| MEDICAL | 6,071 |
| VENTURE | 5,719 |
| PERSONAL | 5,521 |
| DEBTCONSOLIDATION | 5,212 |
| HOMEIMPROVEMENT | 3,605 |

Loan intents are relatively well distributed.

`EDUCATION` is the most frequent purpose, while `HOMEIMPROVEMENT` is the least frequent.

No unexpected categories were identified.

---

## 8.3 `loan_grade`

| Grade | Count |
|---|---:|
| A | 10,777 |
| B | 10,451 |
| C | 6,458 |
| D | 3,626 |
| E | 964 |
| F | 241 |
| G | 64 |

The dataset is heavily concentrated in Grades A and B.

Grades E, F, and G contain substantially fewer observations.

This creates an important class-imbalance issue within the categorical feature itself.

The small number of observations in Grades F and G must be considered when interpreting default rates.

---

## 8.4 `cb_person_default_on_file`

| Category | Count |
|---|---:|
| N | 26,836 |
| Y | 5,745 |

Most applicants do not have a previous default recorded on file.

A smaller but meaningful group has a previous default.

No unexpected categories were identified.

---

# 9. Categorical Distribution Summary

| Variable | Main Observation |
|---|---|
| `person_home_ownership` | RENT and MORTGAGE dominate |
| `loan_intent` | Relatively balanced across purposes |
| `loan_grade` | Strong concentration in A and B |
| `cb_person_default_on_file` | N strongly dominates Y |

---

# 10. Numerical Variables vs Target

The numerical variables were compared across:

- `loan_status = 0`
- `loan_status = 1`

## 10.1 `person_age`

The distributions are very similar.

Both groups have similar medians and interquartile ranges.

However, both contain extreme ages, including values above 140.

### Interpretation

There is no obvious strong separation between default and non-default groups based on age alone.

The extreme ages are primarily a data-quality/business-rule concern.

---

## 10.2 `person_income`

The main distributions are relatively similar.

Both groups are strongly affected by extreme income observations.

The non-default group contains particularly extreme high-income values.

### Interpretation

Income may contain useful predictive information, but the extreme upper tail requires data-quality investigation.

---

## 10.3 `person_emp_length`

The distributions are very similar.

Most observations are concentrated between approximately 0 and 10 years.

Both groups contain extreme values, including values above 100 years.

### Interpretation

The major issue is data validity rather than clear target separation.

---

## 10.4 `loan_amnt`

The default group shows an upward shift.

Defaulting borrowers tend to have higher loan amounts.

### Interpretation

`loan_amnt` appears to have meaningful discriminatory potential between the target classes.

However, the relationship should be interpreted together with:

- income
- loan-to-income ratio
- interest rate
- loan grade
- employment
- credit history

---

## 10.5 `loan_int_rate`

This is one of the clearest numerical differences.

Defaulting loans show substantially higher interest rates.

### Interpretation

Higher interest rates are strongly associated with the default class in this dataset.

However, the temporal/business meaning of the interest rate must be understood before using it as a predictive feature.

---

## 10.6 `loan_percent_income`

This is another strong differentiating variable.

Defaulting borrowers have:

- higher median values
- higher overall distribution
- greater spread

### Interpretation

Borrowers whose loans represent a larger proportion of their income appear substantially more exposed to default.

This feature appears particularly relevant for credit-risk modeling.

---

## 10.7 `cb_person_cred_hist_length`

The two target groups are very similar.

Medians and interquartile ranges are approximately the same.

### Interpretation

There is no obvious strong univariate separation between default and non-default borrowers based solely on credit-history length.

---

# 11. Categorical Variables vs Target

The proportion of defaults was analyzed across categorical variables.

## 11.1 `person_home_ownership`

Default proportions differ substantially by housing status.

- `RENT` shows a relatively high default proportion.
- `OTHER` also shows a high proportion, but has very few observations.
- `MORTGAGE` has a substantially lower default proportion.
- `OWN` has the lowest default proportion among the main categories.

### Interpretation

Home ownership appears to contain useful information about credit risk.

However, the small `OTHER` category must be interpreted cautiously.

---

## 11.2 `loan_intent`

Default proportions vary across loan purposes, but the differences are less dramatic than for loan grade.

Higher default proportions are observed in categories such as:

- `DEBTCONSOLIDATION`
- `HOMEIMPROVEMENT`
- `MEDICAL`

Lower proportions appear in:

- `VENTURE`
- `PERSONAL`
- `EDUCATION`

### Interpretation

Loan purpose may contribute predictive information, but it does not appear to be as strongly associated with default as `loan_grade`.

---

## 11.3 `loan_grade`

This is one of the strongest relationships discovered during EDA.

Default proportions increase strongly and monotonically as loan grade deteriorates.

The approximate pattern is:

- Grade A → relatively low default
- Grade B → higher
- Grade C → higher
- Grade D → substantially higher
- Grade E → very high
- Grade F → extremely high
- Grade G → almost entirely default

### Important Observation

Grades F and G have very few observations.

Therefore, their extremely high default proportions must be interpreted with caution.

Nevertheless, the overall monotonic relationship between grade and default is extremely strong.

---

## 11.4 `cb_person_default_on_file`

Applicants with a previous default recorded on file have a substantially higher default proportion.

The approximate pattern is:

- `N` → lower default proportion
- `Y` → substantially higher default proportion

### Interpretation

Previous default history appears to contain meaningful predictive information.

---

# 12. Data Quality Investigation

The EDA identified several observations that require further validation.

## 12.1 Age and Employment-Length Anomalies

Examples include:

| `person_age` | `person_emp_length` | `person_income` | `loan_status` |
|---:|---:|---:|---:|
| 22 | 123 | 59,000 | 1 |
| 21 | 123 | 192,000 | 0 |
| 23 | 123 | 92,111 | 1 |

These observations strongly suggest invalid employment-history values.

Additional extreme ages were identified, including:

- age 123
- age 144

These values require business-rule validation.

---

## 12.2 Extreme Income Observations

Several high-income observations were identified.

Examples include income values above:

- 1 million
- 1.3 million
- 1.4 million
- 1.7 million
- 1.9 million
- 2 million
- 6 million

These observations were **not automatically classified as errors**.

They require domain validation.

Possible explanations include:

- legitimate high-income applicants
- unusual financial profiles
- unit inconsistencies
- data-entry errors
- encoding problems

---

## 12.3 Other Extreme Income Observations

Additional high-income observations were found, including combinations such as:

| `person_age` | `person_income` | `person_emp_length` | `loan_amnt` | `loan_status` |
|---:|---:|---:|---:|---:|
| 32 | 1,200,000 | 1 | 12,000 | 0 |
| 36 | 1,200,000 | 16 | 10,000 | 0 |
| 40 | 1,200,000 | 1 | 10,000 | 0 |
| 47 | 1,362,000 | 9 | 6,600 | 0 |
| 44 | 1,440,000 | 7 | 6,400 | 0 |
| 63 | 1,782,000 | 13 | 12,025 | 0 |
| 60 | 1,900,000 | 5 | 1,500 | 0 |
| 42 | 2,039,784 | 0 | 8,450 | 0 |
| 144 | 6,000,000 | 12 | 5,000 | 0 |

The combination of extremely high income and other unusual attributes makes these observations particularly important for domain validation.

---

## 12.4 Duplicate Records

The dataset contains:

**165 exact duplicate records.**

These should be addressed explicitly in the preprocessing policy.

---

## 12.5 Missing Interest Rates

`loan_int_rate` contains:

**3,116 missing observations**

This represents approximately **9.56%** of the dataset.

A specific missing-value policy must be established before preprocessing.

---

## 12.6 Missing Employment Length

`person_emp_length` contains:

**895 missing observations**

This represents approximately **2.75%** of the dataset.

The missingness must be handled according to a defined preprocessing policy.

---

## 12.7 Category Validation

All expected categories were validated.

### `person_home_ownership`

- Unexpected categories: none
- Missing expected categories: none

### `loan_intent`

- Unexpected categories: none
- Missing expected categories: none

### `loan_grade`

- Unexpected categories: none
- Missing expected categories: none

### `cb_person_default_on_file`

- Unexpected categories: none
- Missing expected categories: none

---

## 12.8 Target Validation

The target variable was also validated.

- Unexpected target values: none
- Missing expected target values: none

The target contains only the expected binary values:

- `0`
- `1`

---

# 13. Business-Rule Validation

The EDA demonstrated why statistical outlier detection alone is insufficient.

An observation can be:

> statistically unusual

without being:

> business-invalid

Conversely, some observations can violate obvious domain constraints even if they are not statistically extreme.

The clearest example is:

`person_emp_length = 123`

for applicants in their early twenties.

### General Validation Principle

```
Statistical anomaly
        ↓
Investigate
        ↓
Business validation
        ↓
 ┌───────────────┐
 │               │
Valid          Invalid
 │               │
Keep        Correct / Handle
```

---

# 14. Important EDA Conclusions

## 14.1 The Dataset Contains Several Strongly Right-Skewed Variables

The strongest examples are:

- `person_income`
- `person_age`
- `person_emp_length`
- `loan_percent_income`
- `cb_person_cred_hist_length`

This means the mean is not always the best representation of the typical observation.

Median and quantile-based statistics are often more informative for these variables.

---

## 14.2 `person_income` Requires Special Attention

`person_income` has the strongest extreme upper tail.

The maximum value is:

**6,000,000**

However, high-income observations cannot automatically be considered erroneous.

The correct approach is:

- investigate
- validate
- understand the business context
- decide whether the values are valid

---

## 14.3 `loan_amnt` Is Multimodal

`loan_amnt` does not simply exhibit skewness.

It contains multiple concentration points.

This suggests that loan amounts may be influenced by:

- standard lending amounts
- borrower segments
- loan purpose
- financial profiles
- data-generation mechanisms

Therefore, generic transformations should not be applied without understanding the feature.

---

## 14.4 `loan_int_rate` Is Multimodal

The multiple peaks suggest different interest-rate regimes.

This may be associated with borrower risk or loan-grade structure.

This feature requires special attention because interest rates may already encode information about borrower risk.

---

## 14.5 `loan_percent_income` Appears Highly Informative

The distribution of `loan_percent_income` differs clearly between default and non-default borrowers.

Defaulting borrowers tend to have higher loan-to-income ratios.

This suggests that relative financial burden may be an important predictor of default.

---

## 14.6 `loan_grade` Is Highly Associated with Default

`loan_grade` showed the strongest categorical relationship with the target.

Default rates increase strongly as the grade deteriorates.

However, the very small sample sizes in Grades F and G must be considered.

---

## 14.7 Previous Default History Is Informative

`cb_person_default_on_file` also shows a strong relationship with `loan_status`.

Applicants with previous defaults are more likely to default again.

---

## 14.8 Some Features Show Little Univariate Separation

The following variables showed relatively similar distributions between target classes:

- `person_age`
- `person_income`
- `person_emp_length`
- `cb_person_cred_hist_length`

This does **not** mean they are useless.

A variable can have weak univariate separation and still contribute useful information through:

- interactions
- nonlinear relationships
- combinations with other features
- model-specific patterns

---

# 15. Most Important Data-Quality Findings

The most important issues identified during EDA are:

| Issue | Importance | Current Interpretation |
|---|---|---|
| Exact duplicates | High | Clear data-quality issue |
| Missing `loan_int_rate` | High | Requires preprocessing policy |
| Missing `person_emp_length` | Medium | Requires preprocessing policy |
| `person_age = 123/144` | High | Strong business-rule concern |
| `person_emp_length = 123` | Very High | Strong business-rule concern |
| Extreme income values | High | Requires domain validation |
| Small `OTHER` category | Medium | Potential instability |
| Small Grades F/G | High | Statistical instability |
| `loan_percent_income` inconsistencies | Medium | Requires understanding of source/calculation rule |
| Multimodal `loan_amnt` | Medium | Requires domain interpretation |
| Multimodal `loan_int_rate` | High | Requires business/temporal interpretation |

---

# 16. Statistical Outlier vs Data-Quality Error

A central lesson from the EDA is:

**Outlier does not automatically mean error.**

The correct reasoning process is:

```
Statistical anomaly
        ↓
Investigate
        ↓
Business validation
        ↓
 ┌───────────────┐
 │               │
Valid          Invalid
 │               │
Keep        Correct / Handle
```

This principle will guide the preprocessing stage.

---

# 17. EDA → Preprocessing Transition

The EDA phase is now essentially complete.

The next stage is **not immediately model training**.

We first need to transform the EDA findings into explicit preprocessing decisions.

The next stage will answer four major questions.

## 17.1 What Is an Actual Data-Quality Error?

Examples requiring decisions include:

- `person_age = 144`
- `person_age = 123`
- `person_emp_length = 123`
- extreme income values
- exact duplicates
- missing interest rates
- missing employment lengths
- potential ratio inconsistencies

The key principle is:

**Statistical unusualness ≠ data-quality error.**

---

## 17.2 What Is the Cleaning Policy?

We need to create a formal preprocessing specification.

The specification should document:

| Issue | Decision | Rationale | Processing |
|---|---|---|---|
| Exact duplicates | TBD | Duplicate records | TBD |
| Missing `loan_int_rate` | TBD | Missing values | TBD |
| Missing `person_emp_length` | TBD | Missing values | TBD |
| Invalid age | TBD | Business rule | TBD |
| Invalid employment length | TBD | Business rule | TBD |
| Extreme income | TBD | Requires validation | TBD |
| Ratio inconsistencies | TBD | Source/calculation rule | TBD |

No transformation should be implemented before the decision is documented.

---

# 18. Preprocessing vs Feature Engineering

We also need to separate two different responsibilities.

## Preprocessing

Preprocessing should deal with:

- data quality
- missing values
- duplicates
- invalid values
- data types
- category normalization
- validation rules
- transformations required for model compatibility

## Feature Engineering

Feature engineering should deal with:

- derived variables
- new ratios
- transformations motivated by modeling
- categorical encoding
- interactions
- domain-specific predictive features

This separation will become important when designing the ML pipeline.

---

# 19. Why We Started with the Monolithic Dataset

The original dataset was intentionally analyzed as a single dataset first.

This allowed us to understand:

- the complete schema
- data quality
- distributions
- relationships
- missingness
- anomalies
- target behavior
- business rules

Only after understanding the data should we simulate the data-engineering architecture.

---

# 20. Next Architectural Stage

After the preprocessing specification is defined, we will design the AWS data architecture.

The purpose of separating the original dataset into several business datasets is to simulate a realistic data lake/data integration scenario.

Conceptually:

```
Original Credit Risk Dataset
            ↓
          EDA
            ↓
     Data Quality Rules
            ↓
 Preprocessing Specification
            ↓
      Business Domains
            ↓
 ┌──────────┼──────────┐
 ↓          ↓          ↓
Applicant   Loan      Credit
 Data       Data      History
            ↓
       S3 Data Lake
            ↓
           Glue
            ↓
         Athena
            ↓
      SQL JOIN / Merge
            ↓
   Consolidated Dataset
            ↓
   ML Preprocessing
            ↓
      ML Pipeline
```

The AWS architecture should therefore be designed **after** the data-quality and preprocessing decisions, not before.

---

# 21. Final EDA Summary

The Credit Risk dataset contains meaningful structure but also several important data-quality concerns.

The most important findings are:

1. The dataset contains **32,581 observations and 12 variables**.
2. There are **165 exact duplicate records**.
3. `loan_int_rate` has approximately **9.56% missing values**.
4. `person_emp_length` has approximately **2.75% missing values**.
5. Several numerical variables are strongly right-skewed.
6. `person_income` contains an extremely long upper tail.
7. `person_age` contains suspicious extreme ages.
8. `person_emp_length` contains clearly suspicious values such as 123 years.
9. `loan_amnt` appears multimodal.
10. `loan_int_rate` appears multimodal.
11. `loan_percent_income` shows meaningful separation between default and non-default borrowers.
12. `loan_grade` shows a very strong relationship with default.
13. Previous default history is strongly associated with default.
14. Some categorical groups contain very few observations.
15. Statistical outliers must not automatically be removed.
16. Business-rule validation is required before final cleaning decisions.
17. Missing-value treatment must be explicitly defined.
18. Exact duplicate handling must be explicitly defined.
19. Preprocessing must be separated conceptually from feature engineering.
20. The AWS Glue/Athena architecture should be designed after the preprocessing specification is established.

---

# 22. EDA Stage Status

**EDA Status: Completed**

The next stage is:

**Data Quality Decisions → Preprocessing Specification → Preprocessing Design → AWS Data Architecture**

The next phase should begin by converting the EDA findings into explicit, documented preprocessing policies before implementing any cleaning logic.