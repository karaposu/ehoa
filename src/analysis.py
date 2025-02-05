import subprocess
from subprocess import run, PIPE
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import yaml
from utils import get_categories, extract_categories,  extract_rules, create_rules_yaml
from utils import classify_record_with_keyword, check_record_for_keywords , ExpandedDumper, string_to_dict
from utils import get_hierarchical_categories
from utils  import classify_and_refine

from langchain_core.prompts import PromptTemplate
from extract_table import extract_table_from_pdf
import pandas as pd
from tqdm import tqdm
import ast
import re
from prompt_templates import  template1, refiner_template2



def get_statements(pdf_document_path, bank_name):
    df = extract_table_from_pdf(pdf_document_path, bank_name)
    return df

def classify_record_with_bank_pattern(desc, bank_classification_patterns):
    for pattern in bank_classification_patterns:
        match = re.search(pattern['pattern'], desc)
        if match:
            # print(f"Pattern matched: {pattern['pattern']}, Description: {desc}")  # Debugging output
            return {
                'category': pattern['category'],
                'subcategory': pattern['subcategory']
            }
        else:
            pass
            # print(f"Pattern not matched: {pattern['pattern']}, Description: {desc}")  # Debugging output
    return None




def find_category_and_subcategory(desc,
                                  llm,template1,
                                  llm_refiner,
                                  refiner_template2,
                                  categories_and_rules,
                                  list_of_main_categories,
                                  list_of_subcategories,
                                  bank_classification_patterns):
    by_bank_pattern = True
    by_keyword_rule = False

    categories_keywords = extract_categories_and_keywords(categories_and_rules)

    classification_result = classify_record_with_bank_pattern(desc, bank_classification_patterns)
    raw_string_answer = "."
    refined_answer = "."

    if classification_result is None:
        by_bank_pattern = False

        # Try to classify using keyword-based method
        keyword_based_classification_result = classify_record_with_keyword(desc, categories_keywords)
        if keyword_based_classification_result is None:

            # Use LLM-based classification

            classification_result, raw_string_answer, refined_answer = classify_and_refine(llm, template1,
                                                                                           llm_refiner,
                                                                                           refiner_template2,
                                                                                           desc,
                                                                                           categories_and_rules,
                                                                                           list_of_main_categories,
                                                                                       list_of_subcategories)
            if classification_result is None:
                return {'category': 'Uncategorized',
                        'subcategory': 'Uncategorized'}, by_bank_pattern, by_keyword_rule, raw_string_answer, refined_answer

        else:
            # If keyword-based classification is successful
            by_keyword_rule = True
            classification_result = keyword_based_classification_result
            raw_string_answer = "-"
            refined_answer = "-"

    return classification_result, by_bank_pattern, by_keyword_rule, raw_string_answer, refined_answer


def get_bank_patterns(file_path, bank_name):
    with open(file_path, 'r') as file:
        patterns = yaml.safe_load(file)
    if bank_name in patterns['banks']:
        return patterns['banks'][bank_name]
    else:
        raise ValueError(f"No patterns found for bank: {bank_name}")


def extract_identifier_section(record):
    # Define the patterns to match various sections, ensuring "Gelen Transfer" or "Giden Transfer" are included in the identifier
    patterns = [
        r'(Giden Transfer, [^,]+),',  # Matches 'Giden Transfer'
        r'(Gelen Transfer, [^,]+),',  # Matches 'Gelen Transfer'
        r'Encard Harcaması, ([^,]+?)(?=\d+\.\d+ [A-Z]{3}|,|$)',  # Improved to handle line breaks and end of string
        r'Ödeme, ([^,]+)-',  # Matches 'Ödeme'
        r'Para Çekme, ([^,]+),',  # Matches 'Para Çekme'
        r'Masraf/Ücret, ([^,]+),',  # Matches 'Masraf/Ücret'
        r'Diğer, ([^\n]+)$',  # Matches 'Diğer' till the end or newline
    ]

    # Merge patterns into a single regex with alternation
    combined_pattern = '|'.join(patterns)
    match = re.search(combined_pattern, record, re.DOTALL)  # Use DOTALL to match across multiple lines
    if match:
        # Return the first non-empty group found
        return next(group for group in match.groups() if group is not None)

    return None


