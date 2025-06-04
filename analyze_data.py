#!/usr/bin/env python3
"""
Data analysis and reporting utilities for the AI Search Agent.
Analyzes search logs and generates insights.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class SearchAnalyzer:
    """Analyze search logs and generate reports."""
    
    def __init__(self, log_directory: str = "."):
        """Initialize analyzer with log directory."""
        self.log_directory = Path(log_directory)
        self.df: Optional[pd.DataFrame] = None
    
    def load_latest_log(self) -> bool:
        """Load the most recent search log."""
        try:
            csv_files = list(self.log_directory.glob("search_log_*.csv"))
            if not csv_files:
                print("No search log files found")
                return False
            
            # Get the most recent file
            latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
            
            self.df = pd.read_csv(latest_file)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            
            print(f"Loaded {len(self.df)} search records from {latest_file.name}")
            return True
            
        except Exception as e:
            print(f"Error loading log: {e}")
            return False
    
    def load_all_logs(self) -> bool:
        """Load and combine all search logs."""
        try:
            csv_files = list(self.log_directory.glob("search_log_*.csv"))
            if not csv_files:
                print("No search log files found")
                return False
            
            dfs = []
            for file in csv_files:
                df = pd.read_csv(file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dfs.append(df)
            
            self.df = pd.concat(dfs, ignore_index=True)
            self.df = self.df.sort_values('timestamp').reset_index(drop=True)
            
            print(f"Loaded {len(self.df)} total search records from {len(csv_files)} files")
            return True
            
        except Exception as e:
            print(f"Error loading logs: {e}")
            return False
    
    def generate_summary(self) -> Dict:
        """Generate search summary statistics."""
        if self.df is None or self.df.empty:
            return {}
        
        summary = {
            'total_searches': len(self.df),
            'successful_searches': len(self.df[self.df['response_status'] == 'success']),
            'failed_searches': len(self.df[self.df['response_status'] != 'success']),
            'success_rate': len(self.df[self.df['response_status'] == 'success']) / len(self.df) * 100,
            'avg_execution_time': self.df['execution_time'].mean(),
            'total_time': self.df['execution_time'].sum(),
            'date_range': {
                'start': self.df['timestamp'].min().isoformat(),
                'end': self.df['timestamp'].max().isoformat()
            }
        }
        
        return summary
    
    def category_analysis(self) -> Dict:
        """Analyze searches by category."""
        if self.df is None or self.df.empty:
            return {}
        
        category_stats = self.df.groupby('category').agg({
            'response_status': lambda x: (x == 'success').mean() * 100,
            'execution_time': 'mean',
            'generated_query': 'count'
        }).round(2)
        
        category_stats.columns = ['success_rate_%', 'avg_time_sec', 'total_searches']
        
        return category_stats.to_dict('index')
    
    def query_type_analysis(self) -> Dict:
        """Analyze searches by query type."""
        if self.df is None or self.df.empty:
            return {}
        
        type_stats = self.df.groupby('query_type').agg({
            'response_status': lambda x: (x == 'success').mean() * 100,
            'execution_time': 'mean',
            'generated_query': 'count'
        }).round(2)
        
        type_stats.columns = ['success_rate_%', 'avg_time_sec', 'total_searches']
        
        return type_stats.to_dict('index')
    
    def time_analysis(self) -> Dict:
        """Analyze search patterns over time."""
        if self.df is None or self.df.empty:
            return {}
        
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day_of_week'] = self.df['timestamp'].dt.day_name()
        
        hourly_stats = self.df.groupby('hour').agg({
            'response_status': lambda x: (x == 'success').mean() * 100,
            'generated_query': 'count'
        }).round(2)
        
        daily_stats = self.df.groupby('day_of_week').agg({
            'response_status': lambda x: (x == 'success').mean() * 100,
            'generated_query': 'count'
        }).round(2)
        
        return {
            'hourly': hourly_stats.to_dict('index'),
            'daily': daily_stats.to_dict('index')
        }
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a comprehensive text report."""
        if self.df is None or self.df.empty:
            return "No data available for analysis"
        
        report_lines = []
        report_lines.append("AI Search Agent - Analysis Report")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        summary = self.generate_summary()
        report_lines.append("SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(f"Total Searches: {summary['total_searches']}")
        report_lines.append(f"Successful: {summary['successful_searches']}")
        report_lines.append(f"Failed: {summary['failed_searches']}")
        report_lines.append(f"Success Rate: {summary['success_rate']:.1f}%")
        report_lines.append(f"Average Execution Time: {summary['avg_execution_time']:.2f}s")
        report_lines.append(f"Total Time: {summary['total_time']:.2f}s")
        report_lines.append("")
        
        # Category analysis
        category_stats = self.category_analysis()
        report_lines.append("CATEGORY ANALYSIS")
        report_lines.append("-" * 20)
        for category, stats in category_stats.items():
            report_lines.append(f"{category.title()}:")
            report_lines.append(f"  Searches: {stats['total_searches']}")
            report_lines.append(f"  Success Rate: {stats['success_rate_%']:.1f}%")
            report_lines.append(f"  Avg Time: {stats['avg_time_sec']:.2f}s")
        report_lines.append("")
        
        # Query type analysis
        type_stats = self.query_type_analysis()
        report_lines.append("QUERY TYPE ANALYSIS")
        report_lines.append("-" * 20)
        for query_type, stats in type_stats.items():
            report_lines.append(f"{query_type.title()}:")
            report_lines.append(f"  Searches: {stats['total_searches']}")
            report_lines.append(f"  Success Rate: {stats['success_rate_%']:.1f}%")
            report_lines.append(f"  Avg Time: {stats['avg_time_sec']:.2f}s")
        report_lines.append("")
        
        # Recent failures
        failed_searches = self.df[self.df['response_status'] != 'success']
        if not failed_searches.empty:
            report_lines.append("RECENT FAILURES")
            report_lines.append("-" * 20)
            for _, row in failed_searches.tail(5).iterrows():
                report_lines.append(f"{row['timestamp']}: {row['generated_query']}")
                report_lines.append(f"  Status: {row['response_status']}")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Report saved to {output_file}")
        
        return report_content
    
    def create_visualizations(self, output_dir: str = "reports"):
        """Create visualization charts."""
        if self.df is None or self.df.empty:
            print("No data available for visualization")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        plt.style.use('seaborn-v0_8')
        
        # Success rate by category
        plt.figure(figsize=(12, 6))
        category_success = self.df.groupby('category')['response_status'].apply(
            lambda x: (x == 'success').mean() * 100
        )
        category_success.plot(kind='bar', color='skyblue', edgecolor='navy')
        plt.title('Success Rate by Category')
        plt.ylabel('Success Rate (%)')
        plt.xlabel('Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path / 'success_by_category.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Execution time distribution
        plt.figure(figsize=(10, 6))
        self.df['execution_time'].hist(bins=30, color='lightgreen', edgecolor='darkgreen')
        plt.title('Execution Time Distribution')
        plt.xlabel('Execution Time (seconds)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(output_path / 'execution_time_dist.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Searches over time
        plt.figure(figsize=(12, 6))
        daily_counts = self.df.set_index('timestamp').resample('D').size()
        daily_counts.plot(kind='line', marker='o', color='purple')
        plt.title('Daily Search Volume')
        plt.ylabel('Number of Searches')
        plt.xlabel('Date')
        plt.tight_layout()
        plt.savefig(output_path / 'daily_volume.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_path}")


def main():
    """Main analysis function."""
    print("AI Search Agent - Data Analysis")
    print("=" * 40)
    
    analyzer = SearchAnalyzer()
    
    # Try to load data
    if not analyzer.load_latest_log():
        print("No data to analyze")
        return
    
    # Generate and display report
    report = analyzer.generate_report()
    print(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/analysis_report_{timestamp}.txt"
    analyzer.generate_report(report_file)
    
    # Create visualizations
    try:
        analyzer.create_visualizations()
    except ImportError:
        print("Matplotlib not available - skipping visualizations")
    except Exception as e:
        print(f"Error creating visualizations: {e}")


if __name__ == "__main__":
    main()
