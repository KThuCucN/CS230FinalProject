"""
Felipe Avellaneda
CS230
Final Project
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Air Quality Dashboard",
    layout="wide",
    page_icon=":city_sunset:"
)

st.markdown("""
    <style>
    input[type="range"] {
        accent-color: green;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.header("Explore Data")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, encoding='utf-8')
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    df.dropna(subset=['AQI Value', 'lat', 'lng'], inplace=True)
    return df

df = load_data('air_quality_index.csv')

aqi_threshold = st.sidebar.slider(
    "Select minimum AQI value:",
    int(df['AQI Value'].min()),
    int(df['AQI Value'].max()),
    50
)

countries = sorted(df['Country'].dropna().unique().tolist())
countries.insert(0, "All")
selected_country = st.sidebar.selectbox("Select a Country:", countries)

categories = sorted(df['AQI Category'].dropna().unique().tolist())
categories.insert(0, "All")
selected_category = st.sidebar.selectbox("Select an AQI Category:", categories)

if selected_country == "All":
    temp = df
else:
    temp = df[df['Country'] == selected_country]

filtered_df = temp[
    (temp['AQI Value'] >= aqi_threshold) &
    ((selected_category == "All") | (temp['AQI Category'] == selected_category))
]

st.title("Explore The World's Air Quality")
st.markdown("This interactive dashboard allows you to explore air quality data around the world.")

st.subheader("Filtered Data Sample")
st.dataframe(filtered_df.head(10))

st.subheader("Top 10 Cities by AQI Value")
top_cities = filtered_df.nlargest(10, 'AQI Value')
fig, ax = plt.subplots()
ax.barh(top_cities['City'], top_cities['AQI Value'])
ax.set_xlabel('AQI Value')
ax.set_ylabel('City')
ax.set_title('Top 10 Cities by AQI Value')
plt.tight_layout()
st.pyplot(fig)

st.subheader("Trend of Average AQI Value")
if selected_country == "All":
    avg_series = filtered_df.groupby('Country')['AQI Value'].mean()
else:
    avg_series = filtered_df.groupby('City')['AQI Value'].mean()
st.line_chart(avg_series)

st.subheader("Geographical Distribution of AQI Measurements")
map_df = filtered_df[['lat', 'lng', 'AQI Value', 'AQI Category']].copy()
zoom = 1 if selected_country == "All" else 4
view_state = pdk.ViewState(
    latitude=map_df['lat'].mean(),
    longitude=map_df['lng'].mean(),
    zoom=zoom
)
layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_df,
    get_position='[lng, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=50000,
    pickable=True
)
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>AQI:</b> {AQI Value}<br/><b>Category:</b> {AQI Category}",
        "style": {"color": "white"}
    }
)
st.pydeck_chart(deck)

category_counts = filtered_df['AQI Category'].value_counts()
st.markdown("---")
st.subheader("Summary")
for cat, count in category_counts.items():
    st.markdown(f"- **{cat}**: {count}")

st.markdown(
    "This dashboard provides insights into air quality by category and geography. Use the controls to filter and visualize the data interactively."
)
