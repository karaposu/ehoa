
from langchain_community.llms import Ollama
import pandas as pd
from tqdm import tqdm
from utils import get_hierarchical_categories
from utils  import classify_and_refine
from prompt_templates import  template1, refiner_template2
from langchain.chains import SimpleChain, SequentialChain

import os
from langchain.llms import OpenAI

# llm = OpenAI(model="gpt-4")

llm = Ollama(model="gemma2")
llm_refiner = Ollama(model="gemma:2b")

# categorizer_llm = SimpleChain(llm=llm, prompt_template=template1)
# categorizy_formatter_llm = SimpleChain(llm=llm, prompt_template=refiner_template2)


r1= " Encard Harcaması, SHOP SOKOLOV BAPB MINSK BY, 49.04 USD, işlem kuru 33.130000 TL"
r2= " Encard Harcaması, WEBPOS SATIŞ IYZICO/AMAZON.COM.TR ISTANBUL TRTR."

descs= [r1, r2]
categories_and_rules, list_of_main_categories, list_of_subcategories = get_hierarchical_categories(
        'categories.yaml')


classification_result, raw_string_answer, refined_answer = classify_and_refine(llm, template1,
                                                                               llm_refiner, refiner_template2,
                                                                               r1,
                                                                               categories_and_rules,
                                                                                list_of_main_categories,
                                                                        list_of_subcategories)


# print("raw_string_answer: ", raw_string_answer)

# results = []
# raw_answers = []
# refined_answers = []
# for e in tqdm(descs, desc="Classifying records"):
#     classification_result, raw_string_answer, refined_answer = classify_and_refine(llm, template1,  llm_refiner, e,
#                                                                                    categories_and_rules,
#                                                                                    list_of_main_categories,
#                                                                         list_of_subcategories)
#     raw_answers.append(raw_string_answer)
#     refined_answers.append(refined_answer)
#     results.append(classification_result)

