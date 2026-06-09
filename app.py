from flask import Flask, render_template, jsonify, request
import psutil
import time
import requests
import base64
import os
import traceback

app = Flask(__name__)

# ========== 心理學顧問初始化 ==========
def get_advisor():
    class Advisor:
        def analyze_behavior(self, freq, time, resp):
            return {"stress_level": "low", "fatigue_risk": "10%", "recommendation": "狀態良好"}
    return Advisor()

advisor = get_advisor()
_defense_mode = "NORMAL"
_last_analysis = {}

def get_defense_mode():
    return _defense_mode

def set_defense_mode(mode):
    global _defense_mode
    _defense_mode = mode

def update_defense_from_analysis(result):
    pass

# ========== 系統監控 ==========
def get_disk_io():
    try:
        disk_io = psutil.disk_io_counters()
        if disk_io:
            read_speed = disk_io.read_bytes / 1024 / 1024
            write_speed = disk_io.write_bytes / 1024 / 1024
            return f"讀:{read_speed:.1f}MB/s 寫:{write_speed:.1f}MB/s"
    except:
        pass
    return "0.00 B/s"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system_stats')
def system_stats():
    stats = {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'disk_io': get_disk_io(),
        'timestamp': time.time()
    }
    return jsonify(stats)

@app.route('/api/defense/status')
def defense_status():
    return jsonify({'defense_mode': _defense_mode, 'last_analysis': _last_analysis})

@app.route('/api/defense/override', methods=['POST'])
def defense_override():
    global _defense_mode
    data = request.get_json()
    mode = data.get('mode', 'NORMAL')
    if mode in ['NORMAL', 'WARNING', 'LOCKDOWN']:
        _defense_mode = mode
        return jsonify({'status': 'success', 'defense_mode': mode})
    return jsonify({'status': 'error'}), 400

@app.route('/api/psychology/analyze', methods=['POST'])
def psychology_analyze():
    data = request.get_json()
    result = advisor.analyze_behavior(
        data.get('cmd_frequency', 25),
        data.get('time_of_day', '下午'),
        data.get('response_time', 3.5)
    )
    return jsonify({'status': 'success', 'analysis': result})

@app.route('/api/upload_vision', methods=['POST'])
def upload_vision():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '沒有上傳圖片'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '未選擇檔案'}), 400
        
        # 讀取圖片並轉為 base64
        img_data = file.read()
        img_b64 = base64.b64encode(img_data).decode()
        
        # 呼叫 llava 模型分析
        try:
            response = requests.post('http://localhost:11434/api/generate',
                                    json={
                                        'model': 'llava:latest',
                                        'prompt': '請詳細描述這張圖片的內容',
                                        'images': [img_b64],
                                        'stream': False
                                    },
                                    timeout=60)
            if response.status_code == 200:
                analysis = response.json().get('response', '分析失敗')
                return jsonify({'status': 'success', 'analysis': analysis})
            else:
                return jsonify({'status': 'error', 'message': f'模型錯誤: {response.status_code}'}), 500
        except requests.exceptions.Timeout:
            return jsonify({'status': 'error', 'message': '模型分析超時'}), 500
        except Exception as e:
            print(f"llava 錯誤: {e}")
            return jsonify({'status': 'error', 'message': f'llava 呼叫失敗: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/llm_status')
def llm_status():
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if response.status_code == 200:
            return jsonify({'status': 'online'})
    except:
        pass
    return jsonify({'status': 'offline'})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    return jsonify({'sender': '利維坦', 'reply': f"王令已收到：{user_msg}"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
