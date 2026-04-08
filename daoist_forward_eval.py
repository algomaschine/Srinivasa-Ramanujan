"""
daoist_forward_eval.py

A rigorous forward-walk evaluation module for the Daoist Cycle Scanner.
This module simulates real-time trading by iterating through data one bar at a time,
recalculating the "elastic period" and generating signals without look-ahead bias.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
import warnings

warnings.filterwarnings('ignore')

class DaoistForwardEvaluator:
    """
    Evaluates the Daoist Cycle Indicator in a strict forward-walk manner.
    
    Philosophy:
    - At any time t, the system only knows history up to t.
    - The "Cycle Length" is not fixed; it is estimated dynamically from recent Wuji returns.
    - Signals are generated when the system moves from Extreme Yin/Yang back toward Wuji.
    """
    
    def __init__(self, initial_lookback: int = 40, min_lookback: int = 10, max_lookback: int = 100):
        self.initial_lookback = initial_lookback
        self.min_lookback = min_lookback
        self.max_lookback = max_lookback
        
        # State variables for the walk
        self.current_lookback = initial_lookback
        self.recent_wuji_intervals: List[int] = []
        
    def _calculate_daoist_state(self, prices: pd.Series) -> Tuple[float, float, float]:
        """
        Calculates the current Daoist state (Yang, Yin, Tension) 
        using ONLY the available data up to the current point.
        """
        if len(prices) < 5:
            return 0.0, 0.0, 0.0
            
        returns = prices.pct_change().fillna(0)
        
        # Use adaptive lookback based on current estimate
        lb = int(self.current_lookback)
        if len(returns) < lb:
            lb = len(returns)
            
        recent_returns = returns.iloc[-lb:]
        
        # Yang Force: Sum of positive returns normalized
        yang_force = recent_returns[recent_returns > 0].sum()
        # Yin Force: Sum of negative returns normalized (absolute value)
        yin_force = abs(recent_returns[recent_returns < 0].sum())
        
        # Normalize to [-1, 1] range (Tension)
        total_force = yang_force + yin_force
        if total_force == 0:
            tension = 0.0
        else:
            tension = (yang_force - yin_force) / total_force
            
        return yang_force, yin_force, tension

    def _update_elastic_period(self, current_index: int, wuji_crossings: List[int]):
        """
        Updates the internal 'elastic period' estimate based on the time between recent Wuji crossings.
        This mimics the Daoist concept that cycle length breathes and changes.
        """
        if len(wuji_crossings) >= 2:
            # Calculate intervals between the last few crossings
            intervals = [wuji_crossings[i] - wuji_crossings[i-1] 
                        for i in range(1, len(wuji_crossings))]
            
            # Keep only recent intervals (last 3 cycles)
            recent_intervals = intervals[-3:]
            
            if recent_intervals:
                median_interval = np.median(recent_intervals)
                # Smoothly adjust the lookback window
                new_lookback = int(median_interval * 2) # Full cycle is usually 2x half-cycle
                
                # Clamp to reasonable bounds
                self.current_lookback = max(self.min_lookback, min(self.max_lookback, new_lookback))

    def run_forward_walk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes the forward walk simulation.
        
        Args:
            df: DataFrame with 'Close' prices (and optionally 'High', 'Low')
            
        Returns:
            DataFrame with added columns: 
            - 'Daoist_Tension', 'Daoist_Signal', 'Elastic_Period', 'Trade_Return'
        """
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain a 'Close' column")
            
        prices = df['Close'].copy()
        n = len(prices)
        
        # Result containers
        tension_log = []
        signal_log = [] # 1 = Long Entry, -1 = Short Entry, 0 = Hold
        period_log = []
        position_log = [] # 1 = Long, -1 = Short, 0 = Flat
        
        # State tracking
        current_position = 0
        entry_price = 0.0
        wuji_crossings = [] # Indices where tension crossed 0
        
        # Thresholds for "Extreme" states (Entry triggers)
        # In Daoist math, we enter when the extreme starts reverting to Wuji
        EXTREME_THRESHOLD = 0.6 
        
        for i in range(n):
            # Get data up to NOW (inclusive)
            current_prices = prices.iloc[:i+1]
            
            # 1. Calculate State
            yang, yin, tension = self._calculate_daoist_state(current_prices)
            
            # 2. Detect Wuji Crossings (Tension crossing 0)
            # We need previous tension to detect crossing
            prev_tension = tension_log[-1] if tension_log else 0
            
            if (prev_tension > 0 and tension <= 0) or (prev_tension < 0 and tension >= 0):
                wuji_crossings.append(i)
                
            # 3. Update Elastic Period based on history so far
            self._update_elastic_period(i, wuji_crossings)
            
            # 4. Generate Signals
            # Logic: 
            # - If Tension was > Extreme and now dropping -> Short (Yang exhausted)
            # - If Tension was < -Extreme and now rising -> Long (Yin exhausted)
            # Note: We use a slight lag check to confirm reversal
            
            signal = 0
            if i > 5: # Need some history
                # Check extreme conditions
                if prev_tension > EXTREME_THRESHOLD and tension < prev_tension:
                    signal = -1 # Short signal
                elif prev_tension < -EXTREME_THRESHOLD and tension > prev_tension:
                    signal = 1 # Long signal
            
            # 5. Simulate Trade Execution (Simple strategy)
            # Enter on signal, exit on opposite signal or Wuji cross
            trade_return = 0.0
            
            if signal != 0 and current_position == 0:
                # Open position
                current_position = signal
                entry_price = prices.iloc[i]
            elif current_position != 0:
                # Check for exit conditions
                # Exit if signal reverses OR if we hit Wuji (tension ~ 0)
                should_exit = False
                
                if signal == -current_position:
                    should_exit = True # Reversal signal
                elif abs(tension) < 0.1 and current_position != 0:
                    should_exit = True # Reached balance (Wuji), take profit
                    
                if should_exit:
                    exit_price = prices.iloc[i]
                    if current_position == 1: # Long
                        trade_return = (exit_price - entry_price) / entry_price
                    else: # Short
                        trade_return = (entry_price - exit_price) / entry_price
                    
                    current_position = 0
                    entry_price = 0.0
            
            # Log results
            tension_log.append(tension)
            signal_log.append(signal)
            period_log.append(self.current_lookback)
            position_log.append(current_position)
            
        # Construct results DataFrame
        results = df.copy()
        results['Daoist_Tension'] = tension_log
        results['Daoist_Signal_Raw'] = signal_log
        results['Elastic_Period'] = period_log
        results['Position'] = position_log
        
        # Calculate cumulative returns for the strategy
        # Shift position by 1 to avoid lookahead (signal at close i executes at open i+1)
        # For simplicity in this demo, we assume execution at close of signal bar
        results['Strategy_Returns'] = results['Position'].shift(1) * results['Close'].pct_change()
        results['Cumulative_PnL'] = (1 + results['Strategy_Returns'].fillna(0)).cumprod()
        
        return results

    def generate_report(self, results: pd.DataFrame) -> Dict:
        """Generates a performance summary report."""
        if 'Cumulative_PnL' not in results.columns:
            raise ValueError("Must run forward_walk first")
            
        returns = results['Strategy_Returns'].dropna()
        pnl = results['Cumulative_PnL'].iloc[-1]
        
        # Calculate metrics
        total_trades = (results['Position'].diff() != 0).sum() // 2 # Approximate
        
        win_mask = returns > 0
        loss_mask = returns < 0
        
        avg_win = returns[win_mask].mean() if win_mask.any() else 0
        avg_loss = returns[loss_mask].mean() if loss_mask.any() else 0
        
        max_dd = (results['Cumulative_PnL'] / results['Cumulative_PnL'].cummax() - 1).min()
        
        return {
            "Total_Return": pnl - 1,
            "Total_Trades_Estimated": total_trades,
            "Avg_Win": avg_win,
            "Avg_Loss": avg_loss,
            "Win_Rate": len(returns[win_mask]) / len(returns) if len(returns) > 0 else 0,
            "Max_Drawdown": max_dd,
            "Final_Elastic_Period": results['Elastic_Period'].iloc[-1]
        }

def plot_equity_curve(results: pd.DataFrame):
    """Helper to prepare data for plotting equity curve."""
    return results[['Close', 'Cumulative_PnL', 'Elastic_Period']]
