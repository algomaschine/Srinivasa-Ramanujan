"""
Streamlit App: Western vs Daoist Cycle Detection
-------------------------------------------------
A side-by-side comparison of two mathematical philosophies:
1. Western: Cycles as sums of sine waves (Fourier/Goertzel)
2. Daoist: Cycles as dialectical tension of opposites (Yin-Yang)

Supports CSV upload with columns: Date, Open, High, Low, Close, Volume
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from daoist_cycle import DaoistCycle
from daoist_forward_eval import DaoistForwardEvaluator
import io

# Page config
st.set_page_config(page_title="Daoist Cycle Scanner", layout="wide")

st.title("🌊 Western vs Daoist Cycle Detection")
st.markdown("""
This app compares two fundamentally different mathematical approaches to finding cycles:
- **Western Math**: Assumes cycles are harmonic waves. Asks *"What is the period?"*
- **Daoist Math**: Assumes cycles are transformations of opposites. Asks *"Where is the tension?"*

**Upload your own data** (CSV with columns: Date, Open, High, Low, Close, Volume) or use synthetic data below.
""")

# File uploader
st.sidebar.header("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

use_synthetic = False
if uploaded_file is not None:
    try:
        # Read CSV
        df_raw = pd.read_csv(uploaded_file)
        
        # Normalize column names (lowercase, strip spaces)
        df_raw.columns = [c.lower().strip() for c in df_raw.columns]
        
        # Check required columns
        required = ['close']
        if not all(col in df_raw.columns for col in required):
            st.error(f"CSV must contain at least these columns: {required}")
            st.stop()
        
        # Parse date if available
        if 'date' in df_raw.columns:
            df_raw['date'] = pd.to_datetime(df_raw['date'])
            df_raw = df_raw.set_index('date')
        
        # Use close price for analysis
        prices = df_raw['close'].values
        n_points = len(prices)
        
        st.success(f"✅ Loaded {n_points} bars from {df_raw.index[0]} to {df_raw.index[-1]}")
        
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()
else:
    # Generate synthetic data
    use_synthetic = True
    st.sidebar.header("🎲 Generate Synthetic Market Data")
    n_points = st.sidebar.slider("Data Points", 100, 1000, 500)
    noise_level = st.sidebar.slider("Noise Level", 0.0, 5.0, 1.5)
    cycle_1_period = st.sidebar.slider("Primary Cycle Period", 10, 100, 40)
    cycle_2_period = st.sidebar.slider("Secondary Cycle Period", 5, 50, 25)
    
    # Generate synthetic data
    np.random.seed(42)
    t = np.linspace(0, 4 * np.pi, n_points)
    # Western view: superposition of sine waves
    signal = (
        np.sin(t * (2 * np.pi / cycle_1_period) * (n_points / (4 * np.pi))) * 10 +
        np.sin(t * (2 * np.pi / cycle_2_period) * (n_points / (4 * np.pi))) * 5 +
        np.random.normal(0, noise_level, n_points)
    )
    prices = 100 + np.cumsum(signal * 0.1)  # Random walk with cyclical drift
    
    # Create DataFrame for synthetic data
    df_raw = pd.DataFrame({
        'close': prices,
        'open': prices + np.random.normal(0, 0.5, n_points),
        'high': prices + np.abs(np.random.normal(0, 1, n_points)),
        'low': prices - np.abs(np.random.normal(0, 1, n_points)),
        'volume': np.random.uniform(100000, 1000000, n_points)
    }, index=pd.date_range(start='2020-01-01', periods=n_points, freq='D'))

daoist_window = st.sidebar.slider("Daoist Lookback Window", 10, 100, 30)

# --- WESTERN APPROACH (Simplified Goertzel-like) ---
def western_cycle_detect(prices, lookback=50):
    """Simple autocorrelation-based period detection (Western style)"""
    if len(prices) < lookback:
        return 0, []
    
    recent = prices[-lookback:]
    corr = np.correlate(recent - np.mean(recent), recent - np.mean(recent), mode='full')
    corr = corr[len(corr)//2:]
    
    # Find peaks in correlation
    peaks = []
    for i in range(1, len(corr)-1):
        if corr[i] > corr[i-1] and corr[i] > corr[i+1] and i > 5:
            peaks.append(i)
    
    dominant_period = peaks[0] if peaks else 0
    return dominant_period, peaks

western_period, western_peaks = western_cycle_detect(prices, lookback=min(100, len(prices)))

# --- DAOIST APPROACH ---
scanner = DaoistCycle(window=daoist_window)
daoist_result = scanner.scan(prices)

# Create DataFrame for plotting (ensure we have a proper index)
if not isinstance(df_raw.index, pd.DatetimeIndex):
    df_raw = df_raw.set_index('date')

df = df_raw.copy()
df['Time'] = range(len(df))  # Keep for color mapping in phase plot
df['TimeIdx'] = df.reset_index().index  # Numeric index for x-axis plots

# Calculate Yin/Yang for visualization
yang, yin = scanner.calculate_polarities(prices)
df['Yang'] = yang
df['Yin'] = yin
df['Tension'] = (yang - yin) / (yang + yin + 1e-9)
df['Phase'] = scanner.compute_wuji_phase(yang, yin)

# =============================================================================
# MAIN PRICE CHART - Interactive Candlestick with Zoom
# =============================================================================
st.subheader("📈 Price Chart (Zoomable & Responsive)")
st.markdown("Use the range slider below the chart to zoom into specific time periods.")

fig_price = go.Figure()

# Check if we have OHLC data
has_ohlc = all(col in df.columns for col in ['open', 'high', 'low', 'close'])

if has_ohlc:
    # Candlestick chart
    fig_price.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='#2ca02c',
        decreasing_line_color='#d62728'
    ))
else:
    # Line chart if no OHLC
    fig_price.add_trace(go.Scatter(
        x=df.index, 
        y=df['close'], 
        mode='lines', 
        name='Price',
        line=dict(color='#1f77b4', width=1)
    ))

fig_price.update_layout(
    height=500,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode='x unified',
    xaxis_rangeslider_visible=True,  # Enable zoom slider
    xaxis_rangeslider_bgcolor='rgba(200,200,200,0.2)',
    xaxis_rangeslider_bordercolor='rgba(100,100,100,0.5)'
)

st.plotly_chart(fig_price, width="stretch")

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏛️ Western View: Harmonic Decomposition")
    st.markdown(f"""
    - **Dominant Period**: `{western_period:.1f}` bars (fixed)
    - **Philosophy**: Time is uniform. Cycles repeat at regular intervals.
    - **Method**: Autocorrelation finds repeating patterns.
    - **Weakness**: Struggles when cycles stretch/compress or when noise is high.
    """)
    
    # Plot Western-style: Price + highlighted周期
    fig_western = go.Figure()
    fig_western.add_trace(go.Scatter(
        x=df.index, y=df['close'], 
        mode='lines', name='Price',
        line=dict(color='#1f77b4', width=1)
    ))
    
    # Mark detected周期
    if western_period > 0:
        fig_western.add_shape(
            type="rect",
            x0=len(prices) - western_period, y0=min(prices),
            x1=len(prices), y1=max(prices),
            fillcolor="green", opacity=0.1,
            line_width=0
        )
        fig_western.add_annotation(
            x=len(prices) - western_period / 2,
            y=max(prices),
            text=f"Detected Period: {western_period:.0f}",
            showarrow=False,
            yshift=10,
            font=dict(color="green", size=12)
        )
    
    fig_western.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time",
        yaxis_title="Price",
        hovermode='x unified'
    )
    st.plotly_chart(fig_western, width="stretch")

with col2:
    st.subheader("☯️ Daoist View: Dialectical Tension")
    st.markdown(f"""
    - **Current State**: `{daoist_result['interpretation']}`
    - **Elastic Period**: `{daoist_result['dominant_elastic_period']:.1f}` bars (dynamic)
    - **Tension**: `{daoist_result['current_tension']:.3f}` 
      ({'Yang Dominant' if daoist_result['current_tension'] > 0 else 'Yin Dominant'})
    - **Philosophy**: Time is elastic. Cycles emerge from imbalance correction.
    - **Method**: Tracks Qi flow (accumulated force) between opposites.
    """)
    
    # Plot Daoist-style: Tension gauge + Phase orbit
    fig_daoist = go.Figure()
    
    # Tension over time
    fig_daoist.add_trace(go.Scatter(
        x=df['TimeIdx'], y=df['Tension'],
        mode='lines', name='Yin-Yang Tension',
        line=dict(color='#d62728', width=2),
        fill='tozeroy'
    ))
    
    # Wuji lines
    fig_daoist.add_hline(y=0.2, line_dash="dash", line_color="gray", opacity=0.5, annotation_text="Wuji Zone", annotation_position="right")
    fig_daoist.add_hline(y=-0.2, line_dash="dash", line_color="gray", opacity=0.5)
    fig_daoist.add_hline(y=0.6, line_dash="dot", line_color="orange", opacity=0.5, annotation_text="Extreme Yang", annotation_position="right")
    fig_daoist.add_hline(y=-0.6, line_dash="dot", line_color="blue", opacity=0.5, annotation_text="Extreme Yin", annotation_position="right")
    
    fig_daoist.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time",
        yaxis_title="Tension (Yang - Yin)",
        yaxis_range=[-1, 1],
        hovermode='x unified'
    )
    st.plotly_chart(fig_daoist, width="stretch")

# Third row: Phase Space Visualization
st.subheader("🌀 Phase Space: The Taijitu Orbit")
st.markdown("""
In Daoist math, the system moves on a circular path (Taijitu). 
- **Right side** = Yang dominant (price rising energy)
- **Left side** = Yin dominant (price falling energy)  
- **Top/Bottom** = Wuji (pivot points where direction changes)

