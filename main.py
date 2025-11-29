"""
Main Execution Script
Orchestrates the complete analytics pipeline
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_processing import DataProcessor
from eda import EDAAnalyzer
from insights import InsightMiner
from models import ForecastingModel, RegressionModel, RecommendationSystem
from visualization import VisualizationGenerator

# Configuration
CONFIG = {
    'data_file': '10Alytics Hackathon- Fiscal Data.xlsx',
    'output_dir': 'reports',
    'plots_dir': 'reports/plots',
    'presentation_dir': 'presentation'
}


def setup_directories():
    """Create necessary directories"""
    for dir_path in [CONFIG['output_dir'], CONFIG['plots_dir'], CONFIG['presentation_dir']]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def main():
    """Main execution function"""
    print("=" * 80)
    print("FISCAL DATA ANALYTICS PIPELINE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Setup directories
    setup_directories()
    
    # Step 1: Load and Process Data
    print("Step 1: Loading and processing data...")
    processor = DataProcessor(CONFIG['data_file'])
    # Load the 'Data' sheet (not the 'Problem Statement' sheet)
    processed_data, processing_report = processor.process(sheet_name='Data')
    
    print(f"✓ Data loaded: {processed_data.shape[0]} rows × {processed_data.shape[1]} columns")
    print(f"✓ Processing complete\n")
    
    # Save processing report
    with open(f"{CONFIG['output_dir']}/data_processing_report.json", 'w') as f:
        json.dump(processing_report, f, indent=2, default=str)
    
    # Step 2: Exploratory Data Analysis
    print("Step 2: Performing Exploratory Data Analysis...")
    eda_analyzer = EDAAnalyzer(processed_data)
    eda_report = eda_analyzer.generate_eda_report(save_path=CONFIG['plots_dir'])
    
    print(f"✓ EDA complete")
    print(f"✓ Generated {len(eda_report['top_insights'])} key insights\n")
    
    # Save EDA report
    with open(f"{CONFIG['output_dir']}/eda_report.json", 'w') as f:
        json.dump(eda_report, f, indent=2, default=str)
    
    # Step 3: Advanced Insight Mining
    print("Step 3: Mining advanced insights...")
    insight_miner = InsightMiner(processed_data)
    high_value_insights = insight_miner.generate_high_value_insights()
    insights_summary = insight_miner.get_insights_summary()
    
    print(f"✓ Generated {len(high_value_insights)} high-value insights\n")
    
    # Save insights
    with open(f"{CONFIG['output_dir']}/insights_report.json", 'w') as f:
        json.dump(insights_summary, f, indent=2, default=str)
    
    # Step 4: Build Models
    print("Step 4: Building predictive models...")
    
    # Identify date and value columns
    date_cols = processed_data.select_dtypes(include=['datetime64']).columns.tolist()
    numeric_cols = processed_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    model_results = {}
    
    # Forecasting model (if date column exists)
    if date_cols and numeric_cols:
        try:
            date_col = date_cols[0]
            value_col = numeric_cols[0]
            forecast_model = ForecastingModel(processed_data, date_col, value_col)
            
            # Try Prophet
            if hasattr(forecast_model, 'forecast_with_prophet'):
                forecast_result = forecast_model.forecast_with_prophet(periods=12)
                if 'error' not in forecast_result:
                    model_results['forecasting'] = forecast_result
                    print(f"✓ Forecasting model (Prophet) trained")
        except Exception as e:
            print(f"⚠ Forecasting model skipped: {e}")
    
    # Regression model
    if len(numeric_cols) >= 2:
        try:
            reg_model = RegressionModel(processed_data)
            target = numeric_cols[0]
            features = numeric_cols[1:min(6, len(numeric_cols))]
            
            reg_result = reg_model.train_regression_model(
                target_column=target,
                feature_columns=features,
                model_type='random_forest'
            )
            
            if 'error' not in reg_result:
                model_results['regression'] = reg_result
                print(f"✓ Regression model trained (R² = {reg_result['test_metrics']['r2']:.3f})")
        except Exception as e:
            print(f"⚠ Regression model skipped: {e}")
    
    # Save model results
    with open(f"{CONFIG['output_dir']}/model_results.json", 'w') as f:
        json.dump(model_results, f, indent=2, default=str)
    
    print()
    
    # Step 5: Generate Visualizations
    print("Step 5: Generating visualizations...")
    viz_generator = VisualizationGenerator(processed_data)
    
    date_col = date_cols[0] if date_cols else None
    value_cols = numeric_cols[:5] if numeric_cols else []
    
    visualizations = viz_generator.generate_all_visualizations(
        date_column=date_col,
        value_columns=value_cols,
        save_path=CONFIG['plots_dir']
    )
    
    print(f"✓ Generated {len(visualizations)} visualization sets\n")
    
    # Step 6: Generate Recommendations
    print("Step 6: Generating recommendations...")
    if numeric_cols:
        rec_system = RecommendationSystem(processed_data)
        recommendations = rec_system.generate_recommendations(
            target_metric=numeric_cols[0]
        )
        
        with open(f"{CONFIG['output_dir']}/recommendations.json", 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print(f"✓ Generated {len(recommendations)} recommendations\n")
    
    # Step 7: Generate Summary Report
    print("Step 7: Generating summary report...")
    generate_summary_report(processed_data, eda_report, high_value_insights, 
                          model_results, CONFIG['output_dir'])
    print("✓ Summary report generated\n")
    
    print("=" * 80)
    print("PIPELINE COMPLETE!")
    print("=" * 80)
    print(f"All outputs saved to: {CONFIG['output_dir']}/")
    print(f"Visualizations saved to: {CONFIG['plots_dir']}/")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def generate_summary_report(df, eda_report, insights, model_results, output_dir):
    """Generate executive summary report"""
    report = f"""
