import json
import os
import sys

def check_inverted_index(file_path):
    """檢查倒排索引檔案的結構和內容"""
    print(f"檢查倒排索引檔案: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"錯誤: 檔案不存在!")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"檔案讀取成功，包含 {len(data)} 個因素")
        
        # 檢查前5個因素的資料
        for i, (factor, judgments) in enumerate(data.items()):
            if i >= 5:
                break
            print(f"因素 '{factor}': {len(judgments)} 個判決")
        
        # 檢查是否有空值
        empty_factors = [factor for factor, judgments in data.items() if not judgments]
        if empty_factors:
            print(f"警告: 有 {len(empty_factors)} 個因素沒有對應的判決")
            print(f"空因素範例: {empty_factors[:3]}")
        
        return True
    except json.JSONDecodeError:
        print("錯誤: 檔案不是有效的JSON格式")
        return False
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def check_judgments(file_path):
    """檢查判決檔案的結構和內容"""
    print(f"\n檢查判決檔案: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"錯誤: 檔案不存在!")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 判斷資料結構
        if isinstance(data, list):
            print(f"檔案讀取成功，包含 {len(data)} 個判決 (列表格式)")
            # 顯示前3個判決的索引和一些資訊
            for i in range(min(3, len(data))):
                print(f"判決 #{i}: {type(data[i])}")
        elif isinstance(data, dict):
            print(f"檔案讀取成功，包含 {len(data)} 個判決 (字典格式)")
            # 顯示前3個判決的索引和一些資訊
            keys = list(data.keys())[:3]
            for key in keys:
                print(f"判決 #{key}: {type(data[key])}")
        else:
            print(f"警告: 資料結構既不是列表也不是字典，而是 {type(data)}")
        
        return True
    except json.JSONDecodeError:
        print("錯誤: 檔案不是有效的JSON格式")
        return False
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def main():
    """主函數"""
    # 取得目前工作目錄
    current_dir = os.getcwd()
    print(f"目前工作目錄: {current_dir}\n")
    
    # 檢查檔案
    inverted_index_path = 'inverted_index_075.json'
    judgments_path = 'sexoffense_judgments_700.json'
    
    check_inverted_index(inverted_index_path)
    check_judgments(judgments_path)

if __name__ == "__main__":
    main()
