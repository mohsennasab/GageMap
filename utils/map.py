import folium
from shapely.geometry import mapping

def generate_map(all_stations, project_area, filtered_stations):
    print(f"Plotting {len(all_stations)} total stations, highlighting {len(filtered_stations)} inside project area.")

    center = [project_area.centroid.y, project_area.centroid.x]
    m = folium.Map(
        location=center,
        zoom_start=11,  # Slightly more zoomed-in
        tiles="OpenStreetMap",
        control_scale=True,
        attr="Map data © OpenStreetMap contributors"
    )


    # Add project area outline
    geojson = mapping(project_area)
    folium.GeoJson(
        geojson,
        name="Project Area",
        style_function=lambda x: {
            "fillOpacity": 0,
            "color": "black",
            "weight": 2
        }
    ).add_to(m)

    # Plot all stations
    for s in all_stations:
        is_inside = s in filtered_stations
        color = "green" if is_inside else "red"
        popup = f"<b>{s['name']}</b><br>ID: {s['id']}<br>"
        popup += f"Daily Data: {'Yes' if s['has_daily'] else 'No'}<br>"
        popup += f"Instantaneous Data: {'Yes' if s['has_instant'] else 'No'}"

        folium.CircleMarker(
            location=[s["latitude"], s["longitude"]],
            radius=6 if is_inside else 5,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=popup
        ).add_to(m)

    # Legend
    legend_html = '''
    <div style="position: fixed; bottom: 30px; left: 30px; width: 240px; height: 110px;
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding: 10px;">
    <b>Legend</b><br>
    <i style="background: black; border-radius:50%; width: 10px; height: 10px; display: inline-block;"></i> Project Area<br>
    <i style="background: green; border-radius:50%; width: 10px; height: 10px; display: inline-block;"></i> Station inside Project Area<br>
    <i style="background: red; border-radius:50%; width: 10px; height: 10px; display: inline-block;"></i> Station outside Project Area
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)
    # auto-adjust the view to the full bounds of everything drawn
    m.fit_bounds(m.get_bounds())

    return m._repr_html_()
