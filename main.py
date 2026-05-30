import json
import os
import sys
import threading
import time
import socket
import uuid
import webview
import requests as req
import websocket as ws_module
from bottle import Bottle, request, response, static_file

SERVER_PORT = 9527

def find_free_port(start=9527, max_try=10):
    for port in range(start, start + max_try):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except OSError:
            s.close()
            continue
    return None

CONFIG_DIR = os.path.expanduser("~/.qq_bot_manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
CONTACTS_FILE = os.path.join(CONFIG_DIR, "contacts.json")
MSG_DIR = os.path.join(CONFIG_DIR, "messages")
LOG_DIR = os.path.join(CONFIG_DIR, "logs")

# ==================== 环境切换 ====================
def get_api_urls(env="sandbox"):
    """返回 (token_url, gateway_url, api_base, intents) 根据环境"""
    # token URL 沙箱和正式相同
    token_url = "https://bots.qq.com/app/getAppAccessToken"
    if env == "production":
        return (
            token_url,
            "https://api.sgroup.qq.com/gateway",
            "https://api.sgroup.qq.com",
            1846285315
        )
    else:
        return (
            token_url,
            "https://sandbox.api.sgroup.qq.com/gateway",
            "https://sandbox.api.sgroup.qq.com",
            1073742849
        )

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(MSG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def safe_log(msg):
    ts = time.strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}\n"
    try:
        with open(os.path.join(LOG_DIR, "bot.log"), "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

def load_messages(contact_id):
    safe_id = contact_id.replace(":", "_").replace("\\", "_").replace("/", "_")
    path = os.path.join(MSG_DIR, safe_id + ".json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_messages(contact_id, msgs):
    safe_id = contact_id.replace(":", "_").replace("\\", "_").replace("/", "_")
    path = os.path.join(MSG_DIR, safe_id + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(msgs, f, indent=2, ensure_ascii=False)

bot_running = False
bot_connected = False
bot_thread = None
pending_openids = []

app = Bottle()

@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    if request.path.startswith("/api/"):
        response.headers["Content-Type"] = "application/json; charset=utf-8"

@app.route("/", method="GET")
@app.route("/index.html", method="GET")
def serve_index():
    return static_file("index.html", root=get_resource_path("."))

@app.route("/api/check_config")
def api_check_config():
    config = load_config()
    if config and config.get("appId") and config.get("secret"):
        return json.dumps({"status": "ok"})
    return json.dumps({"status": "not_configured"})

@app.route("/api/save_config", method="POST")
def api_save_config():
    try:
        data = request.json
        appId = (data.get("appId") or "").strip()
        secret = (data.get("secret") or "").strip()
        env = (data.get("env") or "sandbox").strip()
        if not appId or not secret:
            return json.dumps({"status": "error", "message": "请填写完整信息"})
        save_config({"appId": appId, "secret": secret, "env": env})
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/contacts")
def api_get_contacts():
    contacts = load_contacts()
    return json.dumps({"contacts": contacts})

@app.route("/api/add_contact", method="POST")
def api_add_contact():
    try:
        data = request.json
        name = (data.get("name") or "").strip()
        openid = (data.get("openid") or "").strip()
        avatar = (data.get("avatar") or "").strip()
        if not name or not openid:
            return json.dumps({"status": "error", "message": "请填写完整信息"})
        contacts = load_contacts()
        for c in contacts:
            if c.get("id") == openid:
                return json.dumps({"status": "error", "message": "该OpenID已存在"})
        contact = {"id": openid, "name": name, "type": "channel"}
        if avatar:
            contact["avatar"] = avatar
        contacts.append(contact)
        save_contacts(contacts)
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/remove_contact", method="POST")
def api_remove_contact():
    try:
        data = request.json
        openid = (data.get("openid") or "").strip()
        contacts = load_contacts()
        contacts = [c for c in contacts if c.get("id") != openid]
        save_contacts(contacts)
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/update_contact", method="POST")
def api_update_contact():
    try:
        data = request.json
        openid = (data.get("openid") or "").strip()
        name = (data.get("name") or "").strip()
        avatar = (data.get("avatar") or "").strip()
        if not openid or not name:
            return json.dumps({"status": "error", "message": "参数不完整"})
        contacts = load_contacts()
        for c in contacts:
            if c.get("id") == openid:
                c["name"] = name
                if avatar:
                    c["avatar"] = avatar
                else:
                    c.pop("avatar", None)
                save_contacts(contacts)
                return json.dumps({"status": "ok"})
        return json.dumps({"status": "error", "message": "联系人不存在"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/messages")
def api_get_messages():
    contact_id = request.query.get("contact_id", "")
    msgs = load_messages(contact_id)
    return json.dumps({"messages": msgs})

msg_seq_counter = 0

@app.route("/api/send_message", method="POST")
def api_send_message():
    try:
        data = request.json
        contact_id = data.get("contact_id", "")
        content = data.get("content", "")
        image = data.get("image", "").strip()
        if not contact_id or (not content and not image):
            return json.dumps({"status": "error", "message": "参数不完整"})

        global msg_seq_counter
        msg_seq_counter += 1

        # 获取 access_token
        config = load_config()
        if not config:
            return json.dumps({"status": "error", "message": "请先配置机器人"})
        env = config.get("env", "sandbox")
        token_url, gateway_url, api_base, _ = get_api_urls(env)

        # 获取 access token
        try:
            resp = req.post(token_url, json={
                "appId": config["appId"],
                "clientSecret": config["secret"]
            }, timeout=10)
            rj = resp.json()
            access_token = rj.get("access_token", "")
            if not access_token:
                return json.dumps({"status": "error", "message": f"Token获取失败: {rj}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Token请求失败: {e}"})

        headers = {
            "Authorization": f"QQBot {access_token}",
            "Content-Type": "application/json"
        }

        # 判断是 C2C(user:) 还是频道(channel:)
        if contact_id.startswith("user:"):
            openid = contact_id[5:]
            # C2C 图片走文件上传接口，消息 body 不能带 image 字段
            if image:
                # 先发文字（如果有）
                if content:
                    text_body = {"content": content, "msg_type": 0}
                    text_resp = req.post(f"{api_base}/v2/users/{openid}/messages", headers=headers, json=text_body, timeout=10)
                    safe_log(f"C2C text to {openid}: {text_resp.status_code}")
                # 上传图片并发送
                file_body = {"file_type": 1, "url": image, "srv_send_msg": True}
                resp = req.post(f"{api_base}/v2/users/{openid}/files", headers=headers, json=file_body, timeout=15)
            else:
                body = {"content": content, "msg_type": 0}
                resp = req.post(f"{api_base}/v2/users/{openid}/messages", headers=headers, json=body, timeout=10)
        else:
            channel_id = contact_id.replace("channel:", "")
            body = {"content": content, "msg_type": 1 if image else 0}
            if image:
                body["image"] = image
            resp = req.post(f"{api_base}/channels/{channel_id}/messages", headers=headers, json=body, timeout=10)
        result = resp.json() if resp.text else {"status_code": resp.status_code}

        if resp.status_code == 200 or resp.status_code == 202:
            msg_api_id = result.get("id") or result.get("message_id") or ""
            msg_body = {"from": "bot", "content": content if content else image}
            if msg_api_id:
                msg_body["msg_id"] = msg_api_id
            msgs = load_messages(contact_id)
            msgs.append(msg_body)
            save_messages(contact_id, msgs)
            safe_log(f"Sent to {contact_id}: {(content or image)[:50]}")
            return json.dumps({"status": "ok", "msg_id": msg_api_id})
        else:
            safe_log(f"Send FAILED to {contact_id}: {resp.status_code} {result}")
            return json.dumps({"status": "error", "message": f"发送失败: {result}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/recall_message", method="POST")
def api_recall_message():
    try:
        data = request.json
        contact_id = data.get("contact_id", "")
        msg_id = data.get("msg_id", "").strip()
        if not contact_id or not msg_id:
            return json.dumps({"status": "error", "message": "参数不完整"})

        config = load_config()
        if not config:
            return json.dumps({"status": "error", "message": "请先配置机器人"})
        env = config.get("env", "sandbox")
        token_url, gateway_url, api_base, _ = get_api_urls(env)

        resp = req.post(token_url, json={
            "appId": config["appId"],
            "clientSecret": config["secret"]
        }, timeout=10)
        rj = resp.json()
        access_token = rj.get("access_token", "")
        if not access_token:
            return json.dumps({"status": "error", "message": f"Token获取失败: {rj}"})

        headers = {
            "Authorization": f"QQBot {access_token}",
            "Content-Type": "application/json"
        }

        if contact_id.startswith("user:"):
            openid = contact_id[5:]
            recall_url = f"{api_base}/v2/users/{openid}/messages/{msg_id}"
        else:
            channel_id = contact_id.replace("channel:", "")
            recall_url = f"{api_base}/channels/{channel_id}/messages/{msg_id}"

        resp = req.delete(recall_url, headers=headers, json={"hidetip": False}, timeout=10)
        if resp.status_code == 200 or resp.status_code == 204:
            # 同步删除本地消息
            msgs = load_messages(contact_id)
            msgs = [m for m in msgs if m.get("msg_id") != msg_id]
            save_messages(contact_id, msgs)
            safe_log(f"Recalled msg {msg_id} from {contact_id}")
            return json.dumps({"status": "ok"})
        else:
            result = resp.json() if resp.text else {"status_code": resp.status_code}
            safe_log(f"Recall FAILED {msg_id}: {resp.status_code} {result}")
            return json.dumps({"status": "error", "message": f"撤回失败: {result}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/clear_messages", method="POST")
def api_clear_messages():
    try:
        data = request.json
        contact_id = data.get("contact_id", "").strip()
        if not contact_id:
            return json.dumps({"status": "error", "message": "参数不完整"})
        save_messages(contact_id, [])
        safe_log(f"Cleared messages for {contact_id}")
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/proxy_image")
def api_proxy_image():
    url = request.query.get("url", "")
    if not url:
        response.status = 400
        return "missing url"
    try:
        config = load_config()
        headers = {}
        if config:
            env = config.get("env", "sandbox")
            token_url, gateway_url, api_base, _ = get_api_urls(env)
            token_resp = req.post(token_url, json={"appId": config["appId"], "clientSecret": config["secret"]}, timeout=8)
            rj = token_resp.json()
            access_token = rj.get("access_token", "")
            if access_token:
                headers["Authorization"] = f"QQBot {access_token}"
        img_resp = req.get(url, headers=headers, timeout=15)
        response.content_type = img_resp.headers.get("content-type", "image/png")
        response.set_header("Cache-Control", "public, max-age=300")
        return img_resp.content
    except Exception as e:
        response.status = 502
        return str(e)

@app.route("/api/bot_status")
def api_bot_status():
    return json.dumps({"running": bot_running, "connected": bot_connected})

@app.route("/api/start_bot", method="POST")
def api_start_bot():
    global bot_running, bot_thread
    if bot_running:
        return json.dumps({"status": "ok", "message": "已在运行中"})
    config = load_config()
    if not config or not config.get("appId"):
        return json.dumps({"status": "error", "message": "请先配置AppID和Secret"})
    bot_running = True
    bot_thread = threading.Thread(target=bot_worker, args=(config,), daemon=True)
    bot_thread.start()
    return json.dumps({"status": "ok", "message": "启动中"})

@app.route("/api/stop_bot", method="POST")
def api_stop_bot():
    global bot_running, bot_connected
    bot_running = False
    bot_connected = False
    return json.dumps({"status": "ok", "message": "已停止"})

@app.route("/api/pending_openids")
def api_get_pending_openids():
    global pending_openids
    result = list(pending_openids)
    pending_openids.clear()
    return json.dumps({"openids": result})

@app.route("/api/confirm_openid", method="POST")
def api_confirm_openid():
    try:
        data = request.json
        openid = (data.get("openid") or "").strip()
        name = (data.get("name") or "").strip()
        if not openid or not name:
            return json.dumps({"status": "error", "message": "参数不完整"})
        contacts = load_contacts()
        found = False
        for c in contacts:
            if c.get("id") == openid:
                c["name"] = name
                found = True
                break
        if not found:
            contacts.append({"id": openid, "name": name, "type": "channel"})
        save_contacts(contacts)
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/open_log_folder", method="POST")
def api_open_log_folder():
    try:
        os.startfile(LOG_DIR)
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route("/api/reset", method="POST")
def api_reset():
    try:
        for f in [CONFIG_FILE, CONTACTS_FILE]:
            if os.path.exists(f):
                os.remove(f)
        for fn in os.listdir(MSG_DIR):
            os.remove(os.path.join(MSG_DIR, fn))
        global bot_running
        bot_running = False
        bot_connected = False
        return json.dumps({"status": "ok"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# ==================== 实时日志 ====================
@app.route("/log_viewer")
def serve_log_viewer():
    return '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>实时日志</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:Consolas,"Microsoft YaHei",monospace; background:#1e1e1e; color:#d4d4d4; padding:16px; height:100vh; display:flex; flex-direction:column; }
h2 { font-size:14px; color:#569cd6; margin-bottom:12px; display:flex; justify-content:space-between; }
.btn { background:#0e639c; color:#fff; border:none; padding:4px 12px; border-radius:4px; cursor:pointer; font-size:12px; }
.btn:hover { background:#1177bb; }
#logBox { flex:1; overflow-y:auto; background:#252526; padding:12px; border-radius:6px; font-size:12px; line-height:1.6; white-space:pre-wrap; word-break:break-all; }
#status { color:#6a9955; font-size:11px; margin-top:8px; }
</style></head>
<body>
<h2><span>QQBotManager 实时日志</span><button class="btn" onclick="location.reload()">刷新</button></h2>
<div id="logBox">加载中...</div>
<div id="status"></div>
<script>
var API_BASE = window.location.origin;
function poll() {
    fetch(API_BASE + "/api/log_content")
        .then(function(r) { return r.json(); })
        .then(function(d) {
            var box = document.getElementById("logBox");
            box.textContent = d.content || "暂无日志";
            box.scrollTop = box.scrollHeight;
            document.getElementById("status").textContent = "更新: " + new Date().toLocaleTimeString() + " | 大小: " + (d.size || 0) + " 字节";
        })
        .catch(function(e) {
            document.getElementById("status").textContent = "错误: " + e;
        });
}
poll();
setInterval(poll, 2000);
</script>
</body></html>'''

@app.route("/api/log_content")
def api_log_content():
    try:
        log_path = os.path.join(LOG_DIR, "bot.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
            return json.dumps({"content": content, "size": os.path.getsize(log_path)})
        return json.dumps({"content": "暂无日志", "size": 0})
    except Exception as e:
        return json.dumps({"content": f"读取错误: {e}", "size": 0})

@app.route("/api/open_log_window", method="POST")
def api_open_log_window():
    """打开日志查看器（由前端用JS window.open实现）"""
    return json.dumps({"status": "ok", "url": "/log_viewer"})

# ==================== 自动扫描联系人 ====================
@app.route("/api/auto_scan_contacts", method="POST")
def api_auto_scan_contacts():
    """从bot.log中扫描未添加的openid，自动加入联系人"""
    try:
        log_path = os.path.join(LOG_DIR, "bot.log")
        if not os.path.exists(log_path):
            return json.dumps({"status": "ok", "added": 0, "message": "日志文件不存在"})
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()

        import re
        added = 0
        contacts = load_contacts()
        existing_ids = {c.get("id") for c in contacts}

        # 从日志中提取所有 contact_id（格式：Msg from channel:xxx 或 user:xxx）
        pattern = re.compile(r"Msg from (\S+):")
        found_ids = set(pattern.findall(content))

        for cid in found_ids:
            contact_id = f"{cid}"
            if contact_id not in existing_ids:
                contacts.append({"id": contact_id, "name": contact_id, "type": "auto"})
                existing_ids.add(contact_id)
                added += 1

        if added > 0:
            save_contacts(contacts)

        return json.dumps({"status": "ok", "added": added, "found": len(found_ids)})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def bot_worker(config):
    global bot_running, bot_connected
    app_id = config["appId"]
    secret = config["secret"]
    env = config.get("env", "sandbox")
    token_url, gateway_url, api_base, intents_val = get_api_urls(env)

    def log(msg):
        ts = time.strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}\n"
        try:
            with open(os.path.join(LOG_DIR, "bot.log"), "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    log("Bot connecting...")

    # Step 1: Get access token
    log("Getting access token...")
    log(f"Environment: {env}")
    try:
        resp = req.post(
            token_url,
            json={"appId": app_id, "clientSecret": secret},
            timeout=15
        )
        token_data = resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            log(f"Token error: {token_data}")
            bot_running = False
            bot_connected = False
            return
        log(f"Token obtained: {access_token[:15]}...")
    except Exception as e:
        log(f"Token request failed: {e}")
        bot_running = False
        bot_connected = False
        return

    # Step 2: Get gateway URL
    log("Getting gateway URL...")
    try:
        gw_resp = req.get(
            gateway_url,
            headers={"Authorization": f"QQBot {access_token}"},
            timeout=15
        )
        gw_data = gw_resp.json()
        ws_url = gw_data.get("url")
        if not ws_url:
            log(f"Gateway error: {gw_data}")
            bot_running = False
            bot_connected = False
            return
        log(f"Gateway: {ws_url}")
    except Exception as e:
        log(f"Gateway request failed: {e}")
        bot_running = False
        bot_connected = False
        return

    # Step 3: Connect WebSocket
    try:
        ws = ws_module.create_connection(ws_url, timeout=10)
        log("WebSocket connected")
    except Exception as e:
        log(f"WebSocket connect failed: {e}")
        bot_running = False
        bot_connected = False
        return

    # Step 4: Build identify payload (matches official botpy SDK)
    # Intents: all public events (no guild_messages/forums - sandbox only)
    identify_payload = json.dumps({
        "op": 2,
        "d": {
            "token": f"QQBot {access_token}",
            "intents": intents_val,
            "shard": [0, 1]
        }
    })

    # Step 5: Wait for HELLO, then identify (official SDK order)
    hb_interval = 30
    last_seq = 0
    identified = False

    while bot_running:
        try:
            ws.settimeout(hb_interval * 0.8)
            msg = ws.recv()
            if not msg or not msg.strip():
                continue
            data = json.loads(msg)
            op = data.get("op")
            seq = data.get("s")

            if seq is not None:
                last_seq = seq

            if op == 10:
                hb_interval = max(data.get("d", {}).get("heartbeat_interval", 30000) / 1000.0, 5)
                log(f"Heartbeat: {hb_interval}s")
                if not identified:
                    ws.send(identify_payload)
                    log("Identify sent")
                    identified = True

            elif op == 11:
                pass

            elif op == 0:
                t = data.get("t", "")
                d = data.get("d", {})

                if t == "READY":
                    bot_connected = True
                    bot_user = d.get("user", {})
                    session_id = d.get("session_id", "")
                    log(f"Bot ready: {bot_user.get('username', 'unknown')} (session: {session_id[:8]}...)")

                elif t in ("MESSAGE_CREATE", "AT_MESSAGE_CREATE", "DIRECT_MESSAGE_CREATE",
                           "C2C_MESSAGE_CREATE", "GROUP_AT_MESSAGE_CREATE", "PUBLIC_MESSAGE_DELETE"):
                    author = d.get("author", {})
                    author_id = author.get("id", "unknown")
                    content = d.get("content", "")
                    channel_id = d.get("channel_id", "")
                    guild_id = d.get("guild_id", "")
                    # 提取附件图片 URL
                    attachments = d.get("attachments", [])
                    image_urls = [a.get("url", "") for a in attachments if a.get("url")]

                    contact_id = f"channel:{channel_id}" if channel_id else f"user:{author_id}"
                    log(f"Msg [{t}] from {contact_id}: {(content or '附件图片')[:50]}")

                    msgs = load_messages(contact_id)
                    msg_entry = {"from": "user", "content": content}
                    if image_urls:
                        msg_entry["images"] = image_urls
                    msgs.append(msg_entry)
                    save_messages(contact_id, msgs)

                    contacts = load_contacts()
                    in_contacts = any(c.get("id") == contact_id for c in contacts)
                    if not in_contacts:
                        found = any(p.get("openid") == contact_id for p in pending_openids)
                        if not found:
                            pending_openids.append({"openid": contact_id})

                else:
                    log(f"Event: {t} data_keys={list(d.keys())[:5]}")

            elif op == 7:
                log("Server requested reconnect")
                try:
                    ws.close()
                except Exception:
                    pass
                ws = ws_module.create_connection(ws_url, timeout=10)
                identified = False
                log("Reconnected (op:7), waiting for HELLO...")

            elif op == 9:
                log("Invalid session - reconnecting fresh...")
                try:
                    ws.close()
                except Exception:
                    pass
                ws = ws_module.create_connection(ws_url, timeout=10)
                identified = False
                log("Reconnected, waiting for HELLO...")

        except ws_module.WebSocketTimeoutException:
            try:
                ws.send(json.dumps({"op": 1, "d": last_seq}))
            except Exception as e:
                log(f"Heartbeat failed: {e}")
                bot_running = False
                bot_connected = False
        except Exception as e:
            log(f"WS error: {e}")
            if bot_running:
                time.sleep(3)
                try:
                    ws = ws_module.create_connection(ws_url, timeout=10)
                    identified = False
                    log("Reconnected, waiting for HELLO...")
                except Exception:
                    bot_running = False
                    bot_connected = False

    try:
        ws.close()
    except Exception:
        pass
    log("Bot stopped")


def start_server(port):
    from bottle import run as bottle_run
    bottle_run(app, host="127.0.0.1", port=port, quiet=True, reloader=False)


if __name__ == "__main__":
    port = find_free_port(SERVER_PORT)
    if port is None:
        print("ERROR: No free port found!")
        sys.exit(1)

    print(f"Starting server on port {port}...")

    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1.5)

    url = f"http://127.0.0.1:{port}/"
    print(f"Loading {url}")

    window = webview.create_window("QQ聊天", url, width=1100, height=750, resizable=True)
    webview.start(debug=False)