# def extract_identifier_section(record):
#     # Combining patterns into a single regex for efficiency
#     patterns = [
#         r'Giden Transfer, ([^,]+),',  # Matches 'Giden Transfer'
#         r'Encard Harcaması, ([^,]+?)(?=\d+\.\d+ [A-Z]{3}|,|$)',  # Improved to handle line breaks and end of string
#         r'Ödeme, ([^,]+)-',  # Matches 'Ödeme'
#         r'Gelen Transfer, ([^,]+),',  # Matches 'Gelen Transfer'
#         r'Para Çekme, ([^,]+),',  # Matches 'Para Çekme'
#         r'Masraf/Ücret, ([^,]+),',  # Matches 'Masraf/Ücret'
#        # r'Diğer, ([^,]+),',  # Matches 'Diğer'
#         r'Diğer, ([^\n]+)$',  # Matches 'Diğer' till the end or newline
#     ]
#
#     # Merge patterns into a single regex with alternation
#     combined_pattern = '|'.join(patterns)
#     match = re.search(combined_pattern, record, re.DOTALL)  # Use DOTALL to match across multiple lines
#     if match:
#         # Return the first non-empty group found
#         return next(group for group in match.groups() if group is not None)
#
#     return None

# def extract_identifier_section(record):
#     # Define regex patterns for various identifier sections
#
#     patterns = [
#         r'Giden Transfer, ([^,]+),',  # Matches 'Giden Transfer'
#         r'Encard Harcaması, ([^,]+),',  # Matches 'Encard Harcaması'
#         r'Ödeme, ([^,]+)-',  # Matches 'Ödeme'
#         r'Gelen Transfer, ([^,]+),',  # Matches 'Gelen Transfer'
#         r'Para Çekme, ([^,]+),',  # Matches 'Para Çekme'
#         r'Masraf/Ücret, ([^,]+),',  # Matches 'Masraf/Ücret'
#         r'Diğer, ([^,]+),',  # Matches 'Diğer'
#     ]
#     # patterns = [
#     #     r'Giden Transfer, (.+?),',  # Matches 'Giden Transfer'
#     #     r'Encard Harcaması, (.+?),',  # Matches 'Encard Harcaması'
#     #     r'Ödeme, (.+?)-',  # Matches 'Ödeme'
#     #     r'Gelen Transfer, (.+?),',  # Matches 'Gelen Transfer'
#     #     r'Para Çekme, (.+?),',  # Matches 'Para Çekme'
#     #     r'Masraf/Ücret, (.+?),',  # Matches 'Masraf/Ücret'
#     #     r'Diğer, (.+?),',  # Matches 'Diğer'
#     # ]
#
#     for pattern in patterns:
#         match = re.search(pattern, record)
#         if match:
#             return match.group(1).strip()
#
#     return None

# def clean_description(desc, cleaning_patterns):
#     for pattern in cleaning_patterns:
#         desc = re.sub(pattern['pattern'], pattern['replacement'], desc)
#     return desc

def clean_description(desc, cleaning_patterns):
    original_desc = desc  # For debugging
    for pattern in cleaning_patterns:
        desc = re.sub(pattern['pattern'], pattern['replacement'], desc)
    # if original_desc == desc:
    #     print(f"No change: {original_desc}")  # Debugging output if no change
    # else:
    #     print(f"Original: {original_desc} -> Cleaned: {desc}")  # Debugging output to see changes
    return desc


def extract_categories_and_keywords(categories_and_rules):
    categories_keywords = {}

    def traverse_categories(categories, parent_category=None):
        for category in categories:
            for cat_name, cat_details in category.items():
                if parent_category:
                    main_category = parent_category
                    subcategory = cat_name
                else:
                    main_category = cat_name
                    subcategory = None

                keywords = []
                if 'rules' in cat_details:
                    rules = cat_details['rules']
                    if isinstance(rules, dict):
                        for rule_type, rule_details in rules.items():
                            if rule_type == 'keyword':
                                keywords.extend(rule_details)
                    elif isinstance(rules, list):
                        for rule in rules:
                            if 'keyword' in rule:
                                keywords.extend(rule['keyword'])

                if main_category not in categories_keywords:
                    categories_keywords[main_category] = {}
                if subcategory:
                    categories_keywords[main_category][subcategory] = keywords
                else:
                    categories_keywords[main_category][main_category] = keywords

                if 'subcategories' in cat_details and cat_details['subcategories']:
                    traverse_categories(cat_details['subcategories'], main_category)

    traverse_categories(categories_and_rules)
    return categories_keywords


