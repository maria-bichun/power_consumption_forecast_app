#Load libraries needed
import streamlit as st
from st_pages import Page, show_pages, add_page_title
import base64
from st_clickable_images import clickable_images
from model.power_comsumption_predictor import PowerConsumptionPredictor
from utils.df_getter import get_df

if 'language' not in st.session_state:
    st.session_state['language'] = 'ru'



#Set content dictionary
text = {'menu_home': {'en': 'Home', 'ru': 'Главная'},
         'menu_forecast': {'en': 'Forecast for today', 'ru': 'Прогноз на сегодня'},
         'menu_archive': {'en': 'Forecast history', 'ru': 'История прогнозов'},
         'menu_about': {'en': 'About the project', 'ru': 'О проекте'},
         'app_title': {'en': 'Power oracle', 'ru': 'Энергетический оракул'},
         'welcome': {'en': 'Welcome to Power consumption forecasting app!', 'ru': 'Добро пожаловать в Приложение, прогнозирующее потребление электроэнергии!'},
         'intro_text': {'en': 'Constant power consumption growth is one of the most significant and hard challenges faced by the contemporary society. During the last decades power demand has been increasing dramatically, and it\'s a phenomenon of global nature. Optimization of spending resourses is the humanity\'s task of a high priority, and advanced technology can assist in that',
                        'ru': 'Постоянный рост потребления электроэнергии - это один из наиболее заметных и сложных вызовов, стоящих перед современным обществом. В течение последних десятилетий спрос на электричество стремительно возрастает, и это явление имеет глобальный характер. Оптимизация расходования ресурсов - приоритетная задача человечества, и передовые технологии приходят в этом на помощь'},
         'project_task': {'en': 'Purpose of this project was to develop a robust and precise model for forecasting power consumption for one day in Kaliningrad region, Russia, using historical data available. We bring to your attention the result',
                          'ru': 'Целью этого проекта было разработать надежную и точную модель прогнозирования объема энергопотребления на сутки для Калининградской области с использованием доступных исторических данных. Представляем вашему вниманию результат'},
         'app_contents': {'en': 'Things You Can Do On This App:', 'ru': 'В этом приложении вы можете:'},
         'bullets': {'en': """
            - Forecast power consuption for today by hour
            - Compare past forecasts to actual target and estimate the forecasting model's quality
            - Get to know more about the project, task and data behind this app
            """,
            'ru': """
            - Получить почасовой прогноз потребления электроэнергии на сегодняшний день
            - Сравнить прогнозы для прошедших дней с фактическим энергопотреблением и оценить качество модели
            - Узнать больше о проекте, задаче и данных, на которых обучена модель
            """}
         }

# Set page configuration 
st.set_page_config(
    page_title=text['app_title'][st.session_state['language']]
)

if 'pcp' not in st.session_state:
    st.session_state['pcp'] = PowerConsumptionPredictor(get_df())

#add a sidebar to select pages
with st.sidebar:
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
    add_page_title()

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


# Add header
header_container = st.container()
with header_container:
    st.header(text['app_title'][st.session_state['language']])
    st.write(text['welcome'][st.session_state['language']])
    st.write(text['intro_text'][st.session_state['language']])

# Create a Streamlit container for the subheader
subheader_container = st.container()

# Define the subheader content
with subheader_container:
    st.write(text['project_task'][st.session_state['language']])
    st.subheader(text['app_contents'][st.session_state['language']])
    st.markdown(text['bullets'][st.session_state['language']])
