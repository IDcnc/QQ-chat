import os
import json
import webview

CONFIG_DIR = os.path.expanduser("~/.qq_bot_manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# API functions
def api_check_config():
    config = load_config()
    return config if config and config.get("appId") else None

def api_save_config(config_json):
    try:
        config = json.loads(config_json)
        save_config(config)
        return "ok"
    except Exception as e:
        return f"Save failed: {str(e)}"

def api_test_connection():
    return "Connection test passed"

def api_get_contacts():
    return [
        {"id": "test:1", "name": "Test Channel", "type": "guild"}
    ]

def api_get_messages(contact_id):
    return [
        {"from": "bot", "content": "Hello! I'm QQ bot"},
        {"from": "user", "content": "Hello!"},
    ]

def api_send_message(contact_id, content):
    return "ok"

def api_reset_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    return "ok"

def api_open_log():
    if os.path.exists(CONFIG_DIR):
        os.startfile(CONFIG_DIR)
        return "Opened"
    return "Folder does not exist"

# Create window
def create_window():
    """Create ultra-simple window - pure English, minimal JS"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>QQ Bot Manager</title>
    <style>
        * { margin:0; padding:0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; height: 100vh; }
        #wizard { display: none; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
        #main { display: none; height: 100vh; }
        .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); width: 400px; }
        h2 { text-align: center; color: #333; margin-top: 0; }
        input { width: 100%; padding: 12px; margin: 12px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        button { width: 100%; padding: 12px; background: #1890ff; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
        button:hover { background: #40a9ff; }
        label { font-size: 14px; color: #666; display: block; margin-top: 8px; }
        .error { color: #ff4d4f; font-size: 12px; margin-top: 8px; }
    </style>
</head>
<body>
    <div id="wizard">
        <div class="card">
            <h2>First Time Setup</h2>
            <label>App ID</label>
            <input type="text" id="appId" placeholder="Enter App ID">
            <label>Secret</label>
            <input type="password" id="secret" placeholder="Enter Secret">
            <div id="errorMsg" class="error"></div>
            <button onclick="saveConfig()">Save</button>
        </div>
    </div>
    
    <div id="main" style="display:flex; height:100vh;">
        <div style="width:280px; background:#2e2e2e; color:white; padding:20px;">
            <h2>Contacts</h2>
            <div id="contactList"></div>
        </div>
        <div style="flex:1; display:flex; flex-direction:column;">
            <div id="chatHeader" style="padding:16px; background:white; border-bottom:1px solid #e8e8e8;">Select a contact</div>
            <div id="messages" style="flex:1; padding:24px; overflow-y:auto; background:#f0f2f5;"></div>
            <div style="padding:16px; background:white; border-top:1px solid #e8e8e8;">
                <button onclick="testAPI()">Test API</button>
            </div>
        </div>
    </div>
    
    <script>
        let apiReady = false;
        
        // Wait for PyWebView API
        function waitForAPI() {
            if (window.pywebview && window.pywebview.api) {
                console.log('API ready');
                apiReady = true;
                initApp();
            } else {
                setTimeout(waitForAPI, 100);
            }
        }
        
        // Start waiting
        waitForAPI();
        
        function initApp() {
            window.pywebview.api.api_check_config().then(config => {
                if (config && config.appId) {
                    document.getElementById('main').style.display = 'flex';
                } else {
                    document.getElementById('wizard').style.display = 'flex';
                }
            }).catch(err => {
                console.error('Init error:', err);
                document.getElementById('wizard').style.display = 'flex';
            });
        }
        
        function saveConfig() {
            const config = {
                appId: document.getElementById('appId').value.trim(),
                secret: document.getElementById('secret').value.trim()
            };
            if (!config.appId || !config.secret) {
                document.getElementById('errorMsg').textContent = 'Please fill all fields';
                return;
            }
            window.pywebview.api.api_save_config(JSON.stringify(config)).then(result => {
                if (result === 'ok') {
                    document.getElementById('wizard').style.display = 'none';
                    document.getElementById('main').style.display = 'flex';
                }
            }).catch(err => {
                document.getElementById('errorMsg').textContent = 'Error: ' + err;
            });
        }
        
        function testAPI() {
            window.pywebview.api.api_test_connection().then(msg => {
                alert('API Test: ' + msg);
            }).catch(err => {
                alert('API Error: ' + err);
            });
        }
    </script>
</body>
</html>"""
    
    print("Creating window...")
    window = webview.create_window("QQ Bot Manager", html=html, width=1100, height=750)
    print("Window created")
    
    print("Exposing API functions...")
    window.expose(api_check_config)
    window.expose(api_save_config)
    window.expose(api_test_connection)
    window.expose(api_get_contacts)
    window.expose(api_get_messages)
    window.expose(api_send_message)
    window.expose(api_reset_config)
    window.expose(api_open_log)
    print("API functions exposed")
    
    return window

if __name__ == "__main__":
    print("=" * 60)
    print("QQ Bot Manager - Simple Version")
    print("=" * 60)
    print("")
    print("This is a simplified version to test if the white screen issue is caused by complex code.")
    print("")
    
    try:
        print("Step 1: Creating window...")
        window = create_window()
        print("")
        print("Step 2: Starting PyWebView main loop...")
        print("Close the window to stop the application.")
        print("=" * 60)
        webview.start(debug=True)
        print("")
        print("PyWebView main loop ended.")
        print("=" * 60)
    except Exception as e:
        print("")
        print("ERROR: " + str(e))
        print("")
        import traceback
        traceback.print_exc()
        print("=" * 60)
    
    print("Application terminated.")
    print("=" * 60)
    input("Press Enter to exit...")
