
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
import folium
import geopandas as gpd
from shapely import wkt
import xarray as xr
#from osgeo import gdal
from Code.directories_creation import create_directories_only_if_not_exist
import pydeck as pdk
import ast
import numpy as np 
from matplotlib import cm
import random
import time
from folium import Circle
from geopandas.tools import sjoin

import s3fs
fs = s3fs.S3FileSystem(anon=False)

st.set_page_config(layout="wide")
numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']



def replace_name(stringa):
    stringa = ''.join( c for c in stringa if c not in '[]""' )
    return stringa



##############################################################################
key = 0
# Block for selecting the run directory based on the case study
working_directory = os.getcwd()
#working_directory = "s3://vania"
database_folder_path = 'Data'  # UI
country_level_db_path = os.path.join(database_folder_path, 'Case_Study', 'Country Level')
        
old_runs_complete = list(os.listdir(os.path.join(working_directory, 'Runs')))
#old_runs_complete = [old_runs_complete[5]]
old_runs = [''.join([i for i in x if not i.isdigit()]) for x in list(os.listdir(os.path.join(working_directory, 'Runs')))]
#old_runs = [old_runs[5]]
old_runs_total = list(os.listdir(os.path.join(working_directory, 'Runs')))

run_directory_ID = st.sidebar.selectbox('Select the Case Study', old_runs)
country = run_directory_ID.split('_')[0]
run_directory = os.path.join(working_directory, 'Runs', old_runs_complete[old_runs.index(run_directory_ID)])

is_case_with_names = True

crs_dict = {'Uganda': 21095,
            'Mozambique': 32737,
            'Nigeria': 26392,  # COMMENT (DARLAIN): need to manage how to work on 3 crs in nigeria
            'Sudan': 29636,
            'Rwanda': 32736,
            'Lesotho': 22287,
            'Burkina_Faso': 32630,
            'RDC': 4061,
            'Malawi': 20936,
            'Niger': 26392,
            'Tanzania': 32737,
            'Chad': 32634,
            'Liberia': 32629,
            'South_Sudan': 20136}  # 4251
crs = crs_dict.get(country)

    
# Importing all results to be put in the dashboard
demographic_data = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Demographics', 'first_analysis_results_df.csv'), index_col=0)

population_data = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Demographics', 'overall_pop_analysis_results_df.csv'), index_col=0)

night_lights_data = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Demographics', 'overall_nights_analysis_results_df.csv'), index_col=0)

specific_night_lights_data = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Demographics', 'overall_spec_nights_analysis_results_df.csv'), index_col=0)

crops_data = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Overall', 'crop_analysis.csv'), index_col=0)

second_level_analysis_data = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Overall', 'second_analysis_results_df.csv'), index_col=0)

polygons = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Demographics', 'polygons.csv'), index_col=0)

file_df = pd.merge(demographic_data, second_level_analysis_data, left_index=True, right_index=True)
file_df['geometry'] = file_df.centroid.apply(wkt.loads)

if is_case_with_names:
    file_df = file_df.reset_index()


file_gdf = gpd.GeoDataFrame(file_df, geometry='geometry')
file_gdf = file_gdf.reset_index()
file_gdf = file_gdf.set_crs(crs)

if file_gdf.crs != 'epsg:4326':
    file_gdf = file_gdf.to_crs(4326)

file_gdf['Community'] = file_gdf['ID']
file_gdf['index'] = file_gdf['ID']
file_gdf = file_gdf.set_index('index')
file_gdf = file_gdf.sort_values('Community')

##############################################################################

which_modes = ['Entire Area', 'Single Cluster', 'Compare Clusters']
which_mode = st.sidebar.selectbox('Select the Mode', which_modes, index=1)

