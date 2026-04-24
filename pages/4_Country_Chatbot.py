import streamlit as st
import requests
from google import genai

st.title("Country Expert Chatbot")
st.write("Select a country and chat with an AI that knows all about it!")

BASE_URL = "https://restcountries.com/v3.1"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()
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

    selected_country = st.selectbox("Select a country to chat about:", country_names)

    country_data = None
    for country in countries:
        if country["name"]["common"] == selected_country:
            country_data = country
            break

    if country_data:
        with st.container():
            st.header(selected_country)

            col1, col2 = st.columns(2)

        with col1:
            flag_url = country_data.get("flags", {}).get("svg") or country_data.get("flags", {}).get("png")
    
            if flag_url:
                st.image(flag_url, use_container_width=True)
            else:
                st.warning("No flag image available.")

            with col2:
                population = country_data.get("population", 0)
                area = country_data.get("area", 0)
                st.metric("Population", f"{population:,}")
                st.metric("Area (km²)", f"{area:,}")
                st.metric("Region", country_data.get("region", "N/A"))

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
                if "subregion" in country_data:
                    st.write(f"**Subregion:** {country_data['subregion']}")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "display_history" not in st.session_state:
        st.session_state.display_history = []

    if "current_country" not in st.session_state:
        st.session_state.current_country = None

    if st.session_state.current_country != selected_country:
        st.session_state.chat_history = []
        st.session_state.display_history = []
        st.session_state.current_country = selected_country

    st.subheader(f"Chat about {selected_country}")

    for message in st.session_state.display_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input(f"Ask something about {selected_country}...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        st.session_state.display_history.append({"role": "user", "content": user_input})

        capital = country_data["capital"][0] if "capital" in country_data and country_data["capital"] else "N/A"
        languages = ", ".join(country_data["languages"].values()) if "languages" in country_data else "N/A"
        currencies = ", ".join([info.get("name", code) for code, info in country_data["currencies"].items()]) if "currencies" in country_data else "N/A"

        country_info = f"""
Country: {selected_country}
Capital: {capital}
Population: {country_data.get('population', 0)}
Region: {country_data.get('region', 'N/A')}
Subregion: {country_data.get('subregion', 'N/A')}
Languages: {languages}
Currencies: {currencies}
"""

        if len(st.session_state.chat_history) == 0:
            first_message = f"You are a knowledgeable expert on {selected_country}. Use this data to answer questions accurately: {country_info}\n\nUser: {user_input}"
            st.session_state.chat_history.append({"role": "user", "parts": [{"text": first_message}]})
        else:
            st.session_state.chat_history.append({"role": "user", "parts": [{"text": user_input}]})

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=st.session_state.chat_history
            )
            answer = response.text

        except Exception as e:
            answer = f"Error generating response: {e}"

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.display_history.append({"role": "assistant", "content": answer})
        st.session_state.chat_history.append({"role": "model", "parts": [{"text": answer}]})

    if len(st.session_state.display_history) > 0:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.display_history = []
            st.rerun()

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching country data: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")

st.write("---")
st.write("Data provided by REST Countries API")
