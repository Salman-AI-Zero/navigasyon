import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

# 1. Sayfa Düzeni
st.set_page_config(page_title="MertNav: Karasu Pure Edition", layout="wide")

# 2. Harita Verisi (Bahçelievler Mantığı: Küçük ve Hızlı)
@st.cache_resource
def get_map():
    # Sadece Karasu merkezini alıyoruz (Bahçelievler ölçeğinde)
    location = (41.1030, 30.7020) 
    G = ox.graph_from_point(location, dist=2500, network_type="drive")
    return G

G = get_map()

st.title("🏙️ MERTNAV: K-RS (Bahçelievler Style)")

# 3. Haritayı Oluştur
m = folium.Map(location=[41.1030, 30.7020], zoom_start=15, tiles="OpenStreetMap")

# Tıklama Yakalayıcı (En basit haliyle)
output = st_folium(m, width="100%", height=500, key="karasu_map")

# 4. Tıklama Gelirse Rota Çiz
if output and output.get("last_clicked"):
    clicked = output["last_clicked"]
    lat, lon = clicked["lat"], clicked["lng"]
    
    # En yakın noktalar
    start_node = ox.nearest_nodes(G, 30.7020, 41.1030) # Senin konumun
    target_node = ox.nearest_nodes(G, lon, lat)
    
    try:
        # Rota hesapla
        route = nx.shortest_path(G, start_node, target_node, weight="length")
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]
        
        # Haritaya rota ekle (Yeşil Hat)
        folium.PolyLine(route_coords, color="green", weight=6).add_to(m)
        folium.Marker([lat, lon], popup="Hedef").add_to(m)
        
        # Haritayı güncelle
        st.rerun() # Tıklandığı an sayfayı yenile ki rota görünsün
        
    except Exception:
        st.error("Yol bulunamadı, lütfen bir caddeye tıklayın.")
