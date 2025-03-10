# -*- coding: utf-8 -*-
import pandas as pd

def load_data(filepath):
    """
    讀取 CSV 檔案並回傳 pandas DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8")
    return df

def get_factors_by_id(case_id, df, id_column="Unnamed: 0", ignore_columns=None):
    """
    根據案件 ID（預設存放在 id_column 欄位）搜尋案件，
    並回傳該案件中所有值為 1 的 factor 欄位名稱。
    
    參數：
      case_id：要查詢的案件 ID
      df：從 CSV 讀取的 DataFrame
      id_column：案件識別的欄位名稱，預設為 "Unnamed: 0"
      ignore_columns：要忽略的欄位列表（例如案件 ID 欄位或其他非 factor 欄位）
    
    回傳：
      若找到對應案件，回傳包含 factor 欄位名稱的列表；若找不到則回傳 None。
    """
    if ignore_columns is None:
        ignore_columns = [id_column]
    
    # 根據 id_column 搜尋符合的案件
    case_row = df[df[id_column] == case_id]
    
    if case_row.empty:
        return None
    
    # 取出該筆案件資料
    case_series = case_row.iloc[0]
    
    # 過濾出除了忽略欄位外，值為 1 的所有欄位名稱
    present_factors = [
        col for col in case_series.index 
        if col not in ignore_columns and case_series[col] == 1
    ]
    
    return present_factors

if __name__ == "__main__":
    filepath = "result_df_075.csv"
    df = load_data(filepath)
    
    # 例如查詢案件 ID 為 2 的資料（請根據實際資料調整 id_column 與案件 ID）
    case_id = 2
    factors = get_factors_by_id(case_id, df, id_column="Unnamed: 0")
    
    if factors is not None:
        print("案件 {} 擁有的法律 factor：".format(case_id), factors)
    else:
        print("找不到案件 ID:", case_id)