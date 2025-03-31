# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import re
import requests


os.environ['GEMINI_API_KEY'] = "AIzaSyCmr5YKCPbqmOztbJtwfOdGhYBDT8aEt6k"
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

# 處理文本編碼和格式化
def process_judgment_text(judgment_data):
    """處理判決數據中可能的編碼問題，並格式化文本"""
    if not isinstance(judgment_data, dict):
        return judgment_data
        
    # 確保判決數據中有必要的結構化資訊
    if 'content' not in judgment_data and isinstance(judgment_data.get('fulltext'), str):
        judgment_data['content'] = judgment_data['fulltext']
    
    # 處理編碼和結構
    for key, value in judgment_data.items():
        if isinstance(value, str):
            # 檢查是否包含可能的亂碼序列
            if '\\u' in value or '\\x' in value:
                try:
                    judgment_data[key] = bytes(value, 'utf-8').decode('unicode_escape')
                except Exception:
                    pass
                    
            # 格式化和美化文本
            if key in ['content', 'fact', 'reason', 'mainText']:
                # 替換換行符為HTML換行
                judgment_data[key] = value.replace('\n', '<br>')
    
    return judgment_data

# 從判決內容提取結構化信息
def extract_judgment_structure(judgment_data):
    """從判決內容中提取結構化信息（事實、理由、主文等）"""
    if not isinstance(judgment_data, dict) or 'content' not in judgment_data:
        return judgment_data
        
    content = judgment_data['content']
    
    # 提取結構化信息
    if 'fact' not in judgment_data or 'reason' not in judgment_data or 'mainText' not in judgment_data:
        # 提取事實、理由和主文
        fact_match = None
        reason_match = None
        main_match = None
        
        # 常見的分段標記
        fact_patterns = ['事實及理由', '事實', '事  實']
        reason_patterns = ['理由', '理  由']
        main_patterns = ['主文', '主  文']
        
        # 找出各部分標記在文本中的位置
        fact_position = -1
        reason_position = -1
        main_position = -1
        
        # 尋找事實部分位置
        for pattern in fact_patterns:
            pos = content.find(pattern)
            if pos != -1:
                fact_match = pattern
                fact_position = pos
                break
        
        # 尋找理由部分位置
        for pattern in reason_patterns:
            pos = content.find(pattern)
            if pos != -1:
                reason_match = pattern
                reason_position = pos
                break
        
        # 尋找主文部分位置
        for pattern in main_patterns:
            pos = content.find(pattern)
            if pos != -1:
                main_match = pattern
                main_position = pos
                break
        
        # 提取主文部分 - 獨立處理
        if main_match:
            main_start = main_position + len(main_match)
            main_end = len(content)
            
            # 確定主文結束位置 (找到下一個最近的段落標記)
            next_section_pos = []
            if fact_position > main_position:
                next_section_pos.append(fact_position)
            if reason_position > main_position:
                next_section_pos.append(reason_position)
                
            if next_section_pos:
                main_end = min(next_section_pos)
            
            judgment_data['mainText'] = content[main_start:main_end].strip()
        
        # 提取事實部分
        if fact_match:
            fact_start = fact_position + len(fact_match)
            fact_end = len(content)
            
            if reason_position > fact_position:
                fact_end = reason_position
            
            # 獲取原始事實文本
            fact_text = content[fact_start:fact_end].strip()
            
            # 使用正則表達式進行格式化
            # 處理中文編號 (一、二、三、etc.)
            fact_text = re.sub(r'([一二三四五六七八九十]+、)', r'<br><br>\1', fact_text)
            
            # 處理數字編號 (1. 2. 等)
            fact_text = re.sub(r'(\d+[.．、])', r'<br><br>\1', fact_text)
            
            # 保留原有段落
            fact_text = re.sub(r'\n+', '<br><br>', fact_text)
            
            # 讓句號後面增加換行以增加可讀性
            fact_text = re.sub(r'([。！？])', r'\1<br>', fact_text)
            
            judgment_data['fact'] = fact_text
        
        # 提取理由部分
        if reason_match:
            reason_start = reason_position + len(reason_match)
            reason_text = content[reason_start:].strip()
            
            # 使用正則表達式進行格式化
            # 處理中文編號 (一、二、三、etc.)
            reason_text = re.sub(r'([一二三四五六七八九十]+、)', r'<br><br>\1', reason_text)
            
            # 處理數字編號 (1. 2. 等)
            reason_text = re.sub(r'(\d+[.．、])', r'<br><br>\1', reason_text)
            
            # 處理層級符號編號
            reason_text = re.sub(r'([\(（][一二三四五六七八九十]+[\)）])', r'<br><br>\1', reason_text)
            reason_text = re.sub(r'([\(（]\d+[\)）])', r'<br><br>\1', reason_text)
            
            # 保留原有段落
            reason_text = re.sub(r'\n+', '<br><br>', reason_text)
            
            # 讓句號後面增加換行以增加可讀性
            reason_text = re.sub(r'([。！？])', r'\1<br>', reason_text)
            
            judgment_data['reason'] = reason_text
    
    return judgment_data

