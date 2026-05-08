import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Bahçelievler Rota Planlayıcı", layout="wide")

st.title("📍 Bahçelievler Bi-Directional Search Görselleştirme")

@st.cache_data
def load_graph(place):
    graph = ox.graph_from_place(place, network_type="drive")
    return graph

place_name = "Bahcelievler, Istanbul, Turkey"
graph = load_graph(place_name)

# Başlangıç noktası (Sabit veya Seçmeli)
nodes_list = list(graph.nodes())
start_node = nodes_list[len(nodes_list) // 2]
start_coords = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])

st.sidebar.info("Haritaya tıklayarak bir hedef nokta seçin.")

# --- Harita Oluşturma ---
m = folium.Map(location=start_coords, zoom_start=14, tiles="cartodbpositron")
folium.Marker(start_coords, tooltip="Başlangıç", icon=folium.Icon(color='green')).add_to(m)

# Tıklanan noktayı yakala
output = st_folium(m, width=1000, height=600)

target_coords = None
if output['last_clicked']:
    target_coords = (output['last_clicked']['lat'], output['last_clicked']['lng'])

if target_coords:
    # En yakın düğümü bul
    target_node = ox.distance.nearest_nodes(graph, target_coords[1], target_coords[0])
    
    # Rota Hesaplama (Senin Bi-directional mantığın veya hazır A*)
    try:
        # Streamlit'te performansı korumak için nx.shortest_path kullanabilirsin
        # Kendi özel fonksiyonunu buraya entegre edebilirsin
        route = nx.shortest_path(graph, start_node, target_node, weight='length')
        
        # Rotayı haritaya ekle
        route_map = ox.plot_route_folium(graph, route, route_map=m, color="#00FF00", weight=5)
        st.success("Yol başarıyla hesaplandı!")
        st_folium(route_map, width=1000, height=600, key="result_map")
        
    except Exception as e:
        st.error(f"Yol bulunamadı: {e}")
