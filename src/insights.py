"""
Advanced Insight Mining Module
Provides clustering, anomaly detection, feature engineering, and hypothesis testing
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from scipy import stats
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Handles feature engineering operations"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize FeatureEngineer
        
        Args:
            df: DataFrame to engineer features from
        """
        self.df = df.copy()
        self.engineered_features: List[str] = []
    
    def create_time_features(self, date_column: str) -> pd.DataFrame:
        """
        Create time-based features
        
        Args:
            date_column: Name of date column
        
        Returns:
            DataFrame with time features added
        """
        if date_column not in self.df.columns:
            return self.df
        
        try:
            self.df[date_column] = pd.to_datetime(self.df[date_column])
            
            self.df['year'] = self.df[date_column].dt.year
            self.df['month'] = self.df[date_column].dt.month
            self.df['quarter'] = self.df[date_column].dt.quarter
            self.df['day_of_week'] = self.df[date_column].dt.dayofweek
            self.df['day_of_year'] = self.df[date_column].dt.dayofyear
            self.df['is_weekend'] = (self.df['day_of_week'] >= 5).astype(int)
            
            self.engineered_features.extend(['year', 'month', 'quarter', 'day_of_week', 
                                           'day_of_year', 'is_weekend'])
        except Exception as e:
            print(f"Error creating time features: {e}")
        
        return self.df
    
    def create_lag_features(self, columns: List[str], lags: List[int] = [1, 3, 6, 12]) -> pd.DataFrame:
        """
        Create lag features for time series
        
        Args:
            columns: List of column names to create lags for
            lags: List of lag periods
        
        Returns:
            DataFrame with lag features added
        """
        for col in columns:
            if col in self.df.columns:
                for lag in lags:
                    lag_col_name = f'{col}_lag_{lag}'
                    self.df[lag_col_name] = self.df[col].shift(lag)
                    self.engineered_features.append(lag_col_name)
        
        return self.df
    
    def create_rolling_features(self, columns: List[str], windows: List[int] = [3, 6, 12]) -> pd.DataFrame:
        """
        Create rolling window features
        
        Args:
            columns: List of column names
            windows: List of window sizes
        
        Returns:
            DataFrame with rolling features added
        """
        for col in columns:
            if col in self.df.columns:
                for window in windows:
                    # Rolling mean
                    self.df[f'{col}_rolling_mean_{window}'] = self.df[col].rolling(window=window).mean()
                    # Rolling std
                    self.df[f'{col}_rolling_std_{window}'] = self.df[col].rolling(window=window).std()
                    # Rolling max
                    self.df[f'{col}_rolling_max_{window}'] = self.df[col].rolling(window=window).max()
                    # Rolling min
                    self.df[f'{col}_rolling_min_{window}'] = self.df[col].rolling(window=window).min()
                    
                    self.engineered_features.extend([
                        f'{col}_rolling_mean_{window}',
                        f'{col}_rolling_std_{window}',
                        f'{col}_rolling_max_{window}',
                        f'{col}_rolling_min_{window}'
                    ])
        
        return self.df
    
    def create_ratio_features(self, numerator_cols: List[str], 
                             denominator_cols: List[str]) -> pd.DataFrame:
        """
        Create ratio features
        
        Args:
            numerator_cols: List of numerator columns
            denominator_cols: List of denominator columns
        
        Returns:
            DataFrame with ratio features added
        """
        for num_col in numerator_cols:
            for den_col in denominator_cols:
                if num_col in self.df.columns and den_col in self.df.columns:
                    ratio_name = f'{num_col}_to_{den_col}_ratio'
                    self.df[ratio_name] = self.df[num_col] / (self.df[den_col] + 1e-6)  # Avoid division by zero
                    self.engineered_features.append(ratio_name)
        
        return self.df
    
    def create_interaction_features(self, columns: List[str]) -> pd.DataFrame:
        """
        Create interaction features (multiplication)
        
        Args:
            columns: List of columns to create interactions for
        
        Returns:
            DataFrame with interaction features added
        """
        for i, col1 in enumerate(columns):
            for col2 in columns[i+1:]:
                if col1 in self.df.columns and col2 in self.df.columns:
                    interaction_name = f'{col1}_x_{col2}'
                    self.df[interaction_name] = self.df[col1] * self.df[col2]
                    self.engineered_features.append(interaction_name)
        
        return self.df