if which_mode == 'Entire Area':  
    
    # Comparison with all the other communities based on input from user in dropdown menu

    row1_1, row1_2 = st.columns((3,3))
    
    key = 1
    if st.sidebar.checkbox("----- Scatter Plot -----", False, key=key):
        with row1_1:            
            key = 2
            comparison_dimensionq_scatter_x = st.sidebar.selectbox('Select the first dimension on which to compare', file_gdf.select_dtypes(include=numerics).columns, key=key,
                                                                   index = 35)
            key = 3
            comparison_dimensionq_scatter_y = st.sidebar.selectbox('Select the second dimension on which to compare', file_gdf.select_dtypes(include=numerics).columns, key=key,
                                                                   index = 9)
            
            key = 4
            comparison_color = st.sidebar.selectbox('Select the third dimension on which to compare', file_gdf.columns, key=key,
                                                                   index = 24)
            
            plot = px.scatter(data_frame=file_gdf, x=comparison_dimensionq_scatter_x, y=comparison_dimensionq_scatter_y, color=comparison_color, hover_name='Community')
            # display the chart
            st.plotly_chart(plot)
            

            compare_df = pd.DataFrame(file_gdf, columns = [comparison_dimensionq_scatter_x,
                                                        comparison_dimensionq_scatter_y,
                                                        comparison_color])
            compare_df = compare_df.rank(ascending=False)
            
            st.write(compare_df)
        
        
    # 2D MAPPING
    key = 5
    mapping_2d = st.sidebar.selectbox('------ 2D MAPPING ------',['ON', 'OFF'], index=1)

    if mapping_2d == 'ON':    
              
        grid = False
        with row1_2:
            "2D MAP"  
            key = 6
            if st.checkbox("National Grid", False, key=key):
                grid = True
                
            
            # center on Liberty Bell
            long = file_gdf.geometry.x.mean()
            lat = file_gdf.geometry.y.mean()
            
            if grid:
                grid_gdf = gpd.read_file(os.path.join(country_level_db_path, country, 'Networks', 'grid.shp'))
                grid_gdf = grid_gdf[grid_gdf.geometry != None]
                grid_gdf = grid_gdf.reset_index()
                if grid_gdf.crs != 'epsg:4326':
                    grid_gdf = grid_gdf.to_crs(4326)
                    
            m = folium.Map(location=[lat, long], zoom_start=9)
            tile = folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Esri Satellite',
                overlay=False,
                control=True
            ).add_to(m)
            
            tile = folium.TileLayer(
                tiles='http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}',
                attr='Google',
                name='Google Hybrid',
                overlay=False,
                control=True
            ).add_to(m)
            
            tile = folium.TileLayer(
                tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
                attr='Google',
                name='Google Maps',
                overlay=False,
                control=True
            ).add_to(m)
            
            folium.TileLayer('stamentoner').add_to(m)
            
            style1 = {'fillColor': '#228B22', 'lineColor': '#228B22'}
            style2 = {'fillColor': '#00FFFFFF', 'lineColor': '#00FFFFFF'}
            style3 = {'fillColor': 'green', 'color': 'green'}
            style4 = {'fillColor': 'red', 'color': 'red'}
            
            feature_group_1 = folium.FeatureGroup(name='Electrified Clusters', show=True)
            feature_group_2 = folium.FeatureGroup(name='Non Electrified Clusters', show=True)
            
            
            polygons_df = pd.read_csv(os.path.join(run_directory, 'Output', 'Analysis', 'Demographics', 'polygons.csv'))
            
            polygons_gdf = gpd.GeoDataFrame(polygons_df)
            polygons_gdf['geometry'] = polygons_gdf.polygons.apply(wkt.loads)
            polygons_gdf = polygons_gdf.set_crs(4326)
            
            a = pd.merge(file_gdf.drop(columns=['polygons']), polygons_gdf, left_index=True, right_index=True)
            
            
            if not polygons_gdf[polygons_gdf.night_lights == 0].empty:
                folium.GeoJson(polygons_gdf[polygons_gdf.night_lights == 0].to_json(), name='non-electrified clusters',
                                style_function=lambda x: style4).add_to(feature_group_2)
            if not polygons_gdf[polygons_gdf.night_lights > 0].empty:
                folium.GeoJson(polygons_gdf[polygons_gdf.night_lights > 0].to_json(), name='electrified clusters',
                                style_function=lambda x: style3).add_to(feature_group_1)
    
            feature_group = folium.FeatureGroup(name='Clusters Info', show=False)
    
            
            for index, row in file_gdf.set_index('ID').iterrows():
                #df_ = pd.DataFrame(file_gdf.drop(columns=['geometry','polygons','centroid']).set_index('ID')).iloc(index)
            
                text = pd.DataFrame(row).drop(['geometry','polygons','centroid']).to_html()
            
                iframe = folium.IFrame(text, width=500, height=350)
            
                popup = folium.Popup(iframe, max_width=500)
            
                x = row.geometry.x
                y = row.geometry.y
            
                marker = folium.Marker([y, x], popup=popup, icon=folium.Icon(color='blue', icon='hospital-o', prefix='fa')).add_to(feature_group)
            
            
            if 'grid_gdf' in locals():
                feature_group_a = folium.FeatureGroup(name='Grid Path')
                feature_group_b = folium.FeatureGroup(name='Grid Info')
                
                status_col_name = [x for x in grid_gdf.columns if
                                   any(ext in x for ext in ['status', 'Status', 'STATUS'])]
                
                if len(status_col_name) >0:
                    status_col_name = status_col_name[0]
                else:
                    status_col_name = 'no_status_column'
            
                voltage_col_name = [x for x in grid_gdf.columns if any(ext in x for ext in ['volt', 'Volt', 'VOLT'])]
            
                if len(voltage_col_name) > 0:
                    voltage_col_name = voltage_col_name[0]
            
                main_attribute = status_col_name
                if main_attribute not in grid_gdf.columns:
                    main_attribute = voltage_col_name
            
                attribute_list = grid_gdf[main_attribute].unique()
                # color_list = [style1, style2,style3, style4]
                color_list = ['green', 'red', 'yellow', 'blue', 'black', 'orange', 'white'][:len(attribute_list)]

                for index, row in grid_gdf.iterrows():
                    properties = color_list[attribute_list.tolist().index(row[main_attribute])]
                    # print(index, row[main_attribute], properties, '\n_______')
                    file = grid_gdf.iloc[[index]].to_json()
                    folium.features.Choropleth(geo_data=file, name=index, line_color=properties, line_weight=3).add_to(feature_group_a)
                
                style = {'fillColor': '#00000000', 'color': '#00000000'}
                folium.GeoJson(grid_gdf.to_json(), name='_info', style_function=lambda x:style,
                               tooltip=folium.features.GeoJsonTooltip(fields = list(grid_gdf.columns[:-1]))).add_to(feature_group_b)
                
                feature_group_a.add_to(m)
                feature_group_b.add_to(m)
            
            feature_group.add_to(m)
            feature_group_1.add_to(m)
            feature_group_2.add_to(m)

                        
            key = 7
            if st.checkbox("Zoom On Specific Community", True, key=key):
                
                
                key = 8
                comm = st.selectbox('Select the Community',file_gdf.index)
                
                comm_gdf = file_gdf[file_gdf.Community == comm]
                
                feature_group_3 = folium.FeatureGroup(name=comm, show=True)
                
                new_lat = float(comm_gdf.geometry.y)
                new_long = float(comm_gdf.geometry.x)
                
                # add marker
                tooltip = comm
                folium.Marker(
                    [new_lat, new_long], popup=comm, tooltip=tooltip
                ).add_to(feature_group_3)
                
                m.location = [new_lat, new_long]
                m.zoom_start = 15
                
                feature_group_3.add_to(m)
            
            
                    
            folium.plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=None,
                                edit_options=None).add_to(m)
            folium.plugins.Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen',
                                      force_separate_button=False).add_to(m)
            folium.plugins.MeasureControl(position='bottomleft', primary_length_unit='meters', secondary_length_unit='miles',
                                          primary_area_unit='sqmeters', secondary_area_unit='acres').add_to(m)
            folium.LayerControl().add_to(m)

            # Displaying a map         
            
            folium_static(m)

    key = 9
    if st.sidebar.checkbox("------ Histograms ------", False, key=key):
        def plot_hist(n):
            #key_slider = random.random()
            bin_size = st.slider("Number of Bins", min_value=3,
                                         max_value=10, value=5, key=n*100)
            plot = px.histogram(x=comparison_dimensions_hist[n], data_frame=file_gdf, nbins=bin_size, color='Community')
            st.plotly_chart(plot)
        # histogram

        
        st.set_option('deprecation.showPyplotGlobalUse', False)
        comparison_dimensions_hist = st.multiselect('Select the parameters on which to compare', file_gdf.select_dtypes(include=numerics).columns,
                                                    default=['area', 'population_worldpop', 'average_wealth_index', 'lights_build'])

        row2_1, row2_2 = st.columns((2,2))
        row3_1, row3_2 = st.columns((2,2))
        

            
        with row2_1:
            if len(comparison_dimensions_hist) > 0:
                plot_hist(0)
        with row2_2:
            if len(comparison_dimensions_hist) > 1:
                plot_hist(1)
        with row3_1:
            if len(comparison_dimensions_hist) > 2:
                plot_hist(2)
        with row3_2:
            if len(comparison_dimensions_hist) > 3:
                plot_hist(3)
                
