import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import time

# 1. Sayfa ve Tema Ayarları
st.set_page_config(page_title="MertNav Karasu Final", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00d4ff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00d4ff; }
    h1 { text-align: center; font-family: 'Courier New', monospace; text-shadow: 2px 2px #ff00ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: K-RS 2026")

# 2. Harita Verisi Yükleme (Karasu Odaklı)
@st.cache_resource
def load_karasu_data():
    # Karasu için en stabil kapsama alanı
    G = ox.graph_from_address("Karasu, Sakarya, Turkey", dist=5000, network_type="drive")
    return G

try:
    G = load_karasu_data()
    st.sidebar.success("📡 Uydu Bağlantısı Stabil")
except Exception as e:
    st.error("Veri yükleme hatası. Lütfen sayfayı yenileyin.")
    st.stop()

# 3. Konum Bilgileri
# Karasu Merkez (Senin konumun)
my_pos = [41.103, 30.702] 

st.sidebar.header("📍 Navigasyon Paneli")
destination = st.sidebar.selectbox(
    "Hedef Seçin:",
    ["Seçiniz...", "Karasu Sahil", "Karasu Terminal", "Karasu Devlet Hastanesi", "Kule Park"]
)

locations = {
    "Karasu Sahil": [41.111, 30.705],
    "Karasu Terminal": [41.092, 30.687],
    "Karasu Devlet Hastanesi": [41.088, 30.695],
    "Kule Park": [41.103, 30.702]
}

# 4. Ana Harita Oluşturma
m = folium.Map(location=my_pos, zoom_start=14, tiles="CartoDB dark_matter")
folium.CircleMarker(
    location=my_pos,
    radius=10,
    color="#00d4ff",
    fill=True,
    fill_color="#00d4ff",
    tooltip="Mevcut Konumum"
).add_to(m)

# 5. Rota Hesaplama ve Efektler
if destination != "Seçiniz...":
    dest_pos = locations[destination]
    
    # Efekt Alanı
    status = st.empty()
    bar = st.progress(0)
    
    status.markdown("### 🔵 [SİSTEM]: Mavi dalgalar merkezden yayılıyor...")
    for i in range(50):
        time.sleep(0.01)
        bar.progress(i + 1)
        
    status.markdown(f"### 🟣 [HEDEF]: {destination} kilitlendi.")
    for i in range(50, 100):
        time.sleep(0.01)
        bar.progress(i + 1)

    try:
        # OSMnx 2.x uyumlu en yakın nokta bulma
        start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])
        target_node = ox.nearest_nodes(G, dest_pos[1], dest_pos[0])
        
        # En kısa yol (Yeşil Hat)
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]

        # Haritaya Ekle
        folium.PolyLine(route_coords, color="#00FF00", weight=8, opacity=1).add_to(m)
        folium.Marker(dest_pos, icon=folium.Icon(color='purple', icon='info-sign')).add_to(m)
        
        status.markdown("### 🟢 [ERİŞİM]: Yeşil hat bağlandı. İyi yolculuklar Mert!")
        time.sleep(1)
        status.empty()
        bar.empty()
        
    except Exception as e:
        st.sidebar.error("Rota çizilemedi. Lütfen başka bir nokta deneyin.")

# 6. Haritayı Ekrana Bas
st_folium(m, width="100%", height=550, key="mertnav_final_map")
