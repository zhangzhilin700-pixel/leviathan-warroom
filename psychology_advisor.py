"""
利維坦王國 - 統計心理學顧問
基於 qwen2.5:7b + 專用 System Prompt
"""

import requests

class PsychologyAdvisor:
    def __init__(self):
        self.model = "qwen2.5:7b"
        self.system_prompt = """你是利維坦王國的「統計心理學顧問」。你的任務是：
1. 分析用戶的操作行為模式
2. 評估決策壓力與疲勞風險
3. 提供管理心理學建議
4. 預測高壓情境下的決策偏差

回答必須簡潔、專業、有數據依據。"""
    
    def analyze_behavior(self, cmd_frequency, time_of_day, response_times):
        """分析用戶行為模式"""
        prompt = f"""{self.system_prompt}

請分析以下用戶行為數據：
- 指令頻率: {cmd_frequency} 次/小時
- 時段: {time_of_day}
- 平均回應等待: {response_times} 秒

請輸出 JSON 格式：
{{"stress_level": "low/medium/high", "fatigue_risk": "0-100%", "recommendation": "建議"}}"""
        
        try:
            response = requests.post('http://localhost:11434/api/generate',
                                    json={'model': self.model, 'prompt': prompt, 'stream': False},
                                    timeout=45)
            if response.status_code == 200:
                return response.json().get('response', '{}')
        except Exception as e:
            print(f"心理學顧問錯誤: {e}")
        return '{"stress_level": "unknown", "fatigue_risk": "0%", "recommendation": "無法分析"}'
    
    def predict_decision_quality(self, hour_of_day, task_complexity):
        """預測決策品質"""
        prompt = f"""{self.system_prompt}
預測在 {hour_of_day} 點，面對複雜度 {task_complexity}/10 的任務時，決策品質預期為何？
只輸出 JSON：{{"quality_score": 0-100, "confidence": "0-100%"}}"""
        
        try:
            response = requests.post('http://localhost:11434/api/generate',
                                    json={'model': self.model, 'prompt': prompt, 'stream': False},
                                    timeout=30)
            if response.status_code == 200:
                return response.json().get('response', '{}')
        except:
            pass
        return '{"quality_score": 70, "confidence": "50%"}'

# 單例
_advisor = None
def get_advisor():
    global _advisor
    if _advisor is None:
        _advisor = PsychologyAdvisor()
    return _advisor

def should_activate_defense(stress_level, fatigue_risk):
    """判斷是否啟動防禦機制"""
    # 壓力高或疲勞風險 > 60% 時啟動
    if stress_level in ["high", "very_high"] or fatigue_risk > 60:
        return True
    return False

def get_defense_action(stress_level, fatigue_risk):
    """根據壓力等級返回防禦動作"""
    if stress_level == "very_high" or fatigue_risk > 80:
        return "LOCKDOWN"  # 完全鎖定
    elif stress_level == "high" or fatigue_risk > 60:
        return "WARNING"   # 警告模式
    else:
        return "NORMAL"    # 正常模式
