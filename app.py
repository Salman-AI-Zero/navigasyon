import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import time

# Sayfa Başlığı
st.set_page_config(page_title="MertNav Karasu", layout="wide")

# Siyah Tema CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1 { color: #00d4ff; text-align: center; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: SAKARYA KARASU")

@st.cache_resource
def load_karasu_map():
    # Sadece Karasu'yu ve çevresindeki 7 kilometrelik sürüş ağını çekiyoruz
    # Bu veri çok küçük olduğu için saniyeler içinde yüklenir!
    G = ox.graph_from_address("Karasu, Sakarya, Turkey", dist=7000, network_type="drive")
    return G

with st.spinner("Karasu haritası hazırlanıyor..."):
    G = load_karasu_map()

st.sidebar.success("Karasu Modu Aktif")

# Karasu merkezli siyah harita
m = folium.Map(location=[41.10, 30.70], zoom_start=13, tiles="CartoDB dark_matter")

# Haritayı Göster
map_data = st_folium(m, width="100%", height=500)

if map_data["last_clicked"]:
    t_lat = map_data["last_clicked"]["lat"]
    t_lon = map_data["last_clicked"]["lng"]
    
    # Animasyon Efekti (Mavi-Mor Dalga Ruhunu yaşatıyoruz)
    status_text = st.empty()
    status_text.text("🔵 Karasu sokaklarında mavi dalgalar yayılıyor...")
    time.sleep(1)
    status_text.text("🟣 Mor dalgalar hedefle buluştu...")
    time.sleep(1)

    # Rota Hesaplama (Karasu Merkez'den tıklanan yere)
    # Karasu merkez koordinatı yaklaşık: 41.100, 30.700
    start_node = ox.distance.nearest_nodes(G, 30.700, 41.100) 
    target_node = ox.distance.nearest_nodes(G, t_lon, t_lat)
    
    try:
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
        
        # Yeşil Zafer Hattı
        folium.PolyLine(route_coords, color="#00FF00", weight=7, opacity=1).add_to(m)
        status_text.text("🟢 Karasu hattı bağlandı!")
        st_folium(m, width="100%", height=500, key="karasu_final")
    except:
        st.error("Karasu sınırları dışına tıkladın, biraz daha merkeze odaklan!")
