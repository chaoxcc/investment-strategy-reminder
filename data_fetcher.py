from datetime import datetime, timedelta

def _safe_import_akshare():
    try:
        import akshare as ak
        return ak
    except ImportError:
        return None


def get_chuangye_index_data(window_days=20):
    """获取创业板指数据，默认20日滚动窗口"""
    ak = _safe_import_akshare()
    if ak is None:
        print("AkShare 未安装，无法获取真实行情")
        return None

    try:
        days_needed = window_days + 30  # 多取一些以防节假日
        start_date = (datetime.now() - timedelta(days=days_needed)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        df = ak.index_zh_a_hist(symbol="399006", period="daily", 
                                start_date=start_date, end_date=end_date)
        df = df.sort_values('日期', ascending=False)
        return df
    except Exception as e:
        print(f"获取创业板指数据失败: {e}")
        return None


def get_nasdaq100_data(window_days=20):
    """获取纳斯达克100数据，默认20日滚动窗口"""
    ak = _safe_import_akshare()
    if ak is None:
        print("AkShare 未安装，无法获取真实行情")
        return None

    try:
        df = ak.index_us_stock_sina(symbol='NDX')
        df = df.sort_values('日期', ascending=False)
        return df
    except Exception as e:
        print(f"获取纳斯达克100数据失败: {e}")
        return None


def get_nasdaq100_with_ma():
    """获取纳斯达克100数据并计算60日均线"""
    ak = _safe_import_akshare()
    if ak is None:
        print("AkShare 未安装，无法获取真实行情")
        return None

    try:
        df = ak.index_us_stock_sina(symbol='NDX')
        df = df.sort_values('日期', ascending=True)
        if len(df) < 60:
            print("纳斯达克100数据不足60日，无法计算MA60")
            return df.sort_values('日期', ascending=False)
        df['MA60'] = df['收盘'].rolling(window=60).mean()
        return df.sort_values('日期', ascending=False)
    except Exception as e:
        print(f"获取纳斯达克100均线数据失败: {e}")
        return None


def get_chuangye_realtime():
    """获取创业板指实时涨跌幅"""
    ak = _safe_import_akshare()
    if ak is None:
        print("AkShare 未安装，无法获取真实行情")
        return None

    try:
        df = ak.stock_zh_index_spot()
        chuangye = df[df['代码'] == '399006']
        if not chuangye.empty:
            return float(chuangye.iloc[0]['涨跌幅'])
        return None
    except Exception as e:
        print(f"获取创业板实时数据失败: {e}")
        return None
