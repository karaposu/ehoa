import subprocess
from subprocess import run, PIPE
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import yaml
from utils import get_categories, extract_categories, get_hierarchical_categories, extract_rules, create_rules_yaml
from langchain_core.prompts import PromptTemplate
from extract_table import extract_table_from_pdf
import pandas as pd
from tqdm import tqdm
import ast
import re


def is_service_enabled(service_name):
    try:
        result = subprocess.run(['systemctl', 'is-enabled', service_name],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip() == 'enabled'
        else:
            print(f"Error checking service status: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# def classify_record_with_keyword(record, categories, parent_path=""):
#     for category, subcategories in categories.items():
#         current_path = f"{parent_path} > {category}" if parent_path else category
#         if isinstance(subcategories, dict):
#             for subcategory, details in subcategories.items():
#                 if 'keywords' in details:
#                     for keyword in details['keywords']:
#                         if keyword.lower() in record.lower():
#                             return f"{current_path} > {subcategory}"
#                 result = classify_record_with_keyword(record, {subcategory: details}, current_path)
#                 if result:
#                     return result
#         elif isinstance(subcategories, list):
#             for item in subcategories:
#                 if isinstance(item, dict):
#                     for subcategory, details in item.items():
#                         if 'keywords' in details:
#                             for keyword in details['keywords']:
#                                 if keyword.lower() in record.lower():
#                                     return f"{current_path} > {subcategory}"
#                         result = classify_record_with_keyword(record, {subcategory: details}, current_path)
#                         if result:
#                             return result
#     return None



def classify_record_with_keyword(record):

    return None

def check_record_for_keywords(record, categories):
    def search_keywords(record, categories, path=[]):
        for category in categories:
            for key, value in category.items():
                current_path = path + [key]
                rules = value.get('keyword', [])
                if any(keyword in record for keyword in rules):
                    return current_path
                subcategories = value.get('subcategories', [])
                result = search_keywords(record, subcategories, current_path)
                if result:
                    return result
        return None

    return search_keywords(record, categories)

class ExpandedDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

def refine_answer(llm, answer_to_be_refined ) :


    refiner_template= '''
    Here is a text {answer_to_be_refined}.  i want you to extract information by searching for Main Category and Subcategory and 
    give me answer in following format
     {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }} 
       do not output extra information! 
    '''

    # refiner_template = '''Here is an answer from another LLM for my question. {answer_to_be_refined} I want you to format the answer in following format
    #  {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }}
    #  do not output extra information! '''
    prompt = PromptTemplate.from_template(refiner_template)
    formatted_prompt = prompt.format(answer_to_be_refined=answer_to_be_refined)
    r = llm.invoke(formatted_prompt)
    return r
def classify_record(llm, record,classes ):

    keyword_based_classification_result = classify_record_with_keyword(record)
    if keyword_based_classification_result is None:

        classes_string = yaml.dump(classes, default_flow_style=False, Dumper=ExpandedDumper)

        # print("....")
        # print("classes_string", classes_string)

        template2= '''
        Prompt Template
        Record:
        {record}

        Category Structure:
        
        {classes}
        
        Task Description:
        
        Identify the Main Category: Determine which of the main categories (e.g., Food & Dining, Utilities, etc.) the string belongs to.
        Determine the Subcategory: Once the main category is identified, determine the specific subcategory within that main category (e.g., within Food & Dining, identify whether it is Groceries, Restaurants, Coffee, or Takeout).
        Extra Information - Rules: There is additional information under each subcategory labeled as 'rules'. These rules include 'keyword' and 'text_based' but should be considered as extra information and not directly involved in the classification task.
        Instructions:
        
        Given the string record, first identify the main category, and then the specific subcategory within that main category. Ignore the 'rules' section as it is for additional context.
        
        Examples:
        Record: "Grocery shopping at Walmart"
        Main Category: Food & Dining
        Subcategory: Groceries
        
        Record: "Monthly electricity bill"
        Main Category: Utilities
        Subcategory: Electricity and Water and Gas
        '''

#         template2= '''
#         Task Description
# When classifying a string, the model should:
#
# Identify the Main Category: Determine which of the main categories (e.g., Food & Dining, Utilities, etc.) the string belongs to.
# Determine the Subcategory: Once the main category is identified, determine the specific subcategory within that main category (e.g., within Food & Dining, identify whether it is Groceries, Restaurants, Coffee, or Takeout).
# Extra Information - Rules: There is additional information under each subcategory labeled as 'rules'. These rules include 'keyword' and 'text_based' but should be considered as extra information and not directly involved in the classification task.
# Example
# Given the string "Grocery shopping at Walmart":
#
# Main Category: Food & Dining
# Subcategory: Groceries
# Another example, "Monthly electricity bill":
#
# Main Category: Utilities
# Subcategory: Electricity and Water and Gas
# Rules
# Each subcategory has associated rules for more detailed classifications, which include keywords and text-based rules. These rules can provide additional context but are not the primary factors for determining the main category and subcategory.
#
#         '''

        # template2 = '''Here is a record of a bank transaction {record}.
        #                ANd here is category-subcategory couples {classes} aa.
        #                understand which category-subcategory couple record belongs to.
        #                 categorize this record into one of categorized.
        #                 and then once category is determined, pick one of the most likely subcategory from same category.
        #
        #               Answer should be in this format with no other extra information or text
        #                 {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }} '''

        # template2 = '''Here is a record of a bank transaction {record}.
        #       you will help me understand categorize this record into one of these  {classes} while being careful about extra information
        #       also once you categorize the record, pick the most suitable subcategory too. (choose subcategory only from belonging to category)
        #       Answer should be in this format with no other extra information or text
        #         {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }} '''

        # template3 = '''Here is my record of my bank transaction {record}.
        # Now classify the record semantically into one these categories and subcategories >{classes}.
        # Make use of data given together with classes!
        # Answer should be in this format with no other extra information or text
        #   {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }} '''

        prompt = PromptTemplate.from_template(template2)
        formatted_prompt = prompt.format(record=record, classes=classes_string)
        r = llm.invoke(formatted_prompt)
        return r


def get_statements(pdf_document_path, bank_name):
    df = extract_table_from_pdf(pdf_document_path, bank_name)
    return df


def postprocess(result_df, raw_df):
    pass


def string_to_dict(string):
    # Ensure the string is enclosed with curly braces if it isn't already
    string = string.strip()
    if not string.startswith("{"):
        string = "{" + string
    if not string.endswith("}"):
        string = string + "}"

    # Replace single quotes with double quotes and handle null values
    clean_string = string.replace("'", '"').replace("null", "None").strip()

    # Remove any characters after the closing brace
    clean_string = re.sub(r'}.*$', '}', clean_string)

    # Add missing quotes around keys and values
    clean_string = re.sub(r'(\w+):', r'"\1":', clean_string)  # Add quotes around keys
    clean_string = re.sub(r': ([\w\s]+)', r': "\1"', clean_string)  # Add quotes around values

    try:
        # Use ast.literal_eval to safely evaluate the string as a dictionary
        return ast.literal_eval(clean_string)
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing string: {clean_string}\n{e}")
        return None

# def string_to_dict(string):
#     clean_string = string.replace("'", '"').replace("null", "None").strip()
#     try:
#         return ast.literal_eval(clean_string)
#     except (SyntaxError, ValueError) as e:
#         print(f"Error parsing string: {clean_string}\n{e}")
#         return None


def do_analysis(llm,llm_refiner,  pdf_document_path, bank_name):
    table_df = get_statements(pdf_document_path, bank_name)
    descs = table_df["Açıklama"].tolist()
    classes = get_hierarchical_categories('categories.yaml')
    # print(" ")
    # print("classes: ", classes)
    # raw_string_answer = classify_record(llm,  descs[0], classes)
    # print("raw_string_answer:", raw_string_answer)
    # r = refine_answer(llm_refiner, raw_string_answer)

    results = []
    for e in tqdm(descs[:10], desc="Classifying records"):
        raw_string_answer = classify_record(llm, e, classes)
        refined_answer = refine_answer(llm_refiner, raw_string_answer)
        if refined_answer:
            r = string_to_dict(refined_answer)
            if r:
                results.append(r)
            else:
                results.append({'category': 'Uncategorized', 'subcategory': 'Uncategorized'})
        else:
            results.append({'category': 'Uncategorized', 'subcategory': 'Uncategorized'})

    result_df = pd.DataFrame(results)
    table_df['category'] = result_df['category']
    table_df['subcategory'] = result_df['subcategory']
    file_name = 'results_all.csv'
    table_df["Tutar"] = table_df["Tutar"].apply(convert_tutar)
    table_df.to_csv(file_name, index=False)

   # table_df["Tutar"] = table_df["Tutar"].apply(convert_tutar)

    return table_df


def convert_tutar(tutar):
    return -float(tutar.replace(" TL", "").replace(".", "").replace(",", ".").replace(" ", ""))


def main():
    pdf_document_path = "./sample_pdfs/sample1.pdf"
    llm = Ollama(model="gemma2")

    llm_refiner = Ollama(model="gemma:2b")
   # llm_refiner = Ollama(model="tinyllama")

    #ollama run gemma:2b
    #ollama run tinyllama

    table_df = get_statements(pdf_document_path, "")
    descs = table_df["Açıklama"].tolist()
    classes = get_hierarchical_categories('categories.yaml')
    # print(" ")
    # print("classes: ", classes)
    # raw_string_answer = classify_record(llm, descs[0], classes)
    # print("raw_string_answer:", raw_string_answer)
    #
    # r= refine_answer(llm_refiner, raw_string_answer)
    # print("refined: ", r)
    # r = string_to_dict(r)
    # print("refined dict: ", r)


    result_df = do_analysis(llm,llm_refiner,  pdf_document_path, "")
    print(result_df)

    # category_totals = result_df.groupby("category")["Tutar"].sum().reset_index()
    # category_totals.columns = ["Category", "Value"]
    #
    # # Group by "category" and "subcategory" and sum the "Tutar" column
    # subcategory_totals = result_df.groupby(["category", "subcategory"])["Tutar"].sum().reset_index()
    # subcategory_totals.columns = ["Category", "Subcategory", "Value"]
    #
    # print(category_totals)



if __name__ == '__main__':
    main()
