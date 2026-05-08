import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

# Sayfa Genişliği
st.set_page_config(page_title="Yol Bulucu", layout="wide")

st.title("📍 Harita Üzerinde Tıkla ve Yol Bul")
st.write("Başlangıç noktası yeşil işaretçidir. Hedef belirlemek için haritada herhangi bir yola tıklayın.")

# 1. Haritayı ve Grafiği Yükle (Önbelleğe alıyoruz ki her seferinde indirmesin)
@st.cache_resource
def get_graph():
    place_name = "Bahcelievler, Istanbul, Turkey"
    graph = ox.graph_from_place(place_name, network_type="drive")
    return graph

graph = get_graph()

# 2. Başlangıç Noktasını Belirle (Bahçelievler'in merkezi)
nodes_list = list(graph.nodes())
start_node = nodes_list[len(nodes_list) // 2]
start_coords = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])

# 3. Haritayı Oluştur
def create_map():
    m = folium.Map(location=start_coords, zoom_start=14, tiles="OpenStreetMap")
    folium.Marker(
        start_coords, 
        tooltip="Başlangıç Noktası", 
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    return m

# 4. Tıklama Olayını Yakala
if 'map_static' not in st.session_state:
    st.session_state.map_static = create_map()

# Haritayı ekrana bas ve tıklamaları dinle
output = st_folium(st.session_state.map_static, width="100%", height=500)

# Tıklama verisini kontrol et
if output['last_clicked']:
    lat = output['last_clicked']['lat']
    lng = output['last_clicked']['lng']
    
    st.sidebar.success(f"Hedef Seçildi: {lat:.4f}, {lng:.4f}")
    
    # 5. En Yakın Düğümü (Node) Bul ve Yolu Hesapla
    target_node = ox.distance.nearest_nodes(graph, lng, lat)
    
    try:
        # En kısa yolu hesapla (Senin bi-directional mantığını buraya fonksiyon olarak gömebilirsin)
        route = nx.shortest_path(graph, start_node, target_node, weight='length')
        
        # Rotayı harita üzerinde göster
        route_map = ox.plot_route_folium(graph, route, color="red", weight=6, opacity=0.7)
        
        # Başlangıç ve bitiş işaretçilerini ekle
        folium.Marker(start_coords, icon=folium.Icon(color='green')).add_to(route_map)
        folium.Marker((lat, lng), icon=folium.Icon(color='red', icon='stop')).add_to(route_map)
        
        st.subheader("İşte Bulunan En Kısa Yol:")
        st_folium(route_map, width="100%", height=500, key="result_map")
        
    except Exception as e:
        st.error("Üzgünüm, bu noktaya bir yol bulunamadı. Lütfen bir yola daha yakın tıklayın.")
