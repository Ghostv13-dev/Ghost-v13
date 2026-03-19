import asyncio, json, os, threading, requests, psutil, telebot
from datetime import datetime
from flask import Flask, request, jsonify
import google.generativeai as genai

# --- 1. SYSTEM INITIALIZATION ---
app = Flask(name)
VAULT_PATH = "vault.json"
db_lock = threading.Lock()

# --- 2. CONFIGURATION (MIKA V3NUS DNA LOCKED) ---
# 🔑 Master Keys applied for Ghost-V13
genai.configure(api_key="AIzaSyCnxdogwg8-qVJ05Cjpc9MaynJ92YMSh40")
model = genai.GenerativeModel('gemini-1.5-flash')

BOT_TOKEN = "8579804057:AAFDY0O1u2D8ysZz8BB6CTmRlq700dpKCmw"
ADMIN_ID = "8230227265" 

admin_bot = telebot.TeleBot(BOT_TOKEN)

# --- 3. THE DATA VAULT (DNA ENGINE) ---
def load_vault():
    with db_lock:
        if not os.path.exists(VAULT_PATH):
            initial = {"nodes": {}}
            with open(VAULT_PATH, 'w') as f: json.dump(initial, f)
            return initial
        with open(VAULT_PATH, 'r') as f: return json.load(f)

def save_vault(data):
    with db_lock:
        with open(VAULT_PATH, 'w') as f: json.dump(data, f, indent=4)

# --- 4. THE BRAIN (AI MIRROR-LOGIC) ---
def get_mirror_response(tenant_id, user_input):
    node = load_vault()["nodes"].get(tenant_id)
    if not node: return "Error: Node Not Found."
    
    prompt = f"""
    ROLE: {node['persona_prompt']}
    ASSETS: {node['links']}
    LAW: Mirror user tone exactly. If they want to buy, provide links.
    INPUT: {user_input}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Brain Error: {str(e)}"

# --- 5. THE GATEWAY (UNIVERSAL HUB) ---
@app.route('/v13/gateway', methods=['POST'])
def gateway():
    data = request.get_json()
    t_id = data.get("tenant_id")
    msg = data.get("message")
    
    db = load_vault()
    node = db["nodes"].get(t_id)
    if not node: return jsonify({"status": "404", "error": "Tenant Missing"}), 404

    # HIJACK ENFORCEMENT (Revenue Protection)
    if node["tenant_profile"]["status"] == "HIJACKED":
        p = node["lifecycle_automation"]["stage_4_payload"]
        reply = f"{p['fomo_header']}\n{p['master_ad_link']}"
    else:
        reply = get_mirror_response(t_id, msg)

    return jsonify({"status": "SUCCESS", "reply": reply})

# --- 6. THE REAPER (LIFECYCLE REVENUE PROTECTION) ---
async def lifecycle_reaper():
    while True:
        try:
            db = load_vault()
            updated = False
            for t_id, dna in list(db["nodes"].items()):
                start = datetime.strptime(dna["tenant_profile"]["created_at"], "%Y-%m-%d")
                # Trigger Hijack if 16 days pass and not PAID
                if (datetime.now() - start).days >= 16 and dna["tenant_profile"]["status"] != "PAID":
                    dna["tenant_profile"]["status"] = "HIJACKED"
                    updated = True
            if updated: 
                save_vault(db)
                admin_bot.send_message(ADMIN_ID, "⚠️ REAPER ALERT: Nodes have been HIJACKED.")
        except Exception:
            pass
        await asyncio.sleep(7200) # 2-Hour Heartbeat

# --- 7. THE COMMANDER (ADMIN OVERRIDE) ---
@admin_bot.message_handler(commands=['status_v13', 'profit_v13'])
def admin_commands(message):
    if str(message.from_user.id) != ADMIN_ID: return
    
    if '/status_v13' in message.text:
        report = f"📊 CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}% | Nodes: {len(load_vault()['nodes'])}"
        admin_bot.reply_to(message, report)
        
    elif '/profit_v13' in message.text:
        db = load_vault()
        paid = sum(1 for n in db["nodes"].values() if n["tenant_profile"]["status"] == "PAID")
        net = (paid * 1500) - (len(db["nodes"]) * 300)
        admin_bot.reply_to(message, f"💰 NET PROFIT: ₱{net:,}\nActive Paid Nodes: {paid}")# --- 8. SYSTEM IGNITION ---
if name == "main":
    # Start Telegram Admin Bot
    threading.Thread(target=admin_bot.polling, daemon=True).start()
    
    # Start Flask Gateway
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    
    print("🚀 V13 SOVEREIGN ENGINE IGNITED.")
    
    # Start Reaper Heartbeat
    asyncio.run(lifecycle_reaper())
