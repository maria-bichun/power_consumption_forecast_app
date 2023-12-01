import streamlit as st
from st_pages import Page, show_pages
import base64
from st_clickable_images import clickable_images

if 'language' not in st.session_state:
    st.session_state['language'] = 'ru'

#Set content dictionary
text = {'menu_home': {'en': 'Home', 'ru': 'Главная'},
         'menu_forecast': {'en': 'Forecast for today', 'ru': 'Прогноз на сегодня'},
         'menu_archive': {'en': 'Forecast history', 'ru': 'История прогнозов'},
         'menu_about': {'en': 'About the project', 'ru': 'О проекте'},
         'header': {'en': 'About the project', 'ru': 'О проекте'},
         }

#add a sidebar to select pages
with st.sidebar:
    images = []
    for file in ["images/russia.png", "images/united-kingdom.png"]:
        with open(file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            images.append(f"data:image/jpeg;base64,{encoded}")

    clicked = clickable_images(images,
                               titles=['RU', 'EN'],
                               div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                               img_style={"margin": "5px", "height": "25px"})
    
    if clicked == 1:
        st.session_state['language'] = 'en'
    if clicked == 0:
        st.session_state['language'] = 'ru'

# Specify what pages should be shown in the sidebar, and what their titles 
# and icons should be
show_pages(
    [
        Page("Home.py", text['menu_home'][st.session_state['language']], "🏠"),
        Page("pages/1_Forecast.py", text['menu_forecast'][st.session_state['language']], ":chart_with_upwards_trend:"),
        Page("pages/2_Archive.py", text['menu_archive'][st.session_state['language']], ":books:"),
        Page("pages/3_About.py", text['menu_about'][st.session_state['language']], ":information_source:")
    ]
)

#define app section
header=st.container()
body=st.container()

#define header
with header:
    header.title(text['header'][st.session_state['language']])

with body:
    st.write('sometext')