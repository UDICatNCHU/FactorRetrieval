import json
import os
import sys

def debug_judgment(index):
    """深入檢查特定索引的判決"""
    file_path = 'sexoffense_judgments_700.json'
    print(f"調試索引 {index} 的判決...")
    
    if not os.path.exists(file_path):
        print(f"錯誤: 檔案不存在於路徑 '{file_path}'")
        # 嘗試在其他位置尋找
        alt_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(alt_path):
            file_path = alt_path
            print(f"在備用路徑找到檔案: '{file_path}'")
        else:
            print("無法找到判決檔案")
            return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            judgments = json.load(f)
        
        # 判斷數據結構
        if isinstance(judgments, list):
            print(f"判決數據是列表結構，共有 {len(judgments)} 項")
            
            if 0 <= index < len(judgments):
                judgment = judgments[index]
                print(f"\n索引 {index} 的判決:")
                print(f"數據類型: {type(judgment)}")
                
                if isinstance(judgment, dict):
                    print(f"鍵名: {list(judgment.keys())}")
                    for key, value in judgment.items():
                        value_preview = str(value)
                        if len(value_preview) > 100:
                            value_preview = value_preview[:100] + "..."
                        print(f"- {key}: {value_preview}")
                else:
                    print(f"內容: {str(judgment)[:200]}...")
            else:
                print(f"錯誤: 索引 {index} 超出範圍 (0-{len(judgments)-1})")
                
        elif isinstance(judgments, dict):
            print(f"判決數據是字典結構，共有 {len(judgments)} 項")
            keys = list(judgments.keys())
            print(f"可用的鍵名範例: {keys[:5]}")
            
            # 嘗試不同的鍵名格式
            possible_keys = [str(index), index, f"{index}"]
            found = False
            
            for key in possible_keys:
                if key in judgments:
                    judgment = judgments[key]
                    print(f"\n使用鍵名 '{key}' 找到的判決:")
                    print(f"數據類型: {type(judgment)}")
                    
                    if isinstance(judgment, dict):
                        print(f"鍵名: {list(judgment.keys())}")
                        for k, v in judgment.items():
                            v_preview = str(v)
                            if len(v_preview) > 100:
                                v_preview = v_preview[:100] + "..."
                            print(f"- {k}: {v_preview}")
                    else:
                        print(f"內容: {str(judgment)[:200]}...")
                    
                    found = True
                    break
            
            if not found:
                print(f"錯誤: 找不到索引 {index} 的判決")
        else:
            print(f"警告: 數據結構既不是列表也不是字典，而是 {type(judgments)}")
        
    except json.JSONDecodeError:
        print("錯誤: 檔案不是有效的JSON格式")
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    # 預設檢查索引2
    index_to_debug = 2
    
    # 如果提供了命令行參數，使用指定的索引
    if len(sys.argv) > 1:
        try:
            index_to_debug = int(sys.argv[1])
        except ValueError:
            print(f"警告: '{sys.argv[1]}' 不是有效的索引數字，使用預設值 2")
    
    debug_judgment(index_to_debug)
