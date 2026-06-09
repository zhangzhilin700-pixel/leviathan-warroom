"""
利維坦王國 - 指令執行器 (強化版)
具備超時控制、錯誤處理
"""

import subprocess
import os

def run_system_command(cmd_input):
    """根據使用者輸入，執行對應的系統指令"""
    
    # 1. 安全檢測 (防火牆)
    if "安全檢測" in cmd_input or "firewall" in cmd_input.lower():
        try:
            result = subprocess.run(
                ['sudo', '/usr/sbin/ufw', 'status'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                return f"```\n{result.stdout}\n```"
            else:
                return f"⚠️ 防火牆狀態查詢失敗: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "⚠️ 防禦系統響應超時"
        except Exception as e:
            return f"⚠️ 執行錯誤: {e}"
    
    # 2. 磁碟狀態
    if "磁碟狀態" in cmd_input or "disk" in cmd_input.lower():
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True, timeout=10)
            return f"```\n{result.stdout}\n```"
        except Exception as e:
            return f"⚠️ 執行錯誤: {e}"
    
    # 3. 系統負載
    if "系統負載" in cmd_input or "load" in cmd_input.lower():
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=5)
            return f"```\n{result.stdout}\n```"
        except Exception as e:
            return f"⚠️ 執行錯誤: {e}"
    
    # 4. 利維坦服務狀態
    if "利維坦狀態" in cmd_input or "leviathan status" in cmd_input.lower():
        try:
            flask_check = subprocess.run(['pgrep', '-f', 'app.py'], capture_output=True, text=True)
            ollama_check = subprocess.run(['pgrep', '-f', 'ollama'], capture_output=True, text=True)
            
            status = "⚙️ 利維坦服務狀態:\n"
            status += f"  - Flask 戰情室: {'✅ 運行中' if flask_check.stdout else '❌ 未運行'}\n"
            status += f"  - Ollama 引擎: {'✅ 運行中' if ollama_check.stdout else '❌ 未運行'}\n"
            return status
        except Exception as e:
            return f"⚠️ 執行錯誤: {e}"
    
    return None  # 非系統指令，交給 AI 處理

# 壓力防禦狀態
_defense_mode = "NORMAL"

def set_defense_mode(mode):
    global _defense_mode
    _defense_mode = mode
    print(f"🛡️ 防禦模式已設定: {mode}")

def get_defense_mode():
    return _defense_mode

def is_command_blocked(cmd_input):
    """檢查高風險指令是否應被鎖定"""
    if _defense_mode == "LOCKDOWN":
        # 完全鎖定，只允許狀態查詢
        safe_keywords = ["狀態", "status", "健康", "壓力", "取消鎖定"]
        if not any(kw in cmd_input for kw in safe_keywords):
            return True, "⚠️ 系統處於高壓力鎖定模式，僅允許狀態查詢。請輸入「取消鎖定」恢復正常。"
    elif _defense_mode == "WARNING":
        # 警告模式，僅針對高風險指令
        high_risk_keywords = ["安全檢測", "重啟", "shutdown", "rm", "delete", "格式化"]
        if any(kw in cmd_input for kw in high_risk_keywords):
            return True, "⚠️ 偵測到高壓力狀態，此指令可能造成風險。請再次輸入確認執行。"
    return False, None
