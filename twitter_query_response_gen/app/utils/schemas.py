from pydantic import BaseModel
from typing import List, Literal

#Output model for LLM1 - openAI
class llm1_ouput_model_content(BaseModel):
    sub_part: str
    issue: str

class llm1_output_model(BaseModel):
    output: List[llm1_ouput_model_content]

#Output model for LLM2 - grok
class llm2_output_model_content(llm1_ouput_model_content):
    sentiment: Literal["positive","neutral","negative"]

class llm2_output_model(BaseModel):
    output: List[llm2_output_model_content]

#Output model for LLM3 - mistral
class llm3_output_model(BaseModel):
    response: str