# FISCAL DATA ANALYTICS - EXECUTIVE SUMMARY

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Overview
- **Total Records**: {len(df):,}
- **Total Features**: {len(df.columns)}
- **Numeric Features**: {len(df.select_dtypes(include=['float64', 'int64']).columns)}
- **Categorical Features**: {len(df.select_dtypes(include=['object']).columns)}

## Key Insights

### Top 10 Non-Obvious Insights

"""
    
    for i, insight in enumerate(eda_report.get('top_insights', [])[:10], 1):
        report += f"""
{i}. **{insight.get('category', 'General')}**: {insight.get('insight', 'N/A')}
   - Impact: {insight.get('impact', 'N/A')}
"""
    
    report += f"""

## High-Value Insights

"""
    
    for insight in insights:
        report += f"""
### {insight.get('title', 'Insight')}
- **Category**: {insight.get('category', 'N/A')}
- **Description**: {insight.get('description', 'N/A')}
- **Business Impact**: {insight.get('business_impact', 'N/A')}
"""
    
    report += f"""

## Model Performance

"""
    
    if 'regression' in model_results:
        reg = model_results['regression']
        report += f"""
### Regression Model
- **Model Type**: {reg.get('model_type', 'N/A')}
- **Target**: {reg.get('target_column', 'N/A')}
- **Test R² Score**: {reg.get('test_metrics', {}).get('r2', 0):.3f}
- **Test RMSE**: {reg.get('test_metrics', {}).get('rmse', 0):.3f}
"""
    
    if 'forecasting' in model_results:
        forecast = model_results['forecasting']
        report += f"""
### Forecasting Model
- **Method**: {forecast.get('method', 'N/A')}
- **Forecast Periods**: {forecast.get('forecast_periods', 'N/A')}
- **RMSE**: {forecast.get('metrics', {}).get('rmse', 0):.3f}
"""
    
    with open(f"{output_dir}/executive_summary.md", 'w') as f:
        f.write(report)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

