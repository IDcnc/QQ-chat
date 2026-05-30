import webview
import os

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_window():
    """最简测试 - 只显示静态HTML"""
    
    # 方法1：直接加载HTML字符串
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>测试</title>
        <style>
            body { 
                font-family: Microsoft YaHei, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { text-align: center; }
            h1 { font-size: 48px; margin-bottom: 20px; }
            p { font-size: 18px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ 成功！</h1>
            <p>如果你能看到这个界面，说明 PyWebView 工作正常</p>
            <p>时间：<span id="time"></span></p>
        </div>
        <script>
            function updateTime() {
                document.getElementById('time').textContent = new Date().toLocaleString('zh-CN');
            }
            updateTime();
            setInterval(updateTime, 1000);
        </script>
    </body>
    </html>
    """
    
    print("🚀 正在创建窗口...")
    window = webview.create_window(
        "PyWebView 测试", 
        html=html_content,
        width=800, 
        height=600
    )
    print("✅ 窗口创建成功")
    return window

if __name__ == "__main__":
    print("="*50)
    print("PyWebView 最简测试")
    print("="*50)
    print(f"Python 版本: {__import__('sys').version}")
    print(f"PyWebView 版本: {webview.__version__}")
    print("="*50)
    
    try:
        window = create_window()
        print("🚀 正在启动 PyWebView...")
        webview.start(debug=True)
        print("✅ PyWebView 已关闭")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*50)
    print("测试结束")
    print("="*50)
