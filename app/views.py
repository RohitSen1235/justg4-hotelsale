from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from app.forms import SignUpForm
import random
import time
import pandas as pd
import numpy as np
import scipy.stats as stats
import xlwt

# declaring empty dataframe globaly for storing fetched data
data:pd.DataFrame
file_name:str =""


#  auxilary functions

def compute_chance_of_sale(input):
    
    global data
    
    mean_vector = [
            20196.902927927928, 
            251488.60382882884, 
            4123266.3087837836, 
            7473981.7263513515, 
            10636653.0990991, 
            67292.44234234234
            ]
    
    n=len(input)
    
    processed_data=process_data(input)
    
    processed_data['distance']=np.nan
    
    for i in range(n):
    
        bld_dis = (processed_data['Building Size (SF)'].iloc[i]-mean_vector[0])**2

        land_dis = (processed_data['Land (SF)'].iloc[i]-mean_vector[1])**2

        tot_Assets_dis = (processed_data['Total Assessment'].iloc[i]-mean_vector[2])**2

        last_sale_dis = (processed_data['Last Sale Price'].iloc[i]-mean_vector[3])**2

        last_loan_amt = (processed_data['Last Loan Amount'].iloc[i]-mean_vector[4])**2

        last_loan_ltv = (processed_data['Last Loan LTV'].iloc[i]-mean_vector[5])**2

        processed_data.loc[i,'distance']= (bld_dis + land_dis + tot_Assets_dis + last_sale_dis + last_loan_amt + last_loan_ltv)**0.5
    
    
    processed_data['scalled_dis']=abs(stats.zscore(processed_data['distance']))

    for i in range(n):

        if processed_data['scalled_dis'].iloc[i] >= 1.0:

            processed_data.loc[i,'scalled_dis']=random.randint(75,100) * 0.01
    
    processed_data['Chance_of_sale']=np.round((1-processed_data['scalled_dis'])*100,2)

    
    return processed_data['Chance_of_sale']


def get_attributes(data):
    
    df=data[['Building Size (SF)','Land (SF)','Total Assessment','Last Sale Price','Last Loan Amount','Last Loan LTV']]
    
    df['Land (SF)']             = df['Land (SF)'].replace('[\$,]', '', regex=True).astype(float)
    
    df['Building Size (SF)']    = df['Building Size (SF)'].replace('[\$,]', '', regex=True).astype(float)
    
    df['Total Assessment']      = df['Total Assessment'].replace('[\$,]', '', regex=True).astype(float)
    
    df['Last Sale Price']       = df['Last Sale Price'].replace('[\$,]', '', regex=True).astype(float)
    
    df['Last Loan Amount']      = df['Last Loan Amount'].replace('[\$,]', '', regex=True).astype(float)
    
    df['Last Loan LTV']         = df['Last Loan LTV'].replace('[\$\%,]', '',regex=True).astype(float)
    
    return df


def handle_missing_values(data):
    
    df2=data[data.columns[0:]].fillna(data[data.columns[0:]].median()).copy()
    
    return df2


def get_ref_vectors(data):
    
    mean_vec=[]
    
    std_vec=[]
    
    for i in data.columns:
    
      mean_vec.append(data[i].mean())
    
      std_vec.append(data[i].std())


    
    return mean_vec,std_vec


def process_data(data):
    
    df=get_attributes(data)
    
    df2=handle_missing_values(df)
    
    return df2


#  VIEWS
def index(request):
    
    content = {"result" : False}

    if request.method == "POST":

        global data
        global file_name

        time.sleep(random.randint(1,3))

        file= request.FILES.get('excel_file')

        file_name=file.name
        
        # print(file_name)
        
        data = pd.read_excel(file)

        # print(data.head(5))

        data['chance_of_sale'] = compute_chance_of_sale(data)

        # print(data[['Parcel ID','chance_of_sale']])

        percentile_90=data['chance_of_sale'].quantile(q=0.99)
        percentile_75=data['chance_of_sale'].quantile(q=0.75)
        percentile_50=data['chance_of_sale'].quantile(q=0.5)
        df=data['chance_of_sale']
        high_chance = df[df >= 90.0].count()
        good_chance = df[df >= 80.0].count() - (high_chance)
        med_chance  = df[df >= 70.0].count() - (good_chance + high_chance)
        some_chance = df[df >= 50.0].count() - (med_chance + good_chance + high_chance)
        not_worth = df[df < 50.0].count()

        content = {
                "result" : True,
                "90_percentile" : percentile_90,
                "75_percentile" : percentile_75,
                "50_percentile" : percentile_50,
                "high_chance" : high_chance,
                "good_chance" : good_chance, 
                "med_chance" :med_chance,
                "some_chance" :some_chance,
                "not_worth" : not_worth,
                "file_name" : file.name,
                }


    return render(request,"index.html",context=content)


def download_file(request):

    if request.method == 'POST':
        
        global data

        global file_name

        # setting respose type to be excel
        response = HttpResponse(content_type='application/ms-excel')
        # setting file name and type as attachment
        response['Content-Disposition'] = f'attachment; filename="{file_name}_sale_chance.xls" '
        # reading raw data
        raw_data=data
        # creating a new dataframe with only essential data
        download_data=raw_data[['Parcel ID','chance_of_sale']]
        # creating a excel workbook
        wb=xlwt.Workbook()
        # adding sheets to workbook
        ws=wb.add_sheet("Parcels_Probable Sale Chance")

        # adding transaction data to worksheet
        # setting font styleherok
        font_style_header = xlwt.XFStyle()
        font_style_header.font.bold = True

        columns=['Parcel ID','chance_of_sale']
        row_num=0
        for i in range(len(columns)):
            ws.write(row_num,i,columns[i],font_style_header)

        font_style_rows = xlwt.XFStyle()
        font_style_rows.font.bold = False

        offset=0
        for i in range(offset,len(download_data)):

            ws.write(i-offset+1, 0, download_data['Parcel ID'].iloc[i], font_style_rows)
            ws.write(i-offset+1, 1, download_data['chance_of_sale'].iloc[i], font_style_rows)

        wb.save(response)

        return(response)


def signin(request):
    
    content={}
    if request.method == "POST":

        form=User(request.POST)

        print(form)
        
        return redirect("/")
    else:

        return render(request,"login.html",context=content)


def signup(request):

    if request.method == "POST":
        
        form = SignUpForm(request.POST)

        if form.is_valid():
        
            user=form.save()
        
            print(user)
        
            return redirect("/registration_successful/")
    else:
        form = SignUpForm()

    content = {"form": form}

    return render(request,"signup.html",context=content)


def registration_successful(request):
    
    content={}

    return render(request,"registration_successful.html",context=content)