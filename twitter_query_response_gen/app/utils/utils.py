from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from ..config import config
from ..prompts import prompts
from .schemas import llm1_output_model,llm2_output_model,llm3_output_model
import json

input_customer_review = "I got a phone and dress from amazon. The phone works fine, but the dress is too loose."
llm1 = ChatOpenAI(model = "gpt-4o",temperature=0.5,api_key=config.settings.openai_key,
              max_retries=2)

# Set up a parser
llm1_parser = PydanticOutputParser(pydantic_object=llm1_output_model)

# Prompt
llm1_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "{llm1_instruction}. Wrap the output:\n{format_instructions}",
        ),
        ("human", "{query}"),
    ]
).partial(format_instructions=llm1_parser.get_format_instructions()) 

llm1_chain = llm1_prompt | llm1 | llm1_parser
llm1_output = llm1_chain.invoke({'llm1_instruction':prompts.llm1_prompt,'query':input_customer_review})
print(llm1_output,"\n")

llm2 = ChatGroq(temperature=0.5, groq_api_key=config.settings.grokai_key, model_name="llama-3.3-70b-versatile")

# Set up a parser
llm2_parser = PydanticOutputParser(pydantic_object=llm2_output_model)

# Prompt
llm2_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "{llm2_instruction}. Wrap the output: \n{format_instructions}",
        )
    ]
).partial(format_instructions=llm2_parser.get_format_instructions()) 

llm1_sub_part_list = []
llm1_issue_list = []
for output in llm1_output.output:
    llm1_sub_part_list.append(output.sub_part)
    llm1_issue_list.append(output.issue)

llm2_chain = llm2_prompt | llm2 | llm2_parser
llm2_output = llm2_chain.invoke({'llm2_instruction':prompts.llm2_prompt.format(llm1_sub_part_output=llm1_sub_part_list,llm1_issue_output=llm1_issue_list)})

print(llm2_output,"\n")

llm2_sub_part_list = []
llm2_issue_list = []
llm2_sentiment_list = []
for output in llm2_output.output:
    llm2_sub_part_list.append(output.sub_part)
    llm2_issue_list.append(output.issue)
    llm2_sentiment_list.append(output.sentiment)

llm3 = ChatMistralAI(temperature=0.5, mistral_api_key=config.settings.mistralai_key, model_name="mistral-small-latest")

# Set up a parser
llm3_parser = PydanticOutputParser(pydantic_object=llm3_output_model)

# Prompt
llm3_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "{llm3_instruction}. Wrap the output: \n{format_instructions}",
        )
    ]
).partial(format_instructions=llm3_parser.get_format_instructions()) 

llm3_chain = llm3_prompt | llm3 | llm3_parser
llm3_output = llm3_chain.invoke({'llm3_instruction':prompts.llm3_prompt.format(llm2_sub_part_output=llm2_sub_part_list,
                                                                 llm2_issue_output=llm2_issue_list,llm2_sentiment_output=llm2_sentiment_list)})

print(llm3_output)