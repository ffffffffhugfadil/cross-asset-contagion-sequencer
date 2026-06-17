"""
demo/visualizer.py
==================
Visualization tools for contagion sequence.

Creates heatmaps, timeline charts, and impact bar charts
for demo videos and presentations.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os


class ContagionVisualizer:
    """
    Create visualizations for contagion predictions.
    
    Usage:
        viz = ContagionVisualizer()
        viz.plot_contagion_sequence(predicted_sequence, actual_sequence)
        viz.plot_correlation_heatmap(correlation_matrix)
        viz.plot_impact_scores(impact_scores)
    """
    
    def __init__(self, style: str = 'dark_background', save_dir: str = 'demo/images'):
        """
        Initialize visualizer with style and save directory.
        
        Args:
            style: Matplotlib style ('dark_background', 'seaborn', etc.)
            save_dir: Directory to save charts
        """
        self.save_dir = save_dir
        try:
            plt.style.use(style)
        except:
            pass  # Fallback to default
        
        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
    
    def _validate_data(self, data: List[Dict], data_name: str) -> bool:
        """
        Validate that data is not empty.
        
        Args:
            data: Data to validate
            data_name: Name of the data for error message
            
        Returns:
            True if valid, False otherwise
        """
        if not data or len(data) == 0:
            print(f"   ⚠️ No {data_name} data available. Skipping chart.")
            return False
        return True
    
    def plot_contagion_sequence(
        self,
        predicted_sequence: List[Dict],
        actual_sequence: Optional[List[Dict]] = None,
        title: str = "Contagion Sequence Prediction",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot predicted contagion sequence as horizontal bar chart.
        
        Args:
            predicted_sequence: List of dicts with 'symbol' and 'estimated_lag_hours'
            actual_sequence: Optional list of dicts with 'symbol' and 'actual_lag_hours'
            title: Chart title
            save_path: Path to save figure (optional)
        """
        # ✅ VALIDATION: Check if data exists
        if not self._validate_data(predicted_sequence, "sequence"):
            return
        
        # If no save_path provided, use default
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'contagion_sequence.png')
        
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Prepare data
            symbols = [p['symbol'] for p in predicted_sequence]
            predicted_lags = [p['estimated_lag_hours'] for p in predicted_sequence]
            
            # Colors based on position (first = red, last = green)
            colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(symbols)))
            
            # Plot predicted bars
            bars = ax.barh(symbols, predicted_lags, color=colors, alpha=0.8, label='Predicted')
            
            # Add actual sequence as dots if provided
            if actual_sequence:
                actual_dict = {a['symbol']: a['actual_lag_hours'] for a in actual_sequence}
                actual_lags = [actual_dict.get(s, 0) for s in symbols]
                ax.scatter(actual_lags, symbols, color='white', s=100, 
                          marker='o', zorder=5, label='Actual', edgecolors='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar, lag in zip(bars, predicted_lags):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                       f'{lag:.0f}h', va='center', fontsize=10)
            
            ax.set_xlabel('Lag Hours (after source stress)', fontsize=12)
            ax.set_ylabel('Asset', fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            else:
                plt.show()
            
            plt.close(fig)
            
        except Exception as e:
            print(f"   ⚠️ Error generating sequence chart: {e}")
    
    def plot_correlation_heatmap(
        self,
        correlation_matrix: Dict[str, Dict[str, float]],
        title: str = "Cross-Asset Correlation Heatmap",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot correlation matrix as heatmap.
        
        Args:
            correlation_matrix: Nested dict: {asset1: {asset2: correlation}}
            title: Chart title
            save_path: Path to save figure
        """
        # ✅ VALIDATION: Check if data exists
        if not correlation_matrix or len(correlation_matrix) == 0:
            print("   ⚠️ No correlation matrix data available. Skipping chart.")
            return
        
        # If no save_path provided, use default
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'correlation_heatmap.png')
        
        try:
            assets = list(correlation_matrix.keys())
            n = len(assets)
            
            # Build matrix
            matrix = np.zeros((n, n))
            for i, a1 in enumerate(assets):
                for j, a2 in enumerate(assets):
                    matrix[i, j] = correlation_matrix.get(a1, {}).get(a2, 0)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create heatmap
            im = ax.imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Correlation', fontsize=10)
            
            # Set ticks and labels
            ax.set_xticks(np.arange(n))
            ax.set_yticks(np.arange(n))
            ax.set_xticklabels(assets, rotation=45, ha='right')
            ax.set_yticklabels(assets)
            
            # Add correlation values in cells
            for i in range(n):
                for j in range(n):
                    text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                                  ha="center", va="center", 
                                  color="white" if abs(matrix[i, j]) > 0.5 else "black",
                                  fontsize=9)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            else:
                plt.show()
            
            plt.close(fig)
            
        except Exception as e:
            print(f"   ⚠️ Error generating correlation heatmap: {e}")
    
    def plot_impact_scores(
        self,
        impact_scores: List[Dict],
        title: str = "Impact Score by Asset",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot impact scores as horizontal bar chart with color coding.
        
        Args:
            impact_scores: List of dicts with 'symbol', 'impact_score', 'signal'
            title: Chart title
            save_path: Path to save figure
        """
        # ✅ VALIDATION: Check if data exists
        if not self._validate_data(impact_scores, "impact score"):
            return
        
        # If no save_path provided, use default
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'impact_scores.png')
        
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Sort by impact score descending
            sorted_scores = sorted(impact_scores, key=lambda x: x['impact_score'], reverse=True)
            symbols = [s['symbol'] for s in sorted_scores]
            scores = [s['impact_score'] for s in sorted_scores]
            signals = [s.get('signal', 'WATCH') for s in sorted_scores]
            
            # Color mapping based on signal
            signal_colors = {
                'EXIT_NOW': '#ff4444',  # Red
                'REDUCE': '#ff8800',    # Orange
                'WATCH': '#ffcc00',     # Yellow
                'HOLD': '#44ff44',      # Green
            }
            colors = [signal_colors.get(signal, '#888888') for signal in signals]
            
            # Create bars
            bars = ax.barh(symbols, scores, color=colors, alpha=0.8)
            
            # Add threshold lines
            ax.axvline(x=0.7, color='red', linestyle='--', alpha=0.5, label='EXIT_NOW threshold (0.7)')
            ax.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='REDUCE threshold (0.4)')
            ax.axvline(x=0.2, color='yellow', linestyle='--', alpha=0.5, label='WATCH threshold (0.2)')
            
            # Add value labels
            for bar, score in zip(bars, scores):
                ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                       f'{score:.2f}', va='center', fontsize=10)
            
            ax.set_xlabel('Impact Score (0.0 - 1.0)', fontsize=12)
            ax.set_ylabel('Asset', fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.legend(loc='lower right')
            ax.set_xlim(0, 1)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            else:
                plt.show()
            
            plt.close(fig)
            
        except Exception as e:
            print(f"   ⚠️ Error generating impact scores chart: {e}")
    
    def plot_timeline(
        self,
        sequence: List[Dict],
        source_asset: str = "BTC",
        title: str = "Contagion Spread Timeline",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot contagion spread timeline.
        
        Args:
            sequence: List of dicts with 'symbol' and 'estimated_lag_hours'
            source_asset: Source asset name
            title: Chart title
            save_path: Path to save figure
        """
        # ✅ VALIDATION: Check if data exists
        if not self._validate_data(sequence, "timeline"):
            return
        
        # If no save_path provided, use default
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'timeline.png')
        
        try:
            fig, ax = plt.subplots(figsize=(12, 4))
            
            # Build timeline
            events = [(source_asset, 0, 'source')]
            max_lag = 0
            
            for item in sequence:
                events.append((item['symbol'], item['estimated_lag_hours'], 'target'))
                max_lag = max(max_lag, item['estimated_lag_hours'])
            
            # Colors
            colors = ['#333333'] + plt.cm.RdYlGn_r(np.linspace(0, 1, len(sequence))).tolist()
            
            # Plot timeline
            y_pos = 0
            for i, (asset, lag, typ) in enumerate(events):
                color = '#ff4444' if typ == 'source' else colors[i]
                
                ax.plot([0, lag], [y_pos, y_pos], 'o-', color=color, linewidth=2, markersize=10)
                ax.text(lag + 0.5, y_pos, f'{asset} (+{lag:.0f}h)', va='center', fontsize=11)
                y_pos += 1
            
            ax.set_xlabel('Hours After Source Stress', fontsize=12)
            ax.set_yticks([])
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlim(-1, max_lag + 3)
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add arrow
            ax.annotate('', xy=(max_lag, -0.5), xytext=(0, -0.5),
                       arrowprops=dict(arrowstyle='->', color='gray', lw=1))
            
            plt.tight_layout()
            
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            else:
                plt.show()
            
            plt.close(fig)
            
        except Exception as e:
            print(f"   ⚠️ Error generating timeline chart: {e}")
    
    def create_demo_figure(
        self,
        predicted_sequence: List[Dict],
        impact_scores: List[Dict],
        source_asset: str = "BTC",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Create a combined figure for demo video.
        
        Combines sequence timeline and impact scores in one figure.
        """
        # ✅ VALIDATION: Check if data exists
        if not self._validate_data(predicted_sequence, "sequence"):
            return
        if not self._validate_data(impact_scores, "impact score"):
            return
        
        # If no save_path provided, use default
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'combined_demo.png')
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Left: Timeline
            events = [(source_asset, 0)]
            for item in predicted_sequence:
                events.append((item['symbol'], item['estimated_lag_hours']))
            
            y_pos = range(len(events))
            lags = [e[1] for e in events]
            symbols = [e[0] for e in events]
            
            colors = ['#ff4444'] + plt.cm.Blues(np.linspace(0.4, 0.9, len(events)-1)).tolist()
            
            ax1.scatter(lags, y_pos, c=colors, s=200, zorder=3)
            for i, (lag, sym) in enumerate(zip(lags, symbols)):
                ax1.annotate(sym, (lag + 0.3, i), va='center', fontsize=10)
            
            ax1.set_xlabel('Hours After Source Stress', fontsize=11)
            ax1.set_yticks([])
            ax1.set_title('Contagion Timeline', fontsize=12, fontweight='bold')
            ax1.set_xlim(-1, max(lags) + 3)
            ax1.grid(True, alpha=0.3, axis='x')
            
            # Right: Impact scores
            sorted_scores = sorted(impact_scores, key=lambda x: x['impact_score'], reverse=True)
            symbols_r = [s['symbol'] for s in sorted_scores]
            scores = [s['impact_score'] for s in sorted_scores]
            
            signal_colors = {'EXIT_NOW': '#ff4444', 'REDUCE': '#ff8800', 
                            'WATCH': '#ffcc00', 'HOLD': '#44ff44'}
            colors_r = [signal_colors.get(s.get('signal', 'WATCH'), '#888888') for s in sorted_scores]
            
            bars = ax2.barh(symbols_r, scores, color=colors_r, alpha=0.8)
            
            for bar, score in zip(bars, scores):
                ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                        f'{score:.2f}', va='center', fontsize=10)
            
            ax2.set_xlabel('Impact Score', fontsize=11)
            ax2.set_title('Impact Scores by Asset', fontsize=12, fontweight='bold')
            ax2.set_xlim(0, 1)
            ax2.grid(True, alpha=0.3, axis='x')
            
            plt.suptitle('Cross-Asset Contagion Sequencer - Prediction Summary', 
                        fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            else:
                plt.show()
            
            plt.close(fig)
            
        except Exception as e:
            print(f"   ⚠️ Error creating combined figure: {e}")
    
    def generate_all_charts(
        self,
        predicted_sequence: List[Dict],
        impact_scores: List[Dict],
        source_asset: str = "BTC",
        event_name: str = "Contagion Event",
        timestamp: Optional[str] = None,
    ) -> None:
        """
        Generate all charts at once for hackathon submission.
        
        Args:
            predicted_sequence: List of dicts with sequence data
            impact_scores: List of dicts with impact scores
            source_asset: Source asset name
            event_name: Name of the event for file naming
            timestamp: Optional timestamp for unique filenames
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        safe_name = event_name.lower().replace(" ", "_").replace("/", "_")[:30]
        
        print(f"\n   🎨 Generating all charts for: {event_name}")
        print("   " + "-" * 40)
        
        # Generate each chart
        self.plot_contagion_sequence(
            predicted_sequence,
            title=f"{event_name}: Contagion Sequence",
            save_path=os.path.join(self.save_dir, f'{safe_name}_sequence_{timestamp}.png')
        )
        
        self.plot_impact_scores(
            impact_scores,
            title=f"{event_name}: Impact Scores",
            save_path=os.path.join(self.save_dir, f'{safe_name}_impact_{timestamp}.png')
        )
        
        self.plot_timeline(
            predicted_sequence,
            source_asset=source_asset,
            title=f"{event_name}: Spread Timeline",
            save_path=os.path.join(self.save_dir, f'{safe_name}_timeline_{timestamp}.png')
        )
        
        self.create_demo_figure(
            predicted_sequence,
            impact_scores,
            source_asset=source_asset,
            save_path=os.path.join(self.save_dir, f'{safe_name}_combined_{timestamp}.png')
        )
        
        print(f"   ✅ All charts saved to: {self.save_dir}/")


# Quick test (requires matplotlib)
if __name__ == "__main__":
    # Sample data
    predicted = [
        {'symbol': 'ETH', 'estimated_lag_hours': 2, 'impact_score': 0.94, 'signal': 'EXIT_NOW'},
        {'symbol': 'BNB', 'estimated_lag_hours': 5, 'impact_score': 0.88, 'signal': 'EXIT_NOW'},
        {'symbol': 'CAKE', 'estimated_lag_hours': 9, 'impact_score': 0.71, 'signal': 'REDUCE'},
        {'symbol': 'LINK', 'estimated_lag_hours': 14, 'impact_score': 0.58, 'signal': 'WATCH'},
        {'symbol': 'ADA', 'estimated_lag_hours': 18, 'impact_score': 0.52, 'signal': 'WATCH'},
    ]
    
    impact_data = [
        {'symbol': 'ETH', 'impact_score': 0.94, 'signal': 'EXIT_NOW'},
        {'symbol': 'BNB', 'impact_score': 0.88, 'signal': 'EXIT_NOW'},
        {'symbol': 'CAKE', 'impact_score': 0.71, 'signal': 'REDUCE'},
        {'symbol': 'LINK', 'impact_score': 0.58, 'signal': 'WATCH'},
        {'symbol': 'ADA', 'impact_score': 0.52, 'signal': 'WATCH'},
    ]
    
    # Test with new features
    viz = ContagionVisualizer(style='dark_background', save_dir='demo/images')
    
    # Generate all charts at once
    viz.generate_all_charts(
        predicted,
        impact_data,
        source_asset='BTC',
        event_name='FTX Collapse Test'
    )
    
    print("\n✅ Demo complete! Check demo/images/ for all charts.")
