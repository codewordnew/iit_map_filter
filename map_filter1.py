from typing import List
import pandas as pd
import folium
import json
import os
from urllib.parse import quote

def load_iit_data(file_path: str) -> pd.DataFrame:
    """
    Load IIT data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file containing IIT data
        
    Returns:
        pd.DataFrame: DataFrame containing IIT information
    """
    try:
        return pd.read_excel(file_path, engine="openpyxl")
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found at: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")

def create_feature_group(geojson_path: str) -> folium.FeatureGroup:
    """
    Create a feature group with India states GeoJSON data.
    
    Args:
        geojson_path (str): Path to the GeoJSON file containing India states data
        
    Returns:
        folium.FeatureGroup: Feature group with India map
    """
    try:
        fg = folium.FeatureGroup("map")
        with open(geojson_path, "r", encoding="utf-8-sig") as f:
            geojson_data = f.read()
        fg.add_child(folium.GeoJson(data=geojson_data))
        return fg
    except FileNotFoundError:
        raise FileNotFoundError(f"GeoJSON file not found at: {geojson_path}")
    except Exception as e:
        raise Exception(f"Error creating feature group: {str(e)}")

def create_popup_html(row: pd.Series) -> str:
    """
    Create HTML content for the popup marker with image URL.
    
    Args:
        row (pd.Series): Row containing IIT information
        
    Returns:
        str: Formatted HTML string for the popup
    """
    # Ensure the image URL is properly encoded
    image_url = quote(str(row['Image']), safe=':/?=')
    
    return f"""
    <div style="width:300px; padding:10px;">
        <h4 style="color:#2c3e50; margin-bottom:10px; font-family: Arial, sans-serif;">
            {row['IIT College']}
        </h4>
        <p style="margin:5px 0;"><b>Rank among IIT in India:</b> {row['IIT Ranking']}</p>
        <p style="margin:5px 0;"><b>NIRF Score:</b> {row['NIRF Score']}</p>
        <div style="margin-top:10px; text-align:center;">
            <img src="{image_url}" 
                 style="max-width:100%; 
                        height:200px; 
                        object-fit:cover; 
                        border-radius:5px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                 onerror="this.onerror=null; this.src='https://via.placeholder.com/300x200?text=Image+Not+Available';"
            >
        </div>
    </div>
    """

def add_iit_markers(fg: folium.FeatureGroup, data: pd.DataFrame) -> None:
    """
    Add IIT markers to the feature group.
    
    Args:
        fg (folium.FeatureGroup): Feature group to add markers to
        data (pd.DataFrame): DataFrame containing IIT information
    """
    for _, row in data.iterrows():
        try:
            popup = folium.Popup(
                html=create_popup_html(row),
                max_width=300
            )
            
            fg.add_child(
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=popup,
                    icon=folium.Icon(
                        color="red",
                        icon='university',
                        prefix='fa'
                    )
                )
            )
        except Exception as e:
            print(f"Error adding marker for {row['IIT College']}: {str(e)}")

def create_iit_map(data_file: str, geojson_file: str, output_file: str) -> None:
    """
    Create an interactive map with IIT locations and information.
    
    Args:
        data_file (str): Path to the Excel file containing IIT data
        geojson_file (str): Path to the GeoJSON file containing India states data
        output_file (str): Path where the output HTML map will be saved
    """
    # Load data
    data = load_iit_data(data_file)
    
    # Create feature group with India map
    fg = create_feature_group(geojson_file)
    
    # Create base map
    map_obj = folium.Map(
        location=[20.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles='CartoDB positron'  # Clean, light theme
    )
    
    # Add custom CSS for better styling
    css = """
    <style>
        .folium-popup {
            font-family: Arial, sans-serif;
        }
        .folium-popup img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10px auto;
        }
        .folium-popup h4 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        .folium-popup p {
            margin: 5px 0;
            color: #34495e;
        }
    </style>
    """
    map_obj.get_root().html.add_child(folium.Element(css))
    
    # Add markers
    add_iit_markers(fg, data)
    map_obj.add_child(fg)
    
    # Save the map
    map_obj.save(output_file)

def main():
    """
    Main function to execute the map creation process.
    """
    data_file = "iit_data.xlsx"
    geojson_file = "india_states.json"
    output_file = "final12.html"
    
    try:
        create_iit_map(data_file, geojson_file, output_file)
        print(f"Map created successfully! Open {output_file} in a web browser to view.")
    except Exception as e:
        print(f"Error creating map: {str(e)}")
        print("\nPlease ensure:")
        print("1. Your Excel file contains all required columns")
        print("2. Image URLs are valid and accessible")
        print("3. GeoJSON file exists and is valid")

if __name__ == "__main__":
    main()