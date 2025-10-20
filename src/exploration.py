
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import geonamescache
import geopandas as gpd

import plotly.express as px

import streamlit as st


st.set_page_config(layout="wide")

st.markdown(f'<h2><span style="color:#E91802">BBC News Coverage & Geographical Analysis Dashboards</span></h2>',
            unsafe_allow_html=True)

st.write("\n")

st.markdown(f'<h4><i><span style="color:#4a4a4a">This Streamlit application visualizes **how BBC News articles mention countries, cities, and nationalities/ideologies** ' \
' across the globe.It provides multiple interactive modules that combine geographical mapping with categorical analysis</span><i></h4>',
            unsafe_allow_html=True)

st.write("\n")

# read data
@st.cache_data
def load_data():
    df_exp = pd.read_csv('../dataset/new_data.csv')
    return df_exp

df_exp = load_data()
# st.dataframe(df_exp, hide_index=True)

st.markdown(f'<h5><i><span style="color:#4a4a4a">🌍 This app explores **BBC News coverage** by combining **sentiment analysis** with **geographical representation** It visualizes how countries, cities, and identities (nationalities/ideologies) are mentioned across the globe, revealing patterns in media narratives.</span><i></h5>',
            unsafe_allow_html=True)



df_exp.nationalities = df_exp.nationalities.str.rstrip('s')
# df_exp.cities = df_exp.cities.str.replace()

# Un stands for the United Nations
df_exp.cities = df_exp.cities.str.replace('Un', 'UN')

# # Mapping of non-standard → official country names
# country_fix = {
#     "UK": "United Kingdom",
#     "USA": "United States",
#     "US": "United States",
#     "UAE": "United Arab Emirates",
#     "South Korea": "Korea, Republic of",
#     "North Korea": "Korea, Democratic People's Republic of",
#     }

# # Apply fixes
# df_exp["countries"] = df_exp["countries"].replace(country_fix)

st.write("\n\n\n")
# Geographical Map of Countries around the Globe
st.markdown("## :material/public: **Geo-Scatter Plot of News Coverage around the Globe**") 
def global_map(): 
    dfc = df_exp.countries.value_counts().reset_index()
    dfc.columns = ['country', 'count']
    dfc = pd.DataFrame(dfc)

    gc = geonamescache.GeonamesCache()
    countries_dict = gc.get_countries()

    # Convert dict → DataFrame
    gcountries = pd.DataFrame.from_dict(countries_dict, orient="index")
    gcountries = gcountries[["name", "iso3"]]

    # Merge by lowercase name
    dfc["country_lower"] = dfc["country"].str.lower()
    gcountries["name_lower"] = gcountries["name"].str.lower()

    merged = dfc.merge(gcountries, left_on="country_lower", right_on="name_lower", how="left")
    merged = merged.drop_duplicates(subset=['country']).reset_index(drop=['index'])


    plot = px.choropleth(merged, locations="iso3",
                color = "count",
                # projection='natural earth',
                color_continuous_scale="ylorrd",
                # title=f"News Coverage Around the Globe"
                )

    # Fix the figure size
    plot.update_layout(
        width=2000,   # set figure width
        height=1000,   # set figure height
        geo=dict(
            projection_type="natural earth",  # optional: fix projection
            showframe=False,
            showcoastlines=True,
            showcountries=True,
            projection_scale=1,  # keep globe size constant
            center=dict(lat=0, lon=0)  # keep centered
        )
    )

    # Disable zooming, dragging, etc.
    plot.update_layout(
        dragmode=False
    )
    plot.update_geos(fitbounds="locations", visible=False)

    # plot.show()
    st.plotly_chart(plot, use_container_width=True)

global_map()


st.write("\n\n\n")
st.markdown(" ## :material/globe_location_pin: Map of Cities Mentioned within a Particular Country ")

country_list = df_exp.countries.dropna().sort_values().unique()
country = st.selectbox("Select Country", country_list, key="country_selector", placeholder="Select Country")

# row_left, row_right = st.

