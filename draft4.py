import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events
import re

from itertools import cycle

def main():

    ################################################
    # select country/operator and draw map         #
    ################################################
    st.title('Oil Fields Map')

    df = pd.read_csv("Global-Oil-and-Gas-Extraction-Tracker-July-2023.csv")

    df[['Country', 'Operator', 'Owner']] = df[['Country', 'Operator', 'Owner']].astype(str)

    def btn_callbk(menu):

        countries = sorted(df['Country'].unique().tolist())
        operators = df['Operator'].unique().tolist()
        operators = sorted(operators, key=lambda x: (x!='nan', str(x)))

        country_counts = {country: df[df['Country'] == country].shape[0] for country in countries}
        operator_counts = {operator: df[df['Operator'] == operator].shape[0] for operator in operators}

        if menu == "country":
            st.session_state.country_selection_disabled_flag = not st.session_state.country_selection_disabled_flag

            if st.session_state.country_selection_disabled_flag:
                st.session_state.selected_countries = [f"{country} ({country_counts[country]})" for country in countries]
            else:
                st.session_state.selected_countries = []
            
            st.session_state.country_menu = []

        if menu == "operator":
            st.session_state.operator_selection_disabled_flag = not st.session_state.operator_selection_disabled_flag

            if st.session_state.operator_selection_disabled_flag:
                st.session_state.selected_operators = [f"{operator} ({operator_counts[operator]})" for operator in operators]
            else:
                st.session_state.selected_operators = []
            
            st.session_state.operator_menu = []

    def get_options(df,col):
        output_df = df
        countries = sorted(df['Country'].unique().tolist())
        operators = df['Operator'].unique().tolist()
        operators = sorted(operators, key=lambda x: (x!='nan', str(x)))

        country_counts = {country: df[df['Country'] == country].shape[0] for country in countries}
        operator_counts = {operator: df[df['Operator'] == operator].shape[0] for operator in operators}
        selected_countries = [re.sub(r'\s*\(\d+\)', '', country) for country in st.session_state.selected_countries]
        selected_operators = [re.sub(r'\s*\(\d+\)', '', operator) for operator in st.session_state.selected_operators]

        # dataframe is filtered by country and by operators
        if selected_countries:
            countries_df = output_df[output_df['Country'].isin(selected_countries)]
        else:
            countries_df = output_df

        if selected_operators:
            operators_df = output_df[output_df['Operator'].isin(selected_operators)]
        else:
            operators_df = output_df

        output_df = pd.concat([countries_df, operators_df]).drop_duplicates() 

        if col == "country":
            if st.session_state.selected_operators:
                selected_operators = [re.sub(r'\s*\(\d+\)', '', operator) for operator in st.session_state.selected_operators]
                if st.session_state.operator_country == "AND":
                    list_by_operators = [x for _, x in operators_df.groupby(by=["Operator"])]
                    list_ctr = []
                    for c in countries:
                        belong = True
                        for i in list_by_operators:
                            if c not in i['Country'].tolist():
                                belong = False
                                break
                        if belong:
                            list_ctr.append(c)

                    output_df = output_df[output_df['Country'].isin(list_ctr)]
                elif st.session_state.operator_country == "OR":
                    output_df = df[df['Operator'].isin(selected_operators)]
            output_df = sorted(output_df['Country'].unique().tolist())
            output_df = [f"{country} ({country_counts[country]})" for country in output_df]

            return output_df
          
        if col == "operator":
            if st.session_state.selected_countries:
                selected_countries = [re.sub(r'\s*\(\d+\)', '', country) for country in st.session_state.selected_countries]
                if st.session_state.radio_country == "AND":
                    list_by_countries = [x for _, x in countries_df.groupby(by=["Country"])]
                    list_op = []
                    for op in operators:
                        belong = True
                        for i in list_by_countries:
                            if op not in i['Operator'].tolist():
                                belong = False
                                break
                        if belong:
                            list_op.append(op)
                    output_df = output_df[output_df['Operator'].isin(list_op)]
                elif st.session_state.radio_country == "OR":
                    output_df = df[df['Country'].isin(selected_countries)]

     
            output_df = output_df['Operator'].unique().tolist()
            output_df = sorted(output_df, key=lambda x: (x!='nan', str(x)))
            output_df = [f"{operator} ({operator_counts[operator]})" for operator in output_df]

            return output_df


    def filter_callbk(menu):
        st.session_state.selected_countries = st.session_state.country_menu
        st.session_state.selected_operators = st.session_state.operator_menu 
        
        # it deletes the selection from the other multiselect menu, so below two lines are a workaround but necessary to keep persistence
        st.session_state.country_menu = st.session_state.selected_countries
        st.session_state.operator_menu = st.session_state.selected_operators
        
        if menu == "country":
            st.session_state.operator_options = get_options(df,"operator")
        
        if menu == "operator":
            st.session_state.country_options = get_options(df,"country")



    countries = sorted(df['Country'].unique().tolist())
    operators = df['Operator'].unique().tolist()
    operators = sorted(operators, key=lambda x: (x!='nan', str(x)))

    country_counts = {country: df[df['Country'] == country].shape[0] for country in countries}
    operator_counts = {operator: df[df['Operator'] == operator].shape[0] for operator in operators}

    # initialization flags for country and operator selection menu
    if "first_run_flag" not in st.session_state:    
        st.session_state.country_selection_disabled_flag = False
        st.session_state.operator_selection_disabled_flag = False

        st.session_state.selected_countries = []
        st.session_state.selected_operators =  []

        st.session_state.country_options = [f"{country} ({country_counts[country]})" for country in countries]
        st.session_state.operator_options = [f"{operator} ({operator_counts[operator]})" for operator in operators]

        st.session_state.first_run_flag = True


    menu1,radio1,select_btn1 = st.columns([3,1,1])
    menu2,radio2,select_btn2 = st.columns([3,1,1])
    
    with menu1:
        container_country = st.container()
        container_country.multiselect("Select Countries:",options=st.session_state.country_options,disabled=st.session_state.country_selection_disabled_flag,on_change=lambda *args: filter_callbk(*args, menu="country"),key="country_menu")
    with radio1:
        st.radio(label="",options=["AND", "OR"],key="radio_country",index=1,on_change=lambda *args: filter_callbk(*args, menu="country"),disabled=st.session_state.country_selection_disabled_flag)
    with select_btn1:
        st.markdown("#") # just to add some extra vertical space
        st.checkbox("All Countries",on_change=lambda *args: btn_callbk(*args, menu="country"))

    with menu2:
        container_operator = st.container()
        container_operator.multiselect("Select Operators:",options=st.session_state.operator_options,disabled=st.session_state.operator_selection_disabled_flag,on_change=lambda *args: filter_callbk(*args, menu="operator"),key="operator_menu")
    with radio2:
        st.radio(label="",options=["AND", "OR"],key="operator_country",index=1,on_change=lambda *args: filter_callbk(*args, menu="operator"),disabled=st.session_state.operator_selection_disabled_flag)
    with select_btn2:
        st.markdown("#") # just to add some extra vertical space
        st.checkbox("All Operators",on_change=lambda *args: btn_callbk(*args, menu="operator"))
    



    # container_country = st.container()
    # st.radio(label="",options=["AND", "OR"],key="radio_country",index=1,on_change=lambda *args: filter_callbk(*args, menu="country"),disabled=st.session_state.country_selection_disabled_flag)
    # st.checkbox("All Countries (ignore this filter)",on_change=lambda *args: btn_callbk(*args, menu="country"))

    # container_operator = st.container()
    # st.radio(label="",options=["AND", "OR"],key="operator_country",index=1,on_change=lambda *args: filter_callbk(*args, menu="operator"),disabled=st.session_state.operator_selection_disabled_flag)
    # st.checkbox("All Operators (ignore this filter)",on_change=lambda *args: btn_callbk(*args, menu="operator"))
    
    # container_country.multiselect("Select Countries:",options=st.session_state.country_options,disabled=st.session_state.country_selection_disabled_flag,on_change=lambda *args: filter_callbk(*args, menu="country"),key="country_menu")
    # container_operator.multiselect("Select Operators:",options=st.session_state.operator_options,disabled=st.session_state.operator_selection_disabled_flag,on_change=lambda *args: filter_callbk(*args, menu="operator"),key="operator_menu")

    selected_countries = st.session_state.selected_countries
    selected_operators = st.session_state.selected_operators

    if len(selected_operators)>0:
        selected_operators = [re.sub(r'\s*\(\d+\)', '', operator) for operator in selected_operators]
        operators_df = df[df['Operator'].isin(selected_operators)]
        countries = sorted(operators_df['Country'].unique().tolist())
        country_counts = {country: operators_df[operators_df['Country'] == country].shape[0] for country in countries}

    if len(selected_countries)>0:
        selected_countries = [re.sub(r'\s*\(\d+\)', '', country) for country in selected_countries]
        countries_df = df[df['Country'].isin(selected_countries)]
        operators = countries_df['Operator'].unique().tolist()
        operators = sorted(operators, key=lambda x: (x!='nan', str(x)))
        operator_counts = {operator: countries_df[countries_df['Operator'] == operator].shape[0] for operator in operators}  

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

    color_option = st.selectbox(
    "Color points by group:",
    ("Same color", "Country", "Fuel type"))

    fig = px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', hover_name='Unit name',
                            zoom=zoom_level, center={'lat': center_lat, 'lon': center_lon},
                            # hover_data=['Unit ID', 'Country', 'Operator', 'Owner'])
                            color = None if color_option == "Same color" or not filtered_df.stack().tolist() else color_option,
                            color_discrete_sequence= px.colors.qualitative.Dark2,
                            hover_data=['Country', 'Operator'])
    fig.update_layout(coloraxis_showscale=False)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig.add_trace(px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', hover_name='Unit name',
    #                         hover_data=['Unit ID', 'Country', 'Operator', 'Owner'], 
    #                         color_discrete_sequence=['blue']).data[0])

    # st.plotly_chart(fig)

    #######################################################
    # select point on map and proceed with pressure etc   #
    #######################################################

    selected_point = plotly_events(fig) # last point selected on the map
    
    # initiate a session state list to store all points we selected from the map
    if 'point_index_list' not in st.session_state:
        st.session_state.point_index_list = []


    if selected_point: # if we have selected a point: 
        if selected_point[0]["pointIndex"] not in st.session_state.point_index_list:
            # if it's not in our session state list then we select it
            st.session_state.point_index_list.append(selected_point[0]["pointIndex"]) 
        # else:
        #     # if it's in our session state list then we deselect it
        #     st.session_state.point_index_list.remove(selected_point[0]["pointIndex"])
        # if len(st.session_state.point_index_list) > 0:
        #     if st.button('Clear Selection'):
        #         st.session_state.point_index_list.clear()
        #         selected_point.clear()



    ##########################################################
    #for each session state, selected_point does not reset itself, it's always non-empty so everytime 
    #we press a button, or change the slider bar, the session state reset and we go into the if statement 118-124
    #again, which results in removing the last selected point
    ##########################################################
    
    col1,_,col2 = st.columns([2,1,2])

    with col1:    
        btn_proceed = st.button('Proceed')

    with col2:    
        btn_clear = st.button('Clear Selection')

    if btn_proceed: # proceed button
        st.session_state.page = "PressureIncreasePage"

    if btn_clear:
        st.session_state.point_index_list.clear()
        selected_point.clear()

    print(selected_point)
    
    # print result
    n = len(st.session_state.point_index_list)
    for index in st.session_state.point_index_list:
        st.write(index, filtered_df.astype(str).iloc[index])
    st.write("Number of chosen points:",n)

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

    