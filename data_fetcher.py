import akshare as ak
from datetime import datetime, timedelta

def get_chuangye_index_data(days=5):
    try:
        df = ak.index_zh_a_hist(symbol="399006", period="daily", start_date=(datetime.now() - timedelta(days=days+10)).strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'))
        df = df.sort_values('日期', ascending=False).head(days+1)
        return df
    except Exception as e:
        print(f'获取创业板指数据失败: {e}')
        return None

def get_nasdaq100_data(days=5):
    try:
        df = ak.index_us_stock_sina(symbol='NDX')
        df = df.sort_values('日期', ascending=False).head(days+1)
        return df
    except Exception as e:
        print(f'获取纳斯达克100数据失败: {e}')
        return None

def get_nasdaq100_with_ma(days=80):
    try:
        df = ak.index_us_stock_sina(symbol='NDX')
        df = df.sort_values('日期', ascending=True).tail(days)
        df['MA60'] = df['收盘'].rolling(window=60).mean()
        return df.sort_values('日期', ascending=False)
    except Exception as e:
        print(f'获取纳斯达克100带均线数据失败: {e}')
        return None

def get_chuangye_realtime():
    try:
        df = ak.stock_zh_index_spot()
        chuangye = df[df['代码'] == '399006']
        if not chuangye.empty:
            return chuangye.iloc[0]['涨跌幅']
        return None
    except Exception as e:
        print(f'获取创业板实时数据失败: {e}')
        return None
