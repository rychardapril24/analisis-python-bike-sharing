import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def get_total_hours_df(hours_df):
  hours_cal_df =  hours_df.groupby(by="hr").agg({
    "count_cr": ["sum"],
    })
  return hours_cal_df

def days_cal_df(days_df):
    days_df_all = days_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return days_df_all


def total_registered_df(days_df):
   reg_df =  days_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(days_df):
   cas_df =  days_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def sum_order (hours_df):
    sum_order_items_df = hours_df.groupby("hr").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def kind_season (days_df): 
    season_df = days_df.groupby(by="season").count_cr.sum().reset_index() 
    return season_df

def get_category_days(dayweek):
    if dayweek in ("Saturday", "Sunday"):
        return 'Weekend'
    else: 
        return 'Weekdays'

def pembagian_waktu(jam):
    if 6 <= jam <= 11:
        return 'Pagi'
    elif 12 <= jam <= 15:
        return 'Siang'
    elif 16 <= jam <= 18:
        return 'Sore'
    else:
        return 'Malam'




days_df = pd.read_csv("days_procdata.csv")
hours_df = pd.read_csv("hours_procdata.csv")

hours_df['periode'] = hours_df['hr'].apply(pembagian_waktu)
hours_df['Kategori'] = hours_df.apply(lambda row: get_category_days( row['day']), axis=1)

datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)   

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

min_date_hour = hours_df["dteday"].min()
max_date_hour = hours_df["dteday"].max()

with st.sidebar:
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
  
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hours = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

hours_cal_df = get_total_hours_df(main_df_hours)
days_df_all = days_cal_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hours)
season_df = kind_season(main_df_hours)


#Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing :sparkles:')

st.subheader('Bike Sharing 2011-2012')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = days_df_all.count_cr.sum()
    st.metric("Total User", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

st.subheader("Number of Rent per Month (2011 - 2012)")

fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(
    days_df["dteday"],
    days_df["count_cr"],
    marker='o', 
    linewidth=2,
    color= "#86A9BF"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)
st.text("Berdasarkan grafik diatas, Rental tertinggi pada bulan September 2012. Selain itu, kita juga dapat melihat adanya penurunan"+ 
        "jumlah order yang cukup signifikan pada bulan Mei 2011, September 2011, Mei 2012, dan November 2012.")

st.subheader("Pada jam berapa Rental Sepeda ramai dan sepi?")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 10))

sns.barplot(x="hr", y="count_cr", data=sum_order_items_df.head(5), palette=["#EEEBE1", "#EEEBE1", "#86A9BF", "#EEEBE1", "#EEEBE1"], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours", fontsize=30)
ax[0].set_title("Jam Rental Sepeda Terbanyak", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="hr", y="count_cr", data=sum_order_items_df.sort_values(by="hr", ascending=True).head(5), palette=["#EEEBE1", "#EEEBE1", "#EEEBE1", "#EEEBE1","#86A9BF"], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours",  fontsize=30)
ax[1].set_title("Jam Rental Sepeda Tersedikit", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)
st.text("Jam rental sepeda terbanyak pada jam 17:00 sebanyak 336860, dan untuk jam rental sepeda tersedikit jam 04:00 sebanyak 4428 ")


st.subheader("Pada musim apa rental sepeda ramai ?")

colors = ["#EEEBE1", "#EEEBE1", "#EEEBE1", "#86A9BF"]
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
        y="count_cr", 
        x="season",
        data=season_df.sort_values(by="season", ascending=False),
        palette=colors,
        ax=ax
    )
ax.set_title("Grafik Rental Sepeda Antar Musim", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)
st.text("Musim paling banyak dalam penyewaan sepeda adalah musim <b>Fall atau Musim Gugur </b> dengan perkiraan 5900 setiap tahunnya")

st.subheader("Perbandingan Customer yang Registered dan Casual")

labels = 'casual', 'registered'
sizes = [18.8, 81.2]
explode = (0, 0.1) 

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',colors=["#EEEBE1", "#86A9BF"],
        shadow=True, startangle=90)
ax1.axis('equal')  

st.pyplot(fig1)
st.text("User yang ter-registrasi ada 81.2% dibandingkan user yang casual hanya 18.8%")


st.subheader("Analisis Clustering")
col4, col5= st.columns(2)

with col4:
    st.text("Clustering Kategori Hari")
    dayweeks = hours_df.groupby(by="day").agg({
    "count_cr" : ["count"],
    "Kategori": ["unique"],})

    dayweeks.columns = ['Jumlah', 'Kategori',]
    st.write(dayweeks)

with col5:
    st.text("Clustering Periode Jam")
    periods = hours_df.groupby(by="hr").agg({
    "count_cr": ["count"],
    "periode": ["unique"],})
    periods.columns = ['Jumlah', 'Periode',]
    st.write(periods)

