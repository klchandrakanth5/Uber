# ================================
# 🚀 IMPORTS
# ================================
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from math import radians, sin, cos, sqrt, atan2
import time
import random
import sqlite3
import streamlit.components.v1 as components

# ✅ ML IMPORTS
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# ================================
# 🚀 PAGE CONFIG
# ================================
st.set_page_config(page_title="Uber AI", layout="wide")

# ================================
# 🚀 DATABASE
# ================================
def init_db():
    conn = sqlite3.connect("uber.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pickup TEXT,
        drop_loc TEXT,
        vehicle TEXT,
        fare REAL
    )''')
    conn.commit()
    conn.close()

init_db()

# ================================
# ✅ ML MODEL
# ================================
@st.cache_resource
def train_model():
    np.random.seed(42)

    n = 1000
    data = pd.DataFrame({
        "distance": np.random.uniform(1, 25, n),
        "hour": np.random.randint(0, 24, n),
        "traffic": np.random.randint(1, 5, n),
    })

    data["fare"] = (
        data["distance"] * 20 +
        data["traffic"] * 15 +
        data["hour"] * 2 +
        np.random.normal(0, 10, n)
    )

    X = data[["distance", "hour", "traffic"]]
    y = data["fare"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    score = r2_score(y_test, pred)

    return model, score

model, model_score = train_model()

# ================================
# 🚀 BANGALORE LOCATIONS (FULL)
# ================================
locations = {
    "Majestic": (12.9780, 77.5714),
    "MG Road": (12.9757, 77.6080),
    "Indiranagar": (12.9783, 77.6405),
    "Whitefield": (12.9698, 77.7501),
    "Electronic City": (12.8452, 77.6770),
    "BTM": (12.9166, 77.6101),
    "HSR Layout": (12.9116, 77.6474),
    "Marathahalli": (12.9591, 77.6974),
    "Yelahanka": (13.1007, 77.5963),
    "Hebbal": (13.0350, 77.5970),
    "Rajajinagar": (12.9915, 77.5544),
    "Banashankari": (12.9250, 77.5468),
    "Jayanagar": (12.9250, 77.5938),
    "KR Puram": (13.0085, 77.6950),
    "Bellandur": (12.9250, 77.6762),
    "Sarjapur": (12.9077, 77.6835)
}

# ================================
# 🚀 FUNCTIONS
# ================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1 - a)), 2)

def generate_phone():
    return f"+91{random.randint(7000000000,9999999999)}"

def generate_plate():
    return f"KA-{random.randint(1,99):02d}-AB-{random.randint(1000,9999)}"

# ================================
# 🚀 UI
# ================================
st.title("🚖 Uber AI — Live Rider Tracking")

# --------------------------------
# STEP 1 — Choose Vehicle Type
# --------------------------------
st.markdown("### 🚦 Step 1: Choose Your Ride")

vcol1, vcol2 = st.columns(2)
with vcol1:
    bike_btn = st.button("🏍️ Bike  (Cheaper & Faster)", use_container_width=True)
with vcol2:
    car_btn = st.button("🚗 Car  (Comfortable & Spacious)", use_container_width=True)

if bike_btn:
    st.session_state["vehicle_choice"] = "Bike"
if car_btn:
    st.session_state["vehicle_choice"] = "Car"

vehicle_choice = st.session_state.get("vehicle_choice", None)

if vehicle_choice:
    emoji = "🏍️" if vehicle_choice == "Bike" else "🚗"
    color = "#00BFFF" if vehicle_choice == "Bike" else "#FFD700"
    st.markdown(
        f"<div style='padding:10px 18px; background:#111; border-left: 4px solid {color};"
        f"border-radius:6px; font-size:16px; color:{color}; margin-bottom:10px;'>"
        f"{emoji} <b>{vehicle_choice}</b> selected</div>",
        unsafe_allow_html=True
    )
else:
    st.info("👆 Please select a vehicle type above to continue.")

# --------------------------------
# STEP 2 — Pickup & Drop
# --------------------------------
st.markdown("### 📍 Step 2: Select Pickup & Drop")

col1, col2 = st.columns(2)
with col1:
    pickup = st.selectbox("Pickup", list(locations.keys()))
with col2:
    drop = st.selectbox("Drop", list(locations.keys()))

# ================================
# 🚀 DISTANCE & FARE
# ================================
lat1, lon1 = locations[pickup]
lat2, lon2 = locations[drop]

distance = haversine(lat1, lon1, lat2, lon2)

if vehicle_choice == "Bike":
    fare = int(distance * 12 + random.randint(20, 60))
elif vehicle_choice == "Car":
    fare = int(distance * 25 + random.randint(80, 200))
else:
    fare = int(distance * 20 + random.randint(50, 150))

st.write(f"📏 Distance: {distance} km")
st.write(f"💰 Fare: ₹{fare}" + (f"  *(Bike rate)*" if vehicle_choice == "Bike" else f"  *(Car rate)*" if vehicle_choice == "Car" else ""))

# ================================
# 🚀 BOOK RIDE
# ================================
booked = False
driver_name = ""
driver_phone = ""
driver_plate = ""

if st.button("🚖 Book Ride"):
    if not vehicle_choice:
        st.warning("⚠️ Please choose a vehicle type (Bike or Car) first!")
    else:
        driver_name  = random.choice(["Rahul", "Amit", "Suresh", "Arjun"])
        driver_phone = generate_phone()
        driver_plate = generate_plate()
        emoji = "🏍️" if vehicle_choice == "Bike" else "🚗"

        st.success(f"✅ {emoji} {vehicle_choice} Ride Accepted by {driver_name}")
        st.info(f"📞 Phone: {driver_phone}")
        st.info(f"🚘 Plate: {driver_plate}")
        booked = True

        st.session_state["booked"] = True
        st.session_state["driver_name"]  = driver_name
        st.session_state["driver_phone"] = driver_phone
        st.session_state["driver_plate"] = driver_plate

        conn = sqlite3.connect("uber.db")
        c = conn.cursor()
        c.execute("INSERT INTO bookings (pickup, drop_loc, vehicle, fare) VALUES (?, ?, ?, ?)",
                  (pickup, drop, vehicle_choice, fare))
        conn.commit()
        conn.close()

booked        = st.session_state.get("booked", False)
driver_name   = st.session_state.get("driver_name", "Rahul")
driver_phone  = st.session_state.get("driver_phone", "+919876543210")
driver_plate  = st.session_state.get("driver_plate", "KA-01-AB-1234")

# ================================
# 🚀 HEATMAP POINTS (cached)
# ================================
@st.cache_data
def generate_heat_points():
    pts = []
    for _ in range(300):
        lat = 12.97 + random.uniform(-0.1, 0.1)
        lon = 77.59 + random.uniform(-0.1, 0.1)
        pts.append([lat, lon])
    return pts

heat_data = generate_heat_points()

# ================================
# 🚀 STATIC VEHICLE MARKERS (cached)
# ================================
@st.cache_data
def generate_vehicle_markers():
    bikes, cars = [], []
    for _ in range(12):
        bikes.append((12.97 + random.uniform(-0.09, 0.09), 77.59 + random.uniform(-0.09, 0.09)))
    for _ in range(10):
        cars.append((12.97 + random.uniform(-0.09, 0.09), 77.59 + random.uniform(-0.09, 0.09)))
    return bikes, cars

bike_positions, car_positions = generate_vehicle_markers()

def bike_icon(highlighted=False):
    border = "#00FF88" if highlighted else "#00BFFF"
    glow   = "#00FF8888" if highlighted else "#00BFFF88"
    return folium.DivIcon(
        html=f'<div style="font-size:22px;background:rgba(0,0,0,0.75);border-radius:50%;'
             f'width:36px;height:36px;display:flex;align-items:center;justify-content:center;'
             f'border:2px solid {border};box-shadow:0 0 10px {glow};">🏍️</div>',
        icon_size=(36, 36), icon_anchor=(18, 18)
    )

def car_icon(highlighted=False):
    border = "#FF8C00" if highlighted else "#FFD700"
    glow   = "#FF8C0088" if highlighted else "#FFD70088"
    return folium.DivIcon(
        html=f'<div style="font-size:22px;background:rgba(0,0,0,0.75);border-radius:50%;'
             f'width:36px;height:36px;display:flex;align-items:center;justify-content:center;'
             f'border:2px solid {border};box-shadow:0 0 10px {glow};">🚗</div>',
        icon_size=(36, 36), icon_anchor=(18, 18)
    )

# ================================
# 🚀 STATIC FOLIUM MAP
# ================================
st.markdown("### 🗺️ Live Map — Dark Heatmap")

m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="CartoDB dark_matter")

folium.Marker([lat1, lon1], popup=f"📍 Pickup: {pickup}", icon=folium.Icon(color="green", icon="home")).add_to(m)
folium.Marker([lat2, lon2], popup=f"🏁 Drop: {drop}",    icon=folium.Icon(color="red",   icon="flag")).add_to(m)

route_color = "#00BFFF" if vehicle_choice == "Bike" else "#FFD700" if vehicle_choice == "Car" else "cyan"
folium.PolyLine([[lat1, lon1], [lat2, lon2]], color=route_color, weight=5, opacity=0.85).add_to(m)

HeatMap(heat_data, radius=18, blur=25, min_opacity=0.3).add_to(m)

if vehicle_choice == "Bike" or vehicle_choice is None:
    for blat, blon in bike_positions:
        folium.Marker([blat, blon], popup="🏍️ Bike Available",
                      icon=bike_icon(highlighted=(vehicle_choice == "Bike"))).add_to(m)

if vehicle_choice == "Car" or vehicle_choice is None:
    for clat, clon in car_positions:
        folium.Marker([clat, clon], popup="🚗 Car Available",
                      icon=car_icon(highlighted=(vehicle_choice == "Car"))).add_to(m)

st_folium(m, width=1200, height=450, returned_objects=[])

# ================================
# 🚀 AI LIVE TRACKING MAP (HTML)
# ================================
st.markdown("---")
st.markdown("### 🤖 AI Live Rider Tracking — Real-Time Movement")

v_emoji  = "🏍️" if vehicle_choice == "Bike" else "🚗"
v_color  = "#00BFFF" if vehicle_choice == "Bike" else "#FFD700"
booked_js = "true" if booked else "false"

live_map_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0a0a0a; font-family:'Segoe UI',sans-serif; color:#fff; }}
  #map {{ width:100%; height:480px; }}

  /* AI PANEL */
  #ai-panel {{
    background:#0d0d0d;
    border:1px solid #1e1e1e;
    padding:14px 18px;
    display:flex;
    gap:16px;
    flex-wrap:wrap;
    align-items:center;
  }}
  .ai-card {{
    background:#111;
    border:1px solid #222;
    border-radius:10px;
    padding:10px 16px;
    min-width:160px;
    flex:1;
  }}
  .ai-card .label {{ font-size:10px; color:#666; text-transform:uppercase; letter-spacing:1px; }}
  .ai-card .value {{ font-size:18px; font-weight:700; margin-top:4px; }}
  .ai-card .sub   {{ font-size:11px; color:#555; margin-top:2px; }}

  /* ETA bar */
  #eta-bar-wrap {{ width:100%; background:#111; border-radius:8px; overflow:hidden; height:6px; margin-top:6px; }}
  #eta-bar {{ height:6px; background:{v_color}; transition:width 1s linear; border-radius:8px; }}

  /* ALERT */
  #alert-box {{
    display:none;
    position:absolute;
    top:12px; left:50%; transform:translateX(-50%);
    background:rgba(255,50,50,0.92);
    color:#fff;
    padding:10px 24px;
    border-radius:30px;
    font-size:14px;
    font-weight:600;
    z-index:9999;
    animation: pulse 0.6s infinite alternate;
    white-space:nowrap;
  }}
  @keyframes pulse {{ from{{opacity:1}} to{{opacity:0.6}} }}

  #status-dot {{
    width:10px; height:10px; border-radius:50%;
    background:#00ff88;
    display:inline-block;
    box-shadow:0 0 8px #00ff88;
    animation: blink 1s infinite;
  }}
  @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}

  /* AI LOG */
  #ai-log {{
    background:#0a0a12;
    border:1px solid #1a1a2e;
    border-radius:8px;
    padding:10px 14px;
    font-size:11px;
    font-family:monospace;
    color:#00ff88;
    height:90px;
    overflow-y:auto;
    flex:2;
    min-width:240px;
  }}
  #ai-log .log-line {{ margin-bottom:3px; }}
  #ai-log .ts {{ color:#444; margin-right:6px; }}
</style>
</head>
<body>

<div style="position:relative;">
  <div id="alert-box">🔔 Rider is VERY CLOSE — Prepare for pickup!</div>
  <div id="map"></div>
</div>

<div id="ai-panel">
  <div class="ai-card">
    <div class="label"><span id="status-dot"></span> AI Status</div>
    <div class="value" id="ai-status" style="color:{v_color};">Tracking</div>
    <div class="sub" id="ai-sub">Rider en route</div>
  </div>
  <div class="ai-card">
    <div class="label">ETA</div>
    <div class="value" id="eta-val" style="color:#fff;">--</div>
    <div id="eta-bar-wrap"><div id="eta-bar" style="width:100%"></div></div>
    <div class="sub">Minutes away</div>
  </div>
  <div class="ai-card">
    <div class="label">Distance to You</div>
    <div class="value" id="dist-val" style="color:{v_color};">--</div>
    <div class="sub">km remaining</div>
  </div>
  <div class="ai-card">
    <div class="label">Driver</div>
    <div class="value" style="font-size:15px;">{driver_name}</div>
    <div class="sub">{driver_plate}</div>
  </div>
  <div id="ai-log" id="ai-log">
    <div class="log-line"><span class="ts">[AI]</span> System initialised...</div>
  </div>
</div>

<script>
// ── MAP INIT ──────────────────────────────────────────────
const map = L.map('map', {{ zoomControl:true }}).setView([{lat1}, {lon1}], 14);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution:'CartoDB', subdomains:'abcd', maxZoom:19
}}).addTo(map);

// Heatmap layer via canvas
const heatPts = {heat_data};
// Simple circle heat using canvas overlay
const heat = L.layerGroup().addTo(map);
heatPts.forEach(p => {{
  L.circleMarker(p, {{
    radius: 8, color:'transparent',
    fillColor:'#ff4500', fillOpacity:0.08
  }}).addTo(heat);
}});

// ── MARKERS ───────────────────────────────────────────────
const pickupIcon = L.divIcon({{
  html:`<div style="font-size:26px;filter:drop-shadow(0 0 6px #00ff88);">📍</div>`,
  iconSize:[30,30], iconAnchor:[15,30], className:''
}});
const dropIcon = L.divIcon({{
  html:`<div style="font-size:26px;filter:drop-shadow(0 0 6px #ff4444);">🏁</div>`,
  iconSize:[30,30], iconAnchor:[15,30], className:''
}});
const riderIcon = L.divIcon({{
  html:`<div style="font-size:30px;filter:drop-shadow(0 0 10px {v_color});animation:spin 2s linear infinite;">
    {v_emoji}
  </div>
  <style>@keyframes spin{{0%{{transform:rotate(-10deg)}}50%{{transform:rotate(10deg)}}100%{{transform:rotate(-10deg)}}}}</style>`,
  iconSize:[36,36], iconAnchor:[18,18], className:''
}});
const youIcon = L.divIcon({{
  html:`<div style="
    width:20px;height:20px;border-radius:50%;
    background:{v_color};border:3px solid #fff;
    box-shadow:0 0 14px {v_color};
    animation:pulseRing 1.5s infinite;
  "></div>
  <style>@keyframes pulseRing{{
    0%{{box-shadow:0 0 0 0 {v_color}88}}
    70%{{box-shadow:0 0 0 16px transparent}}
    100%{{box-shadow:0 0 0 0 transparent}}
  }}</style>`,
  iconSize:[20,20], iconAnchor:[10,10], className:''
}});

L.marker([{lat1},{lon1}], {{icon:pickupIcon}}).addTo(map).bindPopup("📍 Your Pickup");
L.marker([{lat2},{lon2}], {{icon:dropIcon}}).addTo(map).bindPopup("🏁 Drop Point");
const youMarker = L.marker([{lat1},{lon1}], {{icon:youIcon}}).addTo(map);
youMarker.bindTooltip("You", {{permanent:true, direction:'top', className:''}});

// Route polyline
const routeLine = L.polyline([[{lat1},{lon1}],[{lat2},{lon2}]], {{
  color:'{v_color}', weight:4, opacity:0.6, dashArray:'8,6'
}}).addTo(map);

// ── RIDER MOVEMENT AI ─────────────────────────────────────
// Rider starts 0.06 deg away from pickup and moves toward pickup
let riderLat = {lat1} + 0.055;
let riderLon = {lon1} + 0.04;
const targetLat = {lat1};
const targetLon = {lon1};
const totalSteps = 80;
let step = 0;
let alertShown = false;
const booked = {booked_js};

const riderMarker = L.marker([riderLat, riderLon], {{icon:riderIcon}}).addTo(map);
riderMarker.bindPopup(`{v_emoji} {driver_name} — {driver_plate}`);

const trailCoords = [[riderLat, riderLon]];
const trail = L.polyline(trailCoords, {{color:'{v_color}', weight:2, opacity:0.4}}).addTo(map);

// ── AI LOG HELPER ─────────────────────────────────────────
const logEl = document.getElementById('ai-log');
const aiMessages = [
  "AI: Optimal route computed via Dijkstra",
  "AI: Traffic signal override — clear path",
  "AI: ETA recalculated — 2.1 min saved",
  "AI: Surge pricing zone detected nearby",
  "AI: Driver speed nominal — 28 km/h",
  "AI: Route re-optimised via ML model",
  "AI: No obstacles detected on path",
  "AI: Heatmap density — HIGH zone ahead",
  "AI: Pickup zone confirmed — GPS locked",
];
let msgIdx = 0;

function addLog(msg) {{
  const now = new Date().toLocaleTimeString('en-IN',{{hour12:false}});
  const d = document.createElement('div');
  d.className = 'log-line';
  d.innerHTML = `<span class="ts">${{now}}</span>${{msg}}`;
  logEl.appendChild(d);
  logEl.scrollTop = logEl.scrollHeight;
}}

// ── HAVERSINE JS ──────────────────────────────────────────
function haversineJS(lat1,lon1,lat2,lon2){{
  const R=6371, dLat=(lat2-lat1)*Math.PI/180, dLon=(lon2-lon1)*Math.PI/180;
  const a=Math.sin(dLat/2)**2+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}}

// ── MAIN ANIMATION LOOP ───────────────────────────────────
function moveRider() {{
  if (step >= totalSteps) {{
    document.getElementById('ai-status').textContent = "Arrived ✅";
    document.getElementById('ai-sub').textContent    = "Rider at pickup point";
    document.getElementById('eta-val').textContent   = "0";
    document.getElementById('dist-val').textContent  = "0.00";
    document.getElementById('eta-bar').style.width   = "0%";
    addLog("AI: 🎉 Rider has ARRIVED at pickup!");
    return;
  }}

  const t = step / totalSteps;
  riderLat = riderLat + (targetLat - riderLat) * 0.045 + (Math.random()-0.5)*0.0003;
  riderLon = riderLon + (targetLon - riderLon) * 0.045 + (Math.random()-0.5)*0.0003;

  riderMarker.setLatLng([riderLat, riderLon]);
  trailCoords.push([riderLat, riderLon]);
  trail.setLatLngs(trailCoords);

  const dist = haversineJS(riderLat, riderLon, targetLat, targetLon);
  const eta  = Math.max(0, (dist / 0.5 * 60)).toFixed(1);   // ~30 km/h avg
  const pct  = Math.max(0, (dist / haversineJS({lat1}+0.055,{lon1}+0.04,targetLat,targetLon))*100);

  document.getElementById('dist-val').textContent = dist.toFixed(3);
  document.getElementById('eta-val').textContent  = eta;
  document.getElementById('eta-bar').style.width  = pct + "%";

  // Proximity alert
  if (dist < 0.35 && !alertShown) {{
    alertShown = true;
    const alertEl = document.getElementById('alert-box');
    alertEl.style.display = 'block';
    addLog("⚠️ AI ALERT: Rider within 350m — get ready!");
    setTimeout(() => {{ alertEl.style.display='none'; }}, 4000);
  }}
  if (dist < 0.15) {{
    document.getElementById('ai-status').textContent = "Almost Here!";
    document.getElementById('ai-sub').textContent    = "< 150m away";
  }}

  // Periodic AI log
  if (step % 10 === 0) {{
    addLog(aiMessages[msgIdx % aiMessages.length]);
    msgIdx++;
  }}

  step++;
  setTimeout(moveRider, 400);
}}

// Start movement only if booked
if (booked) {{
  addLog("AI: 🚀 Ride booked — starting live tracking...");
  setTimeout(moveRider, 1200);
}} else {{
  addLog("AI: Waiting for ride booking...");
  addLog("AI: Heatmap analysis active");
  addLog("AI: " + {len(heat_data)} + " demand points loaded");
  document.getElementById('ai-status').textContent = "Standby";
  document.getElementById('ai-sub').textContent    = "Book a ride to track";
}}
</script>
</body>
</html>
"""

components.html(live_map_html, height=620, scrolling=False)

# ================================
# 🚀 SIDEBAR
# ================================
st.sidebar.title("🚖 Uber AI Controls")
st.sidebar.success("✅ Live Tracking | Dark Theme | AI Active")

if vehicle_choice:
    emoji = "🏍️" if vehicle_choice == "Bike" else "🚗"
    st.sidebar.info(f"{emoji} Vehicle: **{vehicle_choice}**\n\n📏 Distance: {distance} km\n\n💰 Fare: ₹{fare}")
else:
    st.sidebar.warning("No vehicle selected yet.")

if booked:
    st.sidebar.markdown("---")
    st.sidebar.success(f"🟢 Ride Active\n\n👤 {driver_name}\n📞 {driver_phone}\n🚘 {driver_plate}")

st.sidebar.markdown("---")
st.sidebar.markdown("🔵 Bike markers → Blue glow")
st.sidebar.markdown("🟡 Car markers  → Gold glow")
st.sidebar.markdown("🟢 Green marker → Pickup")
st.sidebar.markdown("🔴 Red marker   → Drop")
st.sidebar.markdown("🏍️/🚗 Animated → Live Rider")


# ================================
# ✅ ML MODEL — IMPROVED + BOTTOM UI DASHBOARD
# ================================
hour = time.localtime().tm_hour
traffic = random.randint(1, 4)
predicted_fare = model.predict([[distance, hour, traffic]])[0]

@st.cache_resource
def train_improved_model():
    """
    Prompt used to design this model:
    
    'Train a second Random Forest Regressor on the same synthetic fare dataset
     but with stronger hyperparameters: n_estimators=300, max_depth=10, random_state=42.
     Compare its R² score against the base model (100 estimators, no depth limit).
     Display in a dark-themed HTML dashboard:
       1. Base model R² score
       2. Accuracy % of base model
       3. Improved model R² score + % improvement delta over base
       4. Fare prediction from the improved model vs base vs rule-based
     All four metrics must show as glowing cards with progress bars.'
    """
    np.random.seed(42)
    n = 1000
    data = pd.DataFrame({
        "distance": np.random.uniform(1, 25, n),
        "hour":     np.random.randint(0, 24, n),
        "traffic":  np.random.randint(1, 5, n),
    })
    data["fare"] = (
        data["distance"] * 20 +
        data["traffic"]  * 15 +
        data["hour"]     * 2  +
        np.random.normal(0, 10, n)
    )
    X = data[["distance", "hour", "traffic"]]
    y = data["fare"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    imp = RandomForestRegressor(n_estimators=300, max_depth=10, random_state=42)
    imp.fit(X_train, y_train)
    score = r2_score(y_test, imp.predict(X_test))
    return imp, score

improved_model, improved_score = train_improved_model()
improved_predicted_fare = improved_model.predict([[distance, hour, traffic]])[0]

# ── Derived display values ──────────────────────────────────
base_acc     = round(model_score    * 100, 2)
imp_acc      = round(improved_score * 100, 2)
delta_acc    = round(imp_acc - base_acc, 2)
sign_acc     = "+" if delta_acc >= 0 else ""
fare_base    = int(predicted_fare)
fare_imp     = int(improved_predicted_fare)
fare_delta   = fare_imp - fare_base
sign_fare    = "+" if fare_delta >= 0 else ""
vehicle_label = vehicle_choice if vehicle_choice else "Not selected"

ml_ui_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background: #0b0b16;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
    padding: 0;
  }}

  /* ══ OUTER WRAPPER — medium card like PowerBI ══ */
  .pbi-wrap {{
    background: #0f0f1e;
    border: 1px solid #1e1e38;
    border-radius: 16px;
    overflow: hidden;
    width: 100%;
    box-shadow: 0 4px 40px rgba(0,0,0,0.6);
  }}

  /* ── Title bar ── */
  .pbi-titlebar {{
    background: #13132b;
    border-bottom: 1px solid #1e1e3a;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .pbi-title-left {{ display: flex; align-items: center; gap: 10px; }}
  .pbi-icon {{ font-size: 18px; filter: drop-shadow(0 0 6px #8b5cf6); }}
  .pbi-name {{
    font-size: 13px; font-weight: 800; letter-spacing: 0.2px;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .pbi-sub {{ font-size: 10px; color: #4b5563; margin-top: 1px; }}
  .pbi-badges {{ display: flex; align-items: center; gap: 8px; }}
  .badge {{
    font-size: 9.5px; font-weight: 700; padding: 3px 9px;
    border-radius: 99px; letter-spacing: 0.8px;
  }}
  .badge.live {{
    background:#0d1f12; border:1px solid #16a34a44;
    color:#4ade80; display:flex; align-items:center; gap:5px;
  }}
  .badge.rf   {{ background:#1a0a3a; border:1px solid #7c3aed44; color:#a78bfa; }}
  .badge.ts   {{ background:#0a1a2a; border:1px solid #2563eb44; color:#60a5fa; }}
  .livdot {{
    width:6px; height:6px; border-radius:50%;
    background:#4ade80; box-shadow:0 0 6px #4ade80;
    animation: blink 1.1s infinite;
  }}
  @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.2}} }}

  /* ── Body padding ── */
  .pbi-body {{ padding: 16px 18px 18px; }}

  /* ── KPI row: 4 cards ── */
  .kpi-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
  }}
  .kpi {{
    background: #0c0c20;
    border: 1px solid #1a1a34;
    border-radius: 12px;
    padding: 14px 14px 12px;
    position: relative;
    overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s;
  }}
  .kpi:hover {{ transform: translateY(-3px); box-shadow: 0 6px 24px rgba(0,0,0,0.5); }}
  .kpi::before {{
    content:''; position:absolute; top:0; left:0; right:0;
    height:2.5px; border-radius:12px 12px 0 0;
  }}
  .kpi::after {{
    content:''; position:absolute; top:-20px; right:-20px;
    width:70px; height:70px; border-radius:50%;
    background: var(--glow); filter:blur(16px); pointer-events:none;
  }}
  .kpi.p {{ --accent:#a78bfa; --glow:#8b5cf618; }}
  .kpi.b {{ --accent:#60a5fa; --glow:#3b82f618; }}
  .kpi.g {{ --accent:#34d399; --glow:#10b98118; }}
  .kpi.o {{ --accent:#fbbf24; --glow:#f59e0b18; }}
  .kpi.p::before {{ background:linear-gradient(90deg,#7c3aed,#a78bfa); }}
  .kpi.b::before {{ background:linear-gradient(90deg,#2563eb,#60a5fa); }}
  .kpi.g::before {{ background:linear-gradient(90deg,#059669,#34d399); }}
  .kpi.o::before {{ background:linear-gradient(90deg,#b45309,#fbbf24); }}

  .kpi-seq  {{ font-size:9px; font-weight:700; color:var(--accent);
               text-transform:uppercase; letter-spacing:1.4px; margin-bottom:8px; opacity:0.7; }}
  .kpi-lbl  {{ font-size:9.5px; color:#6b7280; text-transform:uppercase;
               letter-spacing:1px; font-weight:600; margin-bottom:4px; }}
  .kpi-val  {{ font-size:26px; font-weight:900; color:var(--accent);
               line-height:1; margin-bottom:3px; letter-spacing:-0.5px; }}
  .kpi-desc {{ font-size:10px; color:#374151; margin-bottom:10px; }}
  .bar-t    {{ background:#111130; border-radius:6px; height:4px;
               overflow:hidden; margin-bottom:8px; }}
  .bar-f    {{ height:4px; border-radius:6px; }}
  .kpi.p .bar-f {{ background:linear-gradient(90deg,#7c3aed,#a78bfa); }}
  .kpi.b .bar-f {{ background:linear-gradient(90deg,#2563eb,#60a5fa); }}
  .kpi.g .bar-f {{ background:linear-gradient(90deg,#059669,#34d399); }}
  .kpi.o .bar-f {{ background:linear-gradient(90deg,#b45309,#fbbf24); }}
  .pill {{
    display:inline-flex; align-items:center; gap:3px;
    font-size:9.5px; font-weight:700; padding:2px 8px; border-radius:99px;
  }}
  .pill.gr {{ background:#052e16; color:#4ade80; border:1px solid #16a34a30; }}
  .pill.bl {{ background:#0c1a2e; color:#60a5fa; border:1px solid #2563eb30; }}

  /* ── Bottom 3-column detail strip ── */
  .detail-row {{
    display: grid;
    grid-template-columns: 1.1fr 1.1fr 0.8fr;
    gap: 12px;
  }}
  .det {{
    background: #0c0c20;
    border: 1px solid #1a1a34;
    border-radius: 12px;
    padding: 12px 14px;
  }}
  .det-title {{
    font-size: 9.5px; font-weight: 700; color: #4b5563;
    text-transform: uppercase; letter-spacing: 1.1px;
    border-bottom: 1px solid #13132a;
    padding-bottom: 7px; margin-bottom: 10px;
  }}
  .drow {{
    display:flex; justify-content:space-between; align-items:center;
    padding: 5px 0; border-bottom:1px solid #0f0f22; font-size:11.5px;
  }}
  .drow:last-child {{ border-bottom:none; }}
  .drow .dk {{ color:#6b7280; }}
  .drow .dv {{ font-weight:700; }}
  .drow .dv.p {{ color:#a78bfa; }}
  .drow .dv.b {{ color:#60a5fa; }}
  .drow .dv.g {{ color:#34d399; }}
  .drow .dv.y {{ color:#fbbf24; }}
  .drow .dv.w {{ color:#e2e8f0; }}

  /* mini bar chart in 3rd panel */
  .mini-chart {{ margin-top: 4px; }}
  .mc-row {{ margin-bottom: 8px; }}
  .mc-label {{
    display:flex; justify-content:space-between;
    font-size:10px; color:#6b7280; margin-bottom:3px;
  }}
  .mc-label span:last-child {{ color:#e2e8f0; font-weight:600; }}
  .mc-bar {{ background:#111130; border-radius:4px; height:5px; overflow:hidden; }}
  .mc-fill {{ height:5px; border-radius:4px; }}
</style>
</head>
<body>
<div class="pbi-wrap">

  <!-- TITLE BAR -->
  <div class="pbi-titlebar">
    <div class="pbi-title-left">
      <span class="pbi-icon">🤖</span>
      <div>
        <div class="pbi-name">ML Intelligence Dashboard</div>
        <div class="pbi-sub">Random Forest · Fare Prediction · Accuracy Analytics</div>
      </div>
    </div>
    <div class="pbi-badges">
      <span class="badge rf">RF MODEL</span>
      <span class="badge ts">n=300 · depth=10</span>
      <span class="badge live"><span class="livdot"></span>LIVE</span>
    </div>
  </div>

  <div class="pbi-body">

    <!-- KPI CARDS -->
    <div class="kpi-row">

      <div class="kpi p">
        <div class="kpi-seq">01 · Score</div>
        <div class="kpi-lbl">Base Model R²</div>
        <div class="kpi-val">{round(model_score, 3)}</div>
        <div class="kpi-desc">RF · 100 estimators</div>
        <div class="bar-t"><div class="bar-f" style="width:{int(base_acc)}%"></div></div>
        <span class="pill bl">R² = {round(model_score,4)}</span>
      </div>

      <div class="kpi b">
        <div class="kpi-seq">02 · Accuracy</div>
        <div class="kpi-lbl">Base Accuracy %</div>
        <div class="kpi-val">{base_acc}%</div>
        <div class="kpi-desc">Test set · depth=None</div>
        <div class="bar-t"><div class="bar-f" style="width:{int(base_acc)}%"></div></div>
        <span class="pill bl">Base RF</span>
      </div>

      <div class="kpi g">
        <div class="kpi-seq">03 · Improved RF</div>
        <div class="kpi-lbl">Improved Accuracy</div>
        <div class="kpi-val">{imp_acc}%</div>
        <div class="kpi-desc">300 est · max_depth=10</div>
        <div class="bar-t"><div class="bar-f" style="width:{int(imp_acc)}%"></div></div>
        <span class="pill gr">▲ {sign_acc}{delta_acc}% gain</span>
      </div>

      <div class="kpi o">
        <div class="kpi-seq">04 · Fare</div>
        <div class="kpi-lbl">ML Predicted Fare</div>
        <div class="kpi-val">₹{fare_imp}</div>
        <div class="kpi-desc">Improved RF · {distance} km</div>
        <div class="bar-t"><div class="bar-f" style="width:72%"></div></div>
        <span class="pill bl">Base ₹{fare_base} · Δ{sign_fare}{fare_delta}</span>
      </div>

    </div>

    <!-- DETAIL STRIP -->
    <div class="detail-row">

      <div class="det">
        <div class="det-title">📌 Input Features</div>
        <div class="drow"><span class="dk">Distance</span>     <span class="dv b">{distance} km</span></div>
        <div class="drow"><span class="dk">Hour</span>          <span class="dv w">{hour}:00</span></div>
        <div class="drow"><span class="dk">Traffic</span>       <span class="dv w">{traffic} / 4</span></div>
        <div class="drow"><span class="dk">Vehicle</span>       <span class="dv y">{vehicle_label}</span></div>
        <div class="drow"><span class="dk">Route</span>         <span class="dv w" style="font-size:10px">{pickup} → {drop}</span></div>
      </div>

      <div class="det">
        <div class="det-title">💹 Fare Comparison</div>
        <div class="drow"><span class="dk">Rule-based</span>    <span class="dv w">₹{fare}</span></div>
        <div class="drow"><span class="dk">Base ML</span>       <span class="dv b">₹{fare_base}</span></div>
        <div class="drow"><span class="dk">Improved ML</span>   <span class="dv g">₹{fare_imp}</span></div>
        <div class="drow"><span class="dk">Base R²</span>       <span class="dv p">{round(model_score,4)}</span></div>
        <div class="drow"><span class="dk">Improved R²</span>   <span class="dv g">{round(improved_score,4)}</span></div>
      </div>

      <div class="det">
        <div class="det-title">📊 Accuracy Chart</div>
        <div class="mini-chart">
          <div class="mc-row">
            <div class="mc-label"><span>Base RF</span><span>{base_acc}%</span></div>
            <div class="mc-bar"><div class="mc-fill" style="width:{int(base_acc)}%;background:linear-gradient(90deg,#2563eb,#60a5fa)"></div></div>
          </div>
          <div class="mc-row">
            <div class="mc-label"><span>Improved RF</span><span>{imp_acc}%</span></div>
            <div class="mc-bar"><div class="mc-fill" style="width:{int(imp_acc)}%;background:linear-gradient(90deg,#059669,#34d399)"></div></div>
          </div>
          <div class="mc-row">
            <div class="mc-label"><span>Gain</span><span style="color:#4ade80">{sign_acc}{delta_acc}%</span></div>
            <div class="mc-bar"><div class="mc-fill" style="width:{min(int(abs(delta_acc)*10),100)}%;background:linear-gradient(90deg,#d97706,#fbbf24)"></div></div>
          </div>
        </div>
      </div>

    </div>
  </div><!-- /pbi-body -->
</div><!-- /pbi-wrap -->
</body>
</html>
"""

st.markdown("---")
components.html(ml_ui_html, height=420, scrolling=False)

#System Design