Watch how the orbit is NOT a perfect circle — it breathes and distorts based on market Qi.
""")

# Create phase plot
phase_x = np.cos(df['Phase'])
phase_y = np.sin(df['Phase'])

fig_phase = go.Figure()

# Plot orbit
fig_phase.add_trace(go.Scatter(
    x=phase_x, y=phase_y,
    mode='lines+markers',
    name='System Orbit',
    line=dict(color='#2ca02c', width=2),
    marker=dict(size=3, color=df['Time'], colorscale='Viridis', showscale=True)
))

# Add reference circles
theta = np.linspace(0, 2*np.pi, 100)
fig_phase.add_trace(go.Scatter(
    x=np.cos(theta), y=np.sin(theta),
    mode='lines',
    name='Perfect Balance Circle',
    line=dict(color='gray', dash='dash', width=1),
    opacity=0.3
))

# Label the quadrants
fig_phase.add_annotation(x=1.1, y=0, text="Pure Yang", showarrow=False, font=dict(color='#d62728'))
fig_phase.add_annotation(x=-1.1, y=0, text="Pure Yin", showarrow=False, font=dict(color='#1f77b4'))
fig_phase.add_annotation(x=0, y=1.1, text="Wuji → Yin", showarrow=False, font=dict(color='purple'))
fig_phase.add_annotation(x=0, y=-1.1, text="Wuji → Yang", showarrow=False, font=dict(color='orange'))

# Current position marker
fig_phase.add_trace(go.Scatter(
    x=[phase_x.iloc[-1]], y=[phase_y.iloc[-1]],
    mode='markers',
    name='Current State',
    marker=dict(size=15, color='red', symbol='star')
))

fig_phase.update_layout(
    height=500,
    width=500,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_title="Yang Axis",
    yaxis_title="Yin Axis",
    xaxis_range=[-1.5, 1.5],
    yaxis_range=[-1.5, 1.5],
    shape_type='circle'
)

st.plotly_chart(fig_phase, width="content")

# Conclusion
st.markdown("---")
st.subheader("🧠 Key Insights")
st.markdown(f"""
1. **Period Variability**: 
   - Western detected: `{western_period:.1f}` (static)
   - Daoist detected: `{daoist_result['dominant_elastic_period']:.1f}` ± `{np.std(daoist_result['detected_periods']) if daoist_result['detected_periods'] else 0:.1f}` (dynamic)
   
