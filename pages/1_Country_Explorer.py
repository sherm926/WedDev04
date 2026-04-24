import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

st.title("Country Information Explorer")
st.write("Explore detailed information about countries around the world")

BASE_URL = "https://restcountries.com/v3.1"

FIELDS = "name,flags,population,area,region,capital,languages,currencies,timezones,continents,subregion,coatOfArms"

region = st.selectbox(
    "Select a region:",
    ["Africa", "Americas", "Asia", "Europe", "Oceania"]
)

try:
    if region == "All Regions":
        response = requests.get(f"{BASE_URL}/all?fields={FIELDS}")
    else:
        response = requests.get(f"{BASE_URL}/region/{region}?fields={FIELDS}")
    
    response.raise_for_status()
    countries = response.json()
    
    country_names = []
    for country in countries:
        if "name" in country and "common" in country["name"]:
            country_names.append(country["name"]["common"])
    
    country_names.sort()
    
    selected_country = st.selectbox(
        "Select a country:",
        country_names
    )
    
    country_data = None
    for country in countries:
        if country["name"]["common"] == selected_country:
            country_data = country
            break
    
    if country_data:
        st.header(f"{country_data['name']['common']}")
        
        if "flags" in country_data and "png" in country_data["flags"]:
            st.image(country_data["flags"]["png"], width=300)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            population = country_data.get("population", 0)
            st.metric("Population", f"{population:,}")
        
        with col2:
            area = country_data.get("area", 0)
            st.metric("Area (km²)", f"{area:,}")
        
        with col3:
            st.metric("Region", country_data.get("region", "N/A"))
        
        st.subheader("Country Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "capital" in country_data and len(country_data["capital"]) > 0:
                st.write(f"**Capital:** {country_data['capital'][0]}")
            if "languages" in country_data:
                languages = list(country_data["languages"].values())
                st.write(f"**Languages:** {', '.join(languages)}")
            if "currencies" in country_data:
                currencies = []
                for code, info in country_data["currencies"].items():
                    currencies.append(f"{info.get('name', code)} ({info.get('symbol', '')})")
                st.write(f"**Currencies:** {', '.join(currencies)}")
        with col2:
            if "timezones" in country_data:
                st.write(f"**Timezones:** {', '.join(country_data['timezones'])}")
            if "continents" in country_data:
                st.write(f"**Continents:** {', '.join(country_data['continents'])}")
            if "subregion" in country_data:
                st.write(f"**Subregion:** {country_data['subregion']}")
        st.subheader(f"Population Comparison in {region}")
    
        region_countries = []
        region_populations = []
        
        for country in countries:
            name = country["name"]["common"]
            pop = country.get("population", 0)
            if pop > 0:
                region_countries.append(name)
                region_populations.append(pop)
        
        sorted_data = sorted(zip(region_countries, region_populations), 
                           key=lambda x: x[1], reverse=True)[:10]
        
        top_countries = [x[0] for x in sorted_data]
        top_populations = [x[1] for x in sorted_data]
        
        colors = ['red' if name == selected_country else 'lightblue' 
                 for name in top_countries]
        
        fig_pop = go.Figure()
        fig_pop.add_trace(go.Bar(
            x=top_countries,
            y=top_populations,
            marker_color=colors
        ))
        fig_pop.update_layout(
            xaxis_title="Country",
            yaxis_title="Population",
            hovermode='x unified'
        )
        st.plotly_chart(fig_pop, use_container_width=True)
        
        st.subheader(f"Area vs Population in {region}")
        
        scatter_countries = []
        scatter_areas = []
        scatter_populations = []
        
        for country in countries:
            name = country["name"]["common"]
            area = country.get("area", 0)
            pop = country.get("population", 0)
            if area > 0 and pop > 0:
                scatter_countries.append(name)
                scatter_areas.append(area)
                scatter_populations.append(pop)
        
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=scatter_areas,
            y=scatter_populations,
            mode='markers',
            marker=dict(size=10, opacity=0.6),
            text=scatter_countries,
            hovertemplate='<b>%{text}</b><br>Area: %{x:,.0f} km²<br>Population: %{y:,.0f}<extra></extra>'
        ))
        
        if selected_country in scatter_countries:
            idx = scatter_countries.index(selected_country)
            fig_scatter.add_trace(go.Scatter(
                x=[scatter_areas[idx]],
                y=[scatter_populations[idx]],
                mode='markers',
                marker=dict(size=15, color='red'),
                name=selected_country,
                hovertemplate='<b>%{text}</b><br>Area: %{x:,.0f} km²<br>Population: %{y:,.0f}<extra></extra>',
                text=[selected_country]
            ))
        
        fig_scatter.update_layout(
            xaxis_title="Area (km²)",
            yaxis_title="Population",
            hovermode='closest',
            showlegend=False
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        if "coatOfArms" in country_data and "png" in country_data["coatOfArms"]:
            st.subheader("Coat of Arms")
            st.image(country_data["coatOfArms"]["png"], width=200)

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching country data: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")

st.write("---")
st.write("Data provided by REST Countries API")