#################################################################################################
elif which_mode == 'Single Cluster':
    # Side bar for selecting the community to be investigated
    select = st.sidebar.selectbox('Select the Community',file_gdf.index, index=0)
    
    gisele = st.sidebar.selectbox('GISEle',['Yes','No'], index=1)
    
    select_id = list(file_gdf.index).index(select)
    
# =============================================================================
#     if 'renewvia' in run_directory:
#         select_id = renewvia_rev_dict.get(select)
#     elif 'cesi' in run_directory:
#         select_id = cesi_rev_dict.get(select)
# =============================================================================
       
    community_path = os.path.join(run_directory, 'Output', 'Clusters','Communities', str(select))
    dashboarding_path = os.path.join(community_path, 'Dashboarding')
    
    info_gdf = file_gdf[file_gdf.ID == select] # qui
    
    crops_files_list = [x for x in os.listdir(community_path) if '.tif' in x and 'spam' in x] 
    pop_list = [x for x in os.listdir(community_path) if '.tif' in x and 'ppp' in x] 
    lights_list = [x for x in os.listdir(community_path) if '.tif' in x and 'Harmonized' in x] 
    
    raster_list_2d = [x for x in os.listdir(community_path) if '.tif' in x] 
    raster_list_2d = [x for x in raster_list_2d if x not in crops_files_list]
    raster_list_2d = [x for x in raster_list_2d if x not in pop_list]
    raster_list_2d = [x for x in raster_list_2d if x not in lights_list]
    
    raster_list_3d = raster_list_2d.copy()
        
    row1_1, row1_2 = st.columns((2,2))
    
    with row1_1:
                
        "# Community Description"
            
        # Block of information about the community - name etc. -
        country = replace_name(str(list(info_gdf.admin_0)))
        energy_trend = night_lights_data[night_lights_data.index == select]
        b = pd.DataFrame(data = energy_trend.transpose().values, index=energy_trend.columns, columns=[select])
        
        
        population_trend = population_data[population_data.index == select].transpose().dropna()
        
        max_pop_worldpop = int(info_gdf.population_worldpop / population_trend[select][-1]) # qui
        max_pop_facebook = int(info_gdf.population_facebook / population_trend[select][-1]) # qui
        a = pd.DataFrame(data = population_trend.values, index=population_trend.index, columns=['WorldPop Estimation'])
        a['Facebook Estimation'] = [int(i) for i in a['WorldPop Estimation']*max_pop_facebook]
        a['WorldPop Estimation'] = [int(i) for i in a['WorldPop Estimation']*max_pop_worldpop]
        
        
        'The cluster named %s is located in %s. More precisely, with respect to\
        the first level administrative division it is in %s, while in %s when \
        considering the second level.'\
            % (select, 
               country[1:-1], 
               str(info_gdf.admin_1.values)[2:-2], 
               str(info_gdf.admin_2.values)[2:-2])
        
        if 'No OSM location found' not in str(list(info_gdf.OSM)):
            #info_osm = ast.literal_eval(replace_name(str(info_gdf.OSM.values)))
            info_osm = replace_name(str(info_gdf.OSM.values))
            types = info_osm[0::2]
            names = info_osm[1::2]
            settlements_df = pd.DataFrame({'types': types,
                                            'names': names
                                            })
            towns = settlements_df[settlements_df.types == 'town']
            villages = settlements_df[settlements_df.types == 'village']
            residentials = settlements_df[settlements_df.types == 'residential']

            'In it, there are %i towns (%s), %i villages (%s),\
            and %i residential areas (%s). Moreover, the community is located %s km \
            from the closest important road.'\
                %(len(towns), 
                   replace_name(str(list(towns.names))),
                   len(villages),
                   replace_name(str(list(villages.names))),
                   len(residentials),
                   replace_name(str(list(residentials.names))),
                   round(float(info_gdf.distance_road),2)
                   )
                
        'In it there are %s building where between %s and %s are estimated to live.\
        The community develops itself over approximately %s km2, resulting in a\
        population density of %s people per km2 and a building density of \
        %s buildings per km2. It seems it reached its maximum population in %s, with\
        a growth of %s percent from 2000 to 2020.'\
            % (int(info_gdf.n_buildings),
               min(int(info_gdf.population_worldpop), int(info_gdf.population_facebook)), 
               max(int(info_gdf.population_worldpop), int(info_gdf.population_facebook)),
               round(float(info_gdf['area']), 2),
               round(float(info_gdf['population_density']), 2),
               round(float(info_gdf['building_density']), 2)     ,
               int(a.sort_values("WorldPop Estimation").index[-1]),
               round(abs(a["WorldPop Estimation"][-1] - a["WorldPop Estimation"][0]) / a["WorldPop Estimation"][0] * 100.0,2)
               )
       
        

        if int(info_gdf.night_lights) == 0:
            if int(b.dropna().sum()) == 0:
                'It seems that in 2018 (our most recent data) the village lacked \
                access to electricity as when looking at it from the sky during \
                the night we were not able to see any light. In particular it seems\
                this community never experienced any form of electrification.'
            
            elif int(b.sum()) > 0:
                'It seems that in 2018 (our most recent data) the village lacked \
                access to electricity as when looking at it from the sky during \
                the night we were not able to see any light. Nonetheless, it seems\
                this community experienced some form of electrification in the years: %s.\
                To see more, go to the ENERGY ACCESS TREND in the ANALYSIS section.'\
                    % (b[b[select] > 0].index,
                       )
                        
        
        elif int(info_gdf.night_lights) > 0:
            'It seems that the village has access to electricity since %s, and \
            still has it today. In particular, the %s percent of the area seems to\
            have lights during nights, resulting in a %s percent of buildings being in \
            potentially electrified zone.\
            To see more, go to the ENERGY ACCESS TREND in the ANALYSIS section.'\
                % (b[b[select] > 0].index[0],
                   round(int(info_gdf.night_lights.values), 2),
                   round(int(info_gdf.lights_build.values), 2))
                        
    create_directories_only_if_not_exist(dashboarding_path, False)


    # 2D MAPPING
    with row1_2:
        key = 10
        grid = False
        rasters_on = False
        if st.sidebar.checkbox("------ 2D MAPPING ------", True, key=key):
            # Displaying a map
            key = 11
            if st.sidebar.checkbox("National Grid", False, key=key):
                grid = True
            
            key = 12
            if st.sidebar.checkbox("Rasters ON", False, key=key):
                rasters_on = True
                
            @st.cache(suppress_st_warning=True)
            def single_cluster_2d_mapping():
                "# %s 2D MAP" % (select)
                

                if grid:
                    grid_gdf = gpd.read_file(os.path.join(country_level_db_path, country[1:-1], 'Networks', 'grid.shp'))
                    grid_gdf = grid_gdf[grid_gdf.geometry != None]
                    grid_gdf = grid_gdf.reset_index()
                    if grid_gdf.crs != 'epsg:4326':
                        grid_gdf = grid_gdf.to_crs(4326)
                        
                m = folium.Map(location = [float(info_gdf.geometry.y),float(info_gdf.geometry.x)], zoom_start=14)
                tile = folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri',
                    name='Esri Satellite',
                    overlay=False,
                    control=True
                ).add_to(m)
                
                tile = folium.TileLayer(
                    tiles='http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}',
                    attr='Google',
                    name='Google Hybrid',
                    overlay=False,
                    control=True
                ).add_to(m)
                
                tile = folium.TileLayer(
                    tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
                    attr='Google',
                    name='Google Maps',
                    overlay=False,
                    control=True
                ).add_to(m)
                
                folium.TileLayer('stamentoner').add_to(m)
                
                style1 = {'fillColor': '#228B22', 'lineColor': '#228B22'}
                style2 = {'fillColor': '#00FFFFFF', 'lineColor': '#00FFFFFF'}
                style3 = {'fillColor': 'green', 'color': 'green'}
                style4 = {'fillColor': 'red', 'color': 'red'}
                
                
                if gisele == 'Yes':
                    
                    if int(info_gdf.night_lights)  >0:
                        st.sidebar.subheader("This cluster already has access to electricity.")
                        
                    else:                        
                        feature_group_gisele_users = folium.FeatureGroup(name='GISEle - Users', show=True)
                        feature_group_gisele_subs = folium.FeatureGroup(name='GISEle - Substations', show=True)
                        feature_group_gisele_mv = folium.FeatureGroup(name='GISEle - Medium Voltage Lines', show=True)
                        feature_group_gisele_lv = folium.FeatureGroup(name='GISEle - Low Voltage Lines', show=True)
                        feature_group_gisele_grid_connections= folium.FeatureGroup(name='GISEle - Grid Connections', show=True)
                                                
                        gisele_output_path = os.path.join(run_directory, 'Output', 'GISELE', 'Output')
                        
                        area_gdf = gpd.read_file(os.path.join(community_path, '_commun_{0}.shp'.format(select))).to_crs(crs)
                        
                        
                        #USERS
                        def color_producer_users(val):
                            if val < 0:
                                return "darkred"
                            else:
                                return "yellow"
                            
                        gisele_users_gdf = gpd.read_file(os.path.join(gisele_output_path, 'final_users', 'final_users.shp'), crs=crs) 
                        #gisele_users_gdf = gisele_users_gdf.set_crs(crs)
                        #gisele_users_gdf = gpd.clip(gisele_users_gdf, area_gdf)
                        gisele_users_gdf = sjoin(gisele_users_gdf, area_gdf, how="left").dropna()

                        gisele_users_gdf['lat'] = gisele_users_gdf.to_crs(4326).geometry.y
                        gisele_users_gdf['long'] = gisele_users_gdf.to_crs(4326).geometry.x                                          
                        
                        for i in range(0,len(gisele_users_gdf)):
                            Circle(
                                location=[gisele_users_gdf.iloc[i]['lat'], gisele_users_gdf.iloc[i]['long']],
                                radius=2.5,
                                tooltip=gisele_users_gdf.iloc[[i]].T.to_html(),
                                color=color_producer_users(gisele_users_gdf.iloc[i]["Cluster"])).add_to(feature_group_gisele_users)
                        
                        #SUBS
                        def color_producer_subs(val):
                            if val < 0:
                                return "forestgreen"
                            else:
                                return "blue"
                        
                        
                        gisele_subs_gdf = gpd.read_file(os.path.join(gisele_output_path, 'secondary_substations', 'secondary_substations.shp'), crs=crs) 
                        #gisele_subs_gdf = gisele_subs_gdf.set_crs(crs)
                        #gisele_subs_gdf = gpd.clip(gisele_subs_gdf, area_gdf)
                        # gisele_subs_gdf = sjoin(gisele_subs_gdf, area_gdf, how="left").dropna()
                        
                        gisele_subs_gdf['lat'] = gisele_subs_gdf.to_crs(4326).geometry.y
                        gisele_subs_gdf['long'] = gisele_subs_gdf.to_crs(4326).geometry.x

                        for i in range(0,len(gisele_subs_gdf)):
                            Circle(
                                location=[gisele_subs_gdf.iloc[i]['lat'], gisele_subs_gdf.iloc[i]['long']],
                                radius=5,
                                tooltip=gisele_subs_gdf.iloc[[i]].T.to_html(),
                                color=color_producer_subs(gisele_subs_gdf.iloc[i]["Cluster"])).add_to(feature_group_gisele_subs)

                        #MV
                           
                        gisele_mv_gdf = gpd.read_file(os.path.join(gisele_output_path, 'MV_grid', 'MV_grid.shp'), crs=crs) 
                        #gisele_mv_gdf = gisele_mv_gdf.set_crs(crs)
                        #gisele_mv_gdf = gpd.clip(gisele_mv_gdf, area_gdf) 
                        #gisele_mv_gdf = sjoin(gisele_mv_gdf, area_gdf, how="left").dropna()

                        folium.features.Choropleth(geo_data=gisele_mv_gdf, name='mv', line_color='black', line_weight=6).add_to(feature_group_gisele_mv)
                    

                        style = {'fillColor': '#00000000', 'color': '#00000000'}
                        folium.GeoJson(gisele_mv_gdf.to_crs(4326).to_json(), name='_info', style_function=lambda x:style,
                                        tooltip=folium.features.GeoJsonTooltip(fields = list(gisele_mv_gdf.columns[:-1]))).add_to(feature_group_gisele_mv)                       

                        #LV
                        
                        
                        gisele_lv_gdf = gpd.read_file(os.path.join(gisele_output_path, 'LV_grid', 'LV_grid.shp'), crs=crs) 
                        #gisele_lv_gdf = gisele_lv_gdf.set_crs(crs)
                        #gisele_lv_gdf = gpd.clip(gisele_lv_gdf, area_gdf) 
                        gisele_lv_gdf = sjoin(gisele_lv_gdf, area_gdf, how="left").dropna()
                        
                        folium.features.Choropleth(geo_data=gisele_lv_gdf, name='lv', line_color='red', line_weight=3).add_to(feature_group_gisele_lv)
                        
                        info_lv = list(gisele_lv_gdf.columns)
                        info_lv.remove('geometry')
                    
                        style = {'fillColor': '#00000000', 'color': '#00000000'}
                        folium.GeoJson(gisele_lv_gdf.to_crs(4326).to_json(), name='_info', style_function=lambda x:style,
                                        tooltip=folium.features.GeoJsonTooltip(fields = info_lv)).add_to(feature_group_gisele_lv)                       


                        
                        # GRID CONNECTION
                        gisele_connections_gdf = gpd.read_file(os.path.join(gisele_output_path, 'MILP_processed', 'output_connections', 'output_connections.shp'), crs=crs) 
                        #gisele_connections_gdf = gisele_connections_gdf.set_crs(crs)
                        
                        #gisele_connections_gdf = sjoin(gisele_connections_gdf, area_gdf, how="left").dropna()
                        
                        folium.features.Choropleth(geo_data=gisele_connections_gdf, name='connections', line_color='orange', line_weight=4).add_to(feature_group_gisele_grid_connections)
                                        
                        style = {'fillColor': '#00000000', 'color': '#00000000'}
                        folium.GeoJson(gisele_connections_gdf.to_crs(4326).to_json(), name='_info', style_function=lambda x:style,
                                        tooltip=folium.features.GeoJsonTooltip(fields = list(gisele_connections_gdf.columns[:-1]))).add_to(feature_group_gisele_grid_connections)                       


                        feature_group_gisele_grid_connections.add_to(m)
                        feature_group_gisele_mv.add_to(m)
                        feature_group_gisele_lv.add_to(m)
                        feature_group_gisele_users.add_to(m)
                        feature_group_gisele_subs.add_to(m)
                        

                    
                    
                feature_group_1 = folium.FeatureGroup(name=select, show=True)
                feature_group_2 = folium.FeatureGroup(name='Community Boundaries', show=True)
                
                    
               
                #polygon_gdf = gpd.read_file(os.path.join(run_directory, 'Output', 'Clusters', 
                #                             'Communities', str(renewvia_rev_dict.get(select)), '4326.shp'))
                
                polygon_gdf = gpd.read_file(os.path.join(community_path, '4326.shp'))
                folium.GeoJson(polygon_gdf.geometry.to_json(), name='community boundaries').add_to(feature_group_2)
                
                feature_group = folium.FeatureGroup(name='Clusters Info', show=False)
                
                feature_group_2.add_to(m)
                feature_group_1.add_to(m)
                
                feature_group.add_to(m)
                
                for index, row in file_gdf[file_gdf.ID == select].iterrows(): # qui
                    df_ = pd.DataFrame(file_gdf.drop(columns=['geometry','polygons','centroid']))
                    df_ = df_[df_.index == select]
                                           
                    text = df_.to_html()
                
                    iframe = folium.IFrame(text, width=500, height=350)
                
                    popup = folium.Popup(iframe, max_width=500)
                
                    x = row.geometry.x
                    y = row.geometry.y
                
                    marker = folium.Marker([y, x], popup=popup, icon=folium.Icon(color='blue', icon='hospital-o', prefix='fa')).add_to(feature_group)
                
                
                # add marker for Liberty Bell
                tooltip = select
                folium.Marker(
                    [y, x], popup=select, tooltip=tooltip
                ).add_to(feature_group_1)
                
                if grid:
                    feature_group_a = folium.FeatureGroup(name='Grid Path')
                    feature_group_b = folium.FeatureGroup(name='Grid Info')
                    
                    
                    status_col_name = [x for x in grid_gdf.columns if
                                       any(ext in x for ext in ['status', 'Status', 'STATUS'])]
                    
                    if len(status_col_name) >0:
                        status_col_name = status_col_name[0]
                    else:
                        status_col_name = 'no_status_column'
                
                    voltage_col_name = [x for x in grid_gdf.columns if any(ext in x for ext in ['volt', 'Volt', 'VOLT'])]
                
                    if len(voltage_col_name) > 0:
                        voltage_col_name = voltage_col_name[0]
                
                    main_attribute = status_col_name
                    if main_attribute not in grid_gdf.columns:
                        main_attribute = voltage_col_name
                            
                    attribute_list = grid_gdf[main_attribute].unique()
                    # color_list = [style1, style2,style3, style4]
                    color_list = ['green', 'red', 'yellow', 'blue', 'black', 'orange'][:len(attribute_list)]
                    
                    for index, row in grid_gdf.iterrows():
                        properties = color_list[attribute_list.tolist().index(row[main_attribute])]
                        print(index, row[main_attribute], properties, '\n_______')
                        file = grid_gdf.iloc[[index]].to_json()
                        folium.features.Choropleth(geo_data=file, name=index, line_color=properties, line_weight=3).add_to(feature_group_a)
                    
                    style = {'fillColor': '#00000000', 'color': '#00000000'}
                    folium.GeoJson(grid_gdf.to_json(), name='_info', style_function=lambda x:style,
                                   tooltip=folium.features.GeoJsonTooltip(fields = list(grid_gdf.columns[:-1]))).add_to(feature_group_b)
                    

                    if 'substations.shp' in os.listdir(os.path.join(country_level_db_path, country[1:-1], 'Substations')):
                        feature_group_substations = folium.FeatureGroup(name='Existing Substations')
                        
                            
                        def color_producer_existing_subs(val):
                            if val > 1000000:
                                return "darkred"
                            else:
                                return "orange"
                            
                        substations_gdf = gpd.read_file(os.path.join(country_level_db_path, country[1:-1], 'Substations', 'substations.shp'))

    
                        substations_gdf['lat'] = substations_gdf.to_crs(4326).geometry.y
                        substations_gdf['long'] = substations_gdf.to_crs(4326).geometry.x   
                        
                        for i in range(0,len(substations_gdf)):
                            Circle(
                                location=[substations_gdf.iloc[i]['lat'], substations_gdf.iloc[i]['long']],
                                radius=100,
                                tooltip = substations_gdf.iloc[[i]].T.to_html(),
                                color=color_producer_existing_subs(substations_gdf.iloc[i]["lat"])).add_to(feature_group_substations)
                        
                        feature_group_substations.add_to(m)
                        
                        
                    feature_group_a.add_to(m)
                    feature_group_b.add_to(m)
                    
                        
            
                #raster_list = [x for x in os.listdir(community_path) if '.tif' in x] 
                if rasters_on:
                    for file in raster_list_2d:
                        print('----' + file)
                        file_path = os.path.join(community_path, file)
        
                        if 'tif' in file:      
                            data2 = xr.open_rasterio(file_path)
                            if len(data2.nodatavals) == 100:
                                no_data = float(data2.nodatavals)
                            else:
                                no_data = float(data2.nodatavals[0])
                            # print('no data: ' + str(no_data))
                            #data = data2[0].where(xr.DataArray(data2[0].values >= 0,dims=["y", "x"]), drop=True)
                            data = data2[0].where(xr.DataArray(data2[0].values != no_data,dims=["y", "x"]), drop=True)  
                            data.values[data.values < 0] = np.nan
                                               
                            if data.size > 0:
                                lon, lat = np.meshgrid(data.x.values.astype(np.float64), data.y.values.astype(np.float64))
                                source_extent = [lat.min(), lon.min(), lat.max(), lon.max()]
                                
                                data = np.array(data)
                                #data = np.asarray(data)
                                #data[data < 0] = np.nan()
                                
                                normed_data = (data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data))
                                cm = plt.cm.get_cmap('viridis')
                                colored_data = cm(normed_data)
                
                                folium.raster_layers.ImageOverlay(colored_data,
                                                                  [[lat.min(), lon.min()], [lat.max(), lon.max()]],
                                                                  #colormap=cm.viridis,
                                                                  opacity=0.5, name = file.split('.')[0], show=False).add_to(m)                      
                            
        
                

                
                        
                folium.plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=None,
                                    edit_options=None).add_to(m)
                folium.plugins.Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen',
                                          force_separate_button=False).add_to(m)
                folium.plugins.MeasureControl(position='bottomleft', primary_length_unit='meters', secondary_length_unit='miles',
                                              primary_area_unit='sqmeters', secondary_area_unit='acres').add_to(m)
                folium.LayerControl(position='bottomleft').add_to(m)
                folium_static(m)
                m.save('map_for_cluster_137.html')
            
            single_cluster_2d_mapping()

    # GISELE SECTION
    area_gdf = gpd.read_file(os.path.join(community_path, '_commun_{0}.shp'.format(select))).to_crs(crs)
    
    row1_1_1, row1_1_2 = st.columns((1,3))
    row1_2_1, row1_2_2 = st.columns((2,2))
    
    if int(info_gdf.night_lights)  == 0:
        key = 13
        if st.sidebar.checkbox("Off-grid Solution", False, key=key):
            
            
            
            with row1_1_1:
                '# GISELE : \n # Power System'
                ###  FINANCIAL ANALYSIS
                gisele_input_path = os.path.join(run_directory, 'Output', 'GISELE', 'Input')
                community_boundaries_gdf = gpd.read_file(os.path.join(gisele_input_path, 'Communities_boundaries', 'Communities_boundaries.shp'), crs=crs) 
                community_boundaries_gdf['aleks_ID'] = ['C{0}'.format(x) for x in list(community_boundaries_gdf.cluster_ID)]
                
                
                ID_dict = pd.Series(community_boundaries_gdf.geometry.values, index=community_boundaries_gdf.aleks_ID.values).to_dict()
                
                intermediate_path = os.path.join(run_directory, 'Output', 'GISELE', 'Intermediate')
                
                overall_microgrid_df = pd.read_csv(os.path.join(intermediate_path, 'Microgrid', 'microgrids.csv'), delimiter=';')
                overall_microgrid_df['geometry'] = overall_microgrid_df['Cluster'].map(ID_dict)
                overall_microgrid_gdf = gpd.GeoDataFrame(overall_microgrid_df, geometry='geometry', crs=crs)
                
                microgrid_gdf = sjoin(overall_microgrid_gdf, area_gdf, how="left").dropna()
                
                microgrid_df_trans = pd.DataFrame(microgrid_gdf).drop(columns=['geometry', 'index_right', 'FID'])
                microgrid_df = microgrid_df_trans.T
                microgrid_df[microgrid_df.columns[0]] = [str(x) for x in microgrid_df[microgrid_df.columns[0]]]
                st.dataframe(microgrid_df)
    
            with row1_1_2:
                '# GISELE : \n # Internal Grid'
    
                 
                output_path = os.path.join(run_directory, 'Output', 'GISELE', 'Output')
                
                overall_lv_df = pd.read_csv(os.path.join(output_path, 'LV_resume.csv'), index_col=0)
                overall_lv_df['aleks_ID'] = ['C{0}'.format(int(x)) for x in list(overall_lv_df.Cluster)]
                overall_lv_df['geometry'] = overall_lv_df['aleks_ID'].map(ID_dict)
                overall_lv_gdf = gpd.GeoDataFrame(overall_lv_df, geometry='geometry', crs=crs)
                
                lv_gdf = sjoin(overall_lv_gdf, area_gdf, how="left").dropna()
                lv_gdf['Cluster'] = lv_gdf['aleks_ID']
                lv_df = pd.DataFrame(lv_gdf).drop(columns=['geometry', 'index_right', 'FID', 'aleks_ID'])
                lv_df[lv_df.columns[0]] = [str(x) for x in lv_df[lv_df.columns[0]]]
                
                st.dataframe(lv_df)
            
            with row1_2_1:
                '# System Total Cost [kEUR]'
                cost_columns_off_grid = [x for x in microgrid_gdf.columns if 'Cost' in x and 'Total' not in x]
                cost_columns_lv = [x for x in lv_gdf.columns if 'Cost' in x and 'Total' not in x]
                
                off_grid_costs_df = microgrid_df_trans[cost_columns_off_grid]
                off_grid_costs_df['name'] = str(select)
                
                           
    # =============================================================================
    #             for sub in lv_df.Sub_cluster.drop_duplicates():
    #                 st.dataframe(lv_df[lv_df.Sub_cluster == sub])
    # =============================================================================
    
                
                
                off_grid_costs_df = off_grid_costs_df.set_index('name')
                off_grid_costs_df['Grid Cost [kEUR]'] = lv_df['Grid Cost [euro]'].sum()/1000
                off_grid_costs_df['Substations Cost [kEUR]'] = lv_df['Cost[euro]'].sum()/1000
                
                costs_bar_graph = px.bar(
                        off_grid_costs_df
                        )
                st.plotly_chart(costs_bar_graph)
            
            with row1_2_2:
                '# System Total Cost [kEUR]'
                
                off_grid_costs_df_trans = off_grid_costs_df.T
                costs_pie_graph = px.pie(off_grid_costs_df_trans, values=list(off_grid_costs_df_trans[off_grid_costs_df_trans.columns[0]]), 
                       names=list(off_grid_costs_df_trans.index.astype(str)),
                       hole=0.6)
                st.plotly_chart(costs_pie_graph)
                

            
    
    
    
        
        
        
        
        
        
    
    
    
    
    # Analysis section
    key = 14
    analysis = st.sidebar.selectbox('------- ANALYSIS -------',['ON', 'OFF'], index=0)
    if analysis == 'ON':
        
        def render_slider(slider_year, name, min_year, max_year, animation_speed, year_slider, key):
            key_slider = random.random() if animation_speed else None

            slider_year = year_slider.slider(name,
                               min_year,
                               max_year,
                               value=slider_year,
                               key=key_slider
                                            )

            return slider_year

        def render_map(slider_year, data_df, deck_map):
            data_in_year = data_df[np.array(data_df.year == slider_year)]
                        
            deck_map.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/satellite-streets-v11",
                    initial_view_state=pdk.ViewState(
                        latitude=data_in_year.lat.mean(),
                        longitude=data_in_year.lon.mean(),
                        zoom=13,
                        pitch=50,
                    ),
                    layers=[
                        pdk.Layer(
                            "ColumnLayer",
                            data=data_in_year.drop(columns=['point', 'year']),
                            disk_resolution=12,
                            radius=20,
                            elevation_scale=10,
                            get_position=["lon", "lat"],
                            get_color="[40, value / 5000 * 255, 40, 150]",
                            get_elevation="[value]"
                        ),
                    ],
            )   
            )
                        
       
        
        
        def plot_map(trend_data, name, year_pop_slider, file_list, year_end_slider, key):
            row2_1, row2_2= st.columns((2,2))
            key += 1
            if st.sidebar.checkbox(name, False, key=key):
                year_pop_slider = year_pop_slider
                
                with row2_2:            
                    
                    st.subheader("Animation")
                    animations_pop = {"None": None, "Slow": 0.4, "Medium": 0.2, "Fast": 0.05}
                    key += 1
                    animate_pop = st.selectbox("", options=list(animations_pop.keys()), index=0, key=key)
                    
                    
                    name
                    st.line_chart(trend_data, width = 1300,height=350)
                    
                with row2_1:
                    "Visualization %s in %s" % (name, str(select))
                    year_slider_pop = st.empty()
                    deck_map_pop = st.empty()
                    # Setup presentation widgets
                    
                    animation_speed_pop = animations_pop[animate_pop]
                            
                
                
                year_pop = year_pop_slider - 1
                i_pop = 0
                
                points_list_pop = []
                year_list_pop = []
                lat_list_pop = []
                long_list_pop = []
                value_list_pop = []
                
                for file_pop in file_list:
                    year_pop += 1
                    i_pop += 1
                    
                    file_path_pop = os.path.join(community_path, file_pop)
                    data2_pop = xr.open_rasterio(file_path_pop)
                
                    if len(data2_pop.nodatavals) == 100:
                        no_data_pop = float(data2_pop.nodatavals)
                    else:
                        no_data_pop = float(data2_pop.nodatavals[0])
                        
                    data_pop = data2_pop[0].where(xr.DataArray(data2_pop[0].values != no_data_pop,dims=["y", "x"]), drop=True)  
                    data_pop.values[data_pop.values < 0] = 0
                    
                    
                    values_pop = [item for sublist in data_pop.values for item in sublist]
                    lats_pop = list(data_pop.y.values) * len(data_pop.x.values)
                    longs_pop = list(data_pop.x.values) * len(data_pop.y.values)
                    
                    points_list_pop.append(range(0, len(values_pop)))
                    year_list_pop.append(np.ones(len(values_pop))*int(year_pop))
                    lat_list_pop.append(lats_pop)
                    long_list_pop.append(longs_pop)
                    value_list_pop.append(values_pop)
                
                points_list_pop = [item for sublist in points_list_pop for item in sublist]
                year_list_pop = [item for sublist in year_list_pop for item in sublist]
                lat_list_pop = [item for sublist in lat_list_pop for item in sublist]
                long_list_pop = [item for sublist in long_list_pop for item in sublist]
                value_list_pop = [item for sublist in value_list_pop for item in sublist]
                
                year_list_pop = [ int(x) for x in year_list_pop ]
                
                pop_df = pd.DataFrame({
                    'point': points_list_pop,
                    'lat': lat_list_pop,
                    'lon': long_list_pop,
                    'year': year_list_pop,
                    'value': value_list_pop
                    })
                    
                pop_df = pop_df[pd.to_numeric(pop_df['value'], errors='coerce').notnull()]
                pop_df = pop_df[pop_df['value'] != 0]
                
                if animation_speed_pop:
                    for year_p in range(year_pop_slider, year_end_slider+1):
                        time.sleep(animation_speed_pop)
                        with row2_1:
                            render_slider(year_p, "Select Year", year_pop_slider, year_end_slider, animation_speed_pop, year_slider_pop, key)
                            render_map(year_p, pop_df, deck_map_pop)
                else:
                    with row2_1:
                        year_pop_slider = render_slider(year_end_slider, "Select Year", year_pop_slider, year_end_slider, animation_speed_pop, year_slider_pop, key)
                        render_map(year_pop_slider, pop_df, deck_map_pop)
            
            return key 
        
        key = plot_map(b, "Energy Access Trend", 1992, lights_list, 2018, key)
        key = plot_map(a, "Population Trend", 2000, pop_list, 2020, key)
                     
        # Giving a sense to the crop results (names)
    
        def get_total_dataframe(dataset):
            crops = list(dataset)
            # crops.remove('codes')
            crops_productions =  [dataset[x][select] for x in crops]
            total_dataframe = pd.DataFrame({
            'Crops': crops,
            'Production': tuple(crops_productions)})
            return total_dataframe
        
        
        key = 19    
        if st.sidebar.checkbox("Terrain Analysis", True, key=key):
            row4_1, row4_2 = st.columns((2,2))
            
            columns_names = [x.split('_')[3] for x in list(crops_data.columns)]
            column_dict = pd.Series(columns_names,index=crops_data.columns).to_dict()
            crops_data = crops_data.rename(columns=column_dict)
            
            crops_names = pd.read_csv(os.path.join('Settings', 'crops_list.csv'), delimiter=';')
            crops_names['field_and_partial_file_name'] = crops_names['field_and_partial_file_name'].str.upper()
            crops_dict = pd.Series(crops_names.full_name.values,index=crops_names.field_and_partial_file_name).to_dict()
        
            crops_data = crops_data.rename(columns=crops_dict)
            
            # crops visualization
            crops_data['names'] = crops_data.index
            #crops_data['names'] = crops_data.index.map(renewvia_dict)
            #crops_names = list(crops_data.columns)[:-1]
            crops_data = crops_data.sort_values('names')
            crops_data = crops_data.set_index('names')
            
            select_crops = crops_names
            #get the state selected in the selectbox
            selected_community = crops_data[crops_data.index == select] 
            
            
            
            state_total = get_total_dataframe(selected_community)
            state_total['Production'] = [int(x) for x in state_total['Production']]
            state_total = state_total[state_total.Production > 0]
            state_total = state_total.sort_values('Production', ascending=False)
            
            
            landcover_types = [
                        'Trees_cover_areas',
                        'Shrubs_cover_areas',
                        'Grassland',
                        'Cropland',
                        'Vegetation_aquatic_or_regularly_flooded',
                        'Lichen_Mosses_/_Sparse_vegetation',
                        'Bare_areas',
                        'Built_up_areas',
                        'Snow_and/or_Ice',
                        'Open_water']
            
            community_data = file_gdf[file_gdf.ID == select] # qui
            landcover_values = []
            for types in landcover_types:
                landcover_values.append(float(community_data[types]))
            landcovers_df = pd.DataFrame({
                'land_cover_type' : landcover_types,
                'percentage' : landcover_values})
            landcovers_df = landcovers_df[landcovers_df['percentage'] > 0]
            
            key = 20
            with row4_1:
                labels = landcovers_df['land_cover_type']
                sizes = landcovers_df['percentage']

                fig3 = px.pie(landcovers_df, values=landcovers_df.percentage, names=landcovers_df.land_cover_type)
                fig3.update_layout(title="<b>Land Cover Types [%] </b>")
                st.plotly_chart(fig3)
                
            
            with row4_2:
                if not state_total.empty:
                    state_total_graph = px.bar(
                    state_total, 
                    x='Crops',
                    y='Production',
                    labels={'Number of cases':'Number of cases in %s' % (select)},
                    color='Crops')
                    state_total_graph.update_layout(title="<b>Crops Production [tons]</b>")
                    st.plotly_chart(state_total_graph)
                else:
                    st.write(state_total)
                    
            
        key = 21    
        if st.sidebar.checkbox("General Analysis", False, key=key):
                        
            key = 22
            if st.sidebar.checkbox("Single-Dimension Analysis", True, key=key):
                row5_1, row5_2 = st.columns((2,2))
                row6_1, row6_2 = st.columns((2,2))
                
                def plot_bars(n):
                    name_df = file_gdf.copy()
                    name_df['Name'] = ['Community_{0}'.format(x) for x in file_gdf['Community']]
                    
                    df = name_df.sort_values(single_dimensions[n], ascending=False)
                    
                    rank = list(df['Community']).index(select)
                    "%s : %s, rank: %s over %s" % (single_dimensions[n], round(list(df[single_dimensions[n]])[rank],2), rank+1, len(df))
                    
                    stats = df[single_dimensions[n]].describe()
                    stats = pd.DataFrame(stats).transpose()
                    st.write(stats)
                    
                   
                    graph_1 = px.bar(df,
                                     x='Name',
                                     y=single_dimensions[n],
                                     color = ['blue' if x != rank else 'red' for x in range(0,len(df))],
                                     title=single_dimensions[n])
                    
                    st.plotly_chart(graph_1)
                
                
                st.set_option('deprecation.showPyplotGlobalUse', False)
                single_dimensions = st.sidebar.multiselect('Select up to 4 parameters to analyze', file_gdf.select_dtypes(include=numerics).columns,
                                                            default=['area', 'population_worldpop', 'average_wealth_index', 'lights_build'])
                #st.write(file_gdf.loc[select][comparison_dimensions_hist])
                
                #file_gdf
                
                with row5_1:
                    if len(single_dimensions) > 0:
                        plot_bars(0)
                                    
                with row5_2:
                    if len(single_dimensions) > 1:
                        plot_bars(1)

                with row6_1:
                    if len(single_dimensions) > 2:
                        plot_bars(2)

                with row6_2:
                    if len(single_dimensions) > 3:
                        plot_bars(3)

                
        elif which_mode == 'Compare Clusters': 
            st.write('Functionality still to be implemented')
    
    # 3D MAPPING
    key = 23
    mapping_3d = st.sidebar.selectbox('------ 3D MAPPING ------',['ON', 'OFF'], index=1)
    if mapping_3d == 'ON':
        "# %s 3D MAP" % (select)
        key = 24        
        raster_list_3d = [x.split('.')[0] for x in raster_list_3d]
        raster_name = st.selectbox('Select the Data to Plot',raster_list_3d, index = 1)
        
        #raster_name = 'Harmonized_DN_NTL_2018_simVIIRS'
        
        raster_path = os.path.join(community_path, raster_name)
        csv_path = os.path.join(dashboarding_path, raster_name)
        #radius, nodata = raster_to_csv(raster_path, csv_path)
        
        print('Points exported')
        
    
    # =============================================================================
    #     buildings_path = os.path.join(community_path, 'clipped_buildings.csv')
    #     data = pd.read_csv(buildings_path, delimiter = ' ')
    #     data = data[data.Z > 0]
    # =============================================================================
        
    
