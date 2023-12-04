import streamlit as st
from st_pages import Page, show_pages, show_pages_from_config, hide_pages
import base64
import plotly.express as px
from st_clickable_images import clickable_images
from model.power_comsumption_predictor import PowerConsumptionPredictor
from utils.df_getter import get_df

if 'language' not in st.session_state:
    st.session_state['language'] = 'ru'
if 'pcp' not in st.session_state:
    st.session_state['pcp'] = PowerConsumptionPredictor(get_df())

#Set content dictionary
text = {'menu_home': {'en': 'Home', 'ru': 'Главная'},
         'menu_forecast': {'en': 'Forecast for today', 'ru': 'Прогноз на сегодня'},
         'menu_archive': {'en': 'Forecast history', 'ru': 'История прогнозов'},
         'menu_about': {'en': 'About the project', 'ru': 'О проекте'},
         'header': {'en': 'About the project', 'ru': 'О проекте'},
         'task_source': {'en': """
                         The solution underlying this app was originally the challenge of GlowByte Autumn Hack 2023 hackathon. The participants were to develop a predictive model to forecast power consumption of the region based on available data about power cunsumption in the past and factors influencing it. The model must take into account seasonal, temporal and other dependencies to obtain the most precise forecast. The model is to predict power consumption for 1 day ahead. \n
                         Our team's solution took the third place in the rating having shown high values of prediction quality metrics. The interface presented here was developed to demonstrate machine learning capabilities for solving real business problems, as well as for data visualization purposes
                         """,
                         'ru': """
                         Решение, лежащее в основе этого приложения, было задачей хакатона GlowByte Autumn Hack 2023. Необходимо было разработать предиктивную модель, которая позволит прогнозировать энергопотребление региона на основе имеющихся данных о потреблении электроэнергии в прошлом и соответствующих факторах, влияющих на потребление энергии. Модель должна быть способна учесть сезонные, временные и другие зависимости для более точного прогноза. Модель должна предсказывать общее потребление региона на 1 сутки. \n 
                         Решение нашей команды заняло призовое третье место, показав высокий результат по метрикам качества предсказывающей модели. Представленный здесь пользовательский интерфейс создан для демонстрации возможностей машинного обучения в решении реальных бизнес-задач и визуализации данных
                         """},
         'subheader_data': {'en': 'About the data', 'ru': 'О данных'},
         'data_desc': {'en': 'To train the model we were provided with data on Kaliningrad region, Russia, from 2019-01-01 to 2023-03-31. Test dataset continues the training one and contains data from 2023-04-01 to 2023-07-31',
                      'ru': 'Для обучения модели доступны данные по Калининградской области за период с 2019-01-01 по 2023-03-31. Тестовый датасет представляет собой продолжение обучающего и содержит данные за период с 2023-04-01 по 2023-07-31'},
         'data_columns': {'en': """
* **date** – calendar date
* **time** – time ranging from 0 to 23, meaning 24 hours in a day
* **target** – actual power consumption on a given date
* **temp** – actual air temperature on a given date
* **temp_pred** – temperature forecast on a given date
* **weather_pred** – weather forecast on a given date
                          """,
                          'ru': """
* **date** – дата
* **time** – время, время представлено в диапазоне 0 – 23, что означает 24 часа в сутках
* **target** – Фактическое потребление на указанную дату
* **temp** – фактическая температура на указанную дату
* **temp_pred** – прогноз температуры на указанную дату
* **weather_pred** – прогноз погоды на указанную дату
                          """},
         'subheader_plot': {'en': 'Target plot', 'ru': 'График целевой переменной'},
         'datetime': {'en': 'Time', 'ru': 'Время'},
         'target': {'en': 'Actual power consumption, MWh', 'ru': 'Фактическое потребление электроэнергии, МВт*ч'},
         'subheader_model': {'en': 'About the model', 'ru': 'О модели'}}


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
# show_pages(
#     [
#         Page("Home.py", text['menu_home'][st.session_state['language']], "🏠"),
#         Page("pages/1_Forecast.py", text['menu_forecast'][st.session_state['language']], ":chart_with_upwards_trend:"),
#         Page("pages/2_Archive.py", text['menu_archive'][st.session_state['language']], ":books:"),
#         Page("pages/3_About.py", text['menu_about'][st.session_state['language']], ":information_source:")
#     ]
# )
show_pages_from_config()
if st.session_state['language'] == 'ru':
    hide_pages(["Home", "Forecast for today", "Forecast history", "About the project"])
if st.session_state['language'] == 'en':
    hide_pages(["Главная", "Прогноз на сегодня", "История прогнозов", "О проекте"])

#define app section
header=st.container()
body=st.container()

#define header
with header:
    header.title(text['header'][st.session_state['language']])

with body:
    st.image('images/glowbyte_hack.jpg', caption='GlowByte Autumn Hack 2023')
    st.write(text['task_source'][st.session_state['language']])
    st.subheader(text['subheader_data'][st.session_state['language']])
    st.image('images/kaliningrad.jpg')
    st.write(text['data_desc'][st.session_state['language']])
    st.dataframe(st.session_state['pcp'].raw.head(10))
    st.markdown(text['data_columns'][st.session_state['language']])

    # Create a Plotly line chart for the model's predictions
    fig = px.line(st.session_state['pcp'].df, x='datetime', y='target', title=text['subheader_plot'][st.session_state['language']], labels={'datetime': text['datetime'][st.session_state['language']],
                                                                                                                        'target': text['target'][st.session_state['language']]})
    # Display the chart using st.plotly_chart()
    st.plotly_chart(fig)

    st.subheader(text['subheader_model'][st.session_state['language']])