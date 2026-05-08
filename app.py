import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="MertNav: Pure Map", layout="wide")

# Siyah Arka Plan Zorlaması
st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)

@st.cache_resource
def get_clean_map():
    # Karasu merkezli sokak ağı (Görseldeki ölçekte)
    G = ox.graph_from_address("Karasu, Sakarya, Turkey", dist=3000, network_type="drive")
    return G

G = get_clean_map()
my_pos = [41.1030, 30.7020] # Senin konumun

# --- SADE HARİTA TASARIMI ---
# Görseldeki gibi siyah ve boş bir altlık oluşturuyoruz
m = folium.Map(
    location=my_pos, 
    zoom_start=15, 
    tiles=None, # Arka planı tamamen siliyoruz
    attr='MertNav Pure Style'
)
# Siyah arka planı ekliyoruz
folium.Rectangle(
    bounds=[[41.0, 30.6], [41.2, 30.8]], 
    fill=True, 
    color='#000000', 
    fill_opacity=1
).add_to(m)

# Sokakları çiz (Sadece beyaz ince çizgiler olarak)
for u, v, data in G.edges(data=True):
    if 'geometry' in data:
        coords = [[p[1], p[0]] for p in list(data['geometry'].coords)]
        folium.PolyLine(coords, color="#333333", weight=1, opacity=0.8).add_to(m)

# Senin Konumun (Görseldeki turkuaz nokta)
folium.CircleMarker(
    location=my_pos, 
    radius=6, 
    color="#00fbff", 
    fill=True, 
    fill_color="#00fbff", 
    fill_opacity=1
).add_to(m)

# --- TIKLAMA VE ROTA ---
output = st_folium(m, width="100%", height=600, key="pure_map")

if output and output.get("last_clicked"):
    t_lat = output["last_clicked"]["lat"]
    t_lon = output["last_clicked"]["lng"]
    
    try:
        start_node = ox.nearest_nodes(G, my_pos[1], my_pos[0])
        target_node = ox.nearest_nodes(G, t_lon, t_lat)
        
        route = nx.shortest_path(G, start_node, target_node, weight='length')
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
        
        # Yeşil Rota (İnce ve Keskin)
        folium.PolyLine(route_coords, color="#00ff00", weight=4, opacity=1).add_to(m)
        st.rerun() # Rotayı anında göster
    except:
        pass