# =============================================================================
#         data = pd.read_csv('{}.csv'.format(csv_path), delimiter = ' ')
#         #data = data[data.Z > 0]
#         data = data[data.Z != nodata]
#         
#         html_text = '<b>{0}_class:</b>'.format(raster_name) +' {elevationValue}'
#         elevation_scale = min([max(data.Z),15])
#     
#         
#         def map(data, lat, lon, zoom):
#             st.write(pdk.Deck(
#                 map_style="mapbox://styles/mapbox/satellite-streets-v11",
#                 
#                 initial_view_state={
#                     "latitude": lat,
#                     "longitude": lon,
#                     "zoom": zoom,
#                     "pitch": 50
#                 },
#                 
#                 tooltip={
#                     'html': html_text,
#                     "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"
#                     }
#                 },
#                 layers=[
#                     pdk.Layer(
#                         "HexagonLayer", #['HexagonLayer', 'GridLayer']
#                         data=data,
#                         opacity=0.3,
#                         get_position=["X", "Y"],
#                         #get_elevation="Z",
#                         auto_highlight=True,
#                         radius= radius, #['cellSize', 'get_radius', 'radius']
#                         elevation_scale=elevation_scale,
#                         elevation_range=[0, max(data.Z)],
#                         pickable=True,
#                         extruded=True
#                     ),
#                 ]
#             ))
#     
#         map(data, data.Y.mean(), data.X.mean(), 14)
#     
#     
#     
# =============================================================================
