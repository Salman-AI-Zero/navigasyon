import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="MertNav Karasu Kesin Çözüm", layout="wide")

# Cyberpunk Tema
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00d4ff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: K-RS 2026")

@st.cache_resource
def load_data():
    G = ox.graph_from_address("Karasu, Sakarya, Turkey", dist=5000, network_type="drive")
    return G

G = load_data()

# --- YAN MENÜ KONTROLLERİ ---
st.sidebar.header("📍 Rota Belirle")
destination = st.sidebar.selectbox(
    "Gidilecek Yer Seçin:",
    ["Seçiniz...", "Karasu Sahil", "Karasu Terminal", "Karasu Devlet Hastanesi", "Kule Park"]
)

# Koordinat Sözlüğü
locations = {
    "Karasu Sahil": [41.111, 30.705],
    "Karasu Terminal": [41.092, 30.687],
    "Karasu Devlet Hastanesi": [41.088, 30.695],
    "Kule Park": [41.103, 30.702]
}

my_pos = [41.103, 30.702] # Senin Sabit Konumun
m = folium.Map(location=my_pos, zoom_start=14, tiles="CartoDB dark_matter")
folium.Marker(my_pos, tooltip="Benim Konumum", icon=folium.Icon(color='blue')).add_to(m)

# --- ROTA TETİKLEME ---
if destination != "Seçiniz...":
    dest_pos = locations[destination]
    
    # EFEKT BÖLÜMÜ
    status = st.empty()
    bar = st.progress(0)
    
    status.markdown("### 🔵 Mavi dalgalar merkezden yayılıyor...")
    for i in range(50):
        time.sleep(0.01)
        bar.progress(i+1)
        
    status.markdown(f"### 🟣 Mor hedef kilitlendi: {destination}")
    for i in range(50, 100):
        time.sleep(0.01)
        bar.progress(i+1)

    # Rota Hesaplama
    start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])
    target_node = ox.nearest_nodes(G, dest_pos[1], dest_pos[0])
    route = nx.shortest_path(G, start_node, target_node, weight='length')
    route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]

    # Haritaya Ekleme
    folium.PolyLine(route_coords, color="#00FF00", weight=8, opacity=1).add_to(m)
    folium.Marker(dest_pos, icon=folium.Icon(color='purple')).add_to(m)
    
    status.markdown("### 🟢 Yeşil hat bağlandı! Rota hazır.")
    time.sleep(1)
    status.empty()
    bar.empty()

# Haritayı Göster
st_folium(m, width="100%", height=500, key="fixed_map")
        
    except Exception as e:
        st.sidebar.error("Bu noktaya yol bağlantısı bulunamadı!")
