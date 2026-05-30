import webview
import sys
import os

def create_window():
    """Diagnose white screen - Pure ASCII version"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Diagnostic Test</title>
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
        button {
            margin-top: 20px;
            padding: 12px 24px;
            background: #fff;
            color: #333;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 6px;
            text-align: left;
            font-family: monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SUCCESS!</h1>
        <p>If you can see this page, PyWebView is working!</p>
        <p>Time: <span id="time"></span></p>
        <button onclick="runDiagnostic()">Run Full Diagnostic</button>
        <div id="result" class="result" style="display:none;"></div>
    </div>
    <script>
        // Update time
        function updateTime() {
            document.getElementById('time').textContent = new Date().toLocaleString();
        }
        updateTime();
        setInterval(updateTime, 1000);
        
        // Full diagnostic
        function runDiagnostic() {
            const result = document.getElementById('result');
            result.style.display = 'block';
            result.innerHTML = '=== PyWebView Diagnostic Results ===<br><br>';
            
            // Test 1: Check pywebview object
            result.innerHTML += 'Test 1: window.pywebview exists: ' + (window.pywebview ? 'PASS' : 'FAIL') + '<br>';
            
            // Test 2: Check API object
            if (window.pywebview) {
                result.innerHTML += 'Test 2: window.pywebview.api exists: ' + (window.pywebview.api ? 'PASS' : 'FAIL') + '<br>';
            } else {
                result.innerHTML += 'Test 2: SKIPPED (pywebview not found)<br>';
            }
            
            // Test 3: DOM ready
            result.innerHTML += 'Test 3: DOM ready: PASS<br>';
            
            // Test 4: Event listener
            try {
                document.addEventListener('pywebviewready', function() {
                    result.innerHTML += 'Test 4: pywebviewready event: PASS<br>';
                });
                result.innerHTML += 'Test 4: Event listener added: PASS<br>';
            } catch(e) {
                result.innerHTML += 'Test 4: Event listener: FAIL - ' + e.message + '<br>';
            }
            
            // Test 5: Call API
            if (window.pywebview && window.pywebview.api) {
                result.innerHTML += '<br>Test 5: Calling api_check_config()...<br>';
                window.pywebview.api.api_check_config()
                    .then(config => {
                        result.innerHTML += 'Test 5: API call: PASS<br>';
                        result.innerHTML += 'Config: ' + JSON.stringify(config) + '<br>';
                    })
                    .catch(err => {
                        result.innerHTML += 'Test 5: API call: FAIL - ' + err + '<br>';
                    });
            } else {
                result.innerHTML += '<br>Test 5: SKIPPED (API not available)<br>';
            }
            
            result.innerHTML += '<br>=== Diagnostic Complete ===';
        }
        
        // Log events
        document.addEventListener('pywebviewready', function() {
            console.log('pywebviewready event fired');
            const result = document.getElementById('result');
            if (result && result.style.display === 'block') {
                result.innerHTML += '<br>[Event] pywebviewready fired<br>';
            }
        });
        
        window.onload = function() {
            console.log('window.onload fired');
        };
    </script>
</body>
</html>"""
    
    print("Creating PyWebView window...")
    window = webview.create_window(
        "PyWebView Diagnostic v2", 
        html=html,
        width=1000, 
        height=800
    )
    print("Window created successfully")
    
    # Expose test API
    def api_check_config():
        print("api_check_config() called from JavaScript")
        return {"status": "ok", "message": "API is working!", "version": "PyWebView 6.2.1"}
    
    print("Exposing API functions...")
    window.expose(api_check_config)
    print("API functions exposed successfully")
    
    return window

if __name__ == "__main__":
    print("=" * 60)
    print("PyWebView White Screen Diagnostic Tool v2")
    print("=" * 60)
    print("")
    print("Python version: " + sys.version)
    print("Platform: " + sys.platform)
    print("PyWebView module: " + str(webview))
    print("")
    print("INSTRUCTIONS:")
    print("1. A window should open")
    print("2. You should see 'SUCCESS!' message")
    print("3. Click 'Run Full Diagnostic' button")
    print("4. Check the diagnostic results")
    print("")
    print("If you see white screen:")
    print("- Check Windows Event Viewer for errors")
    print("- Try running as Administrator")
    print("- Check if Edge WebView2 Runtime is installed")
    print("")
    print("=" * 60)
    print("Starting PyWebView...")
    print("=" * 60)
    
    try:
        window = create_window()
        print("")
        print("PyWebView main loop starting...")
        print("Close the window to stop the application")
        print("=" * 60)
        webview.start(debug=True)
        print("")
        print("PyWebView main loop ended")
        print("=" * 60)
    except Exception as e:
        print("")
        print("ERROR: " + str(e))
        print("")
        import traceback
        traceback.print_exc()
        print("=" * 60)
    
    print("Diagnostic test completed")
    print("=" * 60)
    input("Press Enter to exit...")
