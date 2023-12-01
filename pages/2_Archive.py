##Load libraries
import streamlit as st
import plotly.express as px
import datetime
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
if 'show_prediction_message' not in st.session_state:
    st.session_state['show_prediction_message'] = False

#Set content dictionary
text = {'menu_home': {'en': 'Home', 'ru': 'Главная'},
         'menu_forecast': {'en': 'Forecast for today', 'ru': 'Прогноз на сегодня'},
         'menu_archive': {'en': 'Forecast history', 'ru': 'История прогнозов'},
         'header': {'en': 'Forecast history', 'ru': 'История прогнозов'},
        'preword': {'en': 'On this page you can select dates, get forecast in MWh and compare it to real power consuption for the corresponding period',
                    'ru': 'На этой странице вы можете выбрать даты, получить для них прогноз в МВт*ч и сравнить его с реальным энергопотреблением за соответствующий период'},
        'calendar_label': {'en': "Select start and end of period of interest", 'ru': 'Выберите начало и конец интересующего вас периода'},
        'pred_button': {'en': 'Predict', 'ru': 'Прогноз'},
        'datetime': {'en': 'Date and Hour', 'ru': 'Дата и Час'},
        'pred': {'en': 'Predicted Value', 'ru': 'Прогнозное значение'},
        'fact': {'en': 'Actual Value', 'ru': 'Фактическое значение'},
        'down_button': {'en': '📥 Download Forecast', 'ru': '📥 Скачать прогноз'},
        'down_help': {'en': 'Download this table as .xlsx file', 'ru': 'Скачать эту таблицу в формате .xlsx'},
        'chart_title': {'en': "Model's Forecast VS Actual Value", 'ru': 'Прогноз модели / Фактическое значение'},
        'value': {'en': 'Value', 'ru': 'Значение'},
        'chart_var': {'en': 'Power Consumption, MWh', 'ru': 'Энергопотребление, МВт*ч'},
        'chart_pred': {'en': 'Forecast', 'ru': 'Прогноз'},
        'chart_fact': {'en': 'Fact', 'ru': 'Факт'},
        'metrics': {'en': "Prediction quality metrics", 'ru': 'Метрики качества предсказания'}}

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

# Set up the data section that users will interact with
with prediction:
    with st.form('date_select'):
        col1, col2 = st.columns([0.72, 0.28])
        with col1:
            # Define Streamlit inputs
            dates = st.date_input(label=text['calendar_label'][st.session_state['language']], 
                            value=(datetime.date(2023, 7, 24), datetime.date(2023, 7, 30)), 
                            min_value=datetime.date(2023, 4, 1), 
                            max_value=datetime.date(2023, 7, 30))
        with col2:
            # Create a button
            predicted = st.form_submit_button(text['pred_button'][st.session_state['language']])

    # Upon predicting
    if predicted or st.session_state['show_prediction_message']:
        st.session_state['show_prediction_message'] = True  # Set the flag to True when the "Predict" button is pressed
        start_date, end_date = (x.strftime('%Y-%m-%d') for x in dates)
        forecast_fact = st.session_state['pcp'].forecast_vs_fact(start_date, end_date)

        col1, col2 = st.columns([0.72, 0.28])
        with col1: 
            ##Adding visua#lof model prediction        
            st.dataframe(forecast_fact, hide_index=True, column_config={'datetime': st.column_config.DatetimeColumn(label=text['datetime'][st.session_state['language']], format='DD.MM.YYYY, HH'),
                                                                        'predict': st.column_config.NumberColumn(label=text['pred'][st.session_state['language']], format='%.2f'),
                                                                        'target': st.column_config.NumberColumn(label=text['fact'][st.session_state['language']], format='%.2f')}, width=460)
        with col2:
            df_xlsx = to_excel(forecast_fact)
            st.download_button(label=text['down_button'][st.session_state['language']],
                                    data=df_xlsx ,
                                    file_name=f'{start_date}_to_{end_date}_forecast_vs_fact.xlsx',
                                    help=text['down_help'][st.session_state['language']])

        # Create a Plotly line chart for the model's predictions
        to_plot = ['predict', 'target']
        fig = px.line(forecast_fact, x='datetime', y=to_plot, title=text['chart_title'][st.session_state['language']], labels={'datetime': text['datetime'][st.session_state['language']],
                                                                                                                        'value': text['value'][st.session_state['language']],
                                                                                                                        'variable': text['chart_var'][st.session_state['language']]})
        newnames = {'predict':text['chart_pred'][st.session_state['language']], 'target': text['chart_fact'][st.session_state['language']]}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                            legendgroup = newnames[t.name],
                                            hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                            )
                        )

        # Display the chart using st.plotly_chart()
        st.plotly_chart(fig)

        #Display metrics
        metrics = st.session_state['pcp'].evaluate(forecast_fact['target'], forecast_fact['predict'], 'Final model')
        st.subheader(text['metrics'][st.session_state['language']])
        st.markdown(f"""
                 * MAE = {metrics[0]:.4f}
                 * MAPE = {metrics[1]:.4f}
                 * r2 = {metrics[2]:.4f}""")
        
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