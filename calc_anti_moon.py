import streamlit as st
import ephem
import calendar
import matplotlib
import numpy as np
import pandas as pd
import datetime as dt
from datetime import date, timedelta
from pytz import timezone
from math import degrees as deg
from math import radians as rad
from math import cos
from  streamlit_folium import st_folium
import folium

st.set_page_config(layout="wide")
st.title('Calcurate for the Moon')
st.header('ヘッダを表示')
st.subheader('サブヘッダを表示')
st.caption('キャプションを表示')

# Functions
def get_first_date(itime):
    return itime.replace(day=1)

def get_last_date(itime):
    return itime.replace(day=calendar.monthrange(itime.year, itime.month)[1])

def date_range(start_date, end_date):
    diff = (end_date - start_date).days + 1
    return (start_date + timedelta(i) for i in range(diff))

def calc_mlight(vp):
    moon.compute(vp)
    ALTITUDE = deg(moon.alt)
    PHASE = moon.moon_phase * deg(moon.alt)
    tALTITUDE = ALTITUDE / 90
    return round(tALTITUDE * PHASE, 6)

def phase_mlight(vp):
    moon.compute(vp)
    return round(moon.moon_phase, 6)

def alt_mlight(vp):
    moon.compute(vp)
    return round(deg(moon.alt), 6)

# Input arg string
i_year = st.slider(label='Year', min_value=2020, max_value=2040, value=2024)
i_month = st.slider(label='Month', min_value=1, max_value=12, value=2)
i = format(i_year) + '/' + format(i_month)
i_format = '%Y/%m'
itime = dt.datetime.strptime(i, i_format)

# 地図を表示
with st.expander('Location on map'):
    st.subheader('観測地点をクリック')
    # 地図の表示箇所とズームレベルを指定してマップデータを作成
    # attr（アトリビュート）は地図右下に表示する文字列。
    # デフォルトマップの場合は省略可能
    m = folium.Map(
      location=[35.6581, 139.7414],
      zoom_start=8,
      attr='Folium map'
    )
    st_data = st_folium(m, width=725)

    i_locate = st_data["last_clicked"]
    if type(i_locate) is None:
        i_locate = {'lat': 35.6580992222, 'lng': 139.7413574722}

# Body(天体)クラスのインスタンスを作成。
moon = ephem.Moon()

# Observer(観測者)クラスのインスタンスを作成。
vp = ephem.Observer()
vp.lat = i_locate['lat']
vp.lon = i_locate['lng']
vp.elevation = 60

df = pd.DataFrame()
df_phase = pd.DataFrame()
df_alt = pd.DataFrame()
row_list = []
row_list_2 = []
row_list_3 = []
for DATE in date_range(get_first_date(itime), get_last_date(itime)):
    lday = DATE.strftime("%Y/%m/%d")
    list_ = [lday]
    list_2 = [lday]
    list_3 = [lday]
    for TIME in range (12,24):
        u_DATE = timezone('UTC').localize(DATE)
        vp.date = dt.datetime(u_DATE.year, u_DATE.month, u_DATE.day, TIME, 30, 0, 0) - dt.timedelta(hours=9)
        list_.append(calc_mlight(vp))
        list_2.append(phase_mlight(vp))
        list_3.append(alt_mlight(vp))
    for TIME in range (0,12):
        u_DATE = timezone('UTC').localize(DATE)
        p_DATE = u_DATE + timedelta(days=1)
        vp.date = dt.datetime(p_DATE.year, p_DATE.month, p_DATE.day, TIME, 30, 0, 0) - dt.timedelta(hours=9)
        list_.append(calc_mlight(vp))
        list_2.append(phase_mlight(vp))
        list_3.append(alt_mlight(vp))
    row_list.append(list_)
    row_list_2.append(list_2)
    row_list_3.append(list_3)
    list_ = []
    list_2 = []
    list_3 = []

df = pd.DataFrame(row_list, columns = ['Date','12:30','13:30','14:30','15:30','16:30','17:30','18:30','19:30','20:30','21:30','22:30','23:30','0:30','1:30','2:30','3:30','4:30','5:30','6:30','7:30','8:30','9:30','10:30','11:30'])
df["Date"] = pd.to_datetime(df["Date"])
df["Date"] = df["Date"].dt.date
df = df.set_index("Date")

df_phase = pd.DataFrame(row_list_2, columns = ['Date','12:30','13:30','14:30','15:30','16:30','17:30','18:30','19:30','20:30','21:30','22:30','23:30','0:30','1:30','2:30','3:30','4:30','5:30','6:30','7:30','8:30','9:30','10:30','11:30'])
df_phase['Date'] = pd.to_datetime(df_phase['Date'])
df_phase['Date'] = df_phase['Date'].dt.date
df_phase = df_phase.set_index('Date')

df_alt = pd.DataFrame(row_list_3, columns = ['Date','12:30','13:30','14:30','15:30','16:30','17:30','18:30','19:30','20:30','21:30','22:30','23:30','0:30','1:30','2:30','3:30','4:30','5:30','6:30','7:30','8:30','9:30','10:30','11:30'])
df_alt["Date"] = pd.to_datetime(df_alt["Date"])
df_alt["Date"] = df_alt["Date"].dt.date
df_alt = df_alt.set_index("Date")

st.dataframe(df.style.background_gradient(cmap='viridis', axis=None).format('{:.2f}'), height=1122)

with st.expander('Moon phase.'):
    st.dataframe(df_phase.style.background_gradient(cmap='YlOrBr_r', axis=None).format('{:.2f}'), height=1122)

with st.expander('Alter for the moon.'):
    st.dataframe(df_alt.style.background_gradient(cmap='YlGn', axis=None).format('{:.2f}'), height=1122)