import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events
import re

def main():

    ################################################
    # select country/operator and draw map         #
    ################################################
    st.title('Oil Fields Map')

    df = pd.read_csv("Global-Oil-and-Gas-Extraction-Tracker-July-2023.csv")

    df[['Country', 'Operator', 'Owner']] = df[['Country', 'Operator', 'Owner']].astype(str)

    container_country = st.container()
    all_countries = st.checkbox("All Countries")

    container_operator = st.container()
    all_operators = st.checkbox("All Operators")

    countries = sorted(df['Country'].unique().tolist())
    operators = df['Operator'].unique().tolist()
    operators = sorted(operators, key=lambda x: (x!='nan', str(x)))

    country_counts = {country: df[df['Country'] == country].shape[0] for country in countries}
    operator_counts = {operator: df[df['Operator'] == operator].shape[0] for operator in operators}

    selected_operators=[]
    selected_countries=[]

    if all_countries:
        selected_countries = container_country.multiselect("Select Countries:",
        [f"{country} ({country_counts[country]})" for country in countries], 
        [f"{country} ({country_counts[country]})" for country in countries])
    else: 
        if len(selected_operators)>0:
            selected_operators = [re.sub(r'\s*\(\d+\)', '', operator) for operator in selected_operators]
            operators_df = df[df['Operator'].isin(selected_operators)]
            countries = sorted(operators_df['Country'].unique().tolist())
            country_counts = {country: operators_df[operators_df['Country'] == country].shape[0] for country in countries}
            selected_countries =  container_country.multiselect('Select Countries:', 
                [f"{country} ({country_counts[country]})" for country in countries])
        else:
            selected_countries =  container_country.multiselect('Select Countries:', 
                [f"{country} ({country_counts[country]})" for country in countries])

    if all_operators:
        selected_operators = container_operator.multiselect("Select Operators:",
            [f"{operator} ({operator_counts[operator]})" for operator in operators], 
            [f"{operator} ({operator_counts[operator]})" for operator in operators])
    else:    
        if len(selected_countries)>0:
            selected_countries = [re.sub(r'\s*\(\d+\)', '', country) for country in selected_countries]
            countries_df = df[df['Country'].isin(selected_countries)]
            operators = countries_df['Operator'].unique().tolist()
            operators = sorted(operators, key=lambda x: (x!='nan', str(x)))
            operator_counts = {operator: countries_df[countries_df['Operator'] == operator].shape[0] for operator in operators}
            selected_operators =  container_operator.multiselect('Select Operators', 
                [f"{operator} ({operator_counts[operator]})" for operator in operators])   
        else:   
            selected_operators =  container_operator.multiselect('Select Operators', 
                [f"{operator} ({operator_counts[operator]})" for operator in operators])       

    selected_countries = [re.sub(r'\s*\(\d+\)', '', country) for country in selected_countries]
    selected_operators = [re.sub(r'\s*\(\d+\)', '', operator) for operator in selected_operators]

    if selected_countries == []:
        filtered_df = df[(df['Operator'].isin(selected_operators))]
    elif selected_operators == []:
        filtered_df = df[(df['Country'].isin(selected_countries))]
    elif selected_countries!=[] and selected_operators!=[]:
        filtered_df = df[(df['Country'].isin(selected_countries)) & (df['Operator'].isin(selected_operators))]
    else:
        filtered_df = df

    st.dataframe(filtered_df)
    total = filtered_df.count()[0]
    unmarked = filtered_df['Latitude'].isna().sum()
    marked = total - unmarked 

    st.write("Total count:", total)   
    st.write("Marked locations:", marked)   
    st.write("Unknown locations:", unmarked)

    center_lat = filtered_df['Latitude'].mean()
    center_lon = filtered_df['Longitude'].mean()
    zoom_level = 2

    fig = px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', hover_name='Unit name',
                            zoom=zoom_level, center={'lat': center_lat, 'lon': center_lon},
                            hover_data=['Unit ID', 'Country', 'Operator', 'Owner'])

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig.add_trace(px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', hover_name='Unit name',
    #                         hover_data=['Unit ID', 'Country', 'Operator', 'Owner'], 
    #                         color_discrete_sequence=['blue']).data[0])

    # st.plotly_chart(fig)

    #######################################################
    # select point on map and proceed with pressure etc   #
    #######################################################

    selected_points = []
    selected_points = plotly_events(fig) # select points on the map
    
    # initiate a session state list to store all points we selected from the map
    if 'point_index_list' not in st.session_state:
        st.session_state.point_index_list = []

    print(selected_points)

    if selected_points: # if we have selected a point: 
        if selected_points[0]["pointIndex"] not in st.session_state.point_index_list:
            # if it's not in our session state list then we select it
            st.session_state.point_index_list.append(selected_points[0]["pointIndex"]) 
        else:
            # if it's in our session state list then we deselect it
            st.session_state.point_index_list.remove(selected_points[0]["pointIndex"])

    # print result
    n = len(st.session_state.point_index_list)
    st.write(st.session_state.point_index_list)
    st.write(n)

    ##########################################################
    #for each session state, selected_point does not reset itself, it's always non-empty so everytime 
    #we press a button, or change the slider bar, the session state reset and we go into the if statement 118-124
    #again, which results in removing the last selected point
    ##########################################################
    
    if st.button('Proceed'): # proceed button
        st.session_state.page = "PressureIncreasePage"  

    if 'page' not in st.session_state or st.session_state.page != "PressureIncreasePage":
        st.stop()   

    print(st.session_state)
    pressure_increase_page(n)
    

def pressure_increase_page(num):
    st.title("Pressure Increase at Wells and Locations on Map")
    pressures = []
    inj_types = []

    for i in range(num):
        st.write(f"Well {i+1}")
        pressure = st.slider("Increase of Pressure", min_value=0, max_value=100, value=0, key=f"slider{i+1}")
        injection_type = st.radio("Injection Type", ['CO2', 'Water', 'Steam'], index=0, key=f"radio{i+1}")
        pressures.append(pressure)
        inj_types.append(injection_type)

if __name__ == "__main__":
    main()

    