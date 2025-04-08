import datetime
import pandas as pd
import ta
from finmind.data import DataLoader

def fetch_stock_data(symbol):
    # 初始化 FinMind 的資料載入器
    loader = DataLoader()

    # 設定日期範圍
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=180)

    # 從 FinMind 取得台股資料
    try:
        df = loader.taiwan_stock_price(symbol=symbol, start_date=start.strftime('%Y-%m-%d'), end_date=end.strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"Error fetching data from FinMind for {symbol}: {e}")
        return None

    if df.empty:
        print(f"No data available for {symbol}")
        return None

    # 顯示前幾行數據檢查
    print(f"DataFrame structure for {symbol}:")
    print(df.head())

    # 檢查 df 是否包含 'close' 欄位
    if 'close' not in df.columns:
        print(f"Error: 'close' column not found in the data for {symbol}")
        return None

    # 重新命名為 'Close' 以便後續使用
    df.rename(columns={'close': 'Close'}, inplace=True)

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

# 測試用：請在這裡填入你想查詢的台股股票代碼
symbol = '2330'  # 例如台積電的股票代碼
df = fetch_stock_data(symbol)

if df is not None:
    # 顯示結果
    print(df.tail())