class ClusteringAnalyzer:
    """Performs clustering analysis"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize ClusteringAnalyzer
        
        Args:
            df: DataFrame to cluster
        """
        self.df = df.copy()
        self.scaler = StandardScaler()
        self.clusters: Optional[np.ndarray] = None
    
    def perform_kmeans_clustering(self, n_clusters: int = 3, 
                                  columns: Optional[List[str]] = None) -> Dict:
        """
        Perform K-Means clustering
        
        Args:
            n_clusters: Number of clusters
            columns: Columns to use for clustering (default: all numeric)
        
        Returns:
            Dictionary with clustering results
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Prepare data
        X = self.df[columns].dropna()
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Add clusters to dataframe
        cluster_df = X.copy()
        cluster_df['cluster'] = clusters
        
        # Analyze clusters
        cluster_analysis = {}
        for cluster_id in range(n_clusters):
            cluster_data = cluster_df[cluster_df['cluster'] == cluster_id]
            cluster_analysis[f'cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'percentage': (len(cluster_data) / len(cluster_df)) * 100,
                'characteristics': cluster_data[columns].mean().to_dict(),
                'std': cluster_data[columns].std().to_dict()
            }
        
        self.clusters = clusters
        
        return {
            'method': 'K-Means',
            'n_clusters': n_clusters,
            'inertia': kmeans.inertia_,
            'cluster_analysis': cluster_analysis,
            'cluster_labels': clusters.tolist()
        }
    
    def perform_dbscan_clustering(self, eps: float = 0.5, min_samples: int = 5,
                                  columns: Optional[List[str]] = None) -> Dict:
        """
        Perform DBSCAN clustering for anomaly detection
        
        Args:
            eps: Maximum distance between samples
            min_samples: Minimum samples in a neighborhood
            columns: Columns to use for clustering
        
        Returns:
            Dictionary with clustering results
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Prepare data
        X = self.df[columns].dropna()
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(X_scaled)
        
        # Analyze clusters
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        n_noise = list(clusters).count(-1)
        
        cluster_analysis = {
            'method': 'DBSCAN',
            'n_clusters': n_clusters,
            'n_noise_points': n_noise,
            'noise_percentage': (n_noise / len(clusters)) * 100 if len(clusters) > 0 else 0
        }
        
        self.clusters = clusters
        
        return cluster_analysis


class AnomalyDetector:
    """Detects anomalies in the data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize AnomalyDetector
        
        Args:
            df: DataFrame to analyze
        """
        self.df = df.copy()
    
    def detect_with_isolation_forest(self, contamination: float = 0.1,
                                   columns: Optional[List[str]] = None) -> Dict:
        """
        Detect anomalies using Isolation Forest
        
        Args:
            contamination: Expected proportion of anomalies
            columns: Columns to use for detection
        
        Returns:
            Dictionary with anomaly detection results
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Prepare data
        X = self.df[columns].dropna()
        
        # Detect anomalies
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomalies = iso_forest.fit_predict(X)
        
        # Convert to binary (1 = normal, -1 = anomaly)
        anomaly_mask = anomalies == -1
        
        return {
            'method': 'Isolation Forest',
            'n_anomalies': anomaly_mask.sum(),
            'anomaly_percentage': (anomaly_mask.sum() / len(anomalies)) * 100,
            'anomaly_indices': X[anomaly_mask].index.tolist(),
            'anomaly_scores': iso_forest.score_samples(X).tolist()
        }
    
    def detect_statistical_anomalies(self, columns: Optional[List[str]] = None,
                                    threshold: float = 3.0) -> Dict:
        """
        Detect anomalies using statistical methods (Z-score)
        
        Args:
            columns: Columns to analyze
            threshold: Z-score threshold
        
        Returns:
            Dictionary with anomaly detection results
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        anomaly_results = {}
        
        for col in columns:
            if col in self.df.columns:
                data = self.df[col].dropna()
                z_scores = np.abs((data - data.mean()) / data.std())
                anomalies = data[z_scores > threshold]
                
                anomaly_results[col] = {
                    'n_anomalies': len(anomalies),
                    'anomaly_percentage': (len(anomalies) / len(data)) * 100,
                    'anomaly_values': anomalies.tolist()[:10]  # Top 10
                }
        
        return anomaly_results


