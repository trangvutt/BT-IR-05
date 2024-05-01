import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

df=pd.read_csv("Global-Oil-and-Gas-Extraction-Tracker-July-2023.csv")

#convert some columns into string type so they are easier to work
df[['Country', 'Operator', 'Owner']] = df[['Country', 'Operator', 'Owner']].astype(str)


# Get unique countries and operators from the dataframe
container_country = st.container()
all_countries = st.checkbox("All Countries")

container_operator = st.container()
all_operators = st.checkbox("All Operators")

countries = sorted(df['Country'].unique().tolist()) #sort countries in alphabetical order

operators = df['Operator'].unique().tolist()
operators = sorted(operators, key=lambda x: (x!='nan', str(x))) #sort operators in alphabetical order, but i want 'nan' operator to be on top of the list 

# Create Streamlit app
st.title('Oil Fields Map')

country_counts = {country: df[df['Country'] == country].shape[0] for country in countries}

# dropdown widgets for selecting country and operator with an option to select all countries or operators
if all_countries:
    selected_countries = container_country.multiselect("Select Countries:",
        [f"{country} ({country_counts[country]})" for country in countries], 
        [f"{country} ({country_counts[country]})" for country in countries])
else:
    selected_countries =  container_country.multiselect('Select Countries:', 
        [f"{country} ({country_counts[country]})" for country in countries])

operator_counts = {operator: df[df['Operator'] == operator].shape[0] for operator in operators}

if all_operators:
    selected_operators = container_operator.multiselect("Select Operators:",
        [f"{operator} ({operator_counts[operator]})" for operator in operators], 
        [f"{operator} ({operator_counts[operator]})" for operator in operators])
else:
    selected_operators =  container_operator.multiselect('Select Operators', 
        [f"{operator} ({operator_counts[operator]})" for operator in operators])
#source: https://discuss.streamlit.io/t/select-all-on-a-streamlit-multiselect/9799/2

selected_countries = [country.split(' (')[0] if ' (' in country else country for country in selected_countries]
selected_operators = [operator.split(' (')[0] if ' (' in operator else operator for operator in selected_operators]

# print(selected_countries)
# print(selected_operators)

total = df.count()[0]
unmarked = df['Latitude'].isna().sum()
marked = total - unmarked  

#filter the df based on chosen criterias
if selected_countries == []:
    filtered_df = df[(df['Operator'].isin(selected_operators))]
elif selected_operators == []:
    filtered_df = df[(df['Country'].isin(selected_countries))]
else:
    filtered_df = df[(df['Country'].isin(selected_countries)) & (df['Operator'].isin(selected_operators))]

# Plot map with points for each location
fig = px.scatter_mapbox(df, lat=df['Latitude'], lon=df['Longitude'], hover_name=df['Unit name'],
                        hover_data=['Unit ID', 'Country', 'Operator', 'Owner'],
                        zoom=5)

# Customize map layout
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

if filtered_df.shape[0] > 0:
    fig.add_trace(px.scatter_mapbox(filtered_df, lat=filtered_df['Latitude'], lon=filtered_df['Longitude'],
                                    hover_name=filtered_df['Unit name'], hover_data=['Unit ID', 'Country', 'Operator', 'Owner'],
                                    zoom=5, color_discrete_sequence=['blue']).data[0])

    total = filtered_df.count()[0]
    unmarked = filtered_df['Latitude'].isna().sum()
    marked = total - unmarked 
else:
    total = filtered_df.count()[0]
    unmarked = filtered_df['Latitude'].isna().sum()
    marked = total - unmarked

st.write("Total count:", total)   
st.write("Marked locations:", marked)   
st.write("Unknown locations:", unmarked) 

# Display Plotly map
st.plotly_chart(fig)
