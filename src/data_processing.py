"""
Data Processing Module
Handles dataset loading, cleaning, and preprocessing
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class DataLoader:
    """Handles loading of fiscal data from Excel files"""
    
    def __init__(self, file_path: str):
        """
        Initialize DataLoader
        
        Args:
            file_path: Path to the Excel file
        """
        self.file_path = file_path
        self.raw_data: Optional[pd.DataFrame] = None
        self.sheets_info: Dict = {}
    
    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all sheets from Excel file
        
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        excel_file = pd.ExcelFile(self.file_path)
        sheets_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            sheets_data[sheet_name] = df
            self.sheets_info[sheet_name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict()
            }
        
        return sheets_data
    
    def load_primary_sheet(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Load primary sheet (first sheet if not specified)
        
        Args:
            sheet_name: Name of sheet to load (default: first sheet)
        
        Returns:
            DataFrame with raw data
        """
        excel_file = pd.ExcelFile(self.file_path)
        
        if sheet_name is None:
            sheet_name = excel_file.sheet_names[0]
        
        self.raw_data = pd.read_excel(self.file_path, sheet_name=sheet_name)
        return self.raw_data
    
    def get_dataset_summary(self) -> Dict:
        """
        Generate executive summary of the dataset
        
        Returns:
            Dictionary with dataset summary statistics
        """
        if self.raw_data is None:
            raise ValueError("No data loaded. Call load_primary_sheet() first.")
        
        summary = {
            'total_rows': len(self.raw_data),
            'total_columns': len(self.raw_data.columns),
            'column_names': list(self.raw_data.columns),
            'data_types': self.raw_data.dtypes.to_dict(),
            'missing_values': self.raw_data.isnull().sum().to_dict(),
            'missing_percentage': (self.raw_data.isnull().sum() / len(self.raw_data) * 100).to_dict(),
            'duplicate_rows': self.raw_data.duplicated().sum(),
            'memory_usage_mb': self.raw_data.memory_usage(deep=True).sum() / 1024**2,
            'numeric_columns': list(self.raw_data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.raw_data.select_dtypes(include=['object']).columns),
            'date_columns': list(self.raw_data.select_dtypes(include=['datetime64']).columns)
        }
        
        return summary


class DataCleaner:
    """Handles data cleaning operations"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataCleaner
        
        Args:
            df: DataFrame to clean
        """
        self.df = df.copy()
        self.cleaning_log: list = []
    
    def standardize_column_names(self) -> pd.DataFrame:
        """
        Standardize column names (lowercase, replace spaces with underscores)
        
        Returns:
            DataFrame with standardized column names
        """
        original_cols = self.df.columns.tolist()
        self.df.columns = (
            self.df.columns
            .str.lower()
            .str.replace(' ', '_')
            .str.replace('-', '_')
            .str.replace('(', '')
            .str.replace(')', '')
            .str.strip()
        )
        
        self.cleaning_log.append({
            'operation': 'standardize_column_names',
            'details': dict(zip(original_cols, self.df.columns))
        })
        
        return self.df
    
    def fix_data_types(self, date_columns: Optional[list] = None, 
                      numeric_columns: Optional[list] = None) -> pd.DataFrame:
        """
        Fix data types for columns
        
        Args:
            date_columns: List of column names to convert to datetime
            numeric_columns: List of column names to convert to numeric
        
        Returns:
            DataFrame with corrected data types
        """
        # Convert date columns
        if date_columns:
            for col in date_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    self.cleaning_log.append({
                        'operation': 'convert_to_datetime',
                        'column': col
                    })
        
        # Convert numeric columns
        if numeric_columns:
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    self.cleaning_log.append({
                        'operation': 'convert_to_numeric',
                        'column': col
                    })
        
        return self.df
    
    def handle_missing_values(self, strategy: str = 'auto', 
                            threshold: float = 0.5) -> pd.DataFrame:
        """
        Handle missing values based on strategy
        
        Args:
            strategy: 'auto', 'drop', 'forward_fill', 'backward_fill', 'mean', 'median', 'mode'
            threshold: Threshold for dropping columns (if > threshold missing, drop column)
        
        Returns:
            DataFrame with handled missing values
        """
        # Drop columns with too many missing values
        missing_ratio = self.df.isnull().sum() / len(self.df)
        cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()
        
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            self.cleaning_log.append({
                'operation': 'drop_high_missing_columns',
                'columns': cols_to_drop,
                'missing_ratio': missing_ratio[cols_to_drop].to_dict()
            })
        
        # Handle remaining missing values
        if strategy == 'auto':
            # Numeric: fill with median
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self.df[col].isnull().sum() > 0:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
            
            # Categorical: fill with mode
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if self.df[col].isnull().sum() > 0:
                    mode_value = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else 'Unknown'
                    self.df[col].fillna(mode_value, inplace=True)
            
            # Datetime: forward fill
            datetime_cols = self.df.select_dtypes(include=['datetime64']).columns
            for col in datetime_cols:
                if self.df[col].isnull().sum() > 0:
                    self.df[col].fillna(method='ffill', inplace=True)
        
        elif strategy == 'drop':
            self.df = self.df.dropna()
        elif strategy == 'forward_fill':
            self.df = self.df.fillna(method='ffill')
        elif strategy == 'backward_fill':
            self.df = self.df.fillna(method='bfill')
        elif strategy == 'mean':
            self.df = self.df.fillna(self.df.mean())
        elif strategy == 'median':
            self.df = self.df.fillna(self.df.median())
        elif strategy == 'mode':
            self.df = self.df.fillna(self.df.mode().iloc[0])
        
        self.cleaning_log.append({
            'operation': 'handle_missing_values',
            'strategy': strategy,
            'remaining_missing': self.df.isnull().sum().sum()
        })
        
        return self.df
    
    def remove_duplicates(self) -> pd.DataFrame:
        """
        Remove duplicate rows
        
        Returns:
            DataFrame without duplicates
        """
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        removed_count = initial_count - len(self.df)
        
        self.cleaning_log.append({
            'operation': 'remove_duplicates',
            'removed_rows': removed_count
        })
        
        return self.df
    
    def detect_outliers(self, method: str = 'iqr', threshold: float = 3.0) -> Dict:
        """
        Detect outliers in numeric columns
        
        Args:
            method: 'iqr' or 'zscore'
            threshold: Threshold for outlier detection
        
        Returns:
            Dictionary with outlier information
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        outliers = {}
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outlier_mask = z_scores > threshold
            
            outlier_count = outlier_mask.sum()
            outliers[col] = {
                'count': outlier_count,
                'percentage': (outlier_count / len(self.df)) * 100,
                'indices': self.df[outlier_mask].index.tolist()
            }
        
        return outliers
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """
        Get the cleaned DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        return self.df
    
    def get_cleaning_report(self) -> Dict:
        """
        Get summary of all cleaning operations
        
        Returns:
            Dictionary with cleaning report
        """
        return {
            'final_shape': self.df.shape,
            'operations': self.cleaning_log,
            'remaining_missing': self.df.isnull().sum().to_dict(),
            'final_columns': list(self.df.columns)
        }