class HypothesisTester:
    """Performs statistical hypothesis testing"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize HypothesisTester
        
        Args:
            df: DataFrame to test
        """
        self.df = df.copy()
    
    def test_normality(self, columns: Optional[List[str]] = None) -> Dict:
        """
        Test for normality using Shapiro-Wilk test
        
        Args:
            columns: Columns to test
        
        Returns:
            Dictionary with normality test results
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {}
        
        for col in columns:
            if col in self.df.columns:
                data = self.df[col].dropna()
                if len(data) > 3 and len(data) < 5000:  # Shapiro-Wilk works best for small samples
                    stat, p_value = stats.shapiro(data)
                    results[col] = {
                        'statistic': stat,
                        'p_value': p_value,
                        'is_normal': p_value > 0.05
                    }
                else:
                    # Use Kolmogorov-Smirnov test for larger samples
                    stat, p_value = stats.kstest(data, 'norm', 
                                                args=(data.mean(), data.std()))
                    results[col] = {
                        'statistic': stat,
                        'p_value': p_value,
                        'is_normal': p_value > 0.05,
                        'test': 'Kolmogorov-Smirnov'
                    }
        
        return results
    
    def test_correlation_significance(self, col1: str, col2: str) -> Dict:
        """
        Test significance of correlation between two variables
        
        Args:
            col1: First column name
            col2: Second column name
        
        Returns:
            Dictionary with correlation test results
        """
        if col1 not in self.df.columns or col2 not in self.df.columns:
            return {'error': 'Columns not found'}
        
        data = self.df[[col1, col2]].dropna()
        
        if len(data) < 3:
            return {'error': 'Insufficient data'}
        
        # Pearson correlation test
        corr_coef, p_value = stats.pearsonr(data[col1], data[col2])
        
        return {
            'correlation_coefficient': corr_coef,
            'p_value': p_value,
            'is_significant': p_value < 0.05,
            'interpretation': self._interpret_correlation(corr_coef, p_value)
        }
    
    def _interpret_correlation(self, corr: float, p_value: float) -> str:
        """Interpret correlation results"""
        if p_value >= 0.05:
            return "Not statistically significant"
        
        if abs(corr) < 0.3:
            strength = "weak"
        elif abs(corr) < 0.7:
            strength = "moderate"
        else:
            strength = "strong"
        
        direction = "positive" if corr > 0 else "negative"
        
        return f"{strength} {direction} correlation"


class InsightMiner:
    """Main class for advanced insight mining"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize InsightMiner
        
        Args:
            df: DataFrame to mine insights from
        """
        self.df = df.copy()
        self.feature_engineer = FeatureEngineer(df)
        self.clustering_analyzer = ClusteringAnalyzer(df)
        self.anomaly_detector = AnomalyDetector(df)
        self.hypothesis_tester = HypothesisTester(df)
        self.high_value_insights: List[Dict] = []
    
    def generate_high_value_insights(self) -> List[Dict]:
        """
        Generate high-value insights with explanations
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Insight 1: Data segmentation through clustering
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            clustering_result = self.clustering_analyzer.perform_kmeans_clustering(
                n_clusters=3, columns=numeric_cols[:5]
            )
            insights.append({
                'insight_number': 1,
                'category': 'Segmentation',
                'title': 'Natural Data Segments Identified',
                'description': f"K-Means clustering revealed {clustering_result['n_clusters']} distinct segments in the data",
                'business_impact': 'Enables targeted fiscal policies for different segments',
                'evidence': clustering_result['cluster_analysis']
            })
        
        # Insight 2: Anomaly detection
        if len(numeric_cols) >= 2:
            anomaly_result = self.anomaly_detector.detect_with_isolation_forest(
                contamination=0.1, columns=numeric_cols[:5]
            )
            insights.append({
                'insight_number': 2,
                'category': 'Anomaly Detection',
                'title': 'Anomalous Patterns Detected',
                'description': f"Identified {anomaly_result['n_anomalies']} anomalous data points ({anomaly_result['anomaly_percentage']:.1f}%)",
                'business_impact': 'Highlights potential errors, fraud, or exceptional events requiring investigation',
                'evidence': {
                    'anomaly_count': anomaly_result['n_anomalies'],
                    'percentage': anomaly_result['anomaly_percentage']
                }
            })
        
        # Insight 3: Feature relationships
        if len(numeric_cols) >= 2:
            corr_test = self.hypothesis_tester.test_correlation_significance(
                numeric_cols[0], numeric_cols[1]
            )
            if 'correlation_coefficient' in corr_test:
                insights.append({
                    'insight_number': 3,
                    'category': 'Relationships',
                    'title': 'Statistically Significant Relationships',
                    'description': f"Found {corr_test['interpretation']} between key variables",
                    'business_impact': 'Reveals causal or predictive relationships for better decision-making',
                    'evidence': corr_test
                })
        
        # Add more insights...
        
        self.high_value_insights = insights
        return insights
    
    def get_insights_summary(self) -> Dict:
        """
        Get summary of all insights
        
        Returns:
            Dictionary with insights summary
        """
        return {
            'total_insights': len(self.high_value_insights),
            'insights_by_category': self._group_insights_by_category(),
            'high_value_insights': self.high_value_insights
        }
    
    def _group_insights_by_category(self) -> Dict:
        """Group insights by category"""
        categories = {}
        for insight in self.high_value_insights:
            category = insight.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(insight)
        return categories

