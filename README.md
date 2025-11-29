# Fiscal Intelligence Analytics Platform

**A comprehensive analytics solution for transforming fiscal data into actionable intelligence, advancing 8 UN Sustainable Development Goals**

---

## Overview

This platform provides an end-to-end analytics pipeline for fiscal data analysis, from raw data ingestion to actionable insights and recommendations. Built for the 10Alytics Global Hackathon, it analyzes $69 billion in fiscal data across 14 African countries over 65 years, generating data-driven insights that directly advance Sustainable Development Goals (SDGs 1, 2, 3, 4, 8, 9, 10, 16).

## Key Features

- **Automated Data Processing**: Intelligent cleaning, standardization, and preprocessing
- **Comprehensive EDA**: Distribution analysis, correlations, trends, and outlier detection
- **Advanced Analytics**: Clustering, anomaly detection, feature engineering, hypothesis testing
- **Predictive Models**: Time series forecasting (Prophet, ARIMA), regression, classification
- **Interactive Visualizations**: Professional dashboards using matplotlib, seaborn, and plotly
- **Data-Driven Recommendations**: Actionable policy and financial recommendations
- **SDG Alignment**: Explicit connections to 8 UN Sustainable Development Goals

## Project Structure

```
.
├── main.py                          # Main execution script
├── requirements.txt                 # Python dependencies
├── 10Alytics Hackathon- Fiscal Data.xlsx  # Dataset
├── src/                             # Source code modules
│   ├── data_processing.py          # Data loading and cleaning
│   ├── eda.py                      # Exploratory data analysis
│   ├── insights.py                 # Advanced insight mining
│   ├── models.py                   # Predictive models
│   └── visualization.py            # Visualization generation
├── reports/                         # Generated reports and analysis
│   ├── EXECUTIVE_SUMMARY.md       # Executive summary
│   ├── INNOVATION_SECTION.md      # Innovation highlights
│   ├── IMPACT_SECTION.md          # Real-world impact
│   ├── DATASET_SPECIFIC_INSIGHTS.md # Key insights from analysis
│   ├── DATA_DRIVEN_RECOMMENDATIONS.md # Actionable recommendations
│   ├── SDG_ALIGNMENT.md           # SDG alignment documentation
│   └── plots/                      # Generated visualizations
│       ├── trend_dashboard.html   # Interactive dashboard
│       ├── distribution_amount.png
│       ├── outlier_detection.png
│       └── static/                # Static image exports
├── notebooks/                       # Jupyter notebooks
│   └── 01_Quick_Start.ipynb       # Quick start guide
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/dogahwisdom/10Alytics-WisdomDogah-FiscalIntelligence.git
cd 10Alytics-WisdomDogah-FiscalIntelligence

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Run the complete analytics pipeline
python main.py
```

This will:
1. Load and process the fiscal data
2. Perform comprehensive exploratory data analysis
3. Mine advanced insights using clustering and anomaly detection
4. Build predictive models (forecasting, regression, classification)
5. Generate interactive visualizations and dashboards
6. Create comprehensive reports and recommendations

### Viewing Results

- **Reports**: All markdown reports are in `reports/` directory
- **Visualizations**: 
  - Interactive dashboard: `reports/plots/trend_dashboard.html` (open in browser)
  - Static images: `reports/plots/static/`
- **Analysis Results**: JSON files in `reports/` contain detailed analysis data

## Key Insights

The platform generates several categories of insights:

1. **Dataset-Specific Insights**: 8 key findings from the fiscal data analysis
2. **High-Value Insights**: Discovered through advanced analytics (clustering, anomaly detection)
3. **Predictive Forecasts**: Future trends with confidence intervals
4. **Actionable Recommendations**: Data-driven policy and financial recommendations aligned with SDGs

## Usage Examples

### Basic Data Processing

