# Daoist Cycle Scanner

A revolutionary approach to financial cycle detection based on Daoist philosophy rather than traditional Western harmonic analysis.

## 🌊 Philosophy vs Traditional Math

| Aspect | Western Math (Fourier/Goertzel) | Daoist Math (Yin-Yang) |
|--------|--------------------------------|------------------------|
| **Core Question** | "What is the period?" | "Where is the tension?" |
| **Time** | Uniform, linear | Elastic, qualitative |
| **Cycles** | Sine wave superposition | Dialectical opposition (Yin ⇄ Yang) |
| **Noise** | Error to remove | Texture of Qi flow |
| **Prediction** | Linear extrapolation | Reversion from extremes |
| **Output** | Fixed number (e.g., 20 bars) | Dynamic state + elastic range |

## 📦 Installation

### 1. Clone or Download
Ensure you are in the `/workspace` directory containing:
- `daoist_app.py` (Main Streamlit application)
- `daoist_cycle.py` (Core Daoist mathematics engine)
- `daoist_forward_eval.py` (Forward-walk evaluation module)
- `requirements.txt` (Python dependencies)
- `sample_data.csv` (Example OHLCV data)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required Packages:**
- `streamlit` (Interactive web UI)
- `plotly` (Zoomable, responsive charts)
- `pandas` (Data manipulation)
- `numpy` (Numerical operations)
- `scipy` (Signal processing utilities)

### 3. Launch the Application
```bash
streamlit run daoist_app.py
```
The app will open automatically in your browser at `http://localhost:8501` (or the next available port).

## 📊 Usage Guide

### Loading Data
The app accepts CSV files with the following columns (case-insensitive):
- `Date` (YYYY-MM-DD or timestamp)
- `Open`, `High`, `Low`, `Close`
- `Volume` (optional but recommended)

**Example Format:**
```csv
Date,Open,High,Low,Close,Volume
2019-05-26,250.17,269.4,245.11,264.45,450090.22
2019-05-27,264.35,279.59,260.0,270.53,635463.50
```

### Features

#### 1. Interactive Charts
- **Candlestick View**: Zoomable price chart with range slider
- **Western Mode**: Autocorrelation-based cycle detection (fixed period)
- **Daoist Mode**: Yin-Yang tension oscillator (elastic period)
- **Taijitu Orbit**: Phase space visualization of market state

#### 2. Forward-Walk Evaluation
Simulates real-time trading to validate the indicator without look-ahead bias:
- **Metrics**: Total Return, Win Rate, Avg Win/Loss, Max Drawdown
- **Equity Curve**: Cumulative PnL over time
- **Elastic Period Evolution**: Visualizes how the cycle length adapts
- **Export**: Download trade logs as CSV

#### 3. Controls
- **Lookback Window**: Adjust sensitivity (default: 40 bars)
- **Tension Thresholds**: Define extreme zones for entry signals
- **Noise Slider**: Test robustness on synthetic data

## 🧮 How It Works

### The Daoist Engine (`daoist_cycle.py`)
1. **Polarity Decomposition**: Splits price action into Yang (upward force) and Yin (downward force)
2. **Wuji Detection**: Identifies the "still point" where Yin=Yang (maximum uncertainty)
3. **Elastic Period**: Calculates cycle length based on time between Wuji crossings (not fixed!)
4. **Phase Mapping**: Projects state onto the Taijitu (Yin-Yang symbol) for visual intuition

### The Evaluator (`daoist_forward_eval.py`)
1. **Strict Causality**: At bar `t`, only uses data up to `t` (no repainting)
2. **Signal Generation**: 
   - **Long**: When Tension < -0.6 (Extreme Yin)
   - **Short**: When Tension > 0.6 (Extreme Yang)
   - **Exit**: When Tension crosses 0 (Wuji/Balance)
3. **Adaptive Window**: The lookback period expands/contracts based on detected cycle length

## 📈 Sample Data
A sample dataset (`sample_data.csv`) is included for testing. It contains synthetic cyclical data with noise to demonstrate the indicator's adaptive capabilities.

## 🚀 Next Steps
- Compare Daoist signals against your existing strategies
- Export forward-walk results for backtesting in other platforms
- Experiment with different tension thresholds for your asset class

## 📜 License
MIT License - Free for research and commercial use.