# with row_left:
def select_country_map(country):
    """
    Generate a geo-scatter plot of cities mentioned within a given country.
    
    Steps:
    1. Filter the dataframe for rows matching the selected country.
    2. Count how many times each city appears.
    3. Use geonamescache to get latitude/longitude for each city.
    4. Match city names between your data and geonamescache - within selected country.
    5. If multiple entries for a city exist, keep the one with the largest population.
    6. Plot the cities on a world map with bubble sizes proportional to frequency.
    """

    if country in country_list:
        # Count how many times each city is mentioned in df_exp for the given country
        dfc = df_exp[df_exp['countries'] == country]['cities'].value_counts().reset_index()
        dfc.columns = ['city', 'count']  # Rename columns for clarity

        # Ensure dfc is a DataFrame (value_counts returns Series initially)
        dfc = pd.DataFrame(dfc)

        # Load geonamescache data (cities + countries metadata)
        gc = geonamescache.GeonamesCache()
        cities_dict = gc.get_cities()
        countries_dict = gc.get_countries()

        # Convert the geonamescache dictionary into a DataFrame
        # Keep only relevant columns for plotting
        gcities = pd.DataFrame.from_dict(cities_dict, orient="index")
        gcities = gcities[["name", "countrycode", "latitude", "longitude", "population"]]

        # Find the ISO country code (e.g., "UA" for Ukraine) that matches the input country name
        country_code = None
        for code, info in countries_dict.items():
            if info["name"].lower() == country.lower():
                country_code = code
                break

        # If no country match is found, stop the function
        if not country_code:
            print(f"Country '{country}' not found in geonamecache.")
            return

        # Prepare for merging: capitalize city names for consistent matching
        dfc["city_cap"] = dfc["city"].str.capitalize()
        gcities["name_cap"] = gcities["name"].str.capitalize()

        # Merge user city data with geonamescache cities,
        # but only keep cities from the selected country
        merged = dfc.merge(
            gcities[gcities["countrycode"] == country_code], 
            left_on="city_cap", 
            right_on="name_cap", 
            how="left"
        )

        # If a city has multiple entries, keep the one with the largest population
        merged = merged.sort_values(["city", "population"], ascending=[True, False])
        merged = merged.drop_duplicates(subset=["city"]).reset_index(drop=True)


        if merged.values.any():
            # Create a scatter plot on a world map
            plot = px.scatter_geo(
                merged, 
                lat='latitude', 
                lon='longitude',
                size="count",           # bubble size ~ frequency
                color="name",           # color-coded by city name
                title=f"Cities mentioned within {country}"
            )
            
            # Customize the layout for better visuals
            plot.update_layout(
                width=2000,   # figure width
                height=1000,   # figure height
                geo=dict(
                    projection_type="natural earth",  # projection type
                    showframe=False,
                    showcoastlines=True,
                    showcountries=True,
                    projection_scale=1,   # zoom level
                    center=dict(lat=0, lon=0)  # keep centered on the globe
                ),
                dragmode=False  # disable dragging/zooming
            )

            # plot.show()
            st.plotly_chart(plot, use_container_width=True)
        
        else:
            st.markdown(f"<h3><span style='color:Tomato;'>{country}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)

    else:
        # If the provided country is not in the country_list, print a warning
        st.markdown(f"<h3><span style='color:Tomato;'>{country}</span> not in records!</h3>", unsafe_allow_html=True)
        # st.markdown(f"{country} not in records!")


# Example usage
select_country_map(country)



st.write("\n\n\n")
st.markdown(" ## :material/globe_location_pin: Geo-Scatter Plot of Cities mentioned alongside a given Country")

# country_list = df_exp.countries.dropna().unique()
country = st.selectbox("Select Country", country_list, key="country_map_selector", placeholder="Select Country")

# with row_right:
def select_global_country_map(country):
    """
    Generate a geo-scatter plot of cities mentioned within a given country.
    
    Steps:
    1. Filter the dataframe for rows matching the selected country.
    2. Count how many times each city appears.
    3. Use geonamescache to get latitude/longitude for each city.
    4. Match city names between your data and geonamescache - around the globe.
    5. If multiple entries for a city exist, keep the one with the largest population.
    6. Plot the cities on a world map with bubble sizes proportional to frequency.
    """

    if country in country_list:
        # Count how many times each city is mentioned in df_exp for the given country
        dfc = df_exp[df_exp['countries'] == country]['cities'].value_counts().reset_index()
        dfc.columns = ['city', 'count']  # Rename columns for clarity

        # Ensure dfc is a DataFrame (value_counts returns Series initially)
        dfc = pd.DataFrame(dfc)

        # Load geonamescache data (cities + countries metadata)
        gc = geonamescache.GeonamesCache()
        cities_dict = gc.get_cities()
        countries_dict = gc.get_countries()

        # Convert the geonamescache dictionary into a DataFrame
        # Keep only relevant columns for plotting
        gcities = pd.DataFrame.from_dict(cities_dict, orient="index")
        gcities = gcities[["name", "countrycode", "latitude", "longitude", "population"]]

        # Find the ISO country code (e.g., "UA" for Ukraine) that matches the input country name
        country_code = None
        for code, info in countries_dict.items():
            if info["name"].lower() == country.lower():
                country_code = code
                break

        # If no country match is found, stop the function
        if not country_code:
            print(f"Country '{country}' not found in geonamecache.")
            return

        # Prepare for merging: capitalize city names for consistent matching
        dfc["city_cap"] = dfc["city"].str.capitalize()
        gcities["name_cap"] = gcities["name"].str.capitalize()

        # Merge user city data with geonamescache cities,
        # but only keep cities from the selected country
        merged = dfc.merge(
            gcities, 
            left_on="city_cap", 
            right_on="name_cap", 
            how="left"
        )

        # If a city has multiple entries, keep the one with the largest population
        merged = merged.sort_values(["city", "population"], ascending=[True, False])
        merged = merged.drop_duplicates(subset=["city"]).reset_index(drop=True)

        if merged.values.any():
            # Create a scatter plot on a world map
            plot = px.scatter_geo(
                merged, 
                lat='latitude', 
                lon='longitude',
                size="count",           # bubble size ~ frequency
                color="name",           # color-coded by city name
                title=f"Cities mentioned with {country} Globally"
            )
            
            # Customize the layout for better visuals
            plot.update_layout(
                width=2000,   # figure width
                height=1000,   # figure height
                geo=dict(
                    projection_type="natural earth",  # projection type
                    showframe=False,
                    showcoastlines=True,
                    showcountries=True,
                    projection_scale=1,   # zoom level
                    center=dict(lat=0, lon=0)  # keep centered on the globe
                ),
                dragmode=False  # disable dragging/zooming
            )

            # Show the plot
            # plot.show()
            st.plotly_chart(plot, use_container_width=True)
        
        else:
            st.markdown(f"<h3><span style='color:Tomato;'>{country}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)

    else:
        # If the provided country is not in the country_list, print a warning
        st.markdown(f"<h3><span style='color:Tomato;'>{country}</span> not in records!</h3>", unsafe_allow_html=True)
        # st.title(f"{country} not in records")

# Example usage
select_global_country_map(country)


# def select_country(country):
#     """
#     Plot the top cities mentioned in relation to a given country.

#     Steps:
#     1. Filter df_exp for rows belonging to the selected country.
#     2. Count how many times each city is mentioned.
#     3. Keep only the top 15 most frequent cities.
#     4. Plot the results as a bar chart.
#     """

#     if country in country_list:
#         # Filter rows for the selected country and count city mentions
#         dfc = df_exp[df_exp['countries'] == country]['cities'].value_counts().reset_index()

#         # Rename columns: 'city' for the name and 'count' for frequency
#         dfc.columns = ['city', 'count']

#         # Capitalize city names for consistency
#         dfc.city = dfc.city.str.capitalize()

#         # Convert to DataFrame and keep only the top 15 cities
#         dfc = pd.DataFrame(dfc.iloc[:15])

#         # If there are results for this country
#         if dfc.values.any():
#             # Create a bar chart showing top cities mentioned
#             fig = px.bar(dfc, x="city", y="count")

#             # Customize layout (title, axis labels, hide y-axis ticks)
#             fig.update_layout(
#                 title_text=f"Top Cities mentioned with {country}",
#                 xaxis_title="Cities",
#                 yaxis=dict(title=None, showticklabels=False, ticks="")
#                 # Optionally set a range for the y-axis: yaxis_range=[0,10]
#             )

#             # Customize bar color
#             fig.update_traces(marker_color='#873260')

#             # Show the plot
#             fig.show()
#         else:
#             # If no cities were found for this country
#             print(f"{country} correlations could not be sourced! ")

#     else:
#         # If the given country is not in your country_list
#         print(f"{country} does not exist in records! ")


# # Example usage
# select_country('Ukraine')


st.write("\n\n\n")
st.markdown(" ## :material/globe_location_pin: Identities mentioned alongside a given Country")
# """ Nationality / Ideology Exploration """
country = st.selectbox("Select Country", country_list, key="country_map_ideology", placeholder="Select Country")
#What Ideology or Nationality does each country relate with or mentioned with?
def select_ideology(country):
    """
    Plot the top ideologies / beliefs / nationalities mentioned
    in connection with a given country.

    Steps:
    1. Filter the main dataframe for the selected country.
    2. Count how many times each 'nationality' is associated with it.
    3. Keep the top 15 most frequent nationalities.
    4. Plot the results as a bar chart.
    """

    if country in country_list:
        # Filter df_exp to include only rows for the chosen country
        dfr = df_exp[df_exp['countries'] == country]

        # Count occurrences of each nationality associated with the country
        dfr = dfr.groupby('countries')['nationalities'].value_counts().reset_index()

        # Keep only relevant columns (nationality + count)
        dfr = dfr[['nationalities', 'count']]

        # Ensure result is a DataFrame (good practice after groupby operations)
        dfr = pd.DataFrame(dfr)

        # Keep only the top 15 nationalities (for readability in the plot)
        dfr = dfr.iloc[:20, :]

        if dfr.values.any():
            # --- Plotting the bar chart ---
            fig = px.bar(
                dfr, 
                x="nationalities", 
                y="count"
            )

            # Update layout for better presentation
            fig.update_layout(
                title_text=f"Top Ideologies / Beliefs / Nationalities related to {country}",
                xaxis_title="Ideologies / Beliefs / Nationalities",
                
                # Remove y-axis label & tick marks for a cleaner look
                yaxis=dict(title=None, showticklabels=False, ticks="")
                # Optionally, you could enforce a range: yaxis_range=[0,10]
            )

            # Customize bar color
            fig.update_traces(marker_color='#E91802')
            
            # Show the chart
            # fig.show()
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"<h3><span style='color:#E91802;'>{country}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)
            # print("{country} correlations could not be sourced!")

        # Optionally return the processed DataFrame instead of just plotting
        # return dfr  

    else:
        # If the country is not in your country_list, print a warning
        st.markdown(f"<h3><span style='color:#E91802;'>{country}</span> does not exists in records!</h3>", unsafe_allow_html=True)
        # print(f"{country} does not exist in records!")


# Example usage
select_ideology(country)



st.write("\n\n\n")
st.markdown(" ## :material/globe_location_pin: Identities and Location mentioned within a Particular Country")
country = st.selectbox("Select Country", country_list, key="nat_map_ideology", placeholder="Select Country")
#Nationalities and Cities per mentioned Country
def nat_city(country):
    """
    Plot the relationship between nationalities/ideologies and cities mentioned
    for a given country.

    Steps:
    1. Filter the main dataframe for rows belonging to the selected country.
    2. Group by 'nationalities' and count how many times each 'city' appears with it.
    3. Sort by frequency and keep the top 15 combinations.
    4. Plot as a bubble chart (scatter plot with bubble size = count).
    """

    if country in country_list:
        # Group data by nationality → city, then count occurrences
        dfgl = (
            df_exp[df_exp['countries'] == country]
            .groupby('nationalities')['cities']
            .value_counts()  # counts how often each city appears per nationality
            .reset_index()
            .sort_values('count', ascending=False) 
        )

        if dfgl.values.any():

            # --- Plot a scatter plot (bubble chart) ---
            fig = px.scatter(
                dfgl,
                x="cities",             # cities on x-axis
                y="nationalities",      # nationalities on y-axis
                size="count",            # bubble size ~ frequency

            )

            # Update layout for readability
            fig.update_layout(
                title_text=f"Nationality-Ideology vs Cities per Country Mentioned ({country})",
                xaxis_title="Cities where mentioned",
                yaxis_title="Identity"
            )

            # Optional: customize colors
            # fig.update_traces(marker_color='#6D8196')

            # Show the chart
            # fig.show()
            st.plotly_chart(fig)
        else:
            st.markdown(f"<h3><span style='color:#0078FF;'>{country}</span> correlations could not be sourced!</h3>", unsafe_allow_html=True)
            # print(f"{country} correlations relationship could not be sourced!")

    else:
        # If country not in list, log a warning
        st.markdown(f"<h3><span style='color:#0078FF;'>{country}</span> does not exists in records!</h3>", unsafe_allow_html=True)
        # print(f"{country} does not exist in records!")


# Example usage
nat_city(country)