class DataProcessor:
    """Main data processing orchestrator"""
    
    def __init__(self, file_path: str):
        """
        Initialize DataProcessor
        
        Args:
            file_path: Path to the Excel file
        """
        self.loader = DataLoader(file_path)
        self.cleaner: Optional[DataCleaner] = None
        self.processed_data: Optional[pd.DataFrame] = None
    
    def process(self, sheet_name: Optional[str] = None, 
               cleaning_config: Optional[Dict] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete data processing pipeline
        
        Args:
            sheet_name: Sheet name to process
            cleaning_config: Configuration for cleaning operations
        
        Returns:
            Tuple of (processed DataFrame, processing report)
        """
        # Load data
        raw_data = self.loader.load_primary_sheet(sheet_name)
        summary = self.loader.get_dataset_summary()
        
        # Initialize cleaner
        self.cleaner = DataCleaner(raw_data)
        
        # Apply cleaning operations
        if cleaning_config is None:
            cleaning_config = {
                'standardize_names': True,
                'remove_duplicates': True,
                'handle_missing': True,
                'missing_strategy': 'auto',
                'auto_fix_types': True
            }
        
        if cleaning_config.get('standardize_names', True):
            self.cleaner.standardize_column_names()
        
        # Auto-detect and fix data types
        if cleaning_config.get('auto_fix_types', True):
            # Detect date columns
            date_cols = []
            for col in self.cleaner.df.columns:
                if 'time' in col.lower() or 'date' in col.lower():
                    date_cols.append(col)
            
            # Detect numeric columns (columns that can be converted to numeric)
            numeric_cols = []
            for col in self.cleaner.df.columns:
                if col not in date_cols:
                    # Try converting a sample to see if it's numeric
                    sample = self.cleaner.df[col].dropna().head(100)
                    if len(sample) > 0:
                        try:
                            pd.to_numeric(sample, errors='raise')
                            numeric_cols.append(col)
                        except:
                            pass
            
            if date_cols or numeric_cols:
                self.cleaner.fix_data_types(
                    date_columns=date_cols if date_cols else None,
                    numeric_columns=numeric_cols if numeric_cols else None
                )
        
        if cleaning_config.get('remove_duplicates', True):
            self.cleaner.remove_duplicates()
        
        if cleaning_config.get('handle_missing', True):
            self.cleaner.handle_missing_values(
                strategy=cleaning_config.get('missing_strategy', 'auto')
            )
        
        # Get processed data
        self.processed_data = self.cleaner.get_cleaned_data()
        
        # Generate report
        report = {
            'original_summary': summary,
            'cleaning_report': self.cleaner.get_cleaning_report(),
            'processing_successful': True
        }
        
        return self.processed_data, report

