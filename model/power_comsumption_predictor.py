import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
import warnings
warnings.filterwarnings("ignore")

class PowerConsumptionPredictor():
    def __init__(self, df):
        #Get dataset
        self.raw = df
        #add features
        self.df = self.preprocess(self.raw)
        #Get predictor models
        with open("model/model1.pkl" , 'rb') as file:  
            self.lin_model = pickle.load(file)
        with open("model/model2.pkl" , 'rb') as file:  
            self.lgbm_model = pickle.load(file)
    
    #Preprocessing functions
    def preprocess(self, df):
        #fix some minor missing values in weather forecasts
        df = df.ffill()
        #add features
        df = self.add_calendar_features(df)
        df = self.add_lags(df)
        df = self.add_weather_and_daylight(df)
        df = self.add_daysoff(df)
        df = self.add_sin_cos_time(df)
        df = self.add_school_vacations(df) 
        #add datetime single column for outputs
        df['timestr'] = [f'0{str(hour)}:00:00' if hour < 10 else f'{str(hour)}:00:00' for hour in df['time']]
        df['datetime'] = df['date'].astype('str') + ' ' + df['timestr']
        df.drop('timestr', axis=1, inplace=True)
        return(df)

    def add_calendar_features(self, df):
        """
        Функция извлекает из даты и добавляет в датафрейм календарные фичи: день (число), 
        день недели, номер недели, месяц, год
        """
        df['date'] = pd.to_datetime(df['date']).dt.normalize()
        df['dow'] = df['date'].dt.dayofweek
        df['day'] = df['date'].dt.day
        df['week'] = df['date'].dt.isocalendar().week.astype('int32')
        df['month'] = df['date'].dt.month

        #OHE code month
        months = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun',
                7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'}
        for month in months:
            df[months[month]] = np.where((df['month'] == month), 1, 0)

        return df

    def add_lags(self, df):
        """
        Функция добавляет избранные лаги для целевой переменной и температуры
        """
        #add target lags
        for i in [24, 24*2, 24*3, 24*4, 24*5, 24*6, 24*7, 25, 26, 49]:
            df[f'target_lag_{i}'] = df['target'].shift(i)

        #add yesterdays target and temperature statistics
        for feature in ['target', 'temp']:
            daily = df.groupby('date', as_index=False)[feature].agg(daily_mean='mean', daily_median='median', daily_max='max', daily_min='min')
            for stat in ['mean', 'median', 'max', 'min']:
                daily[f'yesterday_{stat}_{feature}'] = daily[f'daily_{stat}'].shift(1)
            df = df.merge(daily[['date', f'yesterday_mean_{feature}', f'yesterday_median_{feature}', f'yesterday_max_{feature}', f'yesterday_min_{feature}']], how='left', on='date')
            df[f'yesterday_diff_{feature}'] = df[f'yesterday_max_{feature}'] - df[f'yesterday_min_{feature}']

        #add a temperature lag
        for i in range(1,5):
            df[f'temp_lag_{i}'] = df['temp'].shift(24*i)

        #delete nans where there's no lag data (start of period)
        df['na_sum'] = df.isna().sum(axis=1)
        df = df[df['na_sum'] == 0]
        df = df.drop('na_sum', axis=1)

        #drop actual temperature as it causes dataleaks
        df = df.drop('temp', axis=1)

        return df

    def add_weather_and_daylight(self, df):
        """
        Функция обрабатывает данные о природном освещении и погоде, создавая в итоге бинарный 
        признак, помечающий часы, когда должно быть светло, потому что солнце над горизонтом,
        но темно из-за погодных условий. Мы используем прогнозную погоду во избежание утечек
        """
        #create columns for certain bad weather types
        bad_weathers = {'пасм': 'overcast', 'дожд': 'rain', 'снег': 'snow', 
                        'ливень': 'heavy_rain', 'гроз': 'thunder', 'шторм': 'storm'}
        for weather_type in bad_weathers:
            df[bad_weathers[weather_type]] = np.where(df['weather_pred'].str.contains(weather_type), 1, 0)

        #process cloudy separately so that not to include 'малообл' 
        df['cloudy'] = np.where((df['weather_pred'].str.contains(' обл')) |
                                (df['weather_pred'].str.startswith('обл')), 1, 0)
        
        #read and preprocess our table with sunset and sunrise times for each day
        daylight = pd.read_csv('data/light_day.csv')
        daylight = daylight.rename(columns={'Дата': 'date', 'Восход': 'sunrise', 'Заход': 'sunset'})
        daylight = daylight[['date', 'sunrise', 'sunset']]
        daylight['date'] = pd.to_datetime(daylight['date']).dt.normalize()
        daylight['day'] = daylight['date'].dt.day
        daylight['month'] = daylight['date'].dt.month
        daylight['sunrise'] = daylight['sunrise'].str.replace(':', '.').str.lstrip('0').astype('float')
        daylight['sunset'] = daylight['sunset'].str.replace(':', '.').str.lstrip('0').astype('float')
        daylight = daylight[['day', 'month', 'sunrise', 'sunset']]

        #merge sunset and sunrise data to original df
        df_with_daylight = df.merge(daylight, on=['month', 'day'], how='left')

        #mark light hours, i.e. those between sunrise and sunset
        df_with_daylight['light'] = np.where(df_with_daylight['time'].between(df_with_daylight['sunrise'], 
                                                                        df_with_daylight['sunset']), 1, 0)
        
        #mark hours that should be light but are dark because of bad weather conditions
        df_with_daylight['dark_weather'] = np.where((df_with_daylight['light'] == 1) & 
                                    (df_with_daylight[['rain', 'heavy_rain', 'thunder', 
                                                    'storm', 'snow', 'overcast', 'cloudy']].any(axis='columns') == 1), 1, 0)
        
        #drop interim features that didn't prove useful
        df_with_daylight = df_with_daylight.drop(['weather_pred', 'sunrise', 'sunset', 'cloudy', 'heavy_rain', 
                                                'thunder', 'storm', 'overcast', 'rain', 'snow', 'light'], axis=1)

        return df_with_daylight

    def add_daysoff(self, df):
        """
        Функция загружает файлы производственных календарей, обрабатывает их и проставляет 
        метку 1 для всех выходных и праздничных дней. Эта категория шире суббот и воскресений
        (что мы ранее извлекли из даты), т.к. включает дополнительно государственные праздники
        и нерабочие дни, объявленные указами президента
        Кроме того, функция создает столбец "рабочий час", отмечая единицами часы, являющиеся
        рабочими по производственному календарю с учетом коротких дней перед праздниками
        """
        #read and preprocess tables with Russian production calendars
        c19 = pd.read_csv('data/calendar2019.csv')
        c20 = pd.read_csv('data/calendar2020.csv')
        c21 = pd.read_csv('data/calendar2021.csv')
        c22 = pd.read_csv('data/calendar2022.csv')
        c23 = pd.read_csv('data/calendar2023.csv')

        def get_daysoff(df, year):
            """
            Функция принимает датафрейм производственного календаря и возвращает список
            всех выходных дней в соответствующем году
            """
            months = {'Январь': '01', 'Февраль': '02', 'Март': '03', 'Апрель': '04', 'Май': '05', 'Июнь': '06',
            'Июль': '07', 'Август': '08', 'Сентябрь': '09', 'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12'}
            
            yearly_daysoff = []
            yearly_short = []
            for month in months:
                #filter out days with *. these are working short days before a holiday
                daysoff = [day for day in df[month].item().split(',') if '*' not in day]            
                daysoff = [day if len(day) > 1 else '0'+day for day in daysoff]

                #make a separate list of short working days (prior to a holiday)
                short_days = [day for day in df[month].item().split(',') if '*' in day]
                short_days = [day if len(day) > 1 else '0'+day for day in short_days]

                #format as proper dates
                daysoff = [(year + '-' + months[month] + '-' + day) for day in daysoff]
                yearly_daysoff.extend(daysoff)
                short_days = [(year + '-' + months[month] + '-' + day) for day in short_days]
                yearly_short.extend(short_days)

            return yearly_daysoff, yearly_short

        #get days off for all 5 years
        all_daysoff = []
        all_short = []
        years = {'2019': c19, '2020': c20, '2021': c21, '2022': c22, '2023': c23}
        for year in years:
            all_daysoff.extend(get_daysoff(df=years[year], year=year)[0])
            all_short.extend(get_daysoff(df=years[year], year=year)[1])

        #add daysoff and short feature to original df
        df['dayoff'] = np.where(df['date'].astype('str').isin(all_daysoff), 1, 0)
        df['working_short'] = np.where(df['date'].astype('str').isin(all_short), 1, 0)

        #mark working hours
        df['working_hour'] = np.where(((df['dayoff'] == 0) & (df['working_short'] == 0) & (df['time'].isin(list(range(9, 18))))) |
                                    ((df['dayoff'] == 0) & (df['working_short'] == 1) & (df['time'].isin(list(range(9, 17))))), 1, 0)
        
        df = df.drop('working_short', axis=1)

        return df    

    def add_sin_cos_time(self, df):
        """
        Функция заменяет оригинальное время (по 24-часовой шкале) его циклической
        категоризацией. Это нужно для того, чтобы расстояние между 23 и 0 часов не было
        больше, чем для любой другой пары соседних часов
        """
        def cos_sin_categorise(data, cos_column_name, sin_column_name, column_to_categorise):
            """
            Применяет cos-sin тригонометрическую категоризацию
            :param data: DataFrame содержащий данные
            :param cos_column_name: Название будущей колонки с cos
            :param sin_column_name: Название будущей колонки с sin
            :param column_to_categorise: Назване колонки, которое хотим категоризовать
            """
            data[cos_column_name] = np.cos((2*np.pi *data[column_to_categorise])/data[column_to_categorise].nunique())
            data[sin_column_name] = np.sin((2*np.pi *data[column_to_categorise])/data[column_to_categorise].nunique())

        cos_sin_categorise(data=df, cos_column_name='cos_time', sin_column_name='sin_time', column_to_categorise='time')
        return df

    def add_school_vacations(self, df):
        """
        Функция отмечает единицами дни школьных каникул и нулями - все остальные дни
        """
        vacs = pd.read_csv('data/holidays.csv')
        vacs = vacs.rename(columns={'Дата': 'date', 'Каникулы': 'school_vac'})
        vacs['date'] = pd.to_datetime(vacs['date']).dt.normalize()
        df = df.merge(vacs, on='date', how='left')
        return df
    
    #count metrics
    def evaluate(self, y_true, y_pred, model_name):
        """
        Функция рассчитывает и выводит метрики модели
        :param y_true: вектор истинных значений целевой переменной
        :param y_pred: вектор предсказаний модели
        :model_name: имя модели (для вывода)
        """
        mae = mean_absolute_error(y_true, y_pred)
        mape = mean_absolute_percentage_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        #print metrics...
        # metrics = {'MAE': mae, 'MAPE': mape, 'r2': r2}
        # for metric in metrics:
        #     print(f"{model_name} {metric}: {metrics[metric]}")

        #... and return them
        return mae, mape, r2   
    
    #prediction functions
    def predict_first(self, df):
        df['pred_stage1'] = self.lin_model.predict(df[['target_lag_24', 'target_lag_96', 'target_lag_120', 'target_lag_144', 'target_lag_168', 'temp_pred', 'dow', 
                                                'day', 'week', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'cos_time', 'working_hour', 'dark_weather', 'yesterday_diff_temp']])
        df['stage1_error'] = df['target'] - df['pred_stage1']
        return df

    def predict_second(self, df, start_date, end_date):
        #get test part of the df
        test = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        X_test = test[['target_lag_24', 'target_lag_48', 'target_lag_72', 'target_lag_96', 'target_lag_120', 'target_lag_144', 'target_lag_168', 'target_lag_25',
                'target_lag_26', 'target_lag_49', 'temp_pred', 'dow', 'day', 'month', 'time', 'yesterday_median_target', 'yesterday_mean_temp',
                'dayoff', 'dark_weather', 'temp_lag_1', 'temp_lag_2', 'temp_lag_3', 'temp_lag_4', 'school_vac']]

        preds = self.lgbm_model.predict(X_test) 
        preds = pd.DataFrame({'error_predicted': preds, 'datetime': test['datetime'], 'y_true': test['target'], 'stage1_predict': test['pred_stage1']}) 
        preds['y_pred'] = preds['stage1_predict'] + preds['error_predicted']
        
        #submission
        sub = pd.DataFrame({'datetime': preds['datetime'], 'predict': preds['y_pred']})
        return sub
    
    #make forecast for today
    def forecast_today(self, start_date, end_date):
        self.df = self.predict_first(self.df)
        return self.predict_second(self.df, start_date, end_date)
    
    #compare historic forecast to fact
    def forecast_vs_fact(self, start_date, end_date):
        self.df = self.predict_first(self.df)
        pred = self.predict_second(self.df, start_date, end_date)
        return pred.merge(self.df, how='left', on='datetime')[['datetime', 'predict', 'target']]
        
