from datetime import datetime, timedelta

def _safe_import_akshare():
    """安全导入akshare"""
    try:
        import akshare as ak
        return ak
    except ImportError:
        print("警告: akshare未安装，无法获取真实行情数据")
        return None

def _safe_import_pandas():
    """安全导入pandas"""
    try:
        import pandas as pd
        return pd
    except ImportError:
        print("警告: pandas未安装")
        return None

def get_chuangye_index_data(window_days=20):
    """
    获取创业板指历史数据
    主接口：akshare的index_zh_a_hist
    备用接口：东方财富接口
    兜底：返回None，由调用方处理
    """
    ak = _safe_import_akshare()
    if ak is None:
        print("akshare未安装，无法获取行情数据")
        return None
    
    # 尝试主接口
    try:
        print("尝试主接口获取创业板指数据...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        df = ak.index_zh_a_hist(
            symbol="399006",
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d")
        )
        
        if df is not None and not df.empty:
            df = df.sort_values('日期', ascending=False).reset_index(drop=True)
            print(f"主接口成功：获取创业板指数据{len(df)}条")
            return df
        
        print("主接口返回空数据，尝试备用接口...")
    except Exception as e:
        print(f"主接口失败: {e}，尝试备用接口...")
    
    # 尝试备用接口：东方财富
    try:
        print("尝试备用接口（东方财富）...")
        df = ak.index_zh_a_hist_em(symbol="399006", period="daily")
        
        if df is not None and not df.empty:
            df = df.sort_values('日期', ascending=False).reset_index(drop=True)
            print(f"备用接口成功：获取创业板指数据{len(df)}条")
            return df
        
        print("备用接口也返回空数据")
    except Exception as e:
        print(f"备用接口也失败: {e}")
    
    print("所有接口均失败，无法获取创业板指数据")
    return None

def get_chuangye_realtime():
    """
    获取创业板指实时涨跌幅
    使用akshare的index_zh_a_hist接口获取最新数据
    """
    ak = _safe_import_akshare()
    if ak is None:
        return None
    
    try:
        # 使用历史数据接口获取最新一天的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        df = ak.index_zh_a_hist(
            symbol="399006",
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d")
        )
        
        if df is None or df.empty:
            print("获取实时数据为空")
            return None
        
        # 按日期降序排列，取最新的一条
        df = df.sort_values('日期', ascending=False)
        latest = df.iloc[0]
        
        # 计算涨跌幅（使用当日涨跌幅字段，如果没有则计算）
        if '涨跌幅' in latest:
            zhangdie = float(latest['涨跌幅'])
        else:
            # 手动计算涨跌幅
            prev_close = float(latest['昨收']) if '昨收' in latest else None
            curr_close = float(latest['收盘'])
            if prev_close:
                zhangdie = (curr_close - prev_close) / prev_close * 100
            else:
                zhangdie = 0.0
        
        print(f"创业板指实时涨跌幅: {zhangdie:.2f}%")
        return zhangdie
        
    except Exception as e:
        print(f"获取创业板指实时数据失败: {e}")
        return None

def get_nasdaq100_data(window_days=20):
    """
    获取纳斯达克100指数数据
    主接口：akshare的index_us_stock_sina
    兜底：尝试其他美股数据源或返回None
    """
    ak = _safe_import_akshare()
    if ak is None:
        return None
    
    # 尝试主接口
    try:
        print("尝试主接口获取纳斯达克100数据...")
        df = ak.index_us_stock_sina(symbol="NDX")
        
        if df is not None and not df.empty:
            pd = _safe_import_pandas()
            if pd:
                df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期', ascending=False).reset_index(drop=True)
            print(f"主接口成功：获取纳斯达克100数据{len(df)}条")
            return df
        
        print("主接口返回空数据，尝试备用数据源...")
    except Exception as e:
        print(f"主接口失败: {e}，尝试备用数据源...")
    
    # 备用方案：尝试使用yfinance或其他数据源
    # 暂时返回None，由调用方处理
    print("所有接口均失败，无法获取纳斯达克100数据")
    return None

def get_nasdaq100_with_ma():
    """
    获取纳斯达克100指数数据并计算60日均线
    """
    df = get_nasdaq100_data()
    
    if df is None or df.empty:
        return None
    
    try:
        import pandas as pd
        
        # 确保有足够的数据计算MA60
        if len(df) < 60:
            print(f"数据不足，无法计算MA60（当前只有{len(df)}条）")
            return df
        
        # 按日期升序排列以便计算均线
        df_sorted = df.sort_values('日期', ascending=True)
        
        # 计算60日均线
        df_sorted['MA60'] = df_sorted['收盘'].rolling(window=60, min_periods=1).mean()
        
        # 再按日期降序排列返回
        df_result = df_sorted.sort_values('日期', ascending=False)
        
        # 获取最新数据
        latest = df_result.iloc[0]
        print(f"纳指100最新: {latest['收盘']:.2f}, MA60: {latest['MA60']:.2f}")
        
        return df_result
        
    except Exception as e:
        print(f"计算MA60失败: {e}")
        return df