2. **State Awareness**: 
   The Daoist approach tells you *where* you are in the cycle (Wuji, Extreme Yang, etc.), 
   not just *how long* the cycle is.

3. **Noise Philosophy**:
   - Western: Noise obscures the true signal.
   - Daoist: Noise IS the signal — it's the texture of Qi flow.

4. **Practical Use**:
   When `abs(Tension) > 0.6`, the system is overextended → expect reversion.
   When `abs(Tension) < 0.2`, the system is at Wuji → expect breakout but direction unknown.
""")


# =============================================================================
# FORWARD WALK EVALUATION SECTION
# =============================================================================
st.markdown("---")
st.header("🔮 Forward-Walk Evaluation (Real-Time Simulation)")
st.markdown("""
This section evaluates the Daoist indicator in **strict forward-walk mode**:
- At each bar `t`, the system only knows history up to `t` (no look-ahead bias)
- The "Elastic Period" adapts dynamically as new Wuji crossings are detected
- Trades are simulated: Enter at extremes, exit at Wuji or reversal

**Philosophy**: We don't predict the future; we react to the present state of tension.
""")

# Run forward walk
evaluator = DaoistForwardEvaluator(
    initial_lookback=daoist_window * 2,
    min_lookback=20,
    max_lookback=100
)

fw_results = evaluator.run_forward_walk(df[['Close']])
report = evaluator.generate_report(fw_results)

# Display metrics
col_metrics = st.columns(5)
with col_metrics[0]:
    st.metric("Total Return", f"{report['Total_Return']*100:.1f}%")
with col_metrics[1]:
    st.metric("Win Rate", f"{report['Win_Rate']*100:.1f}%")
with col_metrics[2]:
    st.metric("Avg Win", f"{report['Avg_Win']*100:.2f}%")
with col_metrics[3]:
    st.metric("Avg Loss", f"{report['Avg_Loss']*100:.2f}%")
with col_metrics[4]:
    st.metric("Max Drawdown", f"{report['Max_Drawdown']*100:.1f}%")

# Plot equity curve and elastic period evolution
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(
        x=fw_results.index, 
        y=fw_results['Cumulative_PnL'],
        mode='lines',
        name='Cumulative PnL',
        line=dict(color='#2ca02c', width=2)
    ))
    fig_equity.add_hline(y=1.0, line_dash="dash", line_color="gray", opacity=0.5)
    fig_equity.update_layout(
        title="Strategy Equity Curve (Forward Walk)",
        xaxis_title="Time",
        yaxis_title="Cumulative Return",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_equity, width="stretch")

with col_chart2:
    fig_period = go.Figure()
    fig_period.add_trace(go.Scatter(
        x=fw_results.index,
        y=fw_results['Elastic_Period'],
        mode='lines',
        name='Elastic Period',
        line=dict(color='#ff7f0e', width=2),
        fill='tozeroy'
    ))
    fig_period.update_layout(
        title="Elastic Period Evolution (Adapts Over Time)",
        xaxis_title="Time",
        yaxis_title="Period (bars)",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_period, width="stretch")

# Detailed view with signals
st.subheader("📊 Signal Detail View")
st.markdown("""
- **Green dots**: Long entry (Yin exhausted, tension rising from extreme)
- **Red dots**: Short entry (Yang exhausted, tension falling from extreme)
- **Gray zone**: Tension near Wuji (exit zone / no position)
""")

fig_signals = go.Figure()

# Price chart
fig_signals.add_trace(go.Scatter(
    x=fw_results.index,
    y=fw_results['Close'],
    mode='lines',
    name='Price',
    line=dict(color='#1f77b4', width=1)
))

# Mark signals
long_signals = fw_results[fw_results['Daoist_Signal_Raw'] == 1]
short_signals = fw_results[fw_results['Daoist_Signal_Raw'] == -1]

fig_signals.add_trace(go.Scatter(
    x=long_signals.index,
    y=long_signals['Close'],
    mode='markers',
    name='Long Entry',
    marker=dict(color='green', size=10, symbol='triangle-up')
))

fig_signals.add_trace(go.Scatter(
    x=short_signals.index,
    y=short_signals['Close'],
    mode='markers',
    name='Short Entry',
    marker=dict(color='red', size=10, symbol='triangle-down')
))

fig_signals.update_layout(
    title="Price with Daoist Entry Signals",
    xaxis_title="Time",
    yaxis_title="Price",
    height=400,
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode='x unified'
)

st.plotly_chart(fig_signals, width="stretch")

# Tension with position overlay
fig_tension_pos = go.Figure()

fig_tension_pos.add_trace(go.Scatter(
    x=fw_results.index,
    y=fw_results['Daoist_Tension'],
    mode='lines',
    name='Tension',
    line=dict(color='#d62728', width=1),
    opacity=0.7
))

# Color-code by position
for pos_val, color, name in [(1, 'green', 'Long'), (-1, 'red', 'Short'), (0, 'gray', 'Flat')]:
    mask = fw_results['Position'] == pos_val
    if mask.any():
        fig_tension_pos.add_trace(go.Scatter(
            x=fw_results.index[mask],
            y=fw_results.loc[mask, 'Daoist_Tension'],
            mode='markers',
            name=f'{name} Position',
            marker=dict(color=color, size=4),
            opacity=0.5
        ))

fig_tension_pos.add_hline(y=0.6, line_dash="dot", line_color="orange", opacity=0.5, annotation_text="Extreme Yang", annotation_position="right")
fig_tension_pos.add_hline(y=-0.6, line_dash="dot", line_color="blue", opacity=0.5, annotation_text="Extreme Yin", annotation_position="right")
fig_tension_pos.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3, annotation_text="Wuji", annotation_position="right")

fig_tension_pos.update_layout(
    title="Tension with Active Positions",
    xaxis_title="Time",
    yaxis_title="Tension",
    yaxis_range=[-1, 1],
    height=300,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig_tension_pos, width="stretch")

# Export data
st.subheader("📥 Export Results")
csv_data = fw_results.to_csv(index=False)
st.download_button(
    label="Download Full Results (CSV)",
    data=csv_data,
    file_name="daoist_forward_walk_results.csv",
    mime="text/csv"
)

st.markdown("""
### 🧠 Interpretation Guide

**Why Forward Walk Matters:**
Most indicators cheat by using future data (repainting). This simulation proves the Daoist approach 
works in real-time because:
1. The Elastic Period changes as new data arrives (it's not fixed)
2. Signals are generated only from known history
3. Exits happen at logical points (Wuji balance or reversal)

**What Makes This "Daoist":**
- The system doesn't assume a fixed cycle length — it breathes with the market
- Entries happen at dialectical extremes (too much Yang creates Yin, too much Yin creates Yang)
- Exits happen at Wuji (balance) — taking profit when tension dissipates
""")
