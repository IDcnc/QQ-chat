import webview

def create_window():
    # 最小化测试 - 纯HTML不调用任何API
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test</title>
    </head>
    <body style="font-family: Microsoft YaHei; padding: 40px;">
        <h1>✅ PyWebView Test Successful!</h1>
        <p>If you can see this, PyWebView is working correctly.</p>
        <button onclick="testAPI()" style="padding: 12px 24px; background: #1890ff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;">Test API</button>
        <div id="result" style="margin-top: 20px; padding: 20px; background: #f0f2f5; border-radius: 6px;"></div>
        <script>
            function testAPI() {
                const result = document.getElementById('result');
                result.innerHTML = 'Testing API...<br>';
                
                // Test 1: Check if pywebview exists
                result.innerHTML += 'window.pywebview: ' + (window.pywebview ? '✅ EXISTS' : '❌ NOT FOUND') + '<br>';
                
                // Test 2: Check if API exists  
                result.innerHTML += 'window.pywebview.api: ' + (window.pywebview && window.pywebview.api ? '✅ EXISTS' : '❌ NOT FOUND') + '<br>';
                
                // Test 3: Try calling API
                if (window.pywebview && window.pywebview.api) {
                    result.innerHTML += 'Trying to call api_check_config()...<br>';
                    window.pywebview.api.api_check_config().then(config => {
                        result.innerHTML += '✅ API call successful! Config: ' + JSON.stringify(config) + '<br>';
                    }).catch(err => {
                        result.innerHTML += '❌ API call failed: ' + err + '<br>';
                    });
                } else {
                    result.innerHTML += '❌ Cannot test API - pywebview not ready<br>';
                    result.innerHTML += 'Please wait 3 seconds and try again...<br>';
                    setTimeout(() => {
                        result.innerHTML += 'Retrying...<br>';
                        result.innerHTML += 'window.pywebview: ' + (window.pywebview ? '✅ EXISTS' : '❌ NOT FOUND') + '<br>';
                    }, 3000);
                }
            }
            
            // Log pywebviewready event
            document.addEventListener('pywebviewready', function() {
                console.log('✅ pywebviewready event fired');
                document.getElementById('result').innerHTML += '✅ pywebviewready event fired<br>';
            });
            
            // Log when page loads
            window.onload = function() {
                console.log('✅ window.onload fired');
                document.getElementById('result').innerHTML += '✅ window.onload fired<br>';
                document.getElementById('result').innerHTML += 'window.pywebview: ' + (window.pywebview ? '✅ EXISTS' : '❌ NOT FOUND') + '<br>';
            };
        </script>
    </body>
    </html>
    """
    window = webview.create_window("PyWebView Test", html=html, width=800, height=600)
    
    # Expose a simple API
    def api_check_config():
        return {"test": "ok", "message": "API is working!"}
    
    window.expose(api_check_config)
    return window

if __name__ == "__main__":
    print("🚀 Starting PyWebView test...")
    create_window()
    webview.start(debug=True)  # Enable debug mode
    print("🛑 PyWebView test stopped")
