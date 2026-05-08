import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="MertNav: K-RS 2026", layout="wide")
st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)

@st.cache_resource
def get_graph():
    # Karasu merkez (41.1030, 30.7020) - Koordinatları sabitledik
    location = (41.1030, 30.7020)
    G = ox.graph_from_point(location, dist=2500, network_type="drive")
    return G

G = get_graph()
my_pos = [41.1030, 30.7020]
start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])

def get_dist(n1, n2):
    return math.sqrt((G.nodes[n1]['x'] - G.nodes[n2]['x']) ** 2 +
                     (G.nodes[n1]['y'] - G.nodes[n2]['y']) ** 2)

st.title("🏙️ MERTNAV: K-RS 2026")

# Haritayı oluştururken dünya haritasına düşmemesi için limitleri zorluyoruz
m = folium.Map(location=my_pos, zoom_start=15, tiles=None, max_bounds=True)

# Siyah Arka Plan (Tıklamayı bozmayan temiz katman)
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    opacity=1
).add_to(m)

# Sokakları çiz (Koordinat hatası giderildi)
for u, v, data in G.edges(data=True):
    if 'geometry' in data:
        line_coords = [[lat, lon] for lon, lat in list(data['geometry'].coords)]
    else:
        line_coords = [[G.nodes[u]['y'], G.nodes[u]['x']], [G.nodes[v]['y'], G.nodes[v]['x']]]
    folium.PolyLine(locations=line_coords, color="#222222", weight=1, opacity=0.4).add_to(m)

folium.CircleMarker(location=my_pos, radius=8, color="#00fbff", fill=True, fill_opacity=1).add_to(m)

output = st_folium(m, width="100%", height=600, key="biased_map", returned_objects=["last_clicked"])

if output and output.get("last_clicked"):
    clicked = output["last_clicked"]
    t_lat, t_lon = clicked["lat"], clicked["lng"]
    target_node = ox.nearest_nodes(G, t_lon, t_lat)
    
    # Biased Algorithm (Senin Bahçelievler Mantığın)
    queue_start, queue_target = [(0, start_node)], [(0, target_node)]
    visited_start, visited_target = {start_node: None}, {target_node: None}
    meeting_node = None

    for _ in range(400):
        if queue_start:
            queue_start.sort(key=lambda x: x[0])
            _, current = queue_start.pop(0)
            for n in G.neighbors(current):
                if n not in visited_start:
                    visited_start[n] = current
                    queue_start.append((get_dist(n, target_node), n))
                    if n in visited_target: meeting_node = n; break
            if meeting_node: break
        if queue_target:
            queue_target.sort(key=lambda x: x[0])
            _, current = queue_target.pop(0)
            for n in G.neighbors(current):
                if n not in visited_target:
                    visited_target[n] = current
                    queue_target.append((get_dist(n, start_node), n))
                    if n in visited_start: meeting_node = n; break
            if meeting_node: break

    if meeting_node:
        path = []
        curr = meeting_node
        while curr: path.append(curr); curr = visited_start[curr]
        path = path[::-1]
        curr = visited_target[meeting_node]
        while curr: path.append(curr); curr = visited_target[curr]
        
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in path]
        folium.PolyLine(locations=route_coords, color="#00ff00", weight=5, opacity=1).add_to(m)
        folium.CircleMarker(location=[t_lat, t_lon], radius=6, color="#ff00ff", fill=True).add_to(m)
        st_folium(m, width="100%", height=600, key="final_map")
