""" 
# Sentiment Analysis Dashboard with Streamlit

This project provides an **interactive dashboard** for exploring categorized news data using Streamlit. It visualizes relationships between predicted categories (from a Hugging Face zero-shot classification pipeline) and metadata such as countries, cities, and nationalities. Users can explore distributions of news categories, view choropleth maps of global category prevalence, and analyze how specific countries, cities, or nationalities are associated with different news categories.


"""

#import important libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import geonamescache
import geopandas as gpd
from shapely.geometry import Point

import plotly.express as px
import streamlit as st


st.set_page_config(layout="wide")

st.markdown(f'<h2><span style="color:#E91802">Sentiment Analysis Dashboard with Streamlit</span></h2>',
            unsafe_allow_html=True)

st.write("\n")

st.markdown(f'<h4><i><span style="color:#4a4a4a">This project provides an **interactive dashboard** \
            for exploring categorized news data using Streamlit. It visualizes relationships between predicted \
            categories (from a Hugging Face zero-shot classification pipeline) and metadata such as countries, cities, \
            and nationalities. Users can explore distributions of news categories,  \
            view choropleth maps of global category prevalence, and analyze how specific countries, \
            cities, or nationalities are associated with different news categories.</span><i></h4>',
            unsafe_allow_html=True)


st.write("\n")


@st.cache_data
def load_data():
    df_preds = pd.read_csv('../dataset/pred_streamlit.csv')
    return df_preds

df_preds = load_data()


# capitalize
df_preds.nationalities = df_preds.nationalities.str.capitalize()
df_preds.cities = df_preds.cities.str.capitalize()
df_preds.predicted_label = df_preds.predicted_label.str.capitalize()

# # Mapping of non-standard → official country names
# country_fix = {
#     "UK": "United Kingdom",
#     "USA": "United States",
#     "UAE": "United Arab Emirates",
#     "South Korea": "Korea, Republic of",
#     "North Korea": "Korea, Democratic People's Republic of",
#     }

# # Apply fixes
# df_preds["countries"] = df_preds["countries"].replace(country_fix)


# country_list = set(list(df_preds.countries.values))
# # label_list = set(list(df_preds.predicted_label.values))
# city_list = set(list(df_preds.cities.values))
# nat_list = set(list(df_preds.nationalities.values))


st.write("\n\n\n")
# Geographical Map of Countries around the Globe
st.markdown("## :material/public: **Geo-Scatter Plot of Prevalence of Predicted Labels per Country**") 

label_list = df_preds.predicted_label.dropna().sort_values().unique()
label = st.selectbox("Select Country", label_list, key="label_selector", placeholder="Select Country")

def label_country(label):
    """
    Plot the global spread of a given news category (predicted label)
    by mapping its mentions across countries.

    Steps:
    1. Check if the input label exists in the dataset.
    2. Filter df_preds for rows matching that label.
    3. Count how many times each country is associated with the label.
    4. Match country names with geonamescache ISO3 codes.
    5. Plot a choropleth world map where color intensity = frequency.
    """

    if label in label_list:
        # Filter rows for the selected label, group by country, and count occurrences
        dfc = (
            df_preds[df_preds['predicted_label'] == label]
            .groupby('predicted_label')['countries']
            .value_counts()      # count how often each country appears
            .reset_index()       # convert Series → DataFrame
        )

        # Rename columns for clarity
        dfc.columns = ['labels', 'country', 'count']

        # Load geonamescache data for countries
        gc = geonamescache.GeonamesCache()
        countries_dict = gc.get_countries()

        # Convert geonamescache dictionary → DataFrame
        gcountries = pd.DataFrame.from_dict(countries_dict, orient="index")
        gcountries = gcountries[["name", "iso3"]]  # keep only useful columns

        # Normalize names for consistent merging (capitalize first letter)
        dfc["country_cap"] = dfc["country"].str.capitalize()
        gcountries["name_cap"] = gcountries["name"].str.capitalize()

        # Merge label-country counts with official geonames country info
        merged = dfc.merge(
            gcountries, 
            left_on="country_cap", 
            right_on="name_cap", 
            how="left"
        )

        # --- Choropleth map ---
        plot = px.choropleth(
            merged,
            locations="iso3",                # ISO3 country codes
            color="count",                   # frequency as color intensity
            color_continuous_scale="peach", # color palette
            title=f"Global Spread of '{label}' mentions"
        )

        # Fix the figure size and projection
        plot.update_layout(
            width=1000,
            height=600,
            geo=dict(
                projection_type="natural earth",  # natural earth projection
                showframe=False,
                showcoastlines=True,
                showcountries=True,
                projection_scale=1,               # keep globe scaling
                center=dict(lat=0, lon=0)         # center map
            )
        )

        # Disable zooming/dragging
        plot.update_layout(dragmode=False)

        # Auto-fit the map bounds to locations
        plot.update_geos(fitbounds="locations", visible=False)

        # Show the final plot
        # plot.show()
        st.plotly_chart(plot, use_container_width=True)

    else:
        # If label not in your label_list, show warning
        st.markdown(f"<h3>Please, Select the right category<span style='color:Tomato;'>{label}</span> not in records!</h3>", unsafe_allow_html=True)
        # print(f"Please, Select the right category \n{label} not in Categories available")


# Example usage
label_country(label)




st.write("\n\n\n")
st.markdown(" ## :material/bar_chart: <span style='color:#D20A2E'>Distribution of Predicted Labels</span>", unsafe_allow_html=True)