# def extract_categories_and_keywords(categories_and_rules):
#     categories_keywords = []
#
#     def traverse_categories(categories, parent_category=None):
#         for category in categories:
#             for cat_name, cat_details in category.items():
#                 if parent_category:
#                     main_category = parent_category
#                     subcategory = cat_name
#                 else:
#                     main_category = cat_name
#                     subcategory = None
#
#                 keywords = []
#                 if 'rules' in cat_details:
#                     for rule_type, rule_details in cat_details['rules'].items():
#                         if rule_type == 'keyword':
#                             keywords.extend(rule_details)
#
#                 if subcategory:
#                     categories_keywords.append((main_category, subcategory, keywords))
#                 else:
#                     categories_keywords.append((main_category, main_category, keywords))
#
#                 if 'subcategories' in cat_details and cat_details['subcategories']:
#                     traverse_categories(cat_details['subcategories'], main_category)
#
#     traverse_categories(categories_and_rules)
#     return categories_keywords

def do_analysis(llm, llm_refiner, pdf_document_path, bank_name):
    table_df = get_statements(pdf_document_path, bank_name)
    descs = table_df["Açıklama"].tolist()

    # Remove the line `descs = clean_descs(descs, bank_name)`

    table_df["desc"] = descs
    categories_and_rules, list_of_main_categories, list_of_subcategories = get_hierarchical_categories(
        'categories.yaml')

    bank_patterns = get_bank_patterns('bank_patterns.yaml', bank_name)
    bank_cleaning_patterns = bank_patterns["cleaning_patterns"]
    bank_classification_patterns = bank_patterns["classification_patterns"]

    results = []
    raw_answers = []
    refined_answers = []
    classified_by_bank_pattern = []
    classified_by_keyword_rule = []
    identifiers = []
    cleaned_descs = []
    classification_cache = {}



    for e in tqdm(descs, desc="Classifying records"):
        # e = clean_description(e, bank_cleaning_patterns)  # Clean the description using bank-specific patterns
        string_id = extract_identifier_section(e)
        cleaned_descs.append(e)
        identifiers.append(string_id)

        if string_id in classification_cache:
            classification_result, by_bank_pattern, by_keyword_rule = classification_cache[string_id]
            raw_string_answer = "from cache"
            refined_answer = "from cache"
        else:
            classification_result, by_bank_pattern, by_keyword_rule, raw_string_answer, refined_answer = find_category_and_subcategory(
                e,
                llm,
                template1,
                llm_refiner,
                refiner_template2,
                categories_and_rules,
                list_of_main_categories,
                list_of_subcategories,
                bank_classification_patterns
                )






            classification_cache[string_id] = (classification_result, by_bank_pattern, by_keyword_rule)

        raw_answers.append(raw_string_answer)
        refined_answers.append(refined_answer)

        results.append(classification_result)
        classified_by_bank_pattern.append(by_bank_pattern)
        classified_by_keyword_rule.append(by_keyword_rule)

    result_df = pd.DataFrame(results)

    table_df['cleaned_descs'] = cleaned_descs
    table_df['category'] = result_df['category']
    table_df['subcategory'] = result_df['subcategory']

    table_df['raw_answers'] = raw_answers
    table_df['refined_answer'] = refined_answers

    table_df['by_bank_pattern'] = classified_by_bank_pattern
    table_df['by_keyword_rule'] = classified_by_keyword_rule
    table_df['identifier'] = identifiers
    table_df["Tutar"] = table_df["Tutar"].apply(convert_tutar)

    file_name = 'results_all.csv'
    table_df.to_csv(file_name, index=False)

    return table_df


# print(" ")
# print("classes: ", classes)
# raw_string_answer = classify_record(llm,  descs[0], classes)
# print("raw_string_answer:", raw_string_answer)
# r = refine_answer(llm_refiner, raw_string_answer)


def convert_tutar(tutar):
    return -float(tutar.replace(" TL", "").replace(".", "").replace(",", ".").replace(" ", ""))


def main():
    pdf_document_path = "./sample_pdfs/sample1.pdf"
    llm = Ollama(model="gemma2")

    llm_refiner = Ollama(model="gemma:2b")

    result_df = do_analysis(llm, llm_refiner, pdf_document_path, "enpara")
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
