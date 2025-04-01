import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel,Field
from typing import Literal
import pandas as pd
import ast

load_dotenv()
#Defining output moddel
class output_model(BaseModel):
    sentiment: Literal["Positive","Neutral","Negative"]
    pros: list[str]
    cons: list[str]
    summary: list[str]

#https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
df = pd.read_csv('IMDB Dataset.csv', on_bad_lines='skip')
print(f"Input: {df.iloc[0,0]}")

df2 = pd.DataFrame(columns=["Sample_index","Review","Actual_sentiment","Predicted_sentiment","Pros_sentiment","Cons_sentiment","Summary"])

def get_output_chatGPT(input_dataframe,output_dataframe,sample_count):
  retesting_count = 3
  output_dataframe_index = int(sample_count * retesting_count)
  for i in range(0,sample_count,1):
    for j in range(0,retesting_count,1):
      prompt = "you are an expert sentiment analyzer and given below is your task list: " \
      "1. Caterorize the sentiment into either positive, negative or neutral" \
      "2. give pros supporting the sentiment. 3. cons that contradict the sentiment. " \
      "4. summarize the text."

      client = OpenAI(api_key=os.environ['OPENAI_KEY'])

      completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
          {"role": "system", "content": prompt},
          {"role": "user", "content": df.iloc[i,0]}
        ],response_format=output_model
      )

      output = completion.choices[0].message
      print("\n\n\n",output)
      output = ast.literal_eval(output.content)
      print(type(output_model))
      # output_dataframe.iloc[j,0] = i + 1
      # output_dataframe.iloc[j,1] = input_dataframe.iloc[i,0]
      # output_dataframe.iloc[j,2] = input_dataframe.iloc[i,1]
      # output_dataframe.iloc[j,3] = output.content.sentiment
      # output_dataframe.iloc[j,4] = output.content.pros
      # output_dataframe.iloc[j,5] = output.content.cons
      # output_dataframe.iloc[j,6] = output.content.summary
      dataframe_append = {"Sample_index": i+1,"Review": input_dataframe.iloc[i,0],"Actual_sentiment": input_dataframe.iloc[i,1],
                          "Predicted_sentiment":output["sentiment"] ,"Pros_sentiment":output["pros"],
                          "Cons_sentiment": output["cons"],"Summary":output["summary"]}

      output_dataframe.loc[len(output_dataframe)] = dataframe_append
  return output_dataframe

df2 = get_output_chatGPT(df,df2,2)
df2.to_csv('sample_output.csv')