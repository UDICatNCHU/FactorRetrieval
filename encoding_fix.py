# -*- coding: utf-8 -*-
import json
import os
import sys

def fix_encoding_in_judgment_file(input_file, output_file=None):
    """
    修復判決檔案中的編碼問題
    
    參數:
    input_file - 輸入的JSON檔案路徑
    output_file - 輸出的JSON檔案路徑 (如果不指定，將覆蓋輸入檔案)
    """
    if not os.path.exists(input_file):
        print(f"錯誤：找不到檔案 '{input_file}'")
        return False
        
    if not output_file:
        output_file = input_file + ".fixed"
    
    try:
        print(f"讀取檔案 '{input_file}'...")
        with open(input_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except UnicodeDecodeError:
                print("嘗試使用其他編碼讀取...")
                f.close()
                with open(input_file, 'r', encoding='latin1') as f2:
                    data = json.load(f2)
        
        print(f"成功讀取數據，類型: {type(data)}")
        
        # 判斷是列表還是字典
        if isinstance(data, list):
            print(f"修復列表型數據，包含 {len(data)} 個判決")
            for i, item in enumerate(data):
                if isinstance(item, str):
                    print(f"修復判決 #{i} (字符串類型)")
                    # 嘗試修復字符串編碼問題
                    try:
                        # 檢查是否可能是亂碼
                        if any(ord(c) > 127 for c in item):
                            try:
                                # 嘗試使用big5解碼
                                fixed_text = item.encode('latin1').decode('big5', errors='replace')
                                if '�' not in fixed_text:
                                    data[i] = fixed_text
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"警告：修復判決 #{i} 時出錯: {e}")
                
                elif isinstance(item, dict):
                    print(f"修復判決 #{i} (字典類型)")
                    # 修復字典中的所有字符串
                    for key, value in item.items():
                        if isinstance(value, str):
                            try:
                                # 檢查是否可能是亂碼
                                if any(ord(c) > 127 for c in value):
                                    try:
                                        # 嘗試使用big5解碼
                                        fixed_text = value.encode('latin1').decode('big5', errors='replace')
                                        if '�' not in fixed_text:
                                            item[key] = fixed_text
                                    except Exception:
                                        pass
                            except Exception as e:
                                print(f"警告：修復判決 #{i} 的欄位 '{key}' 時出錯: {e}")
                    
        elif isinstance(data, dict):
            print(f"修復字典型數據，包含 {len(data)} 個鍵")
            for key in data:
                item = data[key]
                if isinstance(item, str):
                    print(f"修復判決 '{key}' (字符串類型)")
                    # 嘗試修復字符串編碼問題
                    try:
                        # 檢查是否可能是亂碼
                        if any(ord(c) > 127 for c in item):
                            try:
                                # 嘗試使用big5解碼
                                fixed_text = item.encode('latin1').decode('big5', errors='replace')
                                if '�' not in fixed_text:
                                    data[key] = fixed_text
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"警告：修復判決 '{key}' 時出錯: {e}")
                
                elif isinstance(item, dict):
                    print(f"修復判決 '{key}' (字典類型)")
                    # 修復字典中的所有字符串
                    for subkey, value in item.items():
                        if isinstance(value, str):
                            try:
                                # 檢查是否可能是亂碼
                                if any(ord(c) > 127 for c in value):
                                    try:
                                        # 嘗試使用big5解碼
                                        fixed_text = value.encode('latin1').decode('big5', errors='replace')
                                        if '�' not in fixed_text:
                                            item[subkey] = fixed_text
                                    except Exception:
                                        pass
                            except Exception as e:
                                print(f"警告：修復判決 '{key}' 的欄位 '{subkey}' 時出錯: {e}")
        
        print(f"寫入修復後的數據到 '{output_file}'...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("檔案修復完成!")
        return True
        
    except Exception as e:
        print(f"錯誤：{e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python encoding_fix.py 輸入檔案路徑 [輸出檔案路徑]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if fix_encoding_in_judgment_file(input_file, output_file):
        print("成功修復編碼問題!")
    else:
        print("修復編碼問題失敗。")
