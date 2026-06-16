"""
strategy/risk_filter.py
=======================
Risk filters for contagion signals.

Filters signals based on:
- Fear & Greed Index
- Open Interest levels
- Volume confirmation
- Market regime
"""

from typing import Dict, List, Optional, Tuple


class RiskFilter:
    """
    Filter trading signals based on market conditions.
    
    Usage:
        filter = RiskFilter()
        filtered = filter.apply(signals, fear_greed=25, oi_level='high')
    """
    
    def __init__(self):
        """Initialize risk filter with default thresholds."""
        self.fear_greed_thresholds = {
            'extreme_fear': 25,
            'fear': 45,
            'neutral': 55,
            'greed': 75,
            'extreme_greed': 90,
        }
    
    def filter_by_fear_greed(
        self,
        signals: List[Dict],
        fear_greed_index: Optional[int],
    ) -> Tuple[List[Dict], str]:
        """
        Filter signals based on Fear & Greed Index.
        
        Args:
            signals: List of signal dicts
            fear_greed_index: Current Fear & Greed value (0-100)
        
        Returns:
            (filtered_signals, market_condition)
        """
        if fear_greed_index is None:
            return signals, 'unknown'
        
        if fear_greed_index <= self.fear_greed_thresholds['extreme_fear']:
            market_condition = 'extreme_fear'
            # In extreme fear, be more conservative with EXIT_NOW
            # (fear can mean oversold)
            filtered = self._downgrade_signals(signals, downgrade_exit=True)
        elif fear_greed_index >= self.fear_greed_thresholds['extreme_greed']:
            market_condition = 'extreme_greed'
            # In extreme greed, take EXIT_NOW more seriously
            filtered = signals
        elif fear_greed_index <= self.fear_greed_thresholds['fear']:
            market_condition = 'fear'
            filtered = self._downgrade_signals(signals, downgrade_exit=False)
        elif fear_greed_index >= self.fear_greed_thresholds['greed']:
            market_condition = 'greed'
            filtered = signals
        else:
            market_condition = 'neutral'
            filtered = signals
        
        return filtered, market_condition
    
    def _downgrade_signals(
        self,
        signals: List[Dict],
        downgrade_exit: bool = False,
    ) -> List[Dict]:
        """
        Downgrade signals in fearful markets.
        
        EXIT_NOW -> REDUCE or WATCH
        REDUCE -> WATCH
        """
        downgraded = []
        
        for s in signals:
            signal = s['signal']
            
            if downgrade_exit and signal == 'EXIT_NOW':
                new_signal = 'REDUCE'
            elif signal == 'EXIT_NOW':
                new_signal = signal
            elif signal == 'REDUCE':
                new_signal = 'WATCH'
            else:
                new_signal = signal
            
            s_copy = s.copy()
            s_copy['signal'] = new_signal
            s_copy['original_signal'] = signal
            s_copy['filter_applied'] = 'fear_greed'
            downgraded.append(s_copy)
        
        return downgraded
    
    def filter_by_open_interest(
        self,
        signals: List[Dict],
        oi_usd: Optional[float],
        threshold_high: float = 5_000_000_000,  # $5B
    ) -> List[Dict]:
        """
        Amplify or dampen signals based on open interest.
        
        High OI = more liquidation risk = more urgent signals.
        """
        if oi_usd is None:
            return signals
        
        filtered = []
        for s in signals:
            s_copy = s.copy()
            
            if oi_usd > threshold_high and s['signal'] in ['EXIT_NOW', 'REDUCE']:
                # High OI amplifies urgency
                s_copy['signal'] = 'EXIT_NOW' if s['signal'] == 'REDUCE' else s['signal']
                s_copy['oi_amplified'] = True
            elif oi_usd < threshold_high / 10 and s['signal'] == 'EXIT_NOW':
                # Very low OI reduces urgency
                s_copy['signal'] = 'REDUCE'
                s_copy['oi_dampened'] = True
            
            filtered.append(s_copy)
        
        return filtered
    
    def filter_by_volume(
        self,
        signals: List[Dict],
        volume_usd: Optional[float],
        min_volume: float = 10_000_000,  # $10M
    ) -> List[Dict]:
        """
        Filter out signals for low-volume assets.
        """
        if volume_usd is None:
            return signals
        
        filtered = []
        for s in signals:
            if volume_usd < min_volume:
                s_copy = s.copy()
                s_copy['signal'] = 'WATCH'
                s_copy['volume_filtered'] = True
                filtered.append(s_copy)
            else:
                filtered.append(s)
        
        return filtered
    
    def apply(
        self,
        signals: List[Dict],
        fear_greed_index: Optional[int] = None,
        oi_usd: Optional[float] = None,
        volume_usd: Optional[float] = None,
    ) -> Dict:
        """
        Apply all risk filters to signals.
        
        Returns:
            Dict with filtered_signals and applied_filters
        """
        applied_filters = []
        current_signals = signals.copy()
        
        # Apply Fear & Greed filter
        if fear_greed_index is not None:
            current_signals, market_condition = self.filter_by_fear_greed(
                current_signals, fear_greed_index
            )
            applied_filters.append(f'fear_greed_{market_condition}')
        
        # Apply OI filter
        if oi_usd is not None:
            current_signals = self.filter_by_open_interest(current_signals, oi_usd)
            applied_filters.append('open_interest')
        
        # Apply volume filter
        if volume_usd is not None:
            current_signals = self.filter_by_volume(current_signals, volume_usd)
            applied_filters.append('volume')
        
        return {
            'signals': current_signals,
            'applied_filters': applied_filters,
        }


def is_risk_on_environment(
    fear_greed_index: Optional[int],
    btc_dominance: Optional[float],
) -> bool:
    """
    Determine if current environment is risk-on or risk-off.
    
    Returns:
        True if risk-on, False if risk-off
    """
    if fear_greed_index is None:
        return True  # Default to risk-on if unknown
    
    # Risk-on: Greed (55+) or Extreme Greed (75+)
    # Risk-off: Fear (45-) or Extreme Fear (25-)
    return fear_greed_index >= 55
