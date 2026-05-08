import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="MertNav Cloud", layout="wide")

# Siyah Tema CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1 { color: #00d4ff; text-align: center; font-family: 'Courier New', monospace; }
    .stAlert { background-color: #1a1a1a; color: #00FF00; border: 1px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ MERTNAV: CYBERPUNK EDITION")


@st.cache_resource
def load_map():
    # Başlangıçta tüm bölgeyi değil, merkezi çekiyoruz (Hız için)
    G = ox.graph_from_place("Istanbul, Turkey", network_type="drive", retain_all=True)
    return G


with st.spinner("Harita verileri uydudan çekiliyor..."):
    G = load_map()

st.sidebar.success("Sistem Çevrimiçi (Online)")
st.sidebar.info("Hedef belirlemek için haritaya dokun.")

# Ana Harita (Siyah Tema)
m = folium.Map(location=[41.00, 28.85], zoom_start=11, tiles="CartoDB dark_matter")

# Etkileşimli haritayı göster
map_data = st_folium(m, width="100%", height=500)

if map_data["last_clicked"]:
    t_lat = map_data["last_clicked"]["lat"]
    t_lon = map_data["last_clicked"]["lng"]

    # Animasyon Efekti
    progress_bar = st.progress(0)
    status_text = st.empty()

    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
        if percent_complete < 40:
            status_text.text("🔵 Mavi dalgalar yayılıyor...")
        elif percent_complete < 80:
            status_text.text("🟣 Mor dalgalar karşılanıyor...")
        else:
            status_text.text("🟢 Yeşil hat bağlandı!")

    # Rota Hesapla
    start_node = ox.distance.nearest_nodes(G, 28.85, 41.00)  # Bahçelievler Merkez
    target_node = ox.distance.nearest_nodes(G, t_lon, t_lat)

    route = nx.shortest_path(G, start_node, target_node, weight='length')
    route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]

    # Haritayı Yeşille Güncelle
    folium.PolyLine(route_coords, color="#00FF00", weight=6, opacity=0.9).add_to(m)
    st_folium(m, width="100%", height=500, key="final_map")
    st.balloons()  # Zafer kutlaması!