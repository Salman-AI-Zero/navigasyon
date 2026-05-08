import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import time

# 1. Sayfa Konfigürasyonu ve Cyberpunk Tema
st.set_page_config(page_title="MertNav Karasu Final", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1 { color: #00d4ff; text-align: center; font-family: 'Courier New', monospace; text-shadow: 2px 2px #ff00ff; }
    .stText { color: #00d4ff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: K-RS 2026 EDITION")

# 2. Harita Verisini Yükle (Cache - Hız için)
@st.cache_resource
def load_karasu_network():
    # Karasu merkezli 8 kmlik sürüş ağı (Hatasız ve hızlı yükleme için ideal boyut)
    G = ox.graph_from_address("Karasu, Sakarya, Turkey", dist=8000, network_type="drive")
    return G

try:
    G = load_karasu_network()
    st.sidebar.success("📡 Uydu Bağlantısı Stabil")
except Exception as e:
    st.error(f"Harita yüklenemedi: {e}")
    st.stop()

# 3. Başlangıç Konumu (Bizim konumumuz - Karasu Merkez)
# Karasu Merkez Koordinatları: 41.103, 30.702
my_lat, my_lon = 41.103, 30.702
start_node = ox.distance.nearest_nodes(G, my_lon, my_lat)

# 4. Harita Arayüzü
st.sidebar.info("Hedef belirlemek için haritaya bir kez tıkla ve bekle.")
m = folium.Map(location=[my_lat, my_lon], zoom_start=14, tiles="CartoDB dark_matter")

# Bizim olduğumuz yere Mavi bir işaret koyalım (Mavi yayılımın merkezi)
folium.CircleMarker(
    location=[my_lat, my_lon],
    radius=10,
    color="#00d4ff",
    fill=True,
    fill_color="#00d4ff",
    popup="Konumum (Başlangıç)"
).add_to(m)

# Haritayı ekrana bas ve tıklamayı dinle
output = st_folium(
    m, 
    width="100%", 
    height=550, 
    key="mertnav_map",
    returned_objects=["last_clicked"]
)

# 5. Rota ve Efekt Mekanizması
if output and output.get("last_clicked"):
    clicked = output["last_clicked"]
    t_lat, t_lon = clicked["lat"], clicked["lng"]
    
    # Animasyon Alanı (Empty slot kullanarak metinleri sürekli değiştiriyoruz)
    status_box = st.empty()
    progress_bar = st.empty()
    
    # AŞAMA 1: Mavi Yayılım (Bizim konumumuzdan)
    status_box.markdown("### 🔵 [SİSTEM]: Mevcut konumdan Mavi dalgalar yayılıyor...")
    bar = progress_bar.progress(0)
    for i in range(40):
        time.sleep(0.02)
        bar.progress(i + 1)
    
    # AŞAMA 2: Mor Hedef (İşaretlediğin yer)
    status_box.markdown(f"### 🟣 [HEDEF]: {t_lat:.4f}, {t_lon:.4f} noktasında Mor sinyal kilitlendi.")
    for i in range(40, 80):
        time.sleep(0.02)
        bar.progress(i + 1)
        
    # AŞAMA 3: Rota Hesaplama (Yeşil Bağlantı)
    try:
        target_node = ox.distance.nearest_nodes(G, t_lon, t_lat)
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
        
        status_box.markdown("### 🟢 [BAĞLANTI]: Yeşil hat çekildi. Navigasyon hazır!")
        bar.progress(100)
        time.sleep(0.5)
        
        # Haritayı yeşil rota ile güncelle
        folium.Marker([t_lat, t_lon], icon=folium.Icon(color='purple', icon='info-sign')).add_to(m)
        folium.PolyLine(route_coords, color="#00FF00", weight=7, opacity=1).add_to(m)
        
        # Ekranı temizle ve son haritayı göster
        status_box.empty()
        progress_bar.empty()
        st_folium(m, width="100%", height=550, key="final_route_map")
        st.success(f"Rota tamamlandı! Mesafe: {int(nx.path_weight(G, route, weight='length'))} metre.")
        
    except Exception as e:
        st.sidebar.error("Bu noktaya yol bağlantısı bulunamadı!")
