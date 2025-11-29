"""
Predictive and Prescriptive Models Module
Provides forecasting, regression, classification, and recommendation models
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from typing import Dict, Optional, Tuple, List
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Prophet not available. Install with: pip install prophet")

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    print("statsmodels not available. Install with: pip install statsmodels")


class ForecastingModel:
    """Time series forecasting models"""
    
    def __init__(self, df: pd.DataFrame, date_column: str, value_column: str):
        """
        Initialize ForecastingModel
        
        Args:
            df: DataFrame with time series data
            date_column: Name of date column
            value_column: Name of value column to forecast
        """
        self.df = df.copy()
        self.date_column = date_column
        self.value_column = value_column
        self.model = None
        self.forecast_results: Optional[pd.DataFrame] = None
    
    def forecast_with_prophet(self, periods: int = 12, 
                             freq: str = 'M') -> Dict:
        """
        Forecast using Facebook Prophet
        
        Args:
            periods: Number of periods to forecast
            freq: Frequency ('D', 'M', 'Y')
        
        Returns:
            Dictionary with forecast results and metrics
        """
        if not PROPHET_AVAILABLE:
            return {'error': 'Prophet not available'}
        
        try:
            # Prepare data for Prophet
            prophet_df = self.df[[self.date_column, self.value_column]].copy()
            prophet_df.columns = ['ds', 'y']
            prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
            prophet_df = prophet_df.dropna()
            
            # Fit model
            self.model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )
            self.model.fit(prophet_df)
            
            # Make forecast
            future = self.model.make_future_dataframe(periods=periods, freq=freq)
            forecast = self.model.predict(future)
            
            self.forecast_results = forecast
            
            # Calculate metrics on historical data
            historical_forecast = forecast[forecast['ds'] <= prophet_df['ds'].max()]
            y_true = prophet_df['y'].values
            y_pred = historical_forecast['yhat'].values[:len(y_true)]
            
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            
            return {
                'method': 'Prophet',
                'forecast_periods': periods,
                'metrics': {
                    'mse': mse,
                    'mae': mae,
                    'rmse': rmse,
                    'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
                },
                'forecast_data': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).to_dict('records'),
                'model_components': self.model.plot_components(forecast) if hasattr(self.model, 'plot_components') else None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def forecast_with_arima(self, order: Tuple[int, int, int] = (1, 1, 1),
                           periods: int = 12) -> Dict:
        """
        Forecast using ARIMA
        
        Args:
            order: ARIMA order (p, d, q)
            periods: Number of periods to forecast
        
        Returns:
            Dictionary with forecast results
        """
        if not ARIMA_AVAILABLE:
            return {'error': 'ARIMA not available'}
        
        try:
            # Prepare data
            ts_data = self.df.set_index(self.date_column)[self.value_column].dropna()
            ts_data = ts_data.sort_index()
            
            # Fit ARIMA model
            model = ARIMA(ts_data, order=order)
            fitted_model = model.fit()
            
            # Make forecast
            forecast = fitted_model.forecast(steps=periods)
            forecast_ci = fitted_model.get_forecast(steps=periods).conf_int()
            
            # Calculate metrics
            predictions = fitted_model.fittedvalues
            mse = mean_squared_error(ts_data, predictions)
            mae = mean_absolute_error(ts_data, predictions)
            
            return {
                'method': 'ARIMA',
                'order': order,
                'forecast_periods': periods,
                'metrics': {
                    'mse': mse,
                    'mae': mae,
                    'rmse': np.sqrt(mse),
                    'aic': fitted_model.aic,
                    'bic': fitted_model.bic
                },
                'forecast_values': forecast.tolist(),
                'forecast_confidence_intervals': forecast_ci.to_dict('records')
            }
        except Exception as e:
            return {'error': str(e)}


class RegressionModel:
    """Regression models for fiscal prediction"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize RegressionModel
        
        Args:
            df: DataFrame with features and target
        """
        self.df = df.copy()
        self.models = {}
        self.scaler = StandardScaler()
    
    def train_regression_model(self, target_column: str,
                              feature_columns: Optional[List[str]] = None,
                              test_size: float = 0.2,
                              model_type: str = 'random_forest') -> Dict:
        """
        Train regression model
        
        Args:
            target_column: Name of target column
            feature_columns: List of feature columns (default: all numeric except target)
            test_size: Proportion of data for testing
            model_type: 'random_forest', 'linear', 'ridge', 'lasso'
        
        Returns:
            Dictionary with model results and metrics
        """
        if feature_columns is None:
            feature_columns = [col for col in self.df.select_dtypes(include=[np.number]).columns 
                             if col != target_column]
        
        # Prepare data
        X = self.df[feature_columns].dropna()
        y = self.df.loc[X.index, target_column]
        
        if len(X) == 0:
            return {'error': 'No valid data after dropping NaN'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        elif model_type == 'linear':
            model = LinearRegression()
        elif model_type == 'ridge':
            model = Ridge(alpha=1.0)
        elif model_type == 'lasso':
            model = Lasso(alpha=1.0)
        else:
            return {'error': f'Unknown model type: {model_type}'}
        
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_train_pred = model.predict(X_train_scaled)
        y_test_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        train_metrics = {
            'mse': mean_squared_error(y_train, y_train_pred),
            'mae': mean_absolute_error(y_train, y_train_pred),
            'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'r2': r2_score(y_train, y_train_pred)
        }
        
        test_metrics = {
            'mse': mean_squared_error(y_test, y_test_pred),
            'mae': mean_absolute_error(y_test, y_test_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'r2': r2_score(y_test, y_test_pred)
        }
        
        # Feature importance (if available)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            feature_importance = dict(sorted(feature_importance.items(), 
                                           key=lambda x: x[1], reverse=True))
        
        self.models[model_type] = model
        
        return {
            'model_type': model_type,
            'target_column': target_column,
            'feature_columns': feature_columns,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'feature_importance': feature_importance,
            'n_samples_train': len(X_train),
            'n_samples_test': len(X_test)
        }
    
    def predict(self, X: pd.DataFrame, model_type: str = 'random_forest') -> np.ndarray:
        """
        Make predictions using trained model
        
        Args:
            X: Feature DataFrame
            model_type: Type of model to use
        
        Returns:
            Predictions array
        """
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.models[model_type].predict(X_scaled)


class ClassificationModel:
    """Classification models"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize ClassificationModel
        
        Args:
            df: DataFrame with features and target
        """
        self.df = df.copy()
        self.model = None
    
    def train_classification_model(self, target_column: str,
                                  feature_columns: Optional[List[str]] = None,
                                  test_size: float = 0.2) -> Dict:
        """
        Train classification model
        
        Args:
            target_column: Name of target column (categorical)
            feature_columns: List of feature columns
            test_size: Proportion of data for testing
        
        Returns:
            Dictionary with model results
        """
        if feature_columns is None:
            feature_columns = [col for col in self.df.select_dtypes(include=[np.number]).columns 
                             if col != target_column]
        
        # Prepare data
        X = self.df[feature_columns].dropna()
        y = self.df.loc[X.index, target_column]
        
        if len(X) == 0:
            return {'error': 'No valid data'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if len(y.unique()) > 1 else None
        )
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        return {
            'model_type': 'Random Forest Classifier',
            'target_column': target_column,
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'classification_report': classification_report(y_test, y_test_pred, output_dict=True),
            'feature_importance': dict(zip(feature_columns, self.model.feature_importances_))
        }


class RecommendationSystem:
    """Fiscal policy recommendation system"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize RecommendationSystem
        
        Args:
            df: DataFrame with fiscal data
        """
        self.df = df.copy()
    
    def generate_recommendations(self, target_metric: str,
                                constraint_columns: Optional[List[str]] = None) -> List[Dict]:
        """
        Generate fiscal policy recommendations
        
        Args:
            target_metric: Metric to optimize
            constraint_columns: Columns that represent constraints
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Analyze current state
        current_value = self.df[target_metric].mean() if target_metric in self.df.columns else None
        
        # Recommendation 1: Based on trends
        if target_metric in self.df.select_dtypes(include=[np.number]).columns:
            trend = self._calculate_trend(self.df[target_metric])
            recommendations.append({
                'priority': 'High',
                'category': 'Trend Optimization',
                'recommendation': self._generate_trend_recommendation(trend, target_metric),
                'expected_impact': 'Medium to High',
                'implementation': 'Short-term'
            })
        
        # Recommendation 2: Based on correlations
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2 and target_metric in numeric_cols:
            corr_matrix = self.df[numeric_cols].corr()
            top_correlated = corr_matrix[target_metric].abs().sort_values(ascending=False)
            top_correlated = top_correlated[top_correlated < 1.0].head(3)
            
            if len(top_correlated) > 0:
                recommendations.append({
                    'priority': 'Medium',
                    'category': 'Leverage Correlations',
                    'recommendation': f"Focus on improving {', '.join(top_correlated.index[:2].tolist())} as they strongly correlate with {target_metric}",
                    'expected_impact': 'Medium',
                    'implementation': 'Medium-term'
                })
        
        # Add more recommendation logic...
        
        return recommendations
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction"""
        if len(series) < 2:
            return "stable"
        
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        
        if slope > 0:
            return "increasing"
        elif slope < 0:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_trend_recommendation(self, trend: str, metric: str) -> str:
        """Generate recommendation based on trend"""
        if trend == "decreasing":
            return f"Implement intervention strategies to reverse declining trend in {metric}"
        elif trend == "increasing":
            return f"Maintain current policies to sustain positive trend in {metric}"
        else:
            return f"Explore opportunities to accelerate growth in {metric}"