```python
from src.data_processing import DataProcessor

# Load and process data
processor = DataProcessor('10Alytics Hackathon- Fiscal Data.xlsx')
processed_data, report = processor.process(sheet_name='Data')
```

### Exploratory Data Analysis

```python
from src.eda import EDAAnalyzer

# Perform comprehensive EDA
eda_analyzer = EDAAnalyzer(processed_data)
eda_report = eda_analyzer.generate_eda_report(save_path='reports/plots')
```

### Advanced Insights

```python
from src.insights import InsightMiner

# Mine high-value insights
insight_miner = InsightMiner(processed_data)
insights = insight_miner.generate_high_value_insights()
```

### Predictive Modeling

```python
from src.models import ForecastingModel, RegressionModel

# Time series forecasting
forecast_model = ForecastingModel(df, 'date_column', 'value_column')
forecast_result = forecast_model.forecast_with_prophet(periods=12)

# Regression analysis
reg_model = RegressionModel(df)
reg_result = reg_model.train_regression_model(
    target_column='target',
    feature_columns=['feature1', 'feature2'],
    model_type='random_forest'
)
```

## Technologies

- **Python 3.x**: Core programming language
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning algorithms
- **Prophet**: Time series forecasting
- **statsmodels**: Statistical modeling
- **matplotlib/seaborn**: Static visualizations
- **plotly**: Interactive visualizations
- **jupyter**: Interactive notebooks

## Architecture

- **Modular Design**: Each module has a single, well-defined responsibility
- **Object-Oriented**: Clean classes with clear interfaces
- **Scalable**: Handles datasets of varying sizes efficiently
- **Extensible**: Easy to add new features and models
- **Production-Ready**: Comprehensive error handling and validation

## SDG Alignment

This project directly advances 8 UN Sustainable Development Goals:

- **SDG 1** (No Poverty): Better fiscal data enables improved poverty reduction programs
- **SDG 2** (Zero Hunger): Improved resource allocation supports food security
- **SDG 3** (Good Health): Data-driven health spending decisions
- **SDG 4** (Quality Education): Better education budget allocation
- **SDG 8** (Decent Work & Economic Growth): Predictive analytics for economic planning
- **SDG 9** (Industry, Innovation, Infrastructure): Data-driven infrastructure investment
- **SDG 10** (Reduced Inequalities): More equitable resource distribution
- **SDG 16** (Peace, Justice, Strong Institutions): Transparent, data-driven governance

## Documentation

Comprehensive documentation is available:

- **Executive Summary**: `reports/EXECUTIVE_SUMMARY.md`
- **Innovation Details**: `reports/INNOVATION_SECTION.md`
- **Impact Analysis**: `reports/IMPACT_SECTION.md`
- **SDG Alignment**: `reports/SDG_ALIGNMENT.md`
- **Key Insights**: `reports/DATASET_SPECIFIC_INSIGHTS.md`
- **Recommendations**: `reports/DATA_DRIVEN_RECOMMENDATIONS.md`

## Evaluation Criteria Compliance

This project meets all hackathon evaluation criteria:

- ✅ **Understandability**: Clear problem framing and dataset-specific context
- ✅ **Innovativeness**: Advanced techniques (clustering, anomaly detection, feature engineering)
- ✅ **Impactfulness**: Data-driven recommendations with SDG alignment
- ✅ **Applicability**: Production-ready code with comprehensive documentation

See `CRITERIA_COMPLIANCE_REPORT.md` for detailed assessment.

## Contact

**Wisdom Dogah**  
Email: wisdomdogah@outlook.com  
Phone: (+233) 54-254-7949  
GitHub: [github.com/dogahwisdom/10Alytics-WisdomDogah-FiscalIntelligence](https://github.com/dogahwisdom/10Alytics-WisdomDogah-FiscalIntelligence)

## License

This project was developed for the 10Alytics Global Hackathon.

---

**Built for the 10Alytics Global Hackathon | Transforming fiscal data into actionable intelligence**
