import webview
import sys
import os

def create_window():
    """Diagnose white screen issue - pure English version"""
    
    # Super simple HTML without any special characters
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }
        p {
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SUCCESS!</h1>
        <p>If you can see this, PyWebView is working!</p>
        <p>Time: <span id="time"></span></p>
        <button onclick="testAPI()" style="margin-top:20px; padding:12px 24px; background:#fff; color:#333; border:none; border-radius:6px; cursor:pointer; font-size:16px;">Test API</button>
        <div id="apiResult" style="margin-top:20px; padding:20px; background:rgba(255,255,255,0.2); border-radius:6px;"></div>
    </div>
    <script>
        // Update time
        function updateTime() {
            document.getElementById('time').textContent = new Date().toLocaleString();
        }
        updateTime();
        setInterval(updateTime, 1000);
        
        // Test API
        function testAPI() {
            const result = document.getElementById('apiResult');
            result.innerHTML = 'Testing API...<br>';
            
            // Check if pywebview exists
            result.innerHTML += 'window.pywebview: ' + (window.pywebview ? 'FOUND' : 'NOT FOUND') + '<br>';
            
            // Check if API exists
            if (window.pywebview && window.pywebview.api) {
                result.innerHTML += 'window.pywebview.api: FOUND<br>';
                result.innerHTML += 'Trying to call api_check_config()...<br>';
                
                window.pywebview.api.api_check_config().then(config => {
                    result.innerHTML += 'API call SUCCESS!<br>';
                    result.innerHTML += 'Config: ' + JSON.stringify(config) + '<br>';
                }).catch(err => {
                    result.innerHTML += 'API call FAILED: ' + err + '<br>';
                });
            } else {
                result.innerHTML += 'window.pywebview.api: NOT FOUND<br>';
                result.innerHTML += 'PyWebView API not ready<br>';
            }
        }
        
        // Log events
        document.addEventListener('pywebviewready', function() {
            console.log('pywebviewready event fired');
            document.getElementById('apiResult').innerHTML += 'pywebviewready event fired<br>';
        });
        
        window.onload = function() {
            console.log('window.onload fired');
            document.getElementById('apiResult').innerHTML += 'window.onload fired<br>';
        };
    </script>
</body>
</html>"""
    
    print("Creating window...")
    window = webview.create_window(
        "PyWebView Diagnostic Test", 
        html=html,
        width=900, 
        height=700
    )
    print("Window created successfully")
    
    # Expose a simple API
    def api_check_config():
        print("api_check_config() called")
        return {"status": "ok", "message": "API is working!"}
    
    window.expose(api_check_config)
    print("API exposed successfully")
    
    return window

if __name__ == "__main__":
    print("=" * 50)
    print("PyWebView White Screen Diagnostic")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"PyWebView version: {webview.__version__}")
    print(f"Platform: {sys.platform}")
    print("=" * 50)
    
    try:
        print("Step 1: Creating window...")
        window = create_window()
        print("Step 2: Starting PyWebView main loop...")
        webview.start(debug=True)
        print("Step 3: PyWebView main loop ended")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("Diagnostic test completed")
    print("=" * 50)
