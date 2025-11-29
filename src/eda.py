"""
Exploratory Data Analysis Module
Provides comprehensive EDA capabilities including distributions, correlations, trends, and outliers
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class EDAAnalyzer:
    """Comprehensive EDA analysis class"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize EDA Analyzer
        
        Args:
            df: DataFrame to analyze
        """
        self.df = df.copy()
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        self.datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        self.insights: List[Dict] = []
    
    def get_basic_statistics(self) -> Dict:
        """
        Get basic statistical summary
        
        Returns:
            Dictionary with statistical summaries
        """
        stats = {
            'shape': self.df.shape,
            'numeric_summary': self.df[self.numeric_cols].describe().to_dict() if self.numeric_cols else {},
            'categorical_summary': {},
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024**2
        }
        
        # Categorical summary
        for col in self.categorical_cols:
            stats['categorical_summary'][col] = {
                'unique_count': self.df[col].nunique(),
                'top_values': self.df[col].value_counts().head(5).to_dict(),
                'mode': self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else None
            }
        
        return stats
    
    def analyze_distributions(self, save_path: Optional[str] = None) -> Dict:
        """
        Analyze and plot distributions of numeric columns
        
        Args:
            save_path: Path to save plots
        
        Returns:
            Dictionary with distribution statistics
        """
        distribution_stats = {}
        
        for col in self.numeric_cols:
            data = self.df[col].dropna()
            
            # Calculate distribution metrics
            skewness = data.skew()
            kurtosis = data.kurtosis()
            
            distribution_stats[col] = {
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'skewness': skewness,
                'kurtosis': kurtosis,
                'distribution_type': self._classify_distribution(skewness, kurtosis)
            }
            
            # Create distribution plot
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            # Histogram with KDE
            axes[0].hist(data, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
            axes[0].axvline(data.mean(), color='red', linestyle='--', label=f'Mean: {data.mean():.2f}')
            axes[0].axvline(data.median(), color='green', linestyle='--', label=f'Median: {data.median():.2f}')
            axes[0].set_title(f'Distribution of {col}', fontsize=12, fontweight='bold')
            axes[0].set_xlabel(col)
            axes[0].set_ylabel('Frequency')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # Q-Q plot for normality check
            from scipy import stats as scipy_stats
            scipy_stats.probplot(data, dist="norm", plot=axes[1])
            axes[1].set_title(f'Q-Q Plot: {col}', fontsize=12, fontweight='bold')
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(f"{save_path}/distribution_{col}.png", dpi=300, bbox_inches='tight')
            
            plt.close()
        
        return distribution_stats
    
    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """Classify distribution based on skewness and kurtosis"""
        if abs(skewness) < 0.5:
            if abs(kurtosis) < 0.5:
                return "Approximately Normal"
            else:
                return "Normal with heavy/light tails"
        elif skewness > 0.5:
            return "Right-skewed (positive skew)"
        else:
            return "Left-skewed (negative skew)"
    
    def analyze_correlations(self, save_path: Optional[str] = None) -> pd.DataFrame:
        """
        Analyze correlations between numeric variables
        
        Args:
            save_path: Path to save correlation heatmap
        
        Returns:
            Correlation matrix DataFrame
        """
        if len(self.numeric_cols) < 2:
            return pd.DataFrame()
        
        corr_matrix = self.df[self.numeric_cols].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Heatmap of Numeric Variables', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}/correlation_heatmap.png", dpi=300, bbox_inches='tight')
        
        plt.close()
        
        # Find strong correlations
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corrs.append({
                        'variable1': corr_matrix.columns[i],
                        'variable2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        if strong_corrs:
            self.insights.append({
                'type': 'strong_correlation',
                'description': f'Found {len(strong_corrs)} strong correlations (|r| > 0.7)',
                'details': strong_corrs
            })
        
        return corr_matrix
    
    def analyze_trends(self, date_column: Optional[str] = None, 
                      value_columns: Optional[List[str]] = None,
                      save_path: Optional[str] = None) -> Dict:
        """
        Analyze time-based trends
        
        Args:
            date_column: Name of date column
            value_columns: List of columns to analyze trends for
            save_path: Path to save trend plots
        
        Returns:
            Dictionary with trend analysis results
        """
        trend_results = {}
        
        if date_column and date_column in self.df.columns:
            if value_columns is None:
                value_columns = self.numeric_cols[:5]  # Analyze top 5 numeric columns
            
            for col in value_columns:
                if col in self.df.columns:
                    # Create trend plot
                    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
                    
                    # Time series plot
                    axes[0].plot(self.df[date_column], self.df[col], linewidth=2, color='steelblue')
                    axes[0].set_title(f'Trend Analysis: {col} over Time', fontsize=12, fontweight='bold')
                    axes[0].set_xlabel('Date')
                    axes[0].set_ylabel(col)
                    axes[0].grid(True, alpha=0.3)
                    
                    # Rolling average
                    if len(self.df) > 12:
                        window = min(12, len(self.df) // 4)
                        rolling_mean = self.df[col].rolling(window=window).mean()
                        axes[0].plot(self.df[date_column], rolling_mean, 
                                   color='red', linestyle='--', linewidth=2, label=f'{window}-period moving average')
                        axes[0].legend()
                    
                    # Monthly/Yearly aggregation if applicable
                    try:
                        self.df['year'] = pd.to_datetime(self.df[date_column]).dt.year
                        yearly_agg = self.df.groupby('year')[col].agg(['mean', 'sum'])
                        
                        axes[1].bar(yearly_agg.index, yearly_agg['mean'], color='steelblue', alpha=0.7)
                        axes[1].set_title(f'Yearly Average: {col}', fontsize=12, fontweight='bold')
                        axes[1].set_xlabel('Year')
                        axes[1].set_ylabel(f'Average {col}')
                        axes[1].grid(True, alpha=0.3, axis='y')
                    except:
                        pass
                    
                    plt.tight_layout()
                    
                    if save_path:
                        plt.savefig(f"{save_path}/trend_{col}.png", dpi=300, bbox_inches='tight')
                    
                    plt.close()
                    
                    # Calculate trend statistics
                    trend_results[col] = {
                        'mean': self.df[col].mean(),
                        'std': self.df[col].std(),
                        'min': self.df[col].min(),
                        'max': self.df[col].max(),
                        'trend_direction': self._calculate_trend_direction(self.df[col])
                    }
        
        return trend_results
    
    def _calculate_trend_direction(self, series: pd.Series) -> str:
        """Calculate overall trend direction"""
        if len(series) < 2:
            return "Insufficient data"
        
        # Simple linear regression slope
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        
        if slope > 0:
            return "Increasing"
        elif slope < 0:
            return "Decreasing"
        else:
            return "Stable"
    
    def detect_outliers(self, method: str = 'iqr') -> Dict:
        """
        Detect outliers using multiple methods
        
        Args:
            method: 'iqr' or 'zscore'
        
        Returns:
            Dictionary with outlier information
        """
        outlier_results = {}
        
        for col in self.numeric_cols:
            data = self.df[col].dropna()
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            elif method == 'zscore':
                z_scores = np.abs((data - data.mean()) / data.std())
                outliers = data[z_scores > 3]
            
            outlier_results[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(data)) * 100,
                'outlier_values': outliers.tolist()[:10]  # Top 10 outliers
            }
        
        return outlier_results
    
    def analyze_seasonality(self, date_column: Optional[str] = None,
                           value_column: Optional[str] = None) -> Dict:
        """
        Analyze seasonal patterns
        
        Args:
            date_column: Name of date column
            value_column: Name of value column to analyze
        
        Returns:
            Dictionary with seasonality analysis
        """
        if not date_column or date_column not in self.df.columns:
            return {}
        
        if value_column is None and self.numeric_cols:
            value_column = self.numeric_cols[0]
        
        if not value_column or value_column not in self.df.columns:
            return {}
        
        try:
            df_temp = self.df[[date_column, value_column]].copy()
            df_temp[date_column] = pd.to_datetime(df_temp[date_column])
            df_temp['month'] = df_temp[date_column].dt.month
            df_temp['quarter'] = df_temp[date_column].dt.quarter
            df_temp['year'] = df_temp[date_column].dt.year
            
            seasonality = {
                'monthly_pattern': df_temp.groupby('month')[value_column].mean().to_dict(),
                'quarterly_pattern': df_temp.groupby('quarter')[value_column].mean().to_dict(),
                'yearly_pattern': df_temp.groupby('year')[value_column].mean().to_dict()
            }
            
            return seasonality
        except Exception as e:
            return {'error': str(e)}
    
    def generate_top_insights(self, top_n: int = 10) -> List[Dict]:
        """
        Generate top non-obvious insights from EDA
        
        Args:
            top_n: Number of insights to generate
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Insight 1: Data quality
        missing_pct = (self.df.isnull().sum().sum() / (self.df.shape[0] * self.df.shape[1])) * 100
        if missing_pct > 10:
            insights.append({
                'rank': 1,
                'category': 'Data Quality',
                'insight': f'Dataset has {missing_pct:.1f}% missing values, indicating potential data collection gaps',
                'impact': 'High - affects reliability of analysis'
            })
        
        # Insight 2: Distribution patterns
        for col in self.numeric_cols[:3]:
            skew = self.df[col].skew()
            if abs(skew) > 1:
                insights.append({
                    'rank': len(insights) + 1,
                    'category': 'Distribution',
                    'insight': f'{col} shows significant skewness ({skew:.2f}), indicating non-normal distribution',
                    'impact': 'Medium - may require transformation for modeling'
                })
        
        # Insight 3: Correlation insights
        if len(self.numeric_cols) >= 2:
            corr_matrix = self.df[self.numeric_cols].corr()
            max_corr = corr_matrix.unstack().sort_values(ascending=False)
            max_corr = max_corr[max_corr < 1.0].iloc[0]
            if abs(max_corr) > 0.8:
                pair = max_corr.index
                insights.append({
                    'rank': len(insights) + 1,
                    'category': 'Relationships',
                    'insight': f'Strong correlation ({max_corr:.2f}) between {pair[0]} and {pair[1]}',
                    'impact': 'High - potential multicollinearity or causal relationship'
                })
        
        # Add more insights based on specific patterns found
        # ... (additional insight generation logic)
        
        return insights[:top_n]
    
    def generate_eda_report(self, save_path: Optional[str] = None) -> Dict:
        """
        Generate comprehensive EDA report
        
        Args:
            save_path: Path to save plots and report
        
        Returns:
            Dictionary with complete EDA report
        """
        report = {
            'basic_statistics': self.get_basic_statistics(),
            'distributions': self.analyze_distributions(save_path),
            'correlations': self.analyze_correlations(save_path),
            'outliers': self.detect_outliers(),
            'top_insights': self.generate_top_insights(10)
        }
        
        return report

