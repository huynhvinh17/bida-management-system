# bida_system_final_working.py
import streamlit as st
import pandas as pd
import datetime
import json
import os
import time
import plotly.graph_objects as go
import plotly.express as px

# ================== CẤU HÌNH ==================
class BidaConfig:
    SHOP_NAME = "CLUB BILLIARD MR.BOM"
    SHOP_FULL_NAME = "🏆 MR.BOM BILLIARDS CLUB 🏆"
    SHOP_ADDRESS = "332,334 Đường Trần Hưng Đạo, Điện Bàn Đông, Đà Nẵng"
    PHONE = "0905.995.442"
    FANPAGE = "https://www.facebook.com/quan.ang.125714"
    OWNER_PASSWORD = "123456"
    
    TABLES = {
        1: {"name": "BÀN 1", "type": "Libre", "price_per_hour": 40000, "status": "available"},
        2: {"name": "BÀN 2", "type": "Libre", "price_per_hour": 40000, "status": "available"},
        3: {"name": "BÀN 3", "type": "Libre", "price_per_hour": 40000, "status": "available"},
        4: {"name": "BÀN 4", "type": "Libre", "price_per_hour": 40000, "status": "available"},
        5: {"name": "BÀN 5", "type": "Carom", "price_per_hour": 60000, "status": "available"},
        6: {"name": "BÀN 6", "type": "Carom", "price_per_hour": 60000, "status": "available"},
        7: {"name": "BÀN 7", "type": "Lỗ", "price_per_hour": 40000, "status": "available"},
        8: {"name": "BÀN 8", "type": "Lỗ", "price_per_hour": 40000, "status": "available"},
    }
    
    DATA_FOLDER = "bida_data"
    SESSIONS_FILE = f"{DATA_FOLDER}/sessions.json"
    ALERTS_FILE = f"{DATA_FOLDER}/alerts.json"
    MENU_FILE = f"{DATA_FOLDER}/menu.json"

# ================== MENU MANAGER ==================
class MenuManager:
    def __init__(self):
        self.menu = self.load_menu()
    
    def load_menu(self):
        if os.path.exists(BidaConfig.MENU_FILE):
            with open(BidaConfig.MENU_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "🥤 NƯỚC GIẢI KHÁT": {
                "Coca Cola": {"price": 15000, "stock": 100, "unit": "chai"},
                "Pepsi": {"price": 15000, "stock": 100, "unit": "chai"},
            },
            "🍺 BIA": {
                "Heineken": {"price": 30000, "stock": 150, "unit": "lon"},
                "Tiger": {"price": 30000, "stock": 120, "unit": "lon"},
            },
            "☕ CÀ PHÊ & TRÀ": {
                "Cà phê đen": {"price": 15000, "stock": 50, "unit": "ly"},
                "Cà phê sữa": {"price": 18000, "stock": 50, "unit": "ly"},
            }
        }
    
    def save_menu(self):
        with open(BidaConfig.MENU_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.menu, f, indent=2, ensure_ascii=False)
    
    def add_item(self, category, item_name, price, stock, unit):
        if category in self.menu and item_name not in self.menu[category]:
            self.menu[category][item_name] = {"price": price, "stock": stock, "unit": unit}
            self.save_menu()
            return True
        return False
    
    def delete_item(self, category, item_name):
        if category in self.menu and item_name in self.menu[category]:
            del self.menu[category][item_name]
            self.save_menu()
            return True
        return False
    
    def update_item_price(self, category, item_name, new_price):
        if category in self.menu and item_name in self.menu[category]:
            self.menu[category][item_name]["price"] = new_price
            self.save_menu()
            return True
        return False
    
    def update_item_stock(self, category, item_name, new_stock):
        if category in self.menu and item_name in self.menu[category]:
            self.menu[category][item_name]["stock"] = new_stock
            self.save_menu()
            return True
        return False
    
    def add_stock(self, item_name, quantity):
        for category, items in self.menu.items():
            if item_name in items:
                self.menu[category][item_name]["stock"] += quantity
                self.save_menu()
                return True
        return False

