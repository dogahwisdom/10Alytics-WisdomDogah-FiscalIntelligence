"""
Fiscal Intelligence Analytics Platform
Source code package
"""

__version__ = "1.0.0"
__author__ = "10Alytics Hackathon Team"

from .data_processing import DataProcessor, DataLoader, DataCleaner
from .eda import EDAAnalyzer
from .insights import InsightMiner, FeatureEngineer, ClusteringAnalyzer, AnomalyDetector
from .models import ForecastingModel, RegressionModel, ClassificationModel, RecommendationSystem
from .visualization import DashboardGenerator, VisualizationGenerator

__all__ = [
    'DataProcessor',
    'DataLoader',
    'DataCleaner',
    'EDAAnalyzer',
    'InsightMiner',
    'FeatureEngineer',
    'ClusteringAnalyzer',
    'AnomalyDetector',
    'ForecastingModel',
    'RegressionModel',
    'ClassificationModel',
    'RecommendationSystem',
    'DashboardGenerator',
    'VisualizationGenerator'
]

