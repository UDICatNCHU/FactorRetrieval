# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # 用於flash消息

# 讀取所有可用的factors
def load_factors():
    file_path = os.path.join(os.path.dirname(__file__), 'inverted_index_075.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            inverted_index = json.load(file)
        print(f"成功載入 {len(inverted_index)} 個因素")
        return sorted(list(inverted_index.keys()))
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{file_path}'")
        return []
    except json.JSONDecodeError:
        print(f"錯誤：'{file_path}' 不是有效的JSON格式")
        return []
    except Exception as e:
        print(f"載入因素時發生錯誤: {e}")
        return []

# 根據選定的factors搜尋判決
def search_judgments_by_factors(factors):
    file_path = os.path.join(os.path.dirname(__file__), 'inverted_index_075.json')
    
    if not os.path.exists(file_path):
        print(f"搜尋錯誤: 找不到檔案 '{file_path}'")
        return [], "錯誤: 找不到檔案 'inverted_index_075.json'"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            inverted_index = json.load(file)
        
        valid_factors = [factor for factor in factors if factor in inverted_index]
        
        print(f"選擇的因素: {factors}")
        print(f"有效的因素: {valid_factors}")
        
        if not valid_factors:
            return [], "沒有有效的檢索因素"
        
        # 列印第一個因素的判決數量，用於診斷
        print(f"因素 '{valid_factors[0]}' 有 {len(inverted_index[valid_factors[0]])} 個判決")
        
        # 確保每個索引是整數類型
        result_set = set(int(idx) for idx in inverted_index[valid_factors[0]])
        
        for factor in valid_factors[1:]:
            factor_indices = set(int(idx) for idx in inverted_index[factor])
            print(f"因素 '{factor}' 有 {len(factor_indices)} 個判決")
            result_set = result_set.intersection(factor_indices)
            print(f"交集後還剩 {len(result_set)} 個判決")
        
        result_indices = sorted(list(result_set))
        
        message = f"檢索條件: {', '.join(valid_factors)}"
        print(f"最終結果: {len(result_indices)} 個判決")
        
        return result_indices, message
        
    except json.JSONDecodeError:
        error_msg = f"錯誤: '{file_path}' 不是有效的JSON格式"
        print(error_msg)
        return [], error_msg
    except Exception as e:
        error_msg = f"搜尋時發生錯誤: {e}"
        print(error_msg)
        return [], error_msg

# 根據索引獲取判決內容
def get_judgment_by_index(index):
    file_path = os.path.join(os.path.dirname(__file__), 'sexoffense_judgments_700.json')
    
    if not os.path.exists(file_path):
        print(f"錯誤: 找不到檔案 '{file_path}'")
        return None, f"錯誤: 找不到檔案 '{file_path}'"
    
    try:
        # 確保以UTF-8編碼讀取
        with open(file_path, 'r', encoding='utf-8') as file:
            judgments = json.load(file)
        
        print(f"讀取判決檔案成功，數據類型: {type(judgments)}")
        
        if isinstance(judgments, list):
            if 0 <= index < len(judgments):
                judgment_data = judgments[index]
                print(f"找到索引 {index} 的判決，數據類型: {type(judgment_data)}")
                
                # 處理字典型態的判決數據
                if isinstance(judgment_data, dict):
                    # 檢查並確保所有文本字段都以UTF-8編碼存儲
                    for key in judgment_data:
                        if isinstance(judgment_data[key], str):
                            # 檢測是否為無效UTF-8字符串(可能是亂碼來源)
                            try:
                                judgment_data[key].encode('utf-8').decode('utf-8')
                            except UnicodeError:
                                print(f"警告: 欄位 {key} 包含無效的UTF-8字符")
                                # 嘗試用不同編碼解決亂碼問題
                                try:
                                    raw_str = judgment_data[key]
                                    # 嘗試big5編碼
                                    judgment_data[key] = raw_str.encode('latin1').decode('big5', errors='replace')
                                except Exception:
                                    # 如果失敗，至少確保它是有效的UTF-8
                                    judgment_data[key] = judgment_data[key].encode('utf-8', errors='replace').decode('utf-8')
                    
                    # 如果沒有專門的文本欄位，檢查常見欄位名稱
                    if not any(k in judgment_data for k in ['content', 'text', 'full_text']):
                        # 尋找最長的字符串欄位作為主要內容
                        max_len = 0
                        main_content_key = None
                        for key, value in judgment_data.items():
                            if isinstance(value, str) and len(value) > max_len:
                                max_len = len(value)
                                main_content_key = key
                        
                        if main_content_key:
                            judgment_data['content'] = judgment_data[main_content_key]
                            print(f"使用 {main_content_key} 欄位作為主要內容")
                    
                    return judgment_data, None
                
                # 處理字符串型態的判決數據
                elif isinstance(judgment_data, str):
                    print(f"判決數據是字符串，長度: {len(judgment_data)}")
                    try:
                        # 檢查是否為有效UTF-8字符串
                        judgment_data.encode('utf-8').decode('utf-8')
                    except UnicodeError:
                        print("警告: 判決內容包含無效的UTF-8字符")
                        try:
                            # 嘗試big5編碼
                            judgment_data = judgment_data.encode('latin1').decode('big5', errors='replace')
                        except Exception:
                            # 如果失敗，至少確保它是有效的UTF-8
                            judgment_data = judgment_data.encode('utf-8', errors='replace').decode('utf-8')
                    return {"content": judgment_data}, None
                
                else:
                    print(f"判決數據類型不支持: {type(judgment_data)}")
                    return {"content": str(judgment_data)}, None
            else:
                print(f"錯誤: 索引 {index} 超出範圍 (0-{len(judgments)-1})")
                return None, f"錯誤: 索引 {index} 超出範圍"
                
        elif isinstance(judgments, dict):
            # 嘗試不同的索引格式
            possible_keys = [str(index), index, f"{index}"]
            for key in possible_keys:
                if key in judgments:
                    judgment_data = judgments[key]
                    print(f"找到索引 {key} 的判決，數據類型: {type(judgment_data)}")
                    print(f"判決數據內容範例: {str(judgment_data)[:200]}...")
                    # 確保數據是一個字典
                    if not isinstance(judgment_data, dict):
                        judgment_data = {"content": str(judgment_data)}
                    return judgment_data, None
            
            print(f"錯誤: 找不到索引 {index} 的判決，可用索引: {list(judgments.keys())[:5]}...")
            return None, f"錯誤: 找不到索引 {index} 的判決"
        else:
            print(f"錯誤: JSON檔案結構不支援索引訪問，類型為: {type(judgments)}")
            return None, "錯誤: JSON檔案結構不支援索引訪問"
            
    except json.JSONDecodeError:
        error_msg = f"錯誤: '{file_path}' 不是有效的JSON格式"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"獲取判決時發生錯誤: {e}"
        print(error_msg)
        return None, error_msg

@app.route('/')
def index():
    factors = load_factors()
    return render_template('index.html', factors=factors)

@app.route('/search', methods=['POST'])
def search():
    selected_factors = request.form.getlist('factors')
    
    if not selected_factors:
        flash('請至少選擇一個因素')
        return redirect(url_for('index'))
    
    print(f"收到搜尋請求，選擇的因素: {selected_factors}")
    indices, message = search_judgments_by_factors(selected_factors)
    
    return render_template(
        'results.html', 
        indices=indices, 
        message=message, 
        selected_factors=selected_factors,
        count=len(indices)
    )

@app.route('/judgment/<int:index>')
def judgment(index):
    judgment_data, error = get_judgment_by_index(index)
    
    if error:
        flash(error)
        return redirect(url_for('index'))
    
    print(f"判決數據鍵名: {judgment_data.keys() if isinstance(judgment_data, dict) else 'None'}")
    
    # 若判決數據為空或缺乏內容
    if not judgment_data or (isinstance(judgment_data, dict) and not judgment_data):
        flash("錯誤: 找到的判決數據為空")
        return redirect(url_for('index'))
    
    # 處理可能的編碼問題
    if isinstance(judgment_data, dict):
        for key, value in judgment_data.items():
            if isinstance(value, str):
                # 檢查是否包含可能的亂碼序列
                if '\\u' in value or '\\x' in value:
                    try:
                        # 嘗試解碼轉義序列
                        judgment_data[key] = bytes(value, 'utf-8').decode('unicode_escape')
                    except Exception:
                        pass
    
    return render_template('judgment.html', judgment=judgment_data, index=index)

@app.route('/debug')
def debug_info():
    """提供一個診斷頁面，顯示檔案狀態和路徑"""
    info = {
        "current_directory": os.getcwd(),
        "app_directory": os.path.dirname(__file__),
        "inverted_index_exists": os.path.exists(os.path.join(os.path.dirname(__file__), 'inverted_index_075.json')),
        "judgments_exists": os.path.exists(os.path.join(os.path.dirname(__file__), 'sexoffense_judgments_700.json')),
    }
    
    # 嘗試讀取一些資料進行測試
    if info["inverted_index_exists"]:
        try:
            with open(os.path.join(os.path.dirname(__file__), 'inverted_index_075.json'), 'r', encoding='utf-8') as f:
                inverted_data = json.load(f)
                info["inverted_index_keys"] = len(inverted_data)
                if len(inverted_data) > 0:
                    first_key = next(iter(inverted_data))
                    info["first_factor"] = first_key
                    info["first_factor_judgments"] = len(inverted_data[first_key])
        except Exception as e:
            info["inverted_index_error"] = str(e)
    
    return jsonify(info)

if __name__ == '__main__':
    print("應用程式啟動中...")
    print(f"工作目錄: {os.getcwd()}")
    print(f"檔案存在檢查:")
    print(f" - inverted_index_075.json: {os.path.exists('inverted_index_075.json')}")
    print(f" - sexoffense_judgments_700.json: {os.path.exists('sexoffense_judgments_700.json')}")
    app.run(debug=True)