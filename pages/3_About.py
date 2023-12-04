import streamlit as st
import pandas as pd
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
         'subheader_model': {'en': 'About the model', 'ru': 'О модели'},
         'model_desc': {'en': 'In this competition we were to solve a regression task on tabular data. Expectedly top rating positions were taken by various realizations of gradient boosting. However throughout our experiments it occured that a two models ensemble performed better than just a boosting. So first we fitted an l1-regulirized linear regression for its nulifying weights of insignificant features as well as linear models capacity to extrapolate. Then to achieve better quality of prediction we counted the models error and fitted gradient boosting on it. You can read about fitting and testing processes in more detail [here](%s)',
                      'ru': 'В этом соревновании мы работали над задачей регрессии на табличных данных. Ожидаемо все лучшие позиции в рейтинге заняли различные реализации градиентного бустинга. Однако в ходе наших экспериментов лучше, чем просто бустинг показал себя ансамбль из двух моделей. Первым этапом мы обучили линейную регрессию с регуляризацией l1, ради зануления весов незначимых признаков, а также способности линейных моделей к экстраполяции. Затем для повышения точности рассчитали ошибку этой модели и на ней обучили градиентный бустинг. Подробнее об обучении и тестировании вы можете почитать [здесь](%s)'},
         'subheader_features': {'en': 'About the features', 'ru': 'О признаках'},
         'features_desc': {'en': 'Since the forecast quality in this project depended mainly on successful feature engineering, let us have a look at the final feature importances according to the models estimate (both models: linear regression and gradient boosting). Please find below just the top 10 of the features',
                           'ru': 'Поскольку успех предсказания в этой задаче зависел главным образом от генерации информативных признаков, рассмотрим итоговую важность признаков по оценкам моделей (обеих, линейной регрессии и бустинга). Ограничимся топ-10 признаками'},
         'feat_imp': {'en': 'Feature importance', 'ru': 'Важность признаков'},
         'feature': {'en': 'Feature', 'ru': 'Признак'},
         'importance': {'en': 'Weighted importance', 'ru': 'Взвешенная важность'},
         'feat_list': {'en': """
* **target_lag_24** – target value exactly 24 hours (1 day) ago
* **yesterday_median_target** – target median for preceding day (from 0 a.m. to 11 p.m.)
* **target_lag_168** – target value exactly 168 hours (7 days) ago
* **yesterday_mean_temp** – mean temperature for preceding day (from 0 a.m. to 11 p.m.)
* **target_lag_144** – target value exactly 144 hours (6 days) ago
* **day** – calendar day, i.e. the day's number in a month
* **temp_pred** – temperature forecast for current hour
* **dow** – day of week (0 for Monday, 6 for Sunday)
* **target_lag_96** – target value exactly 96 hours (4 days) ago
* **time** – time, i.e. number of the hour in a day
                          """,
                          'ru': """
* **target_lag_24** – значение целевого признака ровно 24 часа (1 сутки) назад
* **yesterday_median_target** – медиана целевого признака за предшествующие сутки (с 0 по 23 час)
* **target_lag_168** – значение целевого признака ровно 168 часов (7 суток) назад
* **yesterday_mean_temp** – средняя температура за предшествующие сутки (с 0 по 23 час)
* **target_lag_144** – значение целевого признака ровно 144 часа (6 суток) назад
* **day** – число по календарю (номер дня в месяце)
* **temp_pred** – прогноз температуры на текущий час
* **dow** – день недели (0 - понедельник, 6 - воскресенье)
* **target_lag_96** – значение целевого признака ровно 96 часов (4 суток) назад
* **time** – время (номер часа в сутках)
                          """}
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
    url = "https://github.com/maria-bichun/power_consumption_forecast_app/blob/main/notebook/two_stage_model_fitting.ipynb"
    st.markdown(text['model_desc'][st.session_state['language']] % url)
    st.subheader(text['subheader_features'][st.session_state['language']])
    st.write(text['features_desc'][st.session_state['language']])

    imp = pd.DataFrame({'feature': ['target_lag_24', 'yesterday_median_target', 'target_lag_168', 'yesterday_mean_temp', 'target_lag_144',
                                   'day', 'temp_pred', 'dow', 'target_lag_96', 'time'], 
                                   'importance': [24.7588, 7.0092, 6.0116, 5.7363, 5.7204, 5.1386, 4.9217, 4.6008, 3.6869, 3.5399]})
    fig = px.bar(imp, x="importance", y="feature", orientation='h',
                 title=text['feat_imp'][st.session_state['language']], 
                 labels={'feature': text['feature'][st.session_state['language']], 'importance': text['importance'][st.session_state['language']]},
             hover_data=["importance"],
             height=400)
    fig.update_layout(yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig)
    st.markdown(text['feat_list'][st.session_state['language']])