# 提取判決基本資訊
def extract_judgment_metadata(judgment_data):
    """提取判決的基本資訊，如法院名稱、案號、日期等"""
    if not isinstance(judgment_data, dict) or 'content' not in judgment_data:
        return judgment_data
        
    content = judgment_data['content']
    
    # 提取法院名稱
    if 'court' not in judgment_data:
        court_match = re.search(r'(.*?)(地方法院|高等法院|最高法院)', content[:200])
        if court_match:
            judgment_data['court'] = court_match.group(0)
    
    # 提取案號
    if 'case_number' not in judgment_data:
        case_match = re.search(r'[\u4e00-\u9fff]+\s*[\u4e00-\u9fff]*\s*字\s*第\s*\d+\s*號', content[:500])
        if case_match:
            judgment_data['case_number'] = case_match.group(0)
    
    # 提取日期
    if 'date' not in judgment_data:
        date_match = re.search(r'中華民國\s*\d+\s*年\s*\d+\s*月\s*\d+\s*日', content[:500])
        if date_match:
            judgment_data['date'] = date_match.group(0)
            
    return judgment_data

@app.route('/judgment/<int:index>')
def judgment(index):
    # 從查詢參數中獲取選定的因素
    selected_factors = request.args.getlist('factors')
    
    # 獲取判決數據
    judgment_data, error = get_judgment_by_index(index)
    
    if error:
        flash(error)
        return redirect(url_for('index'))
    
    print(f"判決數據鍵名: {judgment_data.keys() if isinstance(judgment_data, dict) else 'None'}")
    
    # 若判決數據為空或缺乏內容
    if not judgment_data or (isinstance(judgment_data, dict) and not judgment_data):
        flash("錯誤: 找到的判決數據為空")
        return redirect(url_for('index'))
    
    # 處理判決數據
    if isinstance(judgment_data, dict):
        # 處理文本編碼問題
        judgment_data = process_judgment_text(judgment_data)
        
        # 提取判決結構
        judgment_data = extract_judgment_structure(judgment_data)
        
        # 提取判決元數據
        judgment_data = extract_judgment_metadata(judgment_data)
    
    # 確保判決索引顯示在數據中
    judgment_data['index'] = index
    
    return render_template('judgment.html', judgment=judgment_data, index=index, selected_factors=selected_factors)

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

# 添加 Gemini API 支持
@app.route('/extract_relations', methods=['POST'])
def extract_relations():
    data = request.json
    judgment_id = data.get('judgment_id')
    judgment_text = data.get('judgment_text')
    
    if not judgment_text:
        return jsonify({'error': '沒有提供判決文本'})
    
    # Gemini API的URL和金鑰
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'Gemini API金鑰未設置'})
    
    # 修正完整的 API URL
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # 構建提示
    prompt = f"""
    請從以下判決書中萃取所有人物及其關係。以繁體中文回應，不要包含任何額外解釋或前言。
    
    判決書內容:
    {judgment_text}
    
    請以JSON格式回覆，包含以下資訊:
    1. persons: 人物列表，每個人包含姓名(name)和角色(role)
    2. relations: 人物關係列表，每個關係包含人物1(person1)、關係類型(relation)和人物2(person2)
    3. summary: 簡短摘要，說明本案中重要的人物關係
    """
    
    try:
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }
        
        # 添加 API 金鑰作為 URL 參數
        response = requests.post(
            f"{api_url}?key={api_key}",
            headers=headers,
            json=payload
        )
        
        # 記錄 API 回應狀態碼，幫助診斷
        print(f"Gemini API 回應狀態碼: {response.status_code}")
        
        if response.status_code != 200:
            error_text = response.text[:500] if response.text else "無錯誤訊息"
            print(f"API錯誤詳情: {error_text}")
            return jsonify({'error': f'API回應錯誤: {response.status_code}'})
        
        response_data = response.json()
        print("收到 Gemini 回應")
        
        # 解析Gemini的回應
        if 'candidates' in response_data and response_data['candidates']:
            content = response_data['candidates'][0]['content']
            if 'parts' in content and content['parts']:
                text_response = content['parts'][0]['text']
                print(f"Gemini 回應內容: {text_response[:200]}...")
                
                # 嘗試從回應中提取JSON
                try:
                    # 查找並提取JSON部分
                    json_start = text_response.find('{')
                    json_end = text_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = text_response[json_start:json_end]
                        extracted_data = json.loads(json_str)
                        return jsonify(extracted_data)
                    else:
                        print("未找到JSON格式內容，回傳純文本")
                        # 如果沒有找到JSON，返回整個文本
                        return jsonify({
                            'summary': text_response,
                            'persons': [],
                            'relations': []
                        })
                        
                except json.JSONDecodeError as e:
                    print(f"JSON解析錯誤: {e}")
                    return jsonify({
                        'summary': text_response,
                        'persons': [],
                        'relations': []
                    })
        
        print("無法從回應中解析出有用內容")
        return jsonify({'error': '無法從Gemini回應中提取有用資訊'})
        
    except Exception as e:
        print(f"處理請求發生異常: {e}")
        return jsonify({'error': f'處理請求時發生錯誤: {str(e)}'})

if __name__ == '__main__':
    print("應用程式啟動中...")
    print(f"工作目錄: {os.getcwd()}")
    print(f"檔案存在檢查:")
    print(f" - inverted_index_075.json: {os.path.exists('inverted_index_075.json')}")
    print(f" - sexoffense_judgments_700.json: {os.path.exists('sexoffense_judgments_700.json')}")
    app.run(debug=True)