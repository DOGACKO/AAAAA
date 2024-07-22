import time  # for simulating real-time data, time loop
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import altair as alt
import streamlit as st  # data web application development

# Streamlit page configuration (must be the first Streamlit command)
st.set_page_config(layout="wide")

# Load the data
Erimiş = pd.read_excel("C:/Users/dkoral/Desktop/Haziran_Erimişler_2024_py.xlsx")

# Define regions and their corresponding branches
regions_dict = {
    'İstanbul 1. Bölge': ['Bahçeşehir Şubesi', 'Taksim Şubesi', 'Beylikdüzü Şubesi', 'Yeşilyurt Şubesi', 'Maslak Şubesi', 'Güneşli Şubesi'],
    'İstanbul 2. Bölge': ['Kalamış Şubesi', 'Ataşehir Şubesi', 'Maltepe Şubesi', 'Bağdat Caddesi Şubesi', 'Tuzla Şubesi'],
    'İstanbul 3. Bölge': ['Levent Şubesi', 'Nişantaşı Şubesi'],
    'Batı Anadolu Bölge': ['Bodrum Şubesi', 'Bursa Şubesi', 'Denizli Şubesi', 'Ege Şubesi', 'Eskişehir Şubesi', 'İzmir Şubesi', 'Dokuz Eylül Şubesi', '9 Eylül Şubesi'],
    'Anadolu Bölge': ['Adana Şubesi', 'Anadolu Şubesi', 'Antalya Şubesi', 'Başkent Şubesi', 'Diyarbakır Şubesi', 'Gaziantep Şubesi', 'Kayseri Şubesi', 'Mersin Şubesi', 'Samsun Şubesi', 'Trabzon Şubesi'],
    'Ankara Şubesi': ['Ankara Şubesi'],
    'Yatırım Danışmanlığı Merkezi': ['Yatırım Danışmanlığı Merkezi'],
    'Hepsi': ['Bahçeşehir Şubesi', 'Taksim Şubesi', 'Beylikdüzü Şubesi', 'Yeşilyurt Şubesi', 'Maslak Şubesi', 'Güneşli Şubesi','Kalamış Şubesi', 'Ataşehir Şubesi', 'Maltepe Şubesi', 'Bağdat Caddesi Şubesi', 'Tuzla Şubesi','Levent Şubesi', 'Nişantaşı Şubesi','Bodrum Şubesi', 'Bursa Şubesi', 'Denizli Şubesi', 'Ege Şubesi', 'Eskişehir Şubesi', 'İzmir Şubesi', 'Dokuz Eylül Şubesi', '9 Eylül Şubesi','Adana Şubesi', 'Anadolu Şubesi', 'Antalya Şubesi', 'Başkent Şubesi', 'Diyarbakır Şubesi', 'Gaziantep Şubesi', 'Kayseri Şubesi', 'Mersin Şubesi', 'Samsun Şubesi', 'Trabzon Şubesi','Ankara Şubesi','Yatırım Danışmanlığı Merkezi']
}

# Sidebar for user input
st.sidebar.title("Gösterge Paneli Ayarları")
st.sidebar.markdown("### *Ayarlar*")

# Select region
selected_region = st.sidebar.selectbox('Bölge Seçimi', list(regions_dict.keys()))

# Filter branches based on selected region
filtered_branches = regions_dict[selected_region]

# Select branches within the selected region
selected_branches = st.sidebar.multiselect('Şube Seçimi', filtered_branches, default=filtered_branches)

# List of Months
month_columns = ['Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz']
selected_months = st.sidebar.multiselect('Ayları Seçin', month_columns, default=month_columns)

# Filter data based on selections
filtered_data = Erimiş[Erimiş['Şube'].isin(selected_branches)]

# Filter the data based on selected months
monthly_data = filtered_data[['Müşteri Adı', 'Şube', 'Gelir'] + selected_months].copy()
monthly_data['Toplam_Gelir'] = monthly_data[selected_months].sum(axis=1)

