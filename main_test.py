import os
import json
import webview

# Config paths
CONFIG_DIR = os.path.expanduser("~/.qq_bot_manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    """Load config from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                if config.get("appId") and config.get("secret"):
                    return config
            return None
        except Exception as e:
            print("[load_config] Error: " + str(e))
            return None
    return None

def save_config(config):
    """Save config to file"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("[save_config] Config saved")
        return "ok"
    except Exception as e:
        print("[save_config] Error: " + str(e))
        return str(e)

# ========== API Functions ==========
def api_check_config():
    """Check if config exists and is valid"""
    config = load_config()
    if config:
        print("[API] check_config: OK")
        return {"status": "ok", "appId": config.get("appId")}
    print("[API] check_config: Not configured")
    return {"status": "not_configured"}

def api_save_config(config_json):
    """Save config from JS"""
    try:
        config = json.loads(config_json)
        if not config.get("appId") or not config.get("secret"):
            return "AppId and Secret cannot be empty"
        save_config(config)
        return "ok"
    except Exception as e:
        return "Save failed: " + str(e)

def api_test():
    """Test API"""
    return "API call successful!"

def api_reset():
    """Reset config"""
    try:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        return "ok"
    except Exception as e:
        return "Reset failed: " + str(e)

# ========== Main ==========
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # TEMPORARILY load test.html to verify PyWebView rendering
    html_path = os.path.join(base_dir, "test.html")
    
    print("=== QQ Chat (Test Mode) ===")
    print("HTML path: " + html_path)
    print("Config dir: " + CONFIG_DIR)
    
    # Check if HTML file exists
    if not os.path.exists(html_path):
        print("ERROR: HTML file not found: " + html_path)
        return
    
    print("HTML file found, creating window...")
    
    window = webview.create_window(
        title="QQ Chat - Test",
        url=html_path,
        width=1100,
        height=750,
        min_size=(800, 500)
    )
    
    print("Exposing API functions...")
    window.expose(api_check_config)
    window.expose(api_save_config)
    window.expose(api_test)
    window.expose(api_reset)
    print("API functions exposed")
    
    print("Starting PyWebView...")
    webview.start(debug=True)
    print("PyWebView exited")

if __name__ == "__main__":
    main()
