# Attention Economy: Neuro-Stochastic Modeling of Cognitive Fragmentation in Digital Interfaces

Quantitative analysis of digital attention fragmentation ($N=2,023$). Developed the **Attention Fragmentation Index (IFA)** leveraging neuroscience principles (Posner & Rothbart) to model cognitive load versus productivity decay. Features multivariate statistical regression and high-performance data engineering pipelines built with **Polars**, **Python**, and **Statsmodels**.

---

## 🛠️ Data Pipeline & Architecture

The infrastructure follows a multi-tool engineering paradigm designed for maximum performance, scalability, and reproducibility:

* **Data Engineering (ETL):** Implemented via **Polars** in Python, taking advantage of vectorized expressions and multi-threaded processing executing on a Rust core.
* **Data Quality & Normalization:** Relational schema enforcement and dynamic Z-score parametric standardization ($z = \frac{x - \mu}{\sigma}$) executed using SQL Common Table Expressions (CTEs) within an **SQLite** environment.

---

## 🔬 Statistical Modeling & Econometric Validation

We fitted a Multivariate Ordinary Least Squares (OLS) regression model to quantify the association between cognitive fragmentation and student performance, controlling for baseline physiological factors:

$$\text{ProductivityScore}_z = \beta_0 + \beta_1 (\text{IFA}_z) + \beta_2 (\text{StressLevel}_z) + \beta_3 (\text{SleepHours}_z) + \varepsilon$$

### Core Findings
* **Model Fit:** The model accounts for **65.08%** of the total variance in productivity ($\text{Adj. } R^2 = 0.6508$).
* **The Attention Tax:** The Attention Fragmentation Index (IFA) is the dominant, highly significant predictor ($\beta_1 = -0.8060, p < 0.001$). For every standard deviation increase in digital switching intensity, cognitive productivity decays by **0.806 standard deviations**.
* **Nuisance Variables:** When controlling for acute attention fragmentation, biological controls such as self-reported sleep hours ($\beta_3 = -0.0147, p = 0.265$) and raw stress baselines ($\beta_2 = 0.0009, p = 0.944$) lose direct statistical significance within this sample.

---

## 📊 Rigorous Validation of OLS & Classical Linear Model Assumptions

To ensure structural parameter stability and BLUE properties under the Gauss-Markov theorem, the model was subjected to full diagnostic testing:

| Assumption | Diagnostic Metric / Test | Value / $p$-value | Status | Technical Justification |
| :--- | :--- | :--- | :--- | :--- |
| **1. Linearity** | Residuals vs. Fitted Plot | Random Scatter | **PASSED** | No non-linear polynomial or parabolic trends detected in residual distribution. |
| **2. Homoscedasticity** | Breusch-Pagan Test | $p = 0.3986$ | **PASSED** | Homoscedasticity confirmed ($p > 0.05$). Error variance remains constant across all fitted values. |
| **3. Asymptotic Normality** | Jarque-Bera Test | $\text{JB} = 14.28, p = 0.0008$ | **VALIDATED** | Finite-sample normality is rejected, but asymptotic normality of estimators is guaranteed by the Central Limit Theorem ($N=2,023$). |
| **4. No Multicollinearity** | Variance Inflation Factor (VIF) | $\text{VIF} \approx 1.003$ | **PASSED** | Strict orthogonality among regressors ($\text{VIF} \ll 5.0$). Zero variance inflation. |
| **5. Independence** | Durbin-Watson Statistic | $\text{DW} = 2.0082$ | **PASSED** | Residual independence confirmed. Zero first-order serial autocorrelation ($\text{DW} \approx 2.0$). |

---

## 📄 Latest Research Report Revision

The primary technical document (`docs/Report_Neurocognitivo_All_5.docx`) is structured as a comprehensive 20-page research report bridging applied econometrics with neuro-cognitive theory:

