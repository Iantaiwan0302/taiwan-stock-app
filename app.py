import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import ta

# ----------------------
# 參數設定
# ----------------------
st.set_page_config(page_title="台股智能選股工具", layout="wide")
st.title("📈 台股智能選股工具（初版）")

# 預設台股股票代碼清單（可擴充）
tw_stocks = {
    "台積電": "2330.TW",
    "聯電": "2303.TW",
    "中華電": "2412.TW",
    "鴻海": "2317.TW",
    "玉山金": "2884.TW",
    "台達電": "2308.TW",
    "長榮": "2603.TW",
    "中鋼": "2002.TW"
}

# ----------------------
# 函數：取得股價與計算技術指標
# ----------------------
def fetch_stock_data(symbol):
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=180)
    df = yf.download(symbol, start=start, end=end)
    
    if df.empty:
        print(f"No data available for {symbol}")
        return None
    
    # 列印 df 的結構和前幾行資料以便檢查
    print(f"DataFrame structure for {symbol}:")
    print(df.head())

    # 檢查 df 是否包含 'Close' 欄位
    if 'Close' not in df.columns:
        print(f"Error: 'Close' column not found in the data for {symbol}")
        return None

    # 檢查資料行數，若不足 14 筆資料，無法計算 RSI
    if len(df) < 14:
        print(f"Error: Not enough data for {symbol} to calculate RSI")
        return None
    
    # 去除含有 NaN 的行
    df = df.dropna()

    # 確保 Close 欄位是數字型別，無法轉換為數字的資料設為 NaN
    try:
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    except Exception as e:
        print(f"Error converting 'Close' column to numeric: {e}")
        return None

    # 去除轉換後為 NaN 的行
    df = df.dropna(subset=['Close'])

    # 計算移動平均
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()

    # 計算 RSI 指標
    try:
        rsi_indicator = ta.momentum.RSIIndicator(df['Close'])
        df['RSI'] = rsi_indicator.rsi()
    except Exception as e:
        print(f"Error calculating RSI for {symbol}: {e}")
        df['RSI'] = None  # 如果 RSI 計算失敗，設為 None
    
    return df





# ----------------------
# 函數：評分系統
# ----------------------
def evaluate_stock(df):
    score = 0
    latest = df.iloc[-1]
    close = latest['Close']

    # 均線評分
    if close > latest['MA20']:
        score += 5
    if close > latest['MA60']:
        score += 5

    # RSI 評分
    if 50 < latest['RSI'] < 70:
        score += 5
    elif latest['RSI'] >= 70:
        score += 2

    return score

# ----------------------
# 主區塊：顯示選股結果
# ----------------------
st.subheader("🔥 自動選股推薦")
results = []

for name, symbol in tw_stocks.items():
    df = fetch_stock_data(symbol)
    if df is not None:
        score = evaluate_stock(df)
        latest_price = df.iloc[-1]['Close']
        results.append({
            "名稱": name,
            "代號": symbol,
            "最新股價": round(latest_price, 2),
            "評分": score
        })

# 顯示前 5 名股票
if results:
    results_df = pd.DataFrame(results)
    top_stocks = results_df.sort_values(by="評分", ascending=False).head(5)
    st.dataframe(top_stocks, use_container_width=True)
else:
    st.warning("無法取得股票資料，請稍後再試。")

# ----------------------
# 個股圖表顯示
# ----------------------
st.subheader("🔍 個股技術分析圖")
selected_stock = st.selectbox("選擇股票查看技術圖表：", list(tw_stocks.keys()))

df = fetch_stock_data(tw_stocks[selected_stock])
if df is not None:
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='收盤價'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name='MA60'))
    fig.update_layout(title=f"{selected_stock} 技術分析圖", xaxis_title="日期", yaxis_title="價格")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("無法取得該股票資料")
