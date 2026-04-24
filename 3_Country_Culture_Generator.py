import streamlit as st
import requests
from google import genai

st.title("Country Culture Comparator")
st.write("Select two countries and a topic to get an AI-generated cultural comparison!")

BASE_URL = "https://restcountries.com/v3.1"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

topic = st.selectbox(
    "Select a topic:",
    ["Travel", "Food & Cuisine", "Business Culture", "History", "Language"]
)

extra = st.text_input("Any extra details you want included? (optional)")

try:
    countries = []
    for region in ["Africa", "Americas", "Asia", "Europe", "Oceania"]:
        response = requests.get(f"{BASE_URL}/region/{region}")
        response.raise_for_status()
        countries += response.json()

    country_names = []
    for country in countries:
        if "name" in country and "common" in country["name"]:
            country_names.append(country["name"]["common"])

    country_names.sort()

    col1, col2 = st.columns(2)

    with col1:
        country1 = st.selectbox(
            "Select first country:",
            country_names
        )

    with col2:
        country2 = st.selectbox(
            "Select second country:",
            country_names,
            index=1
        )

    country1_data = None
    country2_data = None

    for country in countries:
        if country["name"]["common"] == country1:
            country1_data = country
            break

    for country in countries:
        if country["name"]["common"] == country2:
            country2_data = country
            break

    if country1_data and country2_data:
        with st.container():
            st.header(f"{country1} vs {country2}")

            col1, col2 = st.columns(2)

            with col1:
                if "flags" in country1_data and "png" in country1_data["flags"]:
                    st.image(country1_data["flags"]["png"], width=250)

                population1 = country1_data.get("population", 0)
                area1 = country1_data.get("area", 0)
                st.metric("Population", f"{population1:,}")
                st.metric("Area (km²)", f"{area1:,}")
                st.metric("Region", country1_data.get("region", "N/A"))

                st.subheader("Details")
                if "capital" in country1_data and len(country1_data["capital"]) > 0:
                    st.write(f"**Capital:** {country1_data['capital'][0]}")
                if "languages" in country1_data:
                    languages = list(country1_data["languages"].values())
                    st.write(f"**Languages:** {', '.join(languages)}")
                if "currencies" in country1_data:
                    currencies = []
                    for code, info in country1_data["currencies"].items():
                        currencies.append(f"{info.get('name', code)} ({info.get('symbol', '')})")
                    st.write(f"**Currencies:** {', '.join(currencies)}")
                if "subregion" in country1_data:
                    st.write(f"**Subregion:** {country1_data['subregion']}")

            with col2:
                if "flags" in country2_data and "png" in country2_data["flags"]:
                    st.image(country2_data["flags"]["png"], width=250)

                population2 = country2_data.get("population", 0)
                area2 = country2_data.get("area", 0)
                st.metric("Population", f"{population2:,}")
                st.metric("Area (km²)", f"{area2:,}")
                st.metric("Region", country2_data.get("region", "N/A"))

                st.subheader("Details")
                if "capital" in country2_data and len(country2_data["capital"]) > 0:
                    st.write(f"**Capital:** {country2_data['capital'][0]}")
                if "languages" in country2_data:
                    languages = list(country2_data["languages"].values())
                    st.write(f"**Languages:** {', '.join(languages)}")
                if "currencies" in country2_data:
                    currencies = []
                    for code, info in country2_data["currencies"].items():
                        currencies.append(f"{info.get('name', code)} ({info.get('symbol', '')})")
                    st.write(f"**Currencies:** {', '.join(currencies)}")
                if "subregion" in country2_data:
                    st.write(f"**Subregion:** {country2_data['subregion']}")

        if st.button("Generate Comparison"):
            if country1 == country2:
                st.warning("Please select two different countries!")
            else:
                country1_info = f"""
Country: {country1}
Capital: {country1_data['capital'][0] if 'capital' in country1_data else 'N/A'}
Population: {country1_data.get('population', 0)}
Region: {country1_data.get('region', 'N/A')}
Subregion: {country1_data.get('subregion', 'N/A')}
Languages: {', '.join(list(country1_data['languages'].values())) if 'languages' in country1_data else 'N/A'}
Currencies: {', '.join([info.get('name', code) for code, info in country1_data['currencies'].items()]) if 'currencies' in country1_data else 'N/A'}
"""

                country2_info = f"""
Country: {country2}
Capital: {country2_data['capital'][0] if 'capital' in country2_data else 'N/A'}
Population: {country2_data.get('population', 0)}
Region: {country2_data.get('region', 'N/A')}
Subregion: {country2_data.get('subregion', 'N/A')}
Languages: {', '.join(list(country2_data['languages'].values())) if 'languages' in country2_data else 'N/A'}
Currencies: {', '.join([info.get('name', code) for code, info in country2_data['currencies'].items()]) if 'currencies' in country2_data else 'N/A'}
"""

                prompt = f"Compare {country1} and {country2} on the topic of {topic}. Here is some data about each country: {country1_info} {country2_info}. Write an informative and engaging comparison. {extra}"

                with st.container():
                    st.subheader(f"{topic}: {country1} vs {country2}")

                    try:
                        result = client.models.generate_content(
                            model="gemini-3-flash-preview",
                            contents=prompt
                        )
                        st.write(result.text)

                    except Exception as e:
                        st.error(f"Error generating response: {e}")

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching country data: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")

st.write("---")
st.write("Data provided by REST Countries API")
