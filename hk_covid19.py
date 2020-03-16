import pandas as pd  
import io  
import requests  
  
url1="http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_wuhan_eng.csv"  
s=requests.get(url1).content  
hk=pd.read_csv(io.StringIO(s.decode('utf-8')))

hk1=hk.iloc[-1]['As of date']
hk2=hk.iloc[-1]['Number of confirmed cases']
hk3=hk.iloc[-1]['Number of ruled out cases']
hk4=hk.iloc[-1]['Number of cases still hospitalised for investigation']
hk5=hk.iloc[-1]['Number of cases fulfilling the reporting criteria']
hk6=hk.iloc[-1]['Number of death cases']
hk7=hk.iloc[-1]['Number of discharge cases']
hk8=hk.iloc[-1]['Number of probable cases']

print('Latest COVID-19 Statistics in HK', "\n"
      'Confirmed:', hk2, "\n"
      'Probable:', hk3, "\n"
      'Death:', hk4, "\n"
      'Discharged:', hk5, "\n"
      'Hospitalised:', hk6, "\n"
      'Ruled out:', hk7, "\n"
      'Reported:', hk8, "\n"
      '---------', "\n"
      'Data Source: data.gov.hk', "\n"
      'Last Updated on:', hk1, "\n"
      'Update Frequency: Every Night'  
      )


