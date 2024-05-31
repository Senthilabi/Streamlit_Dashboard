import streamlit as st
import pandas as pd 
import numpy as np 
import datetime as dt 
from PIL import Image 
import plotly.express as px
import plotly.graph_objects as go
import os
st.set_page_config(page_title='Adidas Dashboard',layout='wide',page_icon=':medal:')
#st.write('Hello World')
df=pd.read_excel('Adidas.xlsx')
#st.write(df.shape)
df.head()
st.title('Sales Dashboard :medal:')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
f1=st.file_uploader('Drop your file here',type=(['csv','pdf','txt','xlsx','xls']))
if f1 is not None:
    file_name=f1
    st.write(file_name)
    df=pd.read_csv(file_name)#,encoding ='ISO-8859-1')
else:
    df=pd.read_excel('Adidas.xlsx')#,encoding ='ISO-8859-1')
col1, col2=st.columns((2))
df['InvoiceDate']=pd.to_datetime(df['InvoiceDate'])
startDate=pd.to_datetime(df['InvoiceDate']).min()
endDate=pd.to_datetime(df['InvoiceDate']).max()
with col1:
    date1=pd.to_datetime(st.date_input('Start date',startDate))
with col2:
    date2=pd.to_datetime(st.date_input('End date',endDate))
df1=df[(df['InvoiceDate']>=date1 )& (df['InvoiceDate']<= date2)].copy()
#st.sidebar.header('Choose Your Region')
#selcting the Region
region=st.sidebar.multiselect('Pick Your Region', df1['Region'].unique())
if not region:
    df2=df1
else:
    df2=df1[df1['Region'].isin(region)]
#Selecting State
state=st.sidebar.multiselect('Pick Your State', df2['State'].unique())
if not state:
    df3=df2
else:
    df3=df2[df2['State'].isin(state) ]

city=st.sidebar.multiselect('Pick Your City', df3['City'].unique())
if not city:
    df4=df3
else:
    df4=df3[df3['City'].isin(city) ]
if not region and not state and not city:
    filtered_df=df
elif not state and not city:
    filtered_df=df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df=df[df['State'].isin(state)]
elif not state and not region:
    filtered_df=df[df['City'].isin(city)]
elif not state:
    filtered_df=df[(df['Region'].isin(region)) & (df['City'].isin(city))]
elif not region:
    filtered_df=df[(df['State'].isin(region)) & (df['City'].isin(city))]
elif not city:
    filtered_df=df[(df['Region'].isin(region)) & (df['State'].isin(state))]
else :
    filtered_df=df3
retailer_df=filtered_df.groupby(by=['Retailer'] , as_index=False)['TotalSales'].sum()
with col1:
    st.subheader('Retailerwise Sales')
    fig=px.bar(retailer_df,x='Retailer',y='TotalSales')#,text=['$ { : , .2f}'.format(x) for x in retailer_df['TotalSales']])
    st.plotly_chart(fig,use_container_width=True,height=200)

with col2:
    st.subheader('Region wise sales')
    fig=px.pie(filtered_df,values='TotalSales',names='Region',hole=0.5 )
    fig.update_traces(text=filtered_df['Region'], textposition='outside')
    st.plotly_chart(fig,use_container_width=True)

cl1,cl2 =st.columns(2)
with cl1:
    with st.expander('Retailer_Viewdata'):
        st.write(retailer_df.style.background_gradient(cmap='Blues'))
        csv= retailer_df.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data',data=csv,file_name='retailer.csv', mime='text/csv',
                    help='Click here to download as CSV')
with cl2:
    with st.expander('Region_Viewdata'):
        region=filtered_df.groupby(by='Region' , as_index=False)['TotalSales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv= region.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data',data=csv,file_name='region.csv', mime='text/csv',
                    help='Click here to download as CSV')
filtered_df['month_year']=filtered_df['InvoiceDate'].dt.to_period('M')
st.subheader('Time Series Data')
linechart=pd.DataFrame(filtered_df.groupby(
                        filtered_df['month_year'].dt.strftime('%Y: %b') )
                        ['TotalSales'].sum()
                        ).reset_index()
fig2=px.line(linechart,x='month_year',y='TotalSales',
                labels={'TotalSales ':'Amount'},height=500,width=1000, template='gridon'
                )
st.plotly_chart(fig2,use_container_width=True)
#Creating a tree map based on Region, State and City
st.subheader('Hierarchical View of sale')
fig3 =px.treemap(filtered_df,path=['Region', 'Retailer'],hover_data=['TotalSales'],values='UnitsSold',
color='Retailer')
fig3.update_layout(width=800, height=600)
st.plotly_chart(fig3,use_container_width=True)

chart1,chart2=st.columns(2)
with chart1:
    st.subheader('Productwise Sales')
    fig4= px.pie(filtered_df,values='TotalSales',names='Product',template='plotly_dark')
    fig.update_traces(text=filtered_df['Product'],textposition='inside')
    st.plotly_chart(fig4,use_container_width=True)
with chart2:
    st.subheader('Retailer wise Sales')
    fig4= px.pie(filtered_df,values='TotalSales',names='Retailer',template='plotly_dark')
    fig.update_traces(text=filtered_df['Retailer'],textposition='inside')
    st.plotly_chart(fig4,use_container_width=True)


    
import plotly.figure_factory as ff 
st.subheader(' :point_right: Monthwise Product sales summary')
with st.expander('Summary Table'):
    df_sample=df[0:5][['Region','State','City','Product','TotalSales']]
    fig=ff.create_table(df_sample,colorscale='Cividis')
    st.plotly_chart(fig,use_container_width=True)
    st.subheader('Monthwise Retailer data')
    filtered_df['Month']=filtered_df['InvoiceDate'].dt.month_name()
    Retailer_year=pd.pivot_table(data=filtered_df,index='Retailer',values='TotalSales',columns='Month')
    st.write(Retailer_year.style.background_gradient(cmap='Blues'))
#create a scatterplot
plot1=px.scatter(filtered_df,x='TotalSales',y='OperatingProfit', size='UnitsSold')
plot1['layout'].update(title='Sales Vs Profit',titlefont=dict(size=20),
                        xaxis=dict(title='TotalSales',titlefont=dict(size=19)),
                        yaxis=dict(title='OPeratingProfit',titlefont=dict(size=19))
                        )
st.plotly_chart(plot1,use_container_width=True)
with st.expander('View data'):
    st.write(filtered_df.iloc[:500,0:20].style.background_gradient(cmap='Oranges'))








#image=Image.open('adidas-logo.jpg')