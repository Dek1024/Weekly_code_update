import pandas as pd

df = pd.read_excel('175_Dayananda.xlsx',sheet_name='Sheet1')
df_1 = pd.read_csv('output.csv')

# df = df.merge(df_1,how='inner',left_on='Email ID',right_on='Email ID')
#df = df.merge(df_1,how='inner',on='Email ID')
result = pd.merge(df,df_1,how="inner",left_on='Email ID',right_on='Email Id')
#result = pd.concat([df,df_1],axis=1,join='inner')
result.to_excel("checking_combined_ouput.xlsx",sheet_name='results')