import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import time

# 1. Başlangıç ve Cyberpunk Stil
st.set_page_config(page_title="MertNav Karasu Tıklama Modu", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00d4ff; }
    h1 { text-align: center; font-family: 'Courier New', monospace; text-shadow: 2px 2px #ff00ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: K-RS 2026")

# 2. Veriyi Yükle (OSMnx 2.x Uyumlu)
@st.cache_resource
def load_map_data():
    # Karasu merkezli sürüş ağı
    G = ox.graph_from_address("Karasu, Sakarya, Turkey", dist=6000, network_type="drive")
    return G

G = load_map_data()
my_pos = [41.103, 30.702] # Senin Sabit Konumun (Merkez)

# 3. Harita ve Tıklama Yakalayıcı
st.sidebar.markdown("### 📡 Navigasyon Aktif\nHaritada bir sokağa tıkla.")

m = folium.Map(location=my_pos, zoom_start=14, tiles="CartoDB dark_matter")
folium.CircleMarker(location=my_pos, radius=10, color="#00d4ff", fill=True).add_to(m)

# Tıklamayı almak için en kritik kısım: "last_clicked" objesini zorla çekiyoruz
output = st_folium(
    m,
    width="100%",
    height=550,
    key="mertnav_interactive",
    returned_objects=["last_clicked"] 
)

# 4. Tıklama Algılandığında Devreye Giren Efektler ve Rota
if output and output.get("last_clicked"):
    t_lat = output["last_clicked"]["lat"]
    t_lon = output["last_clicked"]["lng"]
    
    # Animasyon ve Efekt Slotları
    status = st.empty()
    bar = st.progress(0)
    
    status.markdown("### 🔵 [SİSTEM]: Mavi dalgalar yayılıyor...")
    for i in range(50):
        time.sleep(0.01)
        bar.progress(i + 1)
        
    status.markdown(f"### 🟣 [HEDEF]: {t_lat:.4f}, {t_lon:.4f} kilitlendi.")
    for i in range(50, 100):
        time.sleep(0.01)
        bar.progress(i + 1)

    try:
        # En yakın yolları bul (scikit-learn gerektirir)
        start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])
        target_node = ox.nearest_nodes(G, t_lon, t_lat)
        
        # Rota Hesapla
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]

        # Haritayı güncellemek için yeni bir folium objesi
        folium.PolyLine(route_coords, color="#00FF00", weight=8, opacity=1).add_to(m)
        folium.Marker([t_lat, t_lon], icon=folium.Icon(color='purple')).add_to(m)
        
        status.markdown("### 🟢 [BAĞLANTI]: Yeşil hat çekildi!")
        time.sleep(1)
        status.empty()
        bar.empty()
        
        # Haritayı Rota ile Yeniden Bas
        st_folium(m, width="100%", height=550, key="route_drawn")
        
    except Exception as e:
        st.sidebar.error("Buraya yol bulamadım, sokağa tıklamayı dene!")
