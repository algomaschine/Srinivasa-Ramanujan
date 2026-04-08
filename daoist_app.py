"""
Streamlit App: Western vs Daoist Cycle Detection
-------------------------------------------------
A side-by-side comparison of two mathematical philosophies:
1. Western: Cycles as sums of sine waves (Fourier/Goertzel)
2. Daoist: Cycles as dialectical tension of opposites (Yin-Yang)
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from daoist_cycle import DaoistCycle

# Page config
st.set_page_config(page_title="Daoist Cycle Scanner", layout="wide")

st.title("🌊 Western vs Daoist Cycle Detection")
st.markdown("""
This app compares two fundamentally different mathematical approaches to finding cycles:
- **Western Math**: Assumes cycles are harmonic waves. Asks *"What is the period?"*
- **Daoist Math**: Assumes cycles are transformations of opposites. Asks *"Where is the tension?"*
""")

# Sidebar controls
st.sidebar.header("Generate Synthetic Market Data")
n_points = st.sidebar.slider("Data Points", 100, 1000, 500)
noise_level = st.sidebar.slider("Noise Level", 0.0, 5.0, 1.5)
cycle_1_period = st.sidebar.slider("Primary Cycle Period", 10, 100, 40)
cycle_2_period = st.sidebar.slider("Secondary Cycle Period", 5, 50, 25)
daoist_window = st.sidebar.slider("Daoist Lookback Window", 10, 100, 30)

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

# Create DataFrame for plotting
df = pd.DataFrame({
    'Price': prices,
    'Time': range(len(prices))
})

# Calculate Yin/Yang for visualization
yang, yin = scanner.calculate_polarities(prices)
df['Yang'] = yang
df['Yin'] = yin
df['Tension'] = (yang - yin) / (yang + yin + 1e-9)
df['Phase'] = scanner.compute_wuji_phase(yang, yin)

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
        x=df['Time'], y=df['Price'], 
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
            line_width=0,
            annotation_text=f"Detected Period: {western_period:.0f}",
            annotation_position="top"
        )
    
    fig_western.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time",
        yaxis_title="Price",
        hovermode='x unified'
    )
    st.plotly_chart(fig_western, use_container_width=True)

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
        x=df['Time'], y=df['Tension'],
        mode='lines', name='Yin-Yang Tension',
        line=dict(color='#d62728', width=2),
        fill='tozeroy'
    ))
    
    # Wuji lines
    fig_daoist.add_hline(y=0.2, line_dash="dash", line_color="gray", opacity=0.5, annotation_text="Wuji Zone")
    fig_daoist.add_hline(y=-0.2, line_dash="dash", line_color="gray", opacity=0.5)
    fig_daoist.add_hline(y=0.6, line_dash="dot", line_color="orange", opacity=0.5, annotation_text="Extreme Yang")
    fig_daoist.add_hline(y=-0.6, line_dash="dot", line_color="blue", opacity=0.5, annotation_text="Extreme Yin")
    
    fig_daoist.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time",
        yaxis_title="Tension (Yang - Yin)",
        yaxis_range=[-1, 1],
        hovermode='x unified'
    )
    st.plotly_chart(fig_daoist, use_container_width=True)

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

st.plotly_chart(fig_phase, use_container_width=False)

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

st.info("💡 **Try This**: Increase the noise level. Notice how the Western period stays fixed 
while the Daoist elastic period adapts? That's the power of dialectical math.")