# Pivot table creation
try:
    pivot_table = monthly_data.pivot_table(
        values='Toplam_Gelir',  # Total Gelir for selected months
        index='Müşteri Adı',  # Customer names
        columns='Şube',  # Branches
        aggfunc='sum',  # Aggregation function
        fill_value=0  # Fill missing values with 0
    )
except KeyError as e:
    st.error(f"KeyError: {e}. Lütfen sütun isimlerini kontrol edin.")
    pivot_table = pd.DataFrame()  # Set to empty DataFrame to avoid further errors

pivot_table.reset_index(inplace=True)

if not pivot_table.empty:
    pivot_chart = alt.Chart(pivot_table.melt(id_vars=['Müşteri Adı'], var_name='Şube', value_name='Toplam_Gelir')).mark_bar().encode(
        x=alt.X('Müşteri Adı:N', title='Müşteri'),
        y=alt.Y('Toplam_Gelir:Q', title='Toplam Gelir'),
        color=alt.Color('Şube:N', title='Şube'),
        tooltip=['Müşteri Adı:N', 'Şube:N', 'Toplam_Gelir:Q']
    ).properties(
        height=400,
        width=600,
        title='Müşteri ve Şubeye Göre Gelir'
    )

# Şube Bazında Gelir dağılımı
branch_revenue = monthly_data.groupby('Şube')['Toplam_Gelir'].sum().reset_index()
branch_pie_chart = alt.Chart(branch_revenue).mark_arc().encode(
    theta=alt.Theta(field='Toplam_Gelir', type='quantitative'),
    color=alt.Color(field='Şube', type='nominal'),
    tooltip=[alt.Tooltip('Şube:N', title='Şube'), alt.Tooltip('Toplam_Gelir:Q', title='Gelir')]
).properties(
    height=300,
    title='Şubelere Göre Gelir Dağılımı'
)

# Müşteri & Gelir
top_customers = monthly_data.groupby('Müşteri Adı')['Toplam_Gelir'].sum().reset_index().sort_values(by='Toplam_Gelir', ascending=False).head(10)
top_customers_chart = alt.Chart(top_customers).mark_bar().encode(
    x=alt.X('Müşteri Adı:N', title='Müşteri'),
    y=alt.Y('Toplam_Gelir:Q', title='Toplam Gelir'),
    color=alt.Color('Müşteri Adı:N', legend=None),
    tooltip=['Müşteri Adı:N', 'Toplam_Gelir:Q','Şube:N']
).properties(
    height=300,
    title='Gelirine Göre İlk 10 Müşteri'
)

# Şube Bazında Ortalama Gelir
avg_revenue_branch = monthly_data.groupby('Şube')['Toplam_Gelir'].mean().reset_index()
avg_revenue_branch_chart = alt.Chart(avg_revenue_branch).mark_bar().encode(
    x=alt.X('Şube:N', title='Şube'),
    y=alt.Y('Toplam_Gelir:Q', title='Ortalama Gelir'),
    color=alt.Color('Şube:N', legend=None),
    tooltip=[alt.Tooltip('Şube:N', title='Şube'), alt.Tooltip('Toplam_Gelir:Q', title='Ortalama Gelir')]
).properties(
    height=300,
    title='Şubelere Göre Ortalama Gelir'
)


Gerçekleşmiş_Erime_Oranı = 1.21
# Average Annual Account Amount
avg_account_amount = Gerçekleşmiş_Erime_Oranı
st.sidebar.metric(label="Erime Oranı", value=f"{avg_account_amount:.2f}%")
#komisyon geliri
avg_gelir = 13684265.00
# Binlik ayırıcılarıyla ve ondalıklı biçimlendirme
formatted_avg_gelir = "{:,.2f}".format(avg_gelir)

# Sidebar'da gösterim
st.sidebar.metric(label="Erimişlerin Komisyon Geliri", value=formatted_avg_gelir)
# Display the charts
st.title("Erimişler Gösterge Paneli")
st.markdown("### Şube ve Müşteriye Göre Gelir Analizi")

st.altair_chart(pivot_chart, use_container_width=True)
st.altair_chart(branch_pie_chart, use_container_width=True)
st.altair_chart(top_customers_chart, use_container_width=True)
st.altair_chart(avg_revenue_branch_chart, use_container_width=True)
