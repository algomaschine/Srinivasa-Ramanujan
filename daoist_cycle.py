"""
Daoist Cycle Detection Module
-----------------------------
A speculative mathematical approach to cycle detection based on 
Yin-Yang dialectics rather than Fourier decomposition.

Core Axioms:
1. Cycles are driven by the tension of opposites, not harmonic waves.
2. Time is elastic: Periods stretch/compress based on internal pressure.
3. The "Wuji Point" (balance) is the true predictor of turns, not peaks.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List

class DaoistCycle:
    def __init__(self, window: int = 20):
        """
        Initialize the Daoist Scanner.
        
        Args:
            window: The lookback period for measuring Yin/Yang accumulation.
        """
        self.window = window
        self.yang_history = []
        self.yin_history = []
        
    def calculate_polarities(self, prices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Decompose price action into Yang (expansion) and Yin (contraction) forces.
        Unlike Western math which sees 'noise', we see 'Qi flow'.
        """
        # Simple heuristic: Momentum and Range define the polarity
        diffs = np.diff(prices)
        # Pad to match length
        diffs = np.insert(diffs, 0, 0)
        
        # Yang: Upward momentum + Green candles (simplified here as positive diff)
        yang_force = np.where(diffs > 0, np.abs(diffs), 0)
        
        # Yin: Downward momentum + Red candles
        yin_force = np.where(diffs < 0, np.abs(diffs), 0)
        
        # Smooth with a rolling sum to represent "accumulated Qi"
        df = pd.DataFrame({'yang': yang_force, 'yin': yin_force})
        yang_accum = df['yang'].rolling(window=self.window, min_periods=1).sum().values
        yin_accum = df['yin'].rolling(window=self.window, min_periods=1).sum().values
        
        return yang_accum, yin_accum

    def compute_wuji_phase(self, yang: np.ndarray, yin: np.ndarray) -> np.ndarray:
        """
        Map the system state to the Taijitu (Unit Circle).
        
        Returns an angle theta:
        0 rad       = Pure Yang (Overextended Up)
        pi/2 rad    = Wuji (Transitioning to Yin)
        pi rad      = Pure Yin (Overextended Down)
        3pi/2 rad   = Wuji (Transitioning to Yang)
        """
        # Avoid division by zero
        total_force = yang + yin + 1e-9
        
        # Normalize to [0, 1] where 1 is pure Yang, 0 is pure Yin
        ratio = yang / total_force
        
        # Map ratio to circle. 
        # We use a specific mapping where the 'turn' happens at the equator (Wuji)
        # 0.5 ratio = Wuji. 
        # We map 0.5 -> pi/2 (top of circle) and 0.5 -> 3pi/2 (bottom)?
        # Actually, let's map simple phase:
        # If Yang > Yin, we are in upper hemisphere.
        
        # Phase angle using atan2 for smooth circular representation
        # Center the forces around their mean to find the 'orbit'
        phase = np.arctan2(yang - np.mean(yang), yin - np.mean(yin))
        
        return phase

    def detect_elastic_period(self, phase: np.ndarray) -> List[int]:
        """
        Detect cycles not by fixed wavelength, but by 'Return to Wuji'.
        
        In Daoist math, a cycle is complete when the system passes through
        the state of maximum uncertainty (Wuji) twice in the same direction.
        """
        # Wuji crossings occur when phase crosses 0 or pi (depending on orientation)
        # Let's detect zero-crossings of the derivative of the phase (velocity change)
        # Or simply when Yang == Yin (ratio ~ 0.5)
        
        # Simplified: Detect when the system swings from Yang-dominant to Yin-dominant
        # This is the 'Half-Cycle'. Full cycle is Yang->Yin->Yang.
        
        periods = []
        last_cross_idx = None
        state = None # 'YANG_DOMINANT' or 'YIN_DOMINANT'
        
        # Determine initial state
        if len(phase) == 0:
            return periods
            
        # We use the sine of the phase to detect equator crossings
        # When sin(phase) crosses 0, we are at Wuji
        equator_signal = np.sin(phase)
        
        for i in range(1, len(equator_signal)):
            prev_val = equator_signal[i-1]
            curr_val = equator_signal[i]
            
            # Detect crossing
            if prev_val * curr_val < 0:
                current_state = 'YANG_TO_YIN' if prev_val > 0 else 'YIN_TO_YANG'
                
                if state is not None and state != current_state:
                    # Completed a half-cycle, now looking for full
                    pass
                
                if last_cross_idx is not None:
                    period_length = i - last_cross_idx
                    periods.append(period_length)
                
                last_cross_idx = i
                state = current_state
                
        return periods

    def scan(self, prices: np.ndarray) -> dict:
        """
        Main entry point. Returns the 'Daoist View' of the market.
        """
        yang, yin = self.calculate_polarities(prices)
        phase = self.compute_wuji_phase(yang, yin)
        periods = self.detect_elastic_period(phase)
        
        # Current State Analysis
        current_tension = (yang[-1] - yin[-1]) / (yang[-1] + yin[-1] + 1e-9)
        current_phase = phase[-1]
        
        # Interpretation
        interpretation = ""
        if abs(current_tension) > 0.6:
            interpretation = "EXTREME IMBALANCE (Reversion Imminent)"
        elif abs(current_tension) < 0.2:
            interpretation = "WUJI STATE (High Uncertainty/Pivot Zone)"
        else:
            interpretation = "FLOWING TRANSITION"
            
        avg_period = np.mean(periods) if periods else 0
        
        return {
            "current_tension": float(current_tension),
            "phase_angle": float(current_phase),
            "dominant_elastic_period": float(avg_period),
            "detected_periods": periods,
            "interpretation": interpretation,
            "yang_strength": float(yang[-1]),
            "yin_strength": float(yin[-1])
        }

# Example Usage within a Streamlit context (Mock Data)
if __name__ == "__main__":
    # Generate synthetic 'market' data with varying cycles
    np.random.seed(42)
    t = np.linspace(0, 100, 500)
    # Superposition of two sine waves with noise (The Western View)
    price = 100 + np.sin(t * 0.1) * 10 + np.sin(t * 0.05) * 20 + np.random.normal(0, 2, 500)
    
    scanner = DaoistCycle(window=30)
    result = scanner.scan(price)
    
    print("--- DAOIST CYCLE ANALYSIS ---")
    print(f"Current Tension (Yang-Yin): {result['current_tension']:.4f}")
    print(f"System State: {result['interpretation']}")
    print(f"Elastic Period Detected: {result['dominant_elastic_period']:.2f} bars")
    print(f"Recent Period Variance: {np.std(result['detected_periods']) if result['detected_periods'] else 0:.2f}")
    print("\nNote: Unlike Fourier, this period changes dynamically as tension builds.")
