# bida_system_complete.py
import streamlit as st
import pandas as pd
import datetime
import json
import os
import time
import winsound
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
                "Sprite": {"price": 15000, "stock": 80, "unit": "chai"},
                "Fanta": {"price": 15000, "stock": 60, "unit": "chai"},
                "Sting": {"price": 15000, "stock": 120, "unit": "chai"},
                "Red Bull": {"price": 25000, "stock": 50, "unit": "lon"},
                "Aquafina": {"price": 10000, "stock": 200, "unit": "chai"},
            },
            "🍺 BIA": {
                "Heineken": {"price": 30000, "stock": 150, "unit": "lon"},
                "Tiger": {"price": 30000, "stock": 120, "unit": "lon"},
                "Saigon Special": {"price": 25000, "stock": 100, "unit": "lon"},
                "Saigon Lager": {"price": 22000, "stock": 80, "unit": "lon"},
                "333": {"price": 20000, "stock": 90, "unit": "lon"},
                "Larue": {"price": 25000, "stock": 60, "unit": "lon"},
            },
            "☕ CÀ PHÊ & TRÀ": {
                "Cà phê đen": {"price": 15000, "stock": 50, "unit": "ly"},
                "Cà phê sữa": {"price": 18000, "stock": 50, "unit": "ly"},
                "Trà đá": {"price": 5000, "stock": 100, "unit": "ly"},
                "Trà chanh": {"price": 15000, "stock": 40, "unit": "ly"},
                "Trà đào": {"price": 25000, "stock": 30, "unit": "ly"},
            },
            "🍜 ĐỒ ĂN NHANH": {
                "Mì tôm": {"price": 20000, "stock": 30, "unit": "tô"},
                "Xúc xích chiên": {"price": 15000, "stock": 50, "unit": "đĩa"},
                "Khoai tây chiên": {"price": 25000, "stock": 40, "unit": "đĩa"},
                "Bắp rang": {"price": 20000, "stock": 35, "unit": "phần"},
                "Sandwich": {"price": 35000, "stock": 20, "unit": "cái"},
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
    
   # Xóa hàm cũ và thay bằng:
def play_sound(self, sound_type):
    """Tạm thời tắt âm thanh để tương thích với Linux"""
    pass  # Không làm gì cả
    
    def add_alert(self, table_id, table_name):
        alert = {
            "time": datetime.datetime.now().isoformat(),
            "table_id": table_id,
            "table_name": table_name,
            "status": "pending"
        }
        self.alerts.append(alert)
        self.save_alerts()
        self.play_sound("bell")
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
data_manager = DataManager()

def setup_page():
    st.set_page_config(
        page_title="MR.BOM Billiards Club",
        page_icon="🎱",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%); }
    
    /* Logo Style */
    .mr-bom-logo {
        text-align: center;
        padding: 15px;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        border: 2px solid #ffd700;
        box-shadow: 0 0 30px rgba(255,215,0,0.3);
    }
    .mr-bom-text {
        font-family: 'Orbitron', monospace;
        font-size: 48px;
        font-weight: bold;
        background: linear-gradient(45deg, #ffd700, #ff8c00, #ff4500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 4px;
    }
    
    /* EZ Scoreboard Style - CHUẨN XÁC */
    .ez-scoreboard {
        background: #0a0a0a;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border: 3px solid #ffd700;
        box-shadow: 0 0 20px rgba(255,215,0,0.4);
    }
    .ez-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
    }
    .ez-col {
        flex: 1;
        text-align: center;
    }
    .ez-col-center {
        flex: 0.8;
        text-align: center;
        border-left: 2px solid #ffd700;
        border-right: 2px solid #ffd700;
        padding: 0 20px;
    }
    .ez-player-name {
        font-family: 'Orbitron', monospace;
        font-size: 24px;
        font-weight: bold;
        color: #ffd700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
    }
    .ez-score {
        font-size: 90px;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        color: #ffffff;
        text-shadow: 0 0 15px #ffd700;
        line-height: 1;
        margin: 10px 0;
    }
    .ez-innings {
        font-family: 'Orbitron', monospace;
        font-size: 14px;
        color: #888888;
        margin-top: 10px;
    }
    .ez-stats {
        font-family: 'Orbitron', monospace;
        font-size: 12px;
        color: #ff8c00;
        margin-top: 5px;
    }
    .ez-timer {
        font-family: 'Courier New', monospace;
        font-size: 56px;
        font-weight: bold;
        color: #00ff88;
        text-shadow: 0 0 10px #00ff88;
        letter-spacing: 4px;
    }
    .ez-price {
        font-family: 'Orbitron', monospace;
        font-size: 16px;
        font-weight: bold;
        color: #ffd700;
        margin-top: 15px;
    }
    
    /* Card Style */
    .available-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        cursor: pointer;
        transition: transform 0.3s;
    }
    .available-card:hover { transform: scale(1.05); }
    .occupied-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px;
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .alert-card {
        background: #ff4444;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .stButton button { width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def display_logo():
    st.markdown(f"""
    <div class="mr-bom-logo">
        <div class="mr-bom-text">
            🎱 {BidaConfig.SHOP_FULL_NAME} 🎱
        </div>
        <div style="font-family: monospace; font-size: 12px; color: #ffd700; margin-top: 5px;">
            {BidaConfig.SHOP_ADDRESS} | 📞 {BidaConfig.PHONE}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_ez_scoreboard(session, table_id):
    """Hiển thị bảng tỷ số - Có nút hoán đổi màu VÀNG & TRẮNG"""
    minutes = int(session['elapsed_minutes'])
    seconds = int((session['elapsed_minutes'] - minutes) * 60)
    
    p1_hr = session['score']['player1']
    p2_hr = session['score']['player2']
    p1_avg = session['score']['player1'] / max(session['innings']['player1'], 1)
    p2_avg = session['score']['player2'] / max(session['innings']['player2'], 1)
    
    # Kiểm tra trạng thái đã swap chưa
    swap_key = f"swap_{table_id}"
    if swap_key not in st.session_state:
        st.session_state[swap_key] = False
    
    # Lấy tên và màu sắc dựa trên trạng thái swap
    if st.session_state[swap_key]:
        # Đã swap: Player 1 = Trắng, Player 2 = Vàng
        p1_color = "#ffffff"
        p1_bg = "#1a1a1a"
        p1_border = "#ffffff"
        p1_shadow = "#ffffff"
        p2_color = "#ffd700"
        p2_bg = "#1a1a00"
        p2_border = "#ffd700"
        p2_shadow = "#ffd700"
        p1_icon = "⚪"
        p2_icon = "🟡"
        p1_name_color = "#ffffff"
        p2_name_color = "#ffd700"
    else:
        # Chưa swap: Player 1 = Vàng, Player 2 = Trắng
        p1_color = "#ffd700"
        p1_bg = "#1a1a00"
        p1_border = "#ffd700"
        p1_shadow = "#ffd700"
        p2_color = "#ffffff"
        p2_bg = "#1a1a1a"
        p2_border = "#ffffff"
        p2_shadow = "#ffffff"
        p1_icon = "🟡"
        p2_icon = "⚪"
        p1_name_color = "#ffd700"
        p2_name_color = "#ffffff"
    
    # Dùng Streamlit columns
    col0, col1, col2, col3, col4 = st.columns([0.5, 2, 1, 2, 0.5])
    
    with col0:
        # Nút chuyển đổi bên trái Player 1
        if st.button("◀️", key=f"swap_left_{table_id}", use_container_width=True):
            st.session_state[swap_key] = not st.session_state[swap_key]
            st.rerun()
    
    with col1:
        # Player 1
        st.markdown(f"""
        <div style='background: {p1_bg}; border-radius: 15px; padding: 15px; text-align: center; border: 2px solid {p1_border}; box-shadow: 0 0 15px {p1_shadow};'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 8px;'>
                <div style='width: 25px; height: 25px; background: radial-gradient(circle at 30% 30%, {p1_color}, #666); border-radius: 50%;'></div>
                <h3 style='color: {p1_color}; margin: 0;'>PLAYER 1 {p1_icon}</h3>
            </div>
            <h2 style='color: {p1_name_color}; font-size: 14px; margin: 8px 0;'>{session['player1_name']}</h2>
            <h1 style='font-size: 80px; color: {p1_color}; text-shadow: 0 0 10px {p1_color}; margin: 10px 0;'>{session['score']['player1']}</h1>
            <p style='color: {p1_color}; margin: 5px 0;'>Inn. {session['innings']['player1']}</p>
            <p style='color: {p1_color if p1_color == '#ffd700' else '#aaaaaa'}; font-size: 12px;'>HR {p1_hr} | Avg {p1_avg:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Nút điều khiển Player 1
        st.markdown(f"<p style='color: {p1_color}; text-align: center; margin: 10px 0 5px 0;'>🎮 ĐIỀU KHIỂN</p>", unsafe_allow_html=True)
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("➕1", key=f"p1_1_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player1", 1, True)
                st.rerun()
        with col_b:
            if st.button("➕5", key=f"p1_5_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player1", 5, True)
                st.rerun()
        with col_c:
            if st.button("➖1", key=f"p1_m1_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player1", 1, False)
                st.rerun()
        with col_d:
            if st.button("➖5", key=f"p1_m5_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player1", 5, False)
                st.rerun()
    
    with col2:
        # Timer
        st.markdown(f"""
        <div style='background: #000000; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #333; height: 100%; display: flex; flex-direction: column; justify-content: center;'>
            <h1 style='font-size: 42px; color: #00ff88; letter-spacing: 4px; margin: 0; font-family: monospace;'>{minutes:02d}:{seconds:02d}</h1>
            <p style='color: #aaaaaa; font-size: 12px; margin: 10px 0 0 0;'>{BidaConfig.TABLES[table_id]['price_per_hour']:,}đ/giờ</p>
            <div style='margin-top: 10px;'>
                <span style='color: #ffd700;'>●</span> <span style='color: #ffffff; font-size: 10px;'>●</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Player 2
        st.markdown(f"""
        <div style='background: {p2_bg}; border-radius: 15px; padding: 15px; text-align: center; border: 2px solid {p2_border}; box-shadow: 0 0 15px {p2_shadow};'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 8px;'>
                <div style='width: 25px; height: 25px; background: radial-gradient(circle at 30% 30%, {p2_color}, #666); border-radius: 50%;'></div>
                <h3 style='color: {p2_color}; margin: 0;'>PLAYER 2 {p2_icon}</h3>
            </div>
            <h2 style='color: {p2_name_color}; font-size: 14px; margin: 8px 0;'>{session['player2_name']}</h2>
            <h1 style='font-size: 80px; color: {p2_color}; text-shadow: 0 0 10px {p2_color}; margin: 10px 0;'>{session['score']['player2']}</h1>
            <p style='color: {p2_color}; margin: 5px 0;'>Inn. {session['innings']['player2']}</p>
            <p style='color: {p2_color if p2_color == '#ffd700' else '#aaaaaa'}; font-size: 12px;'>HR {p2_hr} | Avg {p2_avg:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Nút điều khiển Player 2
        st.markdown(f"<p style='color: {p2_color}; text-align: center; margin: 10px 0 5px 0;'>🎮 ĐIỀU KHIỂN</p>", unsafe_allow_html=True)
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("➕1", key=f"p2_1_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player2", 1, True)
                st.rerun()
        with col_b:
            if st.button("➕5", key=f"p2_5_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player2", 5, True)
                st.rerun()
        with col_c:
            if st.button("➖1", key=f"p2_m1_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player2", 1, False)
                st.rerun()
        with col_d:
            if st.button("➖5", key=f"p2_m5_{table_id}", use_container_width=True):
                data_manager.update_score(table_id, "player2", 5, False)
                st.rerun()
    
    with col4:
        # Nút chuyển đổi bên phải Player 2
        if st.button("▶️", key=f"swap_right_{table_id}", use_container_width=True):
            st.session_state[swap_key] = not st.session_state[swap_key]
            st.rerun()
                    
def display_menu_management():
    st.markdown("### 📝 QUẢN LÝ MENU")
    
    tab1, tab2, tab3 = st.tabs(["➕ THÊM MÓN", "✏️ SỬA MÓN", "❌ XÓA MÓN"])
    
    with tab1:
        st.markdown("#### Thêm món mới")
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Chọn danh mục", list(data_manager.menu_manager.menu.keys()), key="add_cat")
        with col2:
            new_item = st.text_input("Tên món mới", key="new_item")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_price = st.number_input("Giá (VNĐ)", min_value=1000, step=1000, value=15000, key="new_price")
        with col2:
            new_stock = st.number_input("Tồn kho", min_value=0, step=1, value=50, key="new_stock")
        with col3:
            new_unit = st.selectbox("Đơn vị", ["chai", "lon", "ly", "tô", "đĩa", "phần"], key="new_unit")
        with col4:
            if st.button("➕ THÊM MÓN", key="add_item"):
                if new_item:
                    if data_manager.menu_manager.add_item(category, new_item, new_price, new_stock, new_unit):
                        st.success(f"✅ Đã thêm món: {new_item}")
                        st.rerun()
                    else:
                        st.error("❌ Món đã tồn tại!")
                else:
                    st.error("❌ Vui lòng nhập tên món!")
    
    with tab2:
        st.markdown("#### Sửa giá hoặc tồn kho")
        col1, col2 = st.columns(2)
        with col1:
            edit_cat = st.selectbox("Chọn danh mục", list(data_manager.menu_manager.menu.keys()), key="edit_cat")
        with col2:
            if edit_cat:
                items = list(data_manager.menu_manager.menu[edit_cat].keys())
                edit_item = st.selectbox("Chọn món", items, key="edit_item")
        
        if edit_cat and edit_item:
            current = data_manager.menu_manager.menu[edit_cat][edit_item]
            col1, col2 = st.columns(2)
            with col1:
                new_price = st.number_input("Giá mới", min_value=1000, step=1000, value=current["price"], key="edit_price")
                if st.button("💾 CẬP NHẬT GIÁ"):
                    data_manager.menu_manager.update_item_price(edit_cat, edit_item, new_price)
                    st.success("✅ Đã cập nhật giá!")
                    st.rerun()
            with col2:
                new_stock = st.number_input("Tồn kho mới", min_value=0, step=1, value=current["stock"], key="edit_stock")
                if st.button("📦 CẬP NHẬT TỒN KHO"):
                    data_manager.menu_manager.update_item_stock(edit_cat, edit_item, new_stock)
                    st.success("✅ Đã cập nhật tồn kho!")
                    st.rerun()
    
    with tab3:
        st.markdown("#### Xóa món")
        col1, col2 = st.columns(2)
        with col1:
            del_cat = st.selectbox("Chọn danh mục", list(data_manager.menu_manager.menu.keys()), key="del_cat")
        with col2:
            if del_cat:
                items = ["-- Chọn --"] + list(data_manager.menu_manager.menu[del_cat].keys())
                del_item = st.selectbox("Chọn món cần xóa", items, key="del_item")
        
        if del_cat and del_item and del_item != "-- Chọn --":
            if st.button("🗑️ XÓA MÓN", type="primary"):
                if data_manager.menu_manager.delete_item(del_cat, del_item):
                    st.success(f"✅ Đã xóa món: {del_item}")
                    st.rerun()

def display_stock_management():
    st.markdown("### 📦 QUẢN LÝ TỒN KHO")
    
    stock_data = []
    for category, items in data_manager.menu_manager.menu.items():
        for item, info in items.items():
            status = "🟢 Tốt" if info['stock'] > 20 else "🟡 Sắp hết" if info['stock'] > 5 else "🔴 Hết"
            stock_data.append({
                "Danh mục": category,
                "Sản phẩm": item,
                "Giá": f"{info['price']:,}đ",
                "Tồn kho": info['stock'],
                "Đơn vị": info['unit'],
                "Trạng thái": status
            })
    
    st.dataframe(pd.DataFrame(stock_data), use_container_width=True, hide_index=True)
    
    st.markdown("### 📥 NHẬP HÀNG")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        all_items = [item for cat in data_manager.menu_manager.menu.values() for item in cat.keys()]
        restock_item = st.selectbox("Chọn sản phẩm", all_items)
    with col2:
        restock_qty = st.number_input("Số lượng", min_value=1, max_value=1000, value=50)
    with col3:
        if st.button("📦 NHẬP HÀNG"):
            if data_manager.menu_manager.add_stock(restock_item, restock_qty):
                st.success(f"✅ Đã nhập {restock_qty} {restock_item}")
                st.rerun()

def display_customer_interface():
    st.markdown("### 🎯 CHỌN BÀN BIDA")
    
    active_sessions = {s["table_id"]: s for s in data_manager.get_active_sessions()}
    
    cols = st.columns(4)
    for idx, table_id in enumerate([1, 2, 3, 4, 5, 6, 7, 8], 0):
        col = cols[idx % 4]
        if idx % 4 == 0 and idx > 0:
            cols = st.columns(4)
            col = cols[0]
        
        with col:
            table = BidaConfig.TABLES[table_id]
            is_active = table_id in active_sessions
            
            if is_active:
                session = active_sessions[table_id]
                minutes = int(session['elapsed_minutes'])
                st.markdown(f"""
                <div class="occupied-card">
                    <h3>🎱 {table['name']}</h3>
                    <div style="font-size: 24px; color: #00ff88;">{minutes:02d}:00</div>
                    <div>🏆 {session['score']['player1']} - {session['score']['player2']}</div>
                    <div>🔴 ĐANG CHƠI</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"📱 VÀO BÀN", key=f"cust_view_{table_id}"):
                    st.session_state.customer_selected_table = table_id
                    st.session_state.show_customer_detail = True
            else:
                st.markdown(f"""
                <div class="available-card">
                    <h3>🎱 {table['name']}</h3>
                    <div>💰 {table['price_per_hour']:,}đ/h</div>
                    <div>✅ TRỐNG</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🎯 ĐẶT BÀN", key=f"cust_book_{table_id}"):
                    st.session_state.customer_book_table = table_id
                    st.session_state.show_customer_booking = True

def display_customer_booking_form():
    if st.session_state.get("show_customer_booking", False):
        with st.expander("🎯 ĐẶT BÀN", expanded=True):
            table_id = st.session_state.customer_book_table
            table = BidaConfig.TABLES[table_id]
            
            st.info(f"🏠 **{table['name']}** - {table['price_per_hour']:,}đ/giờ")
            
            col1, col2 = st.columns(2)
            with col1:
                player1 = st.text_input("🎯 Tên Player 1", key="p1")
                player2 = st.text_input("🎯 Tên Player 2", key="p2")
            with col2:
                st.markdown(f"""
                <div style="background: #2e7d32; padding: 15px; border-radius: 10px;">
                    <b>💰 GIÁ BÀN</b><br>
                    {table['price_per_hour']:,}đ/giờ = {table['price_per_hour']/60:.0f}đ/phút<br>
                    🔔 Bấm chuông khi cần tính tiền
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("✅ XÁC NHẬN", type="primary"):
                if player1 and player2:
                    data_manager.start_session(table_id, player1, "customer", player1, player2)
                    st.success(f"✅ ĐẶT BÀN THÀNH CÔNG!\n{player1} vs {player2}")
                    st.balloons()
                    st.session_state.show_customer_booking = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Nhập tên 2 người chơi!")
            
            if st.button("❌ HỦY"):
                st.session_state.show_customer_booking = False
                st.rerun()

def display_order_section(table_id, session):
    st.markdown("### 🍽️ GỌI MÓN")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        category = st.selectbox("Danh mục", list(data_manager.menu_manager.menu.keys()), key=f"cat_{table_id}")
    with col2:
        if category:
            items = list(data_manager.menu_manager.menu[category].keys())
            item = st.selectbox("Món", items, key=f"item_{table_id}")
    with col3:
        quantity = st.number_input("SL", min_value=1, max_value=20, value=1, key=f"qty_{table_id}")
    
    if category and item:
        info = data_manager.menu_manager.menu[category][item]
        st.caption(f"📦 Tồn: {info['stock']} {info['unit']} | 💰 {info['price']:,}đ")
        
        if info['stock'] < quantity:
            st.error(f"❌ Không đủ hàng! Chỉ còn {info['stock']} {info['unit']}")
        else:
            if st.button(f"➕ THÊM MÓN", key=f"add_{table_id}"):
                success, msg = data_manager.add_order(table_id, category, item, quantity, info['price'])
                if success:
                    st.success(msg)
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(msg)
    
    orders = session.get("orders", [])
    if orders:
        st.markdown("### 📋 MÓN ĐÃ GỌI")
        for idx, order in enumerate(orders):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1: st.write(f"🍽️ {order['item']}")
            with col2: st.write(f"x{order['quantity']}")
            with col3: st.write(f"{order['total']:,}đ")
            with col4:
                if st.button("🗑️", key=f"del_{table_id}_{idx}"):
                    data_manager.remove_order(table_id, idx)
                    st.rerun()
        
        food_total = data_manager.get_food_total(table_id)
        st.info(f"🍽️ Tổng tiền món: {food_total:,}đ")

def display_customer_table_detail():
    if st.session_state.get("show_customer_detail", False) and st.session_state.get("customer_selected_table"):
        table_id = st.session_state.customer_selected_table
        active_sessions = {s["table_id"]: s for s in data_manager.get_active_sessions()}
        
        if table_id in active_sessions:
            session = active_sessions[table_id]
            
            st.markdown(f"## 🎱 {BidaConfig.TABLES[table_id]['name']}")
            
            tab1, tab2, tab3 = st.tabs(["🎯 TỶ SỐ", "🍽️ GỌI MÓN", "💰 HÓA ĐƠN"])
            
            with tab1:
                display_ez_scoreboard(session, table_id)
            
            with tab2:
                display_order_section(table_id, session)
            
            with tab3:
                minutes = int(session['elapsed_minutes'])
                price_per_minute = BidaConfig.TABLES[table_id]['price_per_hour'] / 60
                table_temp = int(price_per_minute * session['elapsed_minutes'])
                food_total = data_manager.get_food_total(table_id)
                
                st.markdown(f"""
                | Khoản mục | Số tiền |
                |-----------|---------|
                | ⏱️ Tiền bàn ({minutes} phút) | {table_temp:,}đ |
                | 🍽️ Tiền món | {food_total:,}đ |
                | **💰 TỔNG CỘNG** | **{table_temp + food_total:,}đ** |
                """)
                
                if st.button("🔔 BÁO TÍNH TIỀN", type="primary", use_container_width=True):
                    data_manager.add_alert(table_id, BidaConfig.TABLES[table_id]['name'])
                    st.success("✅ Đã gửi yêu cầu! Nhân viên sẽ đến ngay!")
                    st.balloons()
                    time.sleep(1)
            
            if st.button("🔙 QUAY LẠI"):
                st.session_state.show_customer_detail = False
                st.session_state.customer_selected_table = None
                st.rerun()

def display_owner_interface():
    st.markdown("### 🎯 QUẢN LÝ BÀN BIDA")
    
    active_sessions = {s["table_id"]: s for s in data_manager.get_active_sessions()}
    pending_alerts = data_manager.get_pending_alerts()
    
    if pending_alerts:
        st.markdown("### 🔔 YÊU CẦU TÍNH TIỀN")
        for idx, alert in enumerate(pending_alerts):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.warning(f"🛎️ **{alert['table_name']}** yêu cầu lúc {alert['time'][11:16]}")
            with col2:
                if st.button(f"💰 TÍNH TIỀN", key=f"pay_{idx}"):
                    st.session_state.owner_pay_table = alert['table_id']
                    st.session_state.show_owner_payment = True
                    data_manager.remove_alert(idx)
                    st.rerun()
            with col3:
                if st.button(f"✅ BỎ QUA", key=f"ignore_{idx}"):
                    data_manager.remove_alert(idx)
                    st.rerun()
        st.markdown("---")
    
    cols = st.columns(4)
    for idx, table_id in enumerate([1, 2, 3, 4, 5, 6, 7, 8], 0):
        col = cols[idx % 4]
        if idx % 4 == 0 and idx > 0:
            cols = st.columns(4)
            col = cols[0]
        
        with col:
            table = BidaConfig.TABLES[table_id]
            is_active = table_id in active_sessions
            
            if is_active:
                session = active_sessions[table_id]
                minutes = int(session['elapsed_minutes'])
                st.markdown(f"""
                <div class="occupied-card">
                    <h3>🎱 {table['name']}</h3>
                    <div>⏱️ {minutes:02d} phút</div>
                    <div>🏆 {session['score']['player1']} - {session['score']['player2']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"💰 TIỀN", key=f"owner_pay_{table_id}"):
                    st.session_state.owner_pay_table = table_id
                    st.session_state.show_owner_payment = True
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="available-card">
                    <h3>🎱 {table['name']}</h3>
                    <div>💰 {table['price_per_hour']:,}đ/h</div>
                    <div>✅ TRỐNG</div>
                </div>
                """, unsafe_allow_html=True)

def display_owner_payment_form():
    if st.session_state.get("show_owner_payment", False) and st.session_state.get("owner_pay_table"):
        table_id = st.session_state.owner_pay_table
        active_sessions = {s["table_id"]: s for s in data_manager.get_active_sessions()}
        
        if table_id in active_sessions:
            session = active_sessions[table_id]
            with st.expander(f"💰 TÍNH TIỀN BÀN SỐ {table_id}", expanded=True):
                minutes = int(session['elapsed_minutes'])
                seconds = int((session['elapsed_minutes'] - minutes) * 60)
                price_per_hour = BidaConfig.TABLES[table_id]['price_per_hour']
                table_fee = int((price_per_hour / 60) * session['elapsed_minutes'])
                food_total = data_manager.get_food_total(table_id)
                
                st.markdown(f"""
                **👤 Khách:** {session['customer_name']}  
                **⏱️ Thời gian:** {minutes:02d}:{seconds:02d} ({session['elapsed_minutes']:.1f} phút)  
                **💰 Tiền bàn:** {table_fee:,}đ  
                **🍽️ Tiền món:** {food_total:,}đ  
                **💵 TỔNG CỘNG:** {table_fee + food_total:,}đ
                """)
                
                if st.button(f"✅ XÁC NHẬN THANH TOÁN", type="primary"):
                    result = data_manager.end_session(table_id)
                    if result:
                        st.success(f"✅ THANH TOÁN THÀNH CÔNG! Tổng: {result['total_amount']:,}đ")
                        st.balloons()
                        st.session_state.show_owner_payment = False
                        st.session_state.owner_pay_table = None
                        time.sleep(2)
                        st.rerun()

def display_detailed_statistics():
    st.markdown("### 📊 THỐNG KÊ DOANH THU HÔM NAY")
    
    total_table, total_food, table_revenue, food_revenue = data_manager.get_today_revenue()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 TỔNG DOANH THU", f"{total_table + total_food:,.0f}đ")
    with col2: st.metric("🎱 DOANH THU BÀN", f"{total_table:,.0f}đ")
    with col3: st.metric("🍽️ DOANH THU MÓN", f"{total_food:,.0f}đ")
    with col4: st.metric("👥 SỐ BÀN", f"{len(table_revenue)}")
    
    st.markdown("---")
    
    if table_revenue:
        st.markdown("#### 🎯 DOANH THU THEO BÀN")
        df = pd.DataFrame([{"Bàn": t, "Tiền bàn": r["table"], "Tiền món": r["food"], "Tổng": r["table"] + r["food"]} 
                          for t, r in table_revenue.items()]).sort_values("Tổng", ascending=False)
        
        fig = go.Figure(data=[
            go.Bar(name="Tiền bàn", x=df["Bàn"], y=df["Tiền bàn"], marker_color="#ffd700"),
            go.Bar(name="Tiền món", x=df["Bàn"], y=df["Tiền món"], marker_color="#ff8c00")
        ])
        fig.update_layout(barmode='stack', title="Doanh thu theo bàn", height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ================== MAIN ==================
def main():
    setup_page()
    display_logo()
    
    # Khởi tạo session state
    for key in ["mode", "owner_authenticated", "show_customer_detail", "show_customer_booking",
                "show_owner_payment", "customer_selected_table", "customer_book_table", "owner_pay_table"]:
        if key not in st.session_state:
            if "selected" in key or "pay" in key or "book" in key:
                st.session_state[key] = None
            elif key == "owner_authenticated":
                st.session_state[key] = False
            else:
                st.session_state[key] = False
    
    # Chọn chế độ
    if st.session_state.mode is None:
        st.markdown("## 🎯 CHỌN CHẾ ĐỘ")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 KHÁCH HÀNG", use_container_width=True):
                st.session_state.mode = "customer"
                st.rerun()
        with col2:
            if st.button("👑 CHỦ QUÁN", use_container_width=True):
                st.session_state.mode = "owner"
                st.rerun()
    else:
        if st.button("🔄 ĐỔI CHẾ ĐỘ", use_container_width=True):
            st.session_state.mode = None
            st.session_state.owner_authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.mode == "customer":
            st.markdown("### 👤 CHẾ ĐỘ: KHÁCH HÀNG")
            if not st.session_state.get("show_customer_detail", False):
                display_customer_interface()
                display_customer_booking_form()
            else:
                display_customer_table_detail()
        
        else:
            if not st.session_state.owner_authenticated:
                st.markdown("### 🔐 NHẬP MẬT KHẨU")
                pwd = st.text_input("Mật khẩu:", type="password")
                if st.button("🔓 XÁC NHẬN"):
                    if pwd == BidaConfig.OWNER_PASSWORD:
                        st.session_state.owner_authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Sai mật khẩu!")
            else:
                st.markdown("### 👑 CHẾ ĐỘ: CHỦ QUÁN")
                tab1, tab2, tab3, tab4 = st.tabs(["🎯 QUẢN LÝ BÀN", "📊 DOANH THU", "📦 QUẢN LÝ KHO", "📝 QUẢN LÝ MENU"])
                
                with tab1:
                    display_owner_interface()
                    display_owner_payment_form()
                with tab2:
                    display_detailed_statistics()
                with tab3:
                    display_stock_management()
                with tab4:
                    display_menu_management()
        
        if data_manager.get_active_sessions() and st.session_state.mode == "owner":
            time.sleep(2)
            st.rerun()

if __name__ == "__main__":
    main()
