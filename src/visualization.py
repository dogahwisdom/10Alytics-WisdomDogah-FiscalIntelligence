"""
Visualization Module
Creates comprehensive dashboards and visualizations using matplotlib, seaborn, and plotly
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11
COLOR_PALETTE = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#F77F00']


class DashboardGenerator:
    """Generates comprehensive dashboards"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize DashboardGenerator
        
        Args:
            df: DataFrame to visualize
        """
        self.df = df.copy()
        self.figures: List = []
    
    def create_trend_dashboard(self, date_column: str,
                               value_columns: List[str],
                               save_path: Optional[str] = None) -> go.Figure:
        """
        Create interactive trend dashboard
        
        Args:
            date_column: Name of date column
            value_columns: List of columns to plot
            save_path: Path to save HTML file
        
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Time Series Trends', 'Year-over-Year Comparison', 
                          'Monthly Patterns', 'Cumulative Trends'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Time series plot
        for i, col in enumerate(value_columns[:3]):
            if col in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=self.df[date_column],
                        y=self.df[col],
                        name=col,
                        line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2),
                        mode='lines+markers'
                    ),
                    row=1, col=1
                )
        
        # Year-over-year comparison
        try:
            self.df['year'] = pd.to_datetime(self.df[date_column]).dt.year
            self.df['month'] = pd.to_datetime(self.df[date_column]).dt.month
            
            yearly_data = self.df.groupby('year')[value_columns[0]].sum()
            fig.add_trace(
                go.Bar(
                    x=yearly_data.index,
                    y=yearly_data.values,
                    name='Yearly Total',
                    marker_color=COLOR_PALETTE[0]
                ),
                row=1, col=2
            )
        except:
            pass
        
        # Monthly patterns
        try:
            monthly_data = self.df.groupby('month')[value_columns[0]].mean()
            fig.add_trace(
                go.Scatter(
                    x=monthly_data.index,
                    y=monthly_data.values,
                    name='Monthly Average',
                    mode='lines+markers',
                    marker_color=COLOR_PALETTE[1]
                ),
                row=2, col=1
            )
        except:
            pass
        
        # Cumulative trends
        try:
            cumulative = self.df[value_columns[0]].cumsum()
            fig.add_trace(
                go.Scatter(
                    x=self.df[date_column],
                    y=cumulative,
                    name='Cumulative',
                    fill='tozeroy',
                    marker_color=COLOR_PALETTE[2]
                ),
                row=2, col=2
            )
        except:
            pass
        
        fig.update_layout(
            title_text="Fiscal Data Trend Dashboard",
            height=800,
            showlegend=True,
            template="plotly_white"
        )
        
        if save_path:
            fig.write_html(f"{save_path}/trend_dashboard.html")
        
        return fig
    
    def create_kpi_dashboard(self, kpi_metrics: Dict[str, float],
                           save_path: Optional[str] = None) -> go.Figure:
        """
        Create KPI dashboard with key metrics
        
        Args:
            kpi_metrics: Dictionary of metric names and values
            save_path: Path to save HTML file
        
        Returns:
            Plotly figure object
        """
        n_metrics = len(kpi_metrics)
        cols = 3
        rows = (n_metrics + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=list(kpi_metrics.keys()),
            specs=[[{"type": "indicator"}] * cols] * rows
        )
        
        positions = [(i // cols + 1, i % cols + 1) for i in range(n_metrics)]
        
        for i, (metric_name, value) in enumerate(kpi_metrics.items()):
            row, col = positions[i]
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=value,
                    title={'text': metric_name},
                    gauge={
                        'axis': {'range': [None, value * 1.5]},
                        'bar': {'color': COLOR_PALETTE[i % len(COLOR_PALETTE)]},
                        'steps': [
                            {'range': [0, value], 'color': "lightgray"},
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': value * 0.9
                        }
                    }
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title_text="Key Performance Indicators Dashboard",
            height=300 * rows,
            template="plotly_white"
        )
        
        if save_path:
            fig.write_html(f"{save_path}/kpi_dashboard.html")
        
        return fig
    
    def create_insight_storyboard(self, insights: List[Dict],
                                 save_path: Optional[str] = None) -> go.Figure:
        """
        Create visual storyboard of insights
        
        Args:
            insights: List of insight dictionaries
            save_path: Path to save HTML file
        
        Returns:
            Plotly figure object
        """
        n_insights = len(insights)
        fig = make_subplots(
            rows=n_insights, cols=1,
            subplot_titles=[f"Insight {i+1}: {ins.get('title', '')}" for i, ins in enumerate(insights)],
            vertical_spacing=0.15
        )
        
        for i, insight in enumerate(insights):
            # Create visualization based on insight type
            if 'evidence' in insight and isinstance(insight['evidence'], dict):
                # Plot evidence data if available
                evidence = insight['evidence']
                if 'cluster_analysis' in evidence:
                    # Clustering visualization
                    clusters = evidence['cluster_analysis']
                    cluster_names = list(clusters.keys())
                    cluster_sizes = [clusters[c]['size'] for c in cluster_names]
                    
                    fig.add_trace(
                        go.Bar(
                            x=cluster_names,
                            y=cluster_sizes,
                            name=f"Insight {i+1}",
                            marker_color=COLOR_PALETTE[i % len(COLOR_PALETTE)]
                        ),
                        row=i+1, col=1
                    )
        
        fig.update_layout(
            title_text="Insight Storyboard",
            height=300 * n_insights,
            showlegend=False,
            template="plotly_white"
        )
        
        if save_path:
            fig.write_html(f"{save_path}/insight_storyboard.html")
        
        return fig
    
    def create_correlation_network(self, corr_matrix: pd.DataFrame,
                                  threshold: float = 0.7,
                                  save_path: Optional[str] = None) -> go.Figure:
        """
        Create network visualization of correlations
        
        Args:
            corr_matrix: Correlation matrix DataFrame
            threshold: Minimum correlation to show
            save_path: Path to save HTML file
        
        Returns:
            Plotly figure object
        """
        # Extract strong correlations
        edges = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= threshold:
                    edges.append({
                        'source': corr_matrix.columns[i],
                        'target': corr_matrix.columns[j],
                        'value': abs(corr_val),
                        'sign': 'positive' if corr_val > 0 else 'negative'
                    })
        
        # Create network plot
        fig = go.Figure()
        
        # Add edges
        for edge in edges:
            fig.add_trace(
                go.Scatter(
                    x=[edge['source'], edge['target']],
                    y=[0, 0],
                    mode='lines',
                    line=dict(width=edge['value']*5, color='steelblue' if edge['sign'] == 'positive' else 'red'),
                    showlegend=False
                )
            )
        
        fig.update_layout(
            title=f"Correlation Network (threshold: {threshold})",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            template="plotly_white"
        )
        
        if save_path:
            fig.write_html(f"{save_path}/correlation_network.html")
        
        return fig


class VisualizationGenerator:
    """Main visualization generator class"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize VisualizationGenerator
        
        Args:
            df: DataFrame to visualize
        """
        self.df = df.copy()
        self.dashboard_gen = DashboardGenerator(df)
    
    def generate_all_visualizations(self, date_column: Optional[str] = None,
                                   value_columns: Optional[List[str]] = None,
                                   save_path: Optional[str] = None) -> Dict:
        """
        Generate all standard visualizations
        
        Args:
            date_column: Name of date column
            value_columns: List of value columns
            save_path: Path to save visualizations
        
        Returns:
            Dictionary with all generated figures
        """
        if value_columns is None:
            value_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()[:5]
        
        visualizations = {}
        
        # 1. Distribution plots
        visualizations['distributions'] = self._create_distribution_plots(value_columns, save_path)
        
        # 2. Correlation heatmap
        visualizations['correlation'] = self._create_correlation_heatmap(save_path)
        
        # 3. Trend dashboard (if date column available)
        if date_column and date_column in self.df.columns:
            visualizations['trend_dashboard'] = self.dashboard_gen.create_trend_dashboard(
                date_column, value_columns, save_path
            )
        
        # 4. Box plots for outlier visualization
        visualizations['outliers'] = self._create_outlier_plots(value_columns, save_path)
        
        return visualizations
    
    def _create_distribution_plots(self, columns: List[str],
                                   save_path: Optional[str] = None) -> List:
        """Create distribution plots for columns"""
        figures = []
        
        for col in columns:
            if col in self.df.columns:
                fig, axes = plt.subplots(1, 2, figsize=(14, 5))
                
                # Histogram
                axes[0].hist(self.df[col].dropna(), bins=30, edgecolor='black', 
                           alpha=0.7, color=COLOR_PALETTE[0])
                axes[0].set_title(f'Distribution of {col}', fontweight='bold')
                axes[0].set_xlabel(col)
                axes[0].set_ylabel('Frequency')
                axes[0].grid(True, alpha=0.3)
                
                # Box plot
                axes[1].boxplot(self.df[col].dropna(), vert=True)
                axes[1].set_title(f'Box Plot: {col}', fontweight='bold')
                axes[1].set_ylabel(col)
                axes[1].grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                if save_path:
                    plt.savefig(f"{save_path}/distribution_{col}.png", dpi=300, bbox_inches='tight')
                
                figures.append(fig)
                plt.close()
        
        return figures
    
    def _create_correlation_heatmap(self, save_path: Optional[str] = None) -> plt.Figure:
        """Create correlation heatmap"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return None
        
        corr_matrix = self.df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
        
        if save_path:
            plt.savefig(f"{save_path}/correlation_heatmap.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def _create_outlier_plots(self, columns: List[str],
                              save_path: Optional[str] = None) -> plt.Figure:
        """Create box plots for outlier detection"""
        numeric_cols = [col for col in columns if col in self.df.columns and col in self.df.select_dtypes(include=[np.number]).columns]
        
        if not numeric_cols:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 6))
        data_to_plot = [self.df[col].dropna() for col in numeric_cols[:10]]
        
        bp = ax.boxplot(data_to_plot, labels=numeric_cols[:10], patch_artist=True)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], COLOR_PALETTE * 2):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title('Outlier Detection - Box Plots', fontsize=14, fontweight='bold')
        ax.set_ylabel('Values')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}/outlier_detection.png", dpi=300, bbox_inches='tight')
        
        return fig

