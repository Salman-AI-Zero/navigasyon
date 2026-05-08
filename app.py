import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

# 1. Sayfa ve Siyah Tema (CSS ile kesin karartma)
st.set_page_config(page_title="MertNav: Pure Edition", layout="wide")
st.markdown("<style>.stApp {background-color: #000000; color: #00fbff;}</style>", unsafe_allow_html=True)

st.title("🏙️ MERTNAV: K-RS 2026")

# 2. Sadece Sokak Verisini Çek (Hazır resim değil, sadece çizgi verisi)
@st.cache_resource
def get_pure_roads():
    # Karasu merkezli 3 kmlik sürüş ağı
    location = (41.1030, 30.7020)
    G = ox.graph_from_point(location, dist=3000, network_type="drive")
    return G

try:
    G = get_pure_roads()
except:
    st.error("Veri bağlantısı hatası.")
    st.stop()

my_pos = [41.1030, 30.7020]

# 3. Haritayı Oluştur (HİÇBİR HAZIR HARİTA/TILE YOK)
m = folium.Map(
    location=my_pos,
    zoom_start=15,
    tiles=None, # Arka planı tamamen sildik
    control_scale=False,
    zoom_control=False
)

# Arka planı kapkaranlık yapıyoruz
folium.Rectangle(
    bounds=[[40.9, 30.5], [41.3, 30.9]],
    fill=True,
    color='#000000',
    fill_color='#000000',
    fill_opacity=1
).add_to(m)

# 4. Sokak Çizgilerini Manuel Çiz (Görseldeki o saf doku için)
for u, v, data in G.edges(data=True):
    if 'geometry' in data:
        coords = [[p[1], p[0]] for p in list(data['geometry'].coords)]
        folium.PolyLine(coords, color="#222222", weight=1, opacity=0.7).add_to(m)

# Başlangıç Noktası (O meşhur turkuaz nokta)
folium.CircleMarker(
    location=my_pos, radius=8, color="#00fbff", fill=True, fill_color="#00fbff", fill_opacity=1
).add_to(m)

# 5. Tıklama ve İşaretleme Mekanizması
output = st_folium(
    m, 
    width="100%", 
    height=600, 
    key="pure_interactive",
    returned_objects=["last_clicked"]
)

if output and output.get("last_clicked"):
    t_lat = output["last_clicked"]["lat"]
    t_lon = output["last_clicked"]["lng"]
    
    try:
        # En yakın noktaları ve yolu bul
        start_node = ox.nearest_nodes(G, 30.7020, 41.1030)
        target_node = ox.nearest_nodes(G, t_lon, t_lat)
        
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
        
        # Yeşil Rota ve Mor Hedef (Görseldeki gibi ince ve net)
        folium.PolyLine(route_coords, color="#00ff00", weight=5, opacity=1).add_to(m)
        folium.CircleMarker(location=[t_lat, t_lon], radius=5, color="#ff00ff", fill=True).add_to(m)
        
        st.rerun() # Rotayı anında çiz
    except:
        st.sidebar.error("Sokağa tıklamadın!")

st.markdown("🔍 *Karasu sokaklarına dokun, yeşil hattı ateşle.*")
