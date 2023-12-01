#Load libraries needed
import streamlit as st
import plotly.express as px
import base64
from st_pages import Page, show_pages, add_page_title
from st_clickable_images import clickable_images
from model.power_comsumption_predictor import PowerConsumptionPredictor
from utils.excel_saver import to_excel
from utils.df_getter import get_df

if 'language' not in st.session_state:
    st.session_state['language'] = 'ru'
if 'pcp' not in st.session_state:
    st.session_state['pcp'] = PowerConsumptionPredictor(get_df())

#Set content dictionary
text = {'menu_home': {'en': 'Home', 'ru': 'Главная'},
         'menu_forecast': {'en': 'Forecast for today', 'ru': 'Прогноз на сегодня'},
         'menu_archive': {'en': 'Forecast history', 'ru': 'История прогнозов'},
         'header': {'en': 'Power consumption forecast for today', 'ru': 'Прогноз потребления электроэнергии на сегодня'},
        'preword': {'en': 'On this page you can predict power consumption in MWh for current date hour by hour',
                    'ru': 'На этой странице вы можете спрогнозировать энергопотребление в МВт*ч на текущую дату по часам'},
        'datetime': {'en': 'Date and Hour', 'ru': 'Дата и Час'},
        'pred': {'en': 'Predicted Value', 'ru': 'Прогнозное значение'},
        'down_button': {'en': '📥 Download Forecast', 'ru': '📥 Скачать прогноз'},
        'down_help': {'en': 'Download this table as .xlsx file', 'ru': 'Скачать эту таблицу в формате .xlsx'},
        'chart_title': {'en': "Model's Forecast", 'ru': 'Прогноз модели'},
        'caption': {'en': 'You could have noticed that "today" is always July 31, 2023 and the data in the table above seems pre-designed. That is due to the fact that July 31, 2023 is the last day in the data available. Though the forecast is being counted right now, when you load the page. With "true today" data provided forecast for it could easily be obtained as well',
                    'ru': 'Вы могли заметить, что "сегодня" это всегда 31 июля 2023, а значения в таблице кажутся подготовленными заранее. Дело в том, что 31 июля - это последний день, для которого у нас имеются данные. При этом прогноз по ним считается прямо сейчас, когда вы загружаете страницу. Если предоставить модели данные по "настоящему сегодняшнему дню", можно так же легко получить прогноз и по ним'}}

#Define forecast dates
START_TEST = '2023-07-31'
END_TEST = '2023-07-31'

forecast = st.session_state['pcp'].forecast_today(START_TEST, END_TEST)

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
        Page("pages/2_Archive.py", text['menu_archive'][st.session_state['language']], ":books:")
    ]
)

#define app section
header=st.container()
prediction=st.container()

#define header
with header:
    header.title(text['header'][st.session_state['language']])
    header.write(text['preword'][st.session_state['language']])

with prediction:
    col1, col2 = st.columns([0.72, 0.28])
    with col1: 
        st.dataframe(forecast, hide_index=True, column_config={'datetime': st.column_config.DatetimeColumn(label=text['datetime'][st.session_state['language']], format='DD.MM.YYYY, HH'),
                                                            'predict': st.column_config.NumberColumn(label=text['pred'][st.session_state['language']], format='%.2f')}, width=280)
    with col2:
        df_xlsx = to_excel(forecast)
        st.download_button(label=text['down_button'][st.session_state['language']],
                                    data=df_xlsx ,
                                    file_name=f'{START_TEST}_power_consumption_forecast.xlsx',
                                    help=text['down_help'][st.session_state['language']])
        
    st.caption(text['caption'][st.session_state['language']])

    # Create a Plotly line chart for the model's predictions
    fig = px.line(forecast, x='datetime', y='predict', title=text['chart_title'][st.session_state['language']], labels={'datetime': text['datetime'][st.session_state['language']],
                                                                                                                        'predict': text['pred'][st.session_state['language']]})
    # Display the chart using st.plotly_chart()
    st.plotly_chart(fig)

st.markdown(
    """
    <style>
        div[data-testid="column"]
        {
            align-self: flex-end;
        } 
    </style>
    """, unsafe_allow_html=True
)