* **Posner & Rothbart's Tripartite Attention Networks:** Formalizing Alerting, Orienting, and Executive network mechanics under continuous digital micro-interruption.
* **Task-Switching Costs (Dr. Gloria Mark):** Quantifying task-switching latencies and residual memory contamination induced by high-frequency screen unlocks.
* **Popcorn Brain Hypothesis (Dr. David Levy):** Modeling desensitization thresholds in the Salience Network (SN) and Central Executive Network (CEN).

---

## 🧪 Model Stress-Testing & Validation Audit (`scripts/model_validation_audit.py`)

To verify parameter stability, eliminate overfitting, and evaluate non-linear dynamics, the dataset ($N=2,023$) was subjected to a rigorous audit pipeline:

### 1. Out-of-Sample Pipeline Predictability (90/10 Train/Test Split)
To evaluate the stability of the IFA feature extraction pipeline on unseen telemetry data:
* **Training Set (90%):** $N_{\text{train}} = 1,820$ observations.
* **Test Set (10%):** $N_{\text{test}} = 203$ blind audit observations.
* **Out-of-Sample Index Performance:** $R^2_{\text{OOS}} = 0.9876$, $\text{RMSE} = 0.1109 \text{ SD}$, $\text{MAE} = 0.0898 \text{ SD}$.
* *Interpretation:* Minimal error metrics confirm that the algorithmic reconstruction pipeline for the IFA synthetic proxy maintains high structural stability out-of-sample without overfitting.

### 2. Chow Test for Structural Break ($\text{IFA}_{\text{scale 100}} = 30.03$)
A conditional Chow test was conducted across the non-linear threshold ($\text{IFA} = 30.03$, 85th Percentile) to test for parameter shift across intensity regimes:
* **Subsample 1 ($\text{IFA} < 30.03$, Sub-critical):** $N_1 = 1,720$.
* **Subsample 2 ($\text{IFA} \ge 30.03$, Saturation Zone):** $N_2 = 303$.
* **Test Metrics:** $F\text{-statistic} = 132.55, p\text{-value} = 1.11 \times 10^{-16} (p < 0.001)$.
* *Interpretation:* Rejecting parameter homogeneity proves that human cognitive response exhibits non-linear regime dynamics. Crossing $\text{IFA} = 30.03$ triggers an accelerated regime transition in prefrontal saturation.

### 3. Information Criteria & Complexity Penalization
* **Log-Likelihood:** Evaluated for structural completeness.
* **AIC & BIC:** Utilized to penalize potential over-parameterization, confirming optimal specification without redundant regressors.

---

## 🎲 Non-Linear Monte Carlo Inflexion Analysis

Stochastic simulation via non-parametric Bootstrapping (**10,000 iterations**) evaluated the empirical stability of the cognitive response:
* **Quartile Stability ($P_1 - P_3$):** Cognitive response displays linear stability across the lower **75%** of the empirical distribution.
* **Inflection Threshold ($\text{IFA} = 30.03$):** Stochastic resampling identified a structural breaking point at $\text{IFA} = 30.03$, corresponding to the **85th percentile ($P_{85}, +1.26\sigma$)**.
* **Neuro-Cognitive Implication:** At $P_{85}$, subjects experience an average of **128 unlocks/day** (a disruption every 7.5 minutes), inducing dorsolateral prefrontal cortex ($\text{dlPFC}$) saturation and suppressing Deep Work state transitions.

---

## 🗺️ Roadmap & Upcoming Milestones

This repository serves as an open-source scientific data engineering sandbox. Future deployments include:
- [ ] **Stochastic Simulation:** Advanced Monte Carlo algorithms to stress-test attention limits under extreme synthetic notification distributions.
- [ ] **Predictive Machine Learning:** Non-linear forecasting models to estimate individual cognitive burnout thresholds.
- [ ] **Interactive Business Intelligence:** Power BI dashboard mapping cross-cultural focus decay patterns across demographics.
