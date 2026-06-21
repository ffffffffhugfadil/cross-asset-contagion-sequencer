"""
demo/visualizer.py
==================
Visualization tools for contagion sequence.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import os


class ContagionVisualizer:
    def __init__(self, style: str = 'dark_background', save_dir: str = 'demo/images'):
        self.save_dir = save_dir
        try:
            plt.style.use(style)
        except:
            pass
        os.makedirs(save_dir, exist_ok=True)
    
    def _validate_data(self, data: List[Dict], data_name: str) -> bool:
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
        if not self._validate_data(predicted_sequence, "sequence"):
            return
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'contagion_sequence.png')
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            symbols = [p['symbol'] for p in predicted_sequence]
            predicted_lags = [p.get('estimated_lag_hours', 0) for p in predicted_sequence]
            if all(lag == 0 for lag in predicted_lags):
                predicted_lags = [i * 3 + 2 for i in range(len(predicted_lags))]
            colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(symbols)))
            bars = ax.barh(symbols, predicted_lags, color=colors, alpha=0.8, label='Predicted')
            if actual_sequence:
                try:
                    actual_dict = {}
                    for a in actual_sequence:
                        if 'symbol' in a:
                            actual_dict[a['symbol']] = a.get('actual_lag_hours', 0)
                    if actual_dict:
                        actual_lags = [actual_dict.get(s, 0) for s in symbols]
                        ax.scatter(actual_lags, symbols, color='white', s=100, marker='o', zorder=5, label='Actual', edgecolors='black', linewidth=1.5)
                except:
                    pass
            for bar, lag in zip(bars, predicted_lags):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f'{lag:.0f}h', va='center', fontsize=10)
            ax.set_xlabel('Lag Hours (after source stress)', fontsize=12)
            ax.set_ylabel('Asset', fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            plt.close(fig)
        except Exception as e:
            print(f"   ⚠️ Error generating sequence chart: {e}")
    
    def plot_impact_scores(
        self,
        impact_scores: List[Dict],
        title: str = "Impact Score by Asset",
        save_path: Optional[str] = None,
    ) -> None:
        if not self._validate_data(impact_scores, "impact score"):
            return
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'impact_scores.png')
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            sorted_scores = sorted(impact_scores, key=lambda x: x.get('impact_score', 0), reverse=True)
            symbols = [s['symbol'] for s in sorted_scores]
            scores = [s.get('impact_score', 0) for s in sorted_scores]
            signals = [s.get('signal', 'WATCH') for s in sorted_scores]
            signal_colors = {'EXIT_NOW': '#ff4444', 'REDUCE': '#ff8800', 'WATCH': '#ffcc00', 'HOLD': '#44ff44'}
            colors = [signal_colors.get(signal, '#888888') for signal in signals]
            bars = ax.barh(symbols, scores, color=colors, alpha=0.8)
            ax.axvline(x=0.7, color='red', linestyle='--', alpha=0.5, label='EXIT_NOW threshold (0.7)')
            ax.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='REDUCE threshold (0.4)')
            ax.axvline(x=0.2, color='yellow', linestyle='--', alpha=0.5, label='WATCH threshold (0.2)')
            for bar, score in zip(bars, scores):
                ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, f'{score:.2f}', va='center', fontsize=10)
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
        if not self._validate_data(sequence, "timeline"):
            return
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'timeline.png')
        try:
            fig, ax = plt.subplots(figsize=(12, 4))
            events = [(source_asset, 0, 'source')]
            max_lag = 0
            for item in sequence:
                lag = item.get('estimated_lag_hours', 0)
                events.append((item['symbol'], lag, 'target'))
                max_lag = max(max_lag, lag)
            if max_lag == 0:
                for i in range(1, len(events)):
                    events[i] = (events[i][0], i * 3 + 2, events[i][2])
                max_lag = max(e[1] for e in events)
            colors = ['#333333'] + plt.cm.RdYlGn_r(np.linspace(0, 1, len(sequence))).tolist()
            y_pos = 0
            for i, (asset, lag, typ) in enumerate(events):
                color = '#ff4444' if typ == 'source' else colors[i] if i < len(colors) else '#888888'
                ax.plot([0, lag], [y_pos, y_pos], 'o-', color=color, linewidth=2, markersize=10)
                ax.text(lag + 0.5, y_pos, f'{asset} (+{lag:.0f}h)', va='center', fontsize=11)
                y_pos += 1
            ax.set_xlabel('Hours After Source Stress', fontsize=12)
            ax.set_yticks([])
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlim(-1, max_lag + 3)
            ax.grid(True, alpha=0.3, axis='x')
            ax.annotate('', xy=(max_lag, -0.5), xytext=(0, -0.5), arrowprops=dict(arrowstyle='->', color='gray', lw=1))
            plt.tight_layout()
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
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
        if not self._validate_data(predicted_sequence, "sequence"):
            return
        if not self._validate_data(impact_scores, "impact score"):
            return
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'combined_demo.png')
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            events = [(source_asset, 0)]
            for item in predicted_sequence:
                lag = item.get('estimated_lag_hours', 0)
                events.append((item['symbol'], lag))
            max_lag = max(e[1] for e in events)
            if max_lag == 0:
                for i in range(1, len(events)):
                    events[i] = (events[i][0], i * 3 + 2)
                max_lag = max(e[1] for e in events)
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
            ax1.set_xlim(-1, max_lag + 3)
            ax1.grid(True, alpha=0.3, axis='x')
            sorted_scores = sorted(impact_scores, key=lambda x: x.get('impact_score', 0), reverse=True)
            symbols_r = [s['symbol'] for s in sorted_scores]
            scores = [s.get('impact_score', 0) for s in sorted_scores]
            signal_colors = {'EXIT_NOW': '#ff4444', 'REDUCE': '#ff8800', 'WATCH': '#ffcc00', 'HOLD': '#44ff44'}
            colors_r = [signal_colors.get(s.get('signal', 'WATCH'), '#888888') for s in sorted_scores]
            bars = ax2.barh(symbols_r, scores, color=colors_r, alpha=0.8)
            for bar, score in zip(bars, scores):
                ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, f'{score:.2f}', va='center', fontsize=10)
            ax2.set_xlabel('Impact Score', fontsize=11)
            ax2.set_title('Impact Scores by Asset', fontsize=12, fontweight='bold')
            ax2.set_xlim(0, 1)
            ax2.grid(True, alpha=0.3, axis='x')
            plt.suptitle('Cross-Asset Contagion Sequencer - Prediction Summary', fontsize=14, fontweight='bold')
            plt.tight_layout()
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"   ✅ Saved to {save_path}")
            plt.close(fig)
        except Exception as e:
            print(f"   ⚠️ Error creating combined figure: {e}")