# ================== QUẢN LÝ DỮ LIỆU ==================
class DataManager:
    def __init__(self):
        os.makedirs(BidaConfig.DATA_FOLDER, exist_ok=True)
        self.menu_manager = MenuManager()
        self.sessions = self.load_sessions()
        self.alerts = self.load_alerts()
        
    def load_sessions(self):
        if os.path.exists(BidaConfig.SESSIONS_FILE):
            with open(BidaConfig.SESSIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for session in data:
                    if 'orders' not in session:
                        session['orders'] = []
                    if 'score' not in session:
                        session['score'] = {"player1": 0, "player2": 0}
                    if 'innings' not in session:
                        session['innings'] = {"player1": 0, "player2": 0}
                return data
        return []
    
    def load_alerts(self):
        if os.path.exists(BidaConfig.ALERTS_FILE):
            with open(BidaConfig.ALERTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_sessions(self):
        with open(BidaConfig.SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, indent=2, ensure_ascii=False)
    
    def save_alerts(self):
        with open(BidaConfig.ALERTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, indent=2, ensure_ascii=False)
    
    def play_sound(self, sound_type):
        """Phát âm thanh trên trình duyệt"""
        sounds = {
            "bell": "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
            "order": "https://www.soundjay.com/misc/sounds/notification-01.mp3",
            "payment": "https://www.soundjay.com/misc/sounds/cash-register-01.mp3",
            "booking": "https://www.soundjay.com/misc/sounds/button-09.mp3",
            "alert": "https://www.soundjay.com/misc/sounds/alarm-clock-01.mp3"
        }
        if sound_type in sounds:
            sound_html = f'<audio autoplay style="display:none;"><source src="{sounds[sound_type]}" type="audio/mpeg"></audio>'
            st.markdown(sound_html, unsafe_allow_html=True)
    
    def add_alert(self, table_id, table_name):
        alert = {
            "time": datetime.datetime.now().isoformat(),
            "table_id": table_id,
            "table_name": table_name,
            "status": "pending"
        }
        self.alerts.append(alert)
        self.save_alerts()
        self.play_sound("alert")
        return True
    
    def remove_alert(self, alert_index):
        if 0 <= alert_index < len(self.alerts):
            self.alerts.pop(alert_index)
            self.save_alerts()
            return True
        return False
    
    def get_pending_alerts(self):
        return [a for a in self.alerts if a.get("status") == "pending"]
    
    def start_session(self, table_id, customer_name, customer_phone, player1_name, player2_name):
        session_id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{table_id}"
        session = {
            "session_id": session_id,
            "table_id": table_id,
            "table_name": BidaConfig.TABLES[table_id]["name"],
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "player1_name": player1_name,
            "player2_name": player2_name,
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "status": "active",
            "total_amount": 0,
            "score": {"player1": 0, "player2": 0},
            "innings": {"player1": 0, "player2": 0},
            "orders": []
        }
        self.sessions.append(session)
        BidaConfig.TABLES[table_id]["status"] = "occupied"
        self.save_sessions()
        self.play_sound("booking")
        return session_id
    
    def add_order(self, table_id, category, item, quantity, price):
        stock = self.menu_manager.menu[category][item]["stock"]
        if stock < quantity:
            return False, f"❌ {item} chỉ còn {stock} {self.menu_manager.menu[category][item]['unit']}!"
        
        for session in self.sessions:
            if session["table_id"] == table_id and session["status"] == "active":
                if 'orders' not in session:
                    session['orders'] = []
                session["orders"].append({
                    "time": datetime.datetime.now().isoformat(),
                    "category": category,
                    "item": item,
                    "quantity": quantity,
                    "price": price,
                    "total": price * quantity
                })
                self.menu_manager.menu[category][item]["stock"] -= quantity
                self.menu_manager.save_menu()
                self.save_sessions()
                self.play_sound("order")
                return True, f"✅ Đã thêm {quantity} {item}!"
        return False, "❌ Lỗi thêm món!"
    
    def remove_order(self, table_id, order_index):
        for session in self.sessions:
            if session["table_id"] == table_id and session["status"] == "active":
                if 'orders' in session and 0 <= order_index < len(session["orders"]):
                    order = session["orders"][order_index]
                    for category, items in self.menu_manager.menu.items():
                        if order["item"] in items:
                            self.menu_manager.menu[category][order["item"]]["stock"] += order["quantity"]
                            break
                    self.menu_manager.save_menu()
                    session["orders"].pop(order_index)
                    self.save_sessions()
                    return True
        return False
    
    def get_food_total(self, table_id):
        for session in self.sessions:
            if session["table_id"] == table_id and session["status"] == "active":
                if 'orders' not in session:
                    session['orders'] = []
                return sum(order["total"] for order in session["orders"])
        return 0
    
    def update_score(self, table_id, player, points, is_increment=True):
        for session in self.sessions:
            if session["table_id"] == table_id and session["status"] == "active":
                if is_increment:
                    session["score"][player] += points
                    session["innings"][player] += 1
                else:
                    session["score"][player] = max(0, session["score"][player] - points)
                self.save_sessions()
                return True
        return False
    
    def end_session(self, table_id):
        for session in self.sessions:
            if session["table_id"] == table_id and session["status"] == "active":
                session["end_time"] = datetime.datetime.now().isoformat()
                session["status"] = "completed"
                start = datetime.datetime.fromisoformat(session["start_time"])
                end = datetime.datetime.fromisoformat(session["end_time"])
                minutes_played = (end - start).total_seconds() / 60
                price_per_hour = BidaConfig.TABLES[table_id]["price_per_hour"]
                price_per_minute = price_per_hour / 60
                table_fee = int(price_per_minute * minutes_played)
                food_fee = sum(order["total"] for order in session.get("orders", []))
                session["table_fee"] = table_fee
                session["food_fee"] = food_fee
                session["total_amount"] = table_fee + food_fee
                session["minutes_played"] = round(minutes_played, 1)
                BidaConfig.TABLES[table_id]["status"] = "available"
                self.save_sessions()
                self.play_sound("payment")
                return session
        return None
    
    def get_active_sessions(self):
        active = []
        for session in self.sessions:
            if session["status"] == "active":
                start = datetime.datetime.fromisoformat(session["start_time"])
                elapsed = datetime.datetime.now() - start
                elapsed_minutes = elapsed.total_seconds() / 60
                if 'orders' not in session:
                    session['orders'] = []
                active.append({
                    "table_id": session["table_id"],
                    "table_name": session["table_name"],
                    "customer_name": session["customer_name"],
                    "player1_name": session.get("player1_name", "Player 1"),
                    "player2_name": session.get("player2_name", "Player 2"),
                    "score": session.get("score", {"player1": 0, "player2": 0}),
                    "innings": session.get("innings", {"player1": 0, "player2": 0}),
                    "orders": session.get("orders", []),
                    "start_time": start,
                    "elapsed_minutes": elapsed_minutes
                })
        return active
    
    def get_today_revenue(self):
        today = datetime.datetime.now().date()
        total_table = 0
        total_food = 0
        table_revenue = {}
        food_revenue = {}
        
        for session in self.sessions:
            if session["status"] == "completed":
                start_date = datetime.datetime.fromisoformat(session["start_time"]).date()
                if start_date == today:
                    table_fee = session.get("table_fee", 0)
                    food_fee = session.get("food_fee", 0)
                    total_table += table_fee
                    total_food += food_fee
                    
                    table_name = session["table_name"]
                    if table_name not in table_revenue:
                        table_revenue[table_name] = {"table": 0, "food": 0}
                    table_revenue[table_name]["table"] += table_fee
                    table_revenue[table_name]["food"] += food_fee
                    
                    for order in session.get("orders", []):
                        item = order["item"]
                        if item not in food_revenue:
                            food_revenue[item] = {"quantity": 0, "revenue": 0}
                        food_revenue[item]["quantity"] += order["quantity"]
                        food_revenue[item]["revenue"] += order["total"]
        
        return total_table, total_food, table_revenue, food_revenue

# ================== GIAO DIỆN ==================

def setup_page():
    st.set_page_config(
        page_title="MR.BOM Billiards Club",
        page_icon="🎱",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%); }
    .mr-bom-logo {
        text-align: center;
        padding: 15px;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        border: 2px solid #ffd700;
    }
    .mr-bom-text {
        font-family: monospace;
        font-size: 48px;
        font-weight: bold;
        background: linear-gradient(45deg, #ffd700, #ff8c00, #ff4500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 4px;
    }
    .available-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        cursor: pointer;
    }
    .available-card:hover { transform: scale(1.02); }
    .occupied-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def display_logo():
    st.markdown(f"""
    <div class="mr-bom-logo">
        <div class="mr-bom-text">
            🎱 {BidaConfig.SHOP_FULL_NAME} 🎱
        </div>
        <div style="font-family: monospace; font-size: 12px; color: #ffd700;">
            {BidaConfig.SHOP_ADDRESS} | 📞 {BidaConfig.PHONE}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_ez_scoreboard(session, table_id, dm):
    minutes = int(session['elapsed_minutes'])
    seconds = int((session['elapsed_minutes'] - minutes) * 60)
    
    p1_hr = session['score']['player1']
    p2_hr = session['score']['player2']
    p1_avg = session['score']['player1'] / max(session['innings']['player1'], 1)
    p2_avg = session['score']['player2'] / max(session['innings']['player2'], 1)
    
    swap_key = f"swap_{table_id}"
    if swap_key not in st.session_state:
        st.session_state[swap_key] = False
    
    if st.session_state[swap_key]:
        p1_color, p2_color = "#ffffff", "#ffd700"
        p1_bg, p2_bg = "#1a1a1a", "#1a1a00"
    else:
        p1_color, p2_color = "#ffd700", "#ffffff"
        p1_bg, p2_bg = "#1a1a00", "#1a1a1a"
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f"""
        <div style='background: {p1_bg}; border-radius: 15px; padding: 15px; text-align: center; border: 2px solid {p1_color};'>
            <h3 style='color: {p1_color};'>🏆 PLAYER 1</h3>
            <h2 style='color: {p1_color}; font-size: 14px;'>{session['player1_name']}</h2>
            <h1 style='font-size: 70px; color: {p1_color};'>{session['score']['player1']}</h1>
            <p style='color: {p1_color};'>Innings: {session['innings']['player1']}</p>
            <p style='color: #aaa;'>HR {p1_hr} | Avg {p1_avg:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("+1", key=f"p1_add1_{table_id}"):
                dm.update_score(table_id, "player1", 1, True)
                st.rerun()
        with col_b:
            if st.button("+5", key=f"p1_add5_{table_id}"):
                dm.update_score(table_id, "player1", 5, True)
                st.rerun()
        with col_c:
            if st.button("-1", key=f"p1_sub1_{table_id}"):
                dm.update_score(table_id, "player1", 1, False)
                st.rerun()
        with col_d:
            if st.button("-5", key=f"p1_sub5_{table_id}"):
                dm.update_score(table_id, "player1", 5, False)
                st.rerun()
    
    with col2:
        st.markdown(f"""
        <div style='background: #000; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #333;'>
            <h1 style='font-size: 42px; color: #0f0;'>{minutes:02d}:{seconds:02d}</h1>
            <p style='color: #aaa;'>{BidaConfig.TABLES[table_id]['price_per_hour']:,}đ/giờ</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 HOAN DOI", key=f"swap_btn_{table_id}"):
            st.session_state[swap_key] = not st.session_state[swap_key]
            st.rerun()
    
    with col3:
        st.markdown(f"""
        <div style='background: {p2_bg}; border-radius: 15px; padding: 15px; text-align: center; border: 2px solid {p2_color};'>
            <h3 style='color: {p2_color};'>🏆 PLAYER 2</h3>
            <h2 style='color: {p2_color}; font-size: 14px;'>{session['player2_name']}</h2>
            <h1 style='font-size: 70px; color: {p2_color};'>{session['score']['player2']}</h1>
            <p style='color: {p2_color};'>Innings: {session['innings']['player2']}</p>
            <p style='color: #aaa;'>HR {p2_hr} | Avg {p2_avg:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("+1", key=f"p2_add1_{table_id}"):
                dm.update_score(table_id, "player2", 1, True)
                st.rerun()
        with col_b:
            if st.button("+5", key=f"p2_add5_{table_id}"):
                dm.update_score(table_id, "player2", 5, True)
                st.rerun()
        with col_c:
            if st.button("-1", key=f"p2_sub1_{table_id}"):
                dm.update_score(table_id, "player2", 1, False)
                st.rerun()
        with col_d:
            if st.button("-5", key=f"p2_sub5_{table_id}"):
                dm.update_score(table_id, "player2", 5, False)
                st.rerun()

def display_customer_interface(dm):
    st.markdown("### 🎯 CHỌN BÀN BIDA")
    active = {s["table_id"]: s for s in dm.get_active_sessions()}
    
    for row in range(2):
        cols = st.columns(4)
        for i in range(4):
            tid = row * 4 + i + 1
            if tid > 8: break
            with cols[i]:
                t = BidaConfig.TABLES[tid]
                if tid in active:
                    s = active[tid]
                    mins = int(s['elapsed_minutes'])
                    st.markdown(f"""
                    <div class="occupied-card">
                        <h3>🎱 {t['name']}</h3>
                        <div style="font-size: 24px; color: #0f0;">{mins:02d}:00</div>
                        <div>🏆 {s['score']['player1']} - {s['score']['player2']}</div>
                        <div>🔴 ĐANG CHƠI</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"📱 VAO BAN", key=f"view_{tid}"):
                        st.session_state.customer_selected_table = tid
                        st.session_state.show_customer_detail = True
                else:
                    st.markdown(f"""
                    <div class="available-card">
                        <h3>🎱 {t['name']}</h3>
                        <div>💰 {t['price_per_hour']:,}đ/h</div>
                        <div>✅ TRỐNG</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🎯 DAT BAN", key=f"book_{tid}"):
                        st.session_state.customer_book_table = tid
                        st.session_state.show_customer_booking = True

def display_customer_booking_form(dm):
    if st.session_state.get("show_customer_booking", False):
        with st.expander("🎯 ĐẶT BÀN", expanded=True):
            tid = st.session_state.customer_book_table
            t = BidaConfig.TABLES[tid]
            st.info(f"🏠 **{t['name']}** - {t['price_per_hour']:,}đ/giờ")
            
            col1, col2 = st.columns(2)
            with col1:
                p1 = st.text_input("🎯 Tên Player 1", key="bk_p1")
                p2 = st.text_input("🎯 Tên Player 2", key="bk_p2")
            with col2:
                st.markdown(f"""
                <div style="background: #2e7d32; padding: 15px; border-radius: 10px;">
                    <b>💰 GIÁ BÀN</b><br>
                    {t['price_per_hour']:,}đ/giờ = {t['price_per_hour']/60:.0f}đ/phút
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("✅ XÁC NHẬN", key="confirm_booking"):
                if p1 and p2:
                    dm.start_session(tid, p1, "customer", p1, p2)
                    st.success(f"✅ ĐẶT BÀN THÀNH CÔNG!\n{p1} vs {p2}")
                    st.balloons()
                    st.session_state.show_customer_booking = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Nhập tên 2 người chơi!")
            
            if st.button("❌ HỦY", key="cancel_booking"):
                st.session_state.show_customer_booking = False
                st.rerun()

def display_order_section(table_id, session, dm):
    st.markdown("### 🍽️ GỌI MÓN")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        cat = st.selectbox("Danh mục", list(dm.menu_manager.menu.keys()), key=f"cat_{table_id}")
    with col2:
        if cat:
            items = list(dm.menu_manager.menu[cat].keys())
            item = st.selectbox("Món", items, key=f"item_{table_id}")
    with col3:
        qty = st.number_input("SL", min_value=1, max_value=20, value=1, key=f"qty_{table_id}")
    
    if cat and item:
        info = dm.menu_manager.menu[cat][item]
        st.caption(f"📦 Tồn: {info['stock']} {info['unit']} | 💰 {info['price']:,}đ")
        if info['stock'] >= qty:
            if st.button(f"➕ THÊM MÓN", key=f"add_{table_id}"):
                success, msg = dm.add_order(table_id, cat, item, qty, info['price'])
                if success:
                    st.success(msg)
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.error(f"❌ Không đủ hàng! Còn {info['stock']} {info['unit']}")
    
    orders = session.get("orders", [])
    if orders:
        st.markdown("### 📋 MÓN ĐÃ GỌI")
        for idx, o in enumerate(orders):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1: st.write(f"🍽️ {o['item']}")
            with c2: st.write(f"x{o['quantity']}")
            with c3: st.write(f"{o['total']:,}đ")
            with c4:
                if st.button("🗑️", key=f"del_{table_id}_{idx}"):
                    dm.remove_order(table_id, idx)
                    st.rerun()
        st.info(f"🍽️ Tổng tiền món: {dm.get_food_total(table_id):,}đ")

def display_customer_table_detail(dm):
    if st.session_state.get("show_customer_detail", False) and st.session_state.get("customer_selected_table"):
        tid = st.session_state.customer_selected_table
        active = {s["table_id"]: s for s in dm.get_active_sessions()}
        
        if tid in active:
            s = active[tid]
            st.markdown(f"## 🎱 {BidaConfig.TABLES[tid]['name']}")
            
            tab1, tab2, tab3 = st.tabs(["🎯 TỶ SỐ", "🍽️ GỌI MÓN", "💰 HÓA ĐƠN"])
            
            with tab1:
                display_ez_scoreboard(s, tid, dm)
            
            with tab2:
                display_order_section(tid, s, dm)
            
            with tab3:
                mins = int(s['elapsed_minutes'])
                price_h = BidaConfig.TABLES[tid]['price_per_hour']
                table_fee = int((price_h / 60) * s['elapsed_minutes'])
                food_total = dm.get_food_total(tid)
                
                st.markdown(f"""
                | Khoản mục | Số tiền |
                |-----------|---------|
                | ⏱️ Tiền bàn ({mins} phút) | {table_fee:,}đ |
                | 🍽️ Tiền món | {food_total:,}đ |
                | **💰 TỔNG CỘNG** | **{table_fee + food_total:,}đ** |
                """)
                
                if st.button("🔔 BÁO TÍNH TIỀN", key=f"bill_{tid}"):
                    dm.add_alert(tid, BidaConfig.TABLES[tid]['name'])
                    st.success("✅ Đã gửi yêu cầu! Nhân viên sẽ đến ngay!")
                    st.balloons()
                    time.sleep(1)
            
            if st.button("🔙 QUAY LẠI", key="back_cust"):
                st.session_state.show_customer_detail = False
                st.session_state.customer_selected_table = None
                st.rerun()

def display_owner_interface(dm):
    st.markdown("### 🎯 QUẢN LÝ BÀN BIDA")
    active = {s["table_id"]: s for s in dm.get_active_sessions()}
    alerts = dm.get_pending_alerts()
    
    if alerts:
        st.markdown("### 🔔 YÊU CẦU TÍNH TIỀN")
        for i, a in enumerate(alerts):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.warning(f"🛎️ **{a['table_name']}** - {a['time'][11:16]}")
            with c2:
                if st.button(f"💰 TÍNH TIỀN", key=f"pay_alert_{i}"):
                    st.session_state.owner_pay_table = a['table_id']
                    st.session_state.show_owner_payment = True
                    dm.remove_alert(i)
                    st.rerun()
            with c3:
                if st.button(f"✅ BỎ QUA", key=f"ignore_{i}"):
                    dm.remove_alert(i)
                    st.rerun()
        st.markdown("---")
    
    for row in range(2):
        cols = st.columns(4)
        for i in range(4):
            tid = row * 4 + i + 1
            if tid > 8: break
            with cols[i]:
                t = BidaConfig.TABLES[tid]
                if tid in active:
                    s = active[tid]
                    mins = int(s['elapsed_minutes'])
                    st.markdown(f"""
                    <div class="occupied-card">
                        <h3>🎱 {t['name']}</h3>
                        <div>⏱️ {mins:02d} phút</div>
                        <div>🏆 {s['score']['player1']} - {s['score']['player2']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"💰 TIỀN", key=f"pay_{tid}"):
                        st.session_state.owner_pay_table = tid
                        st.session_state.show_owner_payment = True
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="available-card">
                        <h3>🎱 {t['name']}</h3>
                        <div>💰 {t['price_per_hour']:,}đ/h</div>
                        <div>✅ TRỐNG</div>
                    </div>
                    """, unsafe_allow_html=True)

def display_owner_payment_form(dm):
    if st.session_state.get("show_owner_payment", False) and st.session_state.get("owner_pay_table"):
        tid = st.session_state.owner_pay_table
        active = {s["table_id"]: s for s in dm.get_active_sessions()}
        if tid in active:
            s = active[tid]
            with st.expander(f"💰 TÍNH TIỀN BÀN SỐ {tid}", expanded=True):
                mins = int(s['elapsed_minutes'])
                secs = int((s['elapsed_minutes'] - mins) * 60)
                price_h = BidaConfig.TABLES[tid]['price_per_hour']
                table_fee = int((price_h / 60) * s['elapsed_minutes'])
                food_total = dm.get_food_total(tid)
                st.markdown(f"""
                **👤 Khách:** {s['customer_name']}  
                **⏱️ Thời gian:** {mins:02d}:{secs:02d} ({s['elapsed_minutes']:.1f} phút)  
                **💰 Tiền bàn:** {table_fee:,}đ  
                **🍽️ Tiền món:** {food_total:,}đ  
                **💵 TỔNG CỘNG:** {table_fee + food_total:,}đ
                """)
                if st.button(f"✅ XÁC NHẬN THANH TOÁN", key=f"confirm_pay_{tid}"):
                    result = dm.end_session(tid)
                    if result:
                        st.success(f"✅ THANH TOÁN THÀNH CÔNG! Tổng: {result['total_amount']:,}đ")
                        st.balloons()
                        st.session_state.show_owner_payment = False
                        st.session_state.owner_pay_table = None
                        time.sleep(2)
                        st.rerun()

def display_stock_management(dm):
    st.markdown("### 📦 QUẢN LÝ TỒN KHO")
    data = []
    for cat, items in dm.menu_manager.menu.items():
        for name, info in items.items():
            data.append({"Danh mục": cat, "Sản phẩm": name, "Giá": f"{info['price']:,}đ", "Tồn kho": info['stock'], "Đơn vị": info['unit']})
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    
    st.markdown("### 📥 NHẬP HÀNG")
    all_items = [item for cat in dm.menu_manager.menu.values() for item in cat.keys()]
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        item = st.selectbox("Chọn sản phẩm", all_items)
    with col2:
        qty = st.number_input("Số lượng", min_value=1, max_value=1000, value=50)
    with col3:
        if st.button("📦 NHẬP HÀNG", key="import_stock"):
            if dm.menu_manager.add_stock(item, qty):
                st.success(f"✅ Đã nhập {qty} {item}")
                st.rerun()

def display_menu_management(dm):
    st.markdown("### 📝 QUẢN LÝ MENU")
    t1, t2, t3 = st.tabs(["➕ THÊM MÓN", "✏️ SỬA MÓN", "❌ XÓA MÓN"])
    
    with t1:
        st.markdown("#### Thêm món mới")
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Danh mục", list(dm.menu_manager.menu.keys()), key="add_cat")
        with col2:
            new_name = st.text_input("Tên món mới", key="new_name")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            price = st.number_input("Giá", min_value=1000, step=1000, value=15000, key="new_price")
        with col2:
            stock = st.number_input("Tồn kho", min_value=0, step=1, value=50, key="new_stock")
        with col3:
            unit = st.selectbox("Đơn vị", ["chai", "lon", "ly", "tô", "đĩa"], key="new_unit")
        with col4:
            if st.button("➕ THÊM", key="do_add"):
                if new_name and dm.menu_manager.add_item(cat, new_name, price, stock, unit):
                    st.success(f"✅ Đã thêm {new_name}")
                    st.rerun()
    
    with t2:
        st.markdown("#### Sửa giá/tồn kho")
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Danh mục", list(dm.menu_manager.menu.keys()), key="edit_cat")
        with col2:
            if cat:
                items = list(dm.menu_manager.menu[cat].keys())
                item = st.selectbox("Món", items, key="edit_item")
        if cat and item:
            curr = dm.menu_manager.menu[cat][item]
            col1, col2 = st.columns(2)
            with col1:
                new_price = st.number_input("Giá mới", value=curr["price"], step=1000, key="new_price_edit")
                if st.button("💾 CẬP NHẬT GIÁ", key="update_price"):
                    dm.menu_manager.update_item_price(cat, item, new_price)
                    st.success("✅ Đã cập nhật giá")
                    st.rerun()
            with col2:
                new_stock = st.number_input("Tồn kho mới", value=curr["stock"], step=1, key="new_stock_edit")
                if st.button("📦 CẬP NHẬT TỒN KHO", key="update_stock"):
                    dm.menu_manager.update_item_stock(cat, item, new_stock)
                    st.success("✅ Đã cập nhật tồn kho")
                    st.rerun()
    
    with t3:
        st.markdown("#### Xóa món")
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Danh mục", list(dm.menu_manager.menu.keys()), key="del_cat")
        with col2:
            if cat:
                items = list(dm.menu_manager.menu[cat].keys())
                item = st.selectbox("Chọn món", ["-- Chọn --"] + items, key="del_item")
        if cat and item and item != "-- Chọn --":
            if st.button("🗑️ XÓA MÓN", key="do_delete"):
                if dm.menu_manager.delete_item(cat, item):
                    st.success(f"✅ Đã xóa {item}")
                    st.rerun()

def display_detailed_statistics(dm):
    st.markdown("### 📊 THỐNG KÊ DOANH THU HÔM NAY")
    total_table, total_food, table_rev, _ = dm.get_today_revenue()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💰 TỔNG DOANH THU", f"{total_table + total_food:,.0f}đ")
    with c2: st.metric("🎱 DOANH THU BÀN", f"{total_table:,.0f}đ")
    with c3: st.metric("🍽️ DOANH THU MÓN", f"{total_food:,.0f}đ")
    with c4: st.metric("👥 SỐ BÀN", f"{len(table_rev)}")
    
    if table_rev:
        st.markdown("#### 🎯 DOANH THU THEO BÀN")
        df = pd.DataFrame([{"Bàn": t, "Tiền bàn": r["table"], "Tiền món": r["food"], "Tổng": r["table"] + r["food"]} for t, r in table_rev.items()])
        fig = go.Figure(data=[
            go.Bar(name="Tiền bàn", x=df["Bàn"], y=df["Tiền bàn"], marker_color="#ffd700"),
            go.Bar(name="Tiền món", x=df["Bàn"], y=df["Tiền món"], marker_color="#ff8c00")
        ])
        fig.update_layout(barmode='stack', title="Doanh thu theo bàn", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_logo()
    
    dm = DataManager()
    
    # Khởi tạo session state
    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "owner_authenticated" not in st.session_state:
        st.session_state.owner_authenticated = False
    if "show_customer_detail" not in st.session_state:
        st.session_state.show_customer_detail = False
    if "show_customer_booking" not in st.session_state:
        st.session_state.show_customer_booking = False
    if "show_owner_payment" not in st.session_state:
        st.session_state.show_owner_payment = False
    if "customer_selected_table" not in st.session_state:
        st.session_state.customer_selected_table = None
    if "customer_book_table" not in st.session_state:
        st.session_state.customer_book_table = None
    if "owner_pay_table" not in st.session_state:
        st.session_state.owner_pay_table = None
    
    # Chọn chế độ
    if st.session_state.mode is None:
        st.markdown("## 🎯 CHỌN CHẾ ĐỘ")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👤 KHACH HANG", key="mode_customer", use_container_width=True):
                st.session_state.mode = "customer"
                st.rerun()
        with c2:
            if st.button("👑 CHU QUAN", key="mode_owner", use_container_width=True):
                st.session_state.mode = "owner"
                st.rerun()
    else:
        if st.button("🔄 DOI CHE DO", key="change_mode", use_container_width=True):
            st.session_state.mode = None
            st.session_state.owner_authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.mode == "customer":
            st.markdown("### 👤 CHẾ ĐỘ: KHÁCH HÀNG")
            if not st.session_state.get("show_customer_detail", False):
                display_customer_interface(dm)
                display_customer_booking_form(dm)
            else:
                display_customer_table_detail(dm)
        else:
            if not st.session_state.owner_authenticated:
                st.markdown("### 🔐 NHẬP MẬT KHẨU")
                pwd = st.text_input("Mat khau:", type="password")
                if st.button("🔓 XAC NHAN", key="check_password"):
                    if pwd == BidaConfig.OWNER_PASSWORD:
                        st.session_state.owner_authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Sai mat khau!")
            else:
                st.markdown("### 👑 CHẾ ĐỘ: CHỦ QUÁN")
                tabs = st.tabs(["🎯 QUAN LY BAN", "📊 DOANH THU", "📦 QUAN LY KHO", "📝 QUAN LY MENU"])
                with tabs[0]:
                    display_owner_interface(dm)
                    display_owner_payment_form(dm)
                with tabs[1]:
                    display_detailed_statistics(dm)
                with tabs[2]:
                    display_stock_management(dm)
                with tabs[3]:
                    display_menu_management(dm)
        
        if dm.get_active_sessions() and st.session_state.mode == "owner":
            time.sleep(2)
            st.rerun()

if __name__ == "__main__":
    main()
