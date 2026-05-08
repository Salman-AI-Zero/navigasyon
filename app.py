import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

# 1. Sistem ve Görsel Ayarlar
st.set_page_config(page_title="MertNav Final", layout="wide")

# Arka planı ve harita çevresini CSS ile karartıyoruz (Tıklamayı engellemez)
st.markdown("""
    <style>
    .stApp {background-color: #000000; color: #00fbff;}
    iframe {background-color: #000000; border: none;}
    .stMarkdown {text-align: center;}
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: K-RS 2026")

# 2. Veri Yükleme (Cache ile J7 Prime'ı yormuyoruz)
@st.cache_resource
def load_karasu_graph():
    # Karasu merkez koordinatı ve 2.5km çap (Bahçelievler ölçeği)
    location = (41.1030, 30.7020)
    G = ox.graph_from_point(location, dist=2500, network_type="drive")
    return G

try:
    G = load_karasu_graph()
except:
    st.error("📡 Harita verisi alınamadı. İnterneti kontrol et.")
    st.stop()

# 3. Başlangıç ve Durum Yönetimi
my_pos = [41.1030, 30.7020] # Senin merkez noktan (Turkuaz)

# Tıklanan noktayı hafızada tutmak için session_state kullanıyoruz
if 'target' not in st.session_state:
    st.session_state.target = None

# 4. Harita Tasarımı (Saf Sokak Görünümü)
m = folium.Map(
    location=my_pos, 
    zoom_start=15, 
    tiles=None, # Gereksiz harita resimlerini yükleme
    control_scale=False,
    zoom_control=False
)

# Siyah arka plan (Haritanın altına eklenir, tıklamayı engellemez)
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    opacity=1
).add_to(m)

# Sokak çizgilerini çiziyoruz
for u, v, data in G.edges(data=True):
    if 'geometry' in data:
        coords = [[p[1], p[0]] for p in list(data['geometry'].coords)]
        folium.PolyLine(coords, color="#222222", weight=1, opacity=0.5).add_to(m)

# Senin Konumun (Turkuaz Nokta)
folium.CircleMarker(
    location=my_pos, radius=8, color="#00fbff", fill=True, fill_color="#00fbff", fill_opacity=1
).add_to(m)

# 5. Tıklama ve Rota Çizimi
# Sadece 'last_clicked' verisini alarak hızı artırıyoruz
output = st_folium(
    m, 
    width="100%", 
    height=600, 
    key="mertnav_interactive",
    returned_objects=["last_clicked"]
)

# Haritaya tıklandığında:
if output and output.get("last_clicked"):
    clicked = output["last_clicked"]
    st.session_state.target = [clicked["lat"], clicked["lng"]]

# Rota varsa çiz
if st.session_state.target:
    t_lat, t_lon = st.session_state.target
    
    try:
        # En yakın yolları bul (scikit-learn gerektirir)
        start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])
        target_node = ox.nearest_nodes(G, t_lon, t_lat)
        
        # En kısa yolu hesapla
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
        
        # Yeşil Rota ve Mor Hedef
        folium.PolyLine(route_coords, color="#00ff00", weight=5, opacity=1).add_to(m)
        folium.CircleMarker(location=[t_lat, t_lon], radius=5, color="#ff00ff", fill=True).add_to(m)
        
        # Ekranı anında güncelle
        st.rerun()
    except:
        st.sidebar.warning("Yol bağlantısı kurulamadı.")

st.markdown("👇 *Haritada bir sokağa tıkla ve rotayı izle.*")