def category_label():
    n_labels = df_preds.predicted_label.value_counts().reset_index()

    fig = px.bar(n_labels, x="predicted_label", y="count") 

        
    fig.update_layout(
        title_text=" ",
        xaxis_title="\n Category Labels",
        yaxis_title="Number of Mentions",
        # yaxis_range=[0,10]
    )

    fig.update_traces(marker_color='#D20A2E')

    # fig.show()
    st.plotly_chart(fig, use_container_width=True)

category_label()



st.write("\n\n\n")
st.markdown(" ## :material/public:  <span style='color:#5A051A'> What news category was cognizance with a particular country?</span>", unsafe_allow_html=True)

country_list = df_preds.countries.dropna().sort_values().unique()
country = st.selectbox("Select Country", country_list, key="country_selector", placeholder="Select Country")

def country_labels(country):
    """
    Plot the distribution of news categories (predicted labels)
    associated with a given country.

    Steps:
    1. Filter df_preds for rows matching the selected country.
    2. Count how many times each predicted label (category) appears.
    3. Plot the results as a bar chart.
    """

    if country in country_list:
        # Filter rows for the selected country and count label frequencies
        df = (
            df_preds[df_preds['countries'] == country]['predicted_label']
            .value_counts()  # count each category
            .reset_index()   # convert to DataFrame
        )

        # Rename columns for clarity
        df.columns = ['Category', 'Count']

        # Create a bar chart of categories vs. counts
        fig = px.bar(df, x="Category", y="Count")

        # Customize chart layout
        fig.update_layout(
            title_text=" ",                       # optional: empty title
            xaxis_title="\n News Category",       # label for x-axis
            yaxis_title="Number of Mentions",    # label for y-axis
            # yaxis_range=[0,10]                  # optional fixed y-axis range
        )

        # Customize bar color
        fig.update_traces(marker_color='#5A051A')

        # Show the plot
        st.plotly_chart(fig, use_container_width=True)

    else:
        # If the country is not found in your country_list
        st.markdown(f"<h3><span style='color:#5A051A;'>{country}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)
     
country_labels(country)




st.write("\n\n\n")
st.markdown(" ## :material/bar_chart:  <span style='color:#EE1E52'> What news category was cognizance with a particular city?</span>", unsafe_allow_html=True)

city_list = df_preds.cities.dropna().sort_values().unique()
city = st.selectbox("Select Country", city_list, key="city_selector", placeholder="Select Country")

def city_labels(city):
    """
    Plot the distribution of news categories (predicted labels)
    associated with a given city.

    Steps:
    1. Filter df_preds for rows matching the selected city.
    2. Count how many times each predicted label (category) appears.
    3. Plot the results as a bar chart.
    """

    if city in city_list:
        # Filter rows for the selected city and count label frequencies
        df = (
            df_preds[df_preds['cities'] == city]['predicted_label']
            .value_counts()    # count occurrences of each category
            .reset_index()     # convert Series → DataFrame
        )

        # By default, value_counts gives columns ["index", "predicted_label"]
        # You might want to rename them for clarity:
        # df.columns = ["predicted_label", "count"]

        # Create a bar chart of categories vs. counts
        fig = px.bar(df, x="predicted_label", y="count")

        # Customize layout (title, axis labels, hide y-ticks if desired)
        fig.update_layout(
            title_text=f"News often related to {city}",
            xaxis_title="\n News Category",
            yaxis_title="Number of Occurence",
            yaxis=dict(title="", showticklabels=False, ticks="")
            # yaxis_range=[0,10]   # optional: fix the y-axis range
        )

        # Customize bar color
        fig.update_traces(marker_color='#EE1E52')

        # Show the plot
        st.plotly_chart(fig, use_container_width=True)

    else:
        # If the city is not found in your city_list
        st.markdown(f"<h3><span style='color:#EE1E52'>{city}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)

city_labels(city)



st.write("\n\n\n")
st.markdown(" ## :material/bar_chart:  <span style='color:#550000'> What news category was cognizance with a particular Identity?</span>", unsafe_allow_html=True)

nat_list = df_preds.nationalities.dropna().sort_values().unique()
nat = st.selectbox("Select Country", nat_list, key="nationality_selector", placeholder="Select Country")

def nat_labels(nat):
    """
    Plot the distribution of news categories (predicted labels)
    associated with a given nationality.

    Steps:
    1. Check if the input nationality exists in the dataset.
    2. Filter df_preds for rows matching that nationality.
    3. Count how many times each predicted label (category) appears.
    4. Plot the results as a bar chart.
    """

    if nat in nat_list:
        # Filter rows by nationality and count label frequencies
        df = (
            df_preds[df_preds['nationalities'] == nat]['predicted_label']
            .value_counts()    # count each category
            .reset_index()     # convert Series → DataFrame
        )

        # Optional: rename columns for clarity
        # df.columns = ["predicted_label", "count"]

        # Create bar chart
        fig = px.bar(df, x="predicted_label", y="count")

        # Customize chart layout
        fig.update_layout(
            title_text=f"News category often related to a {nat}",
            xaxis_title="\n News Category",
            yaxis=dict(title="", showticklabels=False, ticks="")
            # yaxis_range=[0,10]   # optional: lock y-axis range
        )

        # Customize bar color
        fig.update_traces(marker_color='#550000')

        # Show the plot
        st.plotly_chart(fig, use_container_width=True)

    else:
        # If nationality not found in dataset
        st.markdown(f"<h3><span style='color:#550000'>{nat}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)


# Example usage
nat_labels(nat)









