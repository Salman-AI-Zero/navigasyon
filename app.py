import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import math
import time

# 1. Sayfa ve Cyberpunk Stil
st.set_page_config(page_title="MertNav: Biased Karasu", layout="wide")
st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)

@st.cache_resource
def get_graph():
    # Karasu merkezli sokak ağı (Senin Bahçelievler ölçeğinde)
    location = (41.1030, 30.7020)
    G = ox.graph_from_point(location, dist=2500, network_type="drive")
    return G

G = get_graph()
my_pos = [41.1030, 30.7020]
start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])

# 2. Mesafe Fonksiyonu (Senin Biased Mantığın)
def get_dist(n1, n2):
    return math.sqrt((G.nodes[n1]['x'] - G.nodes[n2]['x']) ** 2 +
                     (G.nodes[n1]['y'] - G.nodes[n2]['y']) ** 2)

st.title("🏙️ MERTNAV: BIASED FLOW")

# 3. Haritayı Oluştur (Sadece Siyah ve Sokaklar)
m = folium.Map(location=my_pos, zoom_start=15, tiles=None)

# Siyah Arka Plan
folium.Rectangle(bounds=[[40, 30], [42, 31]], fill=True, color='#000000', fill_opacity=1).add_to(m)

# Mevcut Sokakları Çiz (Gri - Arka Plan)
for u, v, data in G.edges(data=True):
    if 'geometry' in data:
        folium.PolyLine(coords=[[p[1], p[0]] for p in list(data['geometry'].coords)], 
                        color="#1a1a1a", weight=1, opacity=0.5).add_to(m)

# Senin Konumun (Turkuaz)
folium.CircleMarker(location=my_pos, radius=8, color="#00fbff", fill=True, fill_opacity=1).add_to(m)

# 4. Tıklama Algılayıcı
output = st_folium(m, width="100%", height=600, key="biased_map", returned_objects=["last_clicked"])

if output and output.get("last_clicked"):
    clicked = output["last_clicked"]
    t_lat, t_lon = clicked["lat"], clicked["lng"]
    target_node = ox.nearest_nodes(G, t_lon, t_lat)
    
    # --- SENİN BIASED ALGORİTMANIN STREAMLIT UYARLAMASI ---
    status = st.empty()
    queue_start = [(0, start_node)]
    queue_target = [(0, target_node)]
    visited_start = {start_node: None}
    visited_target = {target_node: None}
    meeting_node = None

    status.markdown("### ⚡ Tarama Başlatıldı...")
    
    # Animasyon döngüsü (Hızlı tarama)
    for _ in range(300):
        if queue_start:
            queue_start.sort(key=lambda x: x[0])
            _, current = queue_start.pop(0)
            for neighbor in G.neighbors(current):
                if neighbor not in visited_start:
                    priority = get_dist(neighbor, target_node)
                    visited_start[neighbor] = current
                    queue_start.append((priority, neighbor))
                    if neighbor in visited_target:
                        meeting_node = neighbor; break
            if meeting_node: break

        if queue_target:
            queue_target.sort(key=lambda x: x[0])
            _, current = queue_target.pop(0)
            for neighbor in G.neighbors(current):
                if neighbor not in visited_target:
                    priority = get_dist(neighbor, start_node)
                    visited_target[neighbor] = current
                    queue_target.append((priority, neighbor))
                    if neighbor in visited_start:
                        meeting_node = neighbor; break
            if meeting_node: break

    # Yolu Birleştir ve Çiz
    if meeting_node:
        path = []
        curr = meeting_node
        while curr: path.append(curr); curr = visited_start[curr]
        path = path[::-1]
        curr = visited_target[meeting_node]
        while curr: path.append(curr); curr = visited_target[curr]
        
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in path]
        
        # Haritaya Rota ve Efektleri Ekle
        folium.PolyLine(route_coords, color="#00ff00", weight=5, opacity=1).add_to(m)
        folium.CircleMarker(location=[t_lat, t_lon], radius=6, color="#ff00ff", fill=True).add_to(m)
        
        status.success("🟢 Rota Bağlantısı Kuruldu!")
        st_folium(m, width="100%", height=600, key="final_map")
