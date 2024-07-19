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


def dummy_classify_record_with_keyword(record):
    return None


def classify_record_with_keyword(record, categories_keywords):
    for category, subcategories in categories_keywords.items():
        for subcategory, keywords in subcategories.items():
            for keyword in keywords:
                if keyword.lower() in record.lower():
                    return {'category': category, 'subcategory': subcategory}
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


def refine_answer(llm, answer_to_be_refined):
    refiner_template = '''
    Here is a text {answer_to_be_refined}.  i want you to extract information by searching for Main Category and Subcategory and 
    give me answer in following format
     {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }} 
       do not output extra information and remove words like "likely"! 
    '''

    # refiner_template = '''Here is an answer from another LLM for my question. {answer_to_be_refined} I want you to format the answer in following format
    #  {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }}
    #  do not output extra information! '''
    prompt = PromptTemplate.from_template(refiner_template)
    formatted_prompt = prompt.format(answer_to_be_refined=answer_to_be_refined)
    r = llm.invoke(formatted_prompt)
    return r


def classify_record(llm, record, classes):
    # keyword_based_classification_result = classify_record_with_keyword(record)
    # if keyword_based_classification_result is None:

    classes_string = yaml.dump(classes, default_flow_style=False, Dumper=ExpandedDumper)

    # print("....")
    # print("classes_string", classes_string)

    template2 = '''
    Prompt Template
    String record to classify:
    {record}

    Category Structure:

    {classes}

    Task Description:

    Identify the Main Category: Determine which of the main categories (e.g., Food & Dining, Utilities, etc.) the string belongs to.
    Determine the Subcategory: Once the main category is identified, determine the specific subcategory within that main category (e.g., within Food & Dining, identify whether it is Groceries, Restaurants, Coffee, or Takeout).
    Extra Information - Rules: There is additional information under each subcategory labeled as 'rules'. These rules include 'keyword' and 'text_based' but should be considered as extra information and not directly involved in the classification task.

    Instructions:
    Given the string record, first identify the main category, and then the specific subcategory within that main category (your final answer shouldnt include words like "likely").
    Use the 'rules' section for additional context.

    Examples:
    Record: "Grocery shopping at Walmart"
    Main Category: Food & Dining
    Subcategory: Groceries

    Record: "Monthly electricity bill"
    Main Category: Utilities
    Subcategory: Electricity and Water and Gas
    '''

    prompt = PromptTemplate.from_template(template2)
    formatted_prompt = prompt.format(record=record, classes=classes_string)
    print("----")
    print(formatted_prompt)
    r = llm.invoke(formatted_prompt)
    return r


def get_statements(pdf_document_path, bank_name):
    df = extract_table_from_pdf(pdf_document_path, bank_name)
    return df


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

def is_valid_category(text, list_of_categories):
    if text in list_of_categories:
        return True
    else:
        return False


def is_answer_valid(answer, list_of_categories, list_of_subcategories):
    if answer is not None:
        if is_valid_category(answer.get("category"), list_of_categories):
            if is_valid_category(answer.get("subcategory"), list_of_subcategories):
                return True
        print("cat or subcat not valid!")
    return False


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


# def classify_record_with_bank_pattern(desc, bank_classification_patterns):
#     for pattern in bank_classification_patterns:
#         if re.search(pattern['pattern'], desc):
#             return {
#                 'category': pattern['category'],
#                 'subcategory': pattern['subcategory']
#             }
#     return None

#
# def classify_record_with_bank_pattern(desc, bank_patterns):
#     classification_patterns = bank_patterns.get("classification_patterns", [])
#
#     for pattern in classification_patterns:
#         if re.search(pattern['pattern'], desc):
#             return {
#                 'category': pattern['category'],
#                 'subcategory': pattern['subcategory']
#             }
#
#     # Return None if no pattern matches
#     return None


def find_category_and_subcategory(desc, llm, llm_refiner, categories_and_rules, list_of_main_categories,
                                  list_of_subcategories, bank_classification_patterns):
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

            classification_result, raw_string_answer, refined_answer = classify_and_refine(llm, llm_refiner, desc,
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


def classify_and_refine(llm, llm_refiner, desc, categories_and_rules, list_of_main_categories, list_of_subcategories):
    raw_string_answer = classify_record(llm, desc, categories_and_rules)
    refined_answer = refine_answer(llm_refiner, raw_string_answer)

    if not refined_answer:
        return None, None, None

    refined_answer_dict = string_to_dict(refined_answer)
    if refined_answer_dict is None:
        return None, raw_string_answer, refined_answer

    if not is_answer_valid(refined_answer_dict, list_of_main_categories, list_of_subcategories):
        raw_string_answer = classify_record(llm, desc, categories_and_rules)
        refined_answer = refine_answer(llm_refiner, raw_string_answer)
        if not refined_answer:
            return None, raw_string_answer, refined_answer

        refined_answer_dict = string_to_dict(refined_answer)
        if refined_answer_dict is None:
            return None, raw_string_answer, refined_answer

    return refined_answer_dict, raw_string_answer, refined_answer


# def classify_and_refine(llm, llm_refiner, desc, categories_and_rules, list_of_main_categories, list_of_subcategories):
#     raw_string_answer = classify_record(llm, desc, categories_and_rules)
#     refined_answer = refine_answer(llm_refiner, raw_string_answer)
#
#     if not refined_answer:
#         return None
#
#     refined_answer_dict = string_to_dict(refined_answer)
#     if refined_answer_dict is None:
#         return None
#
#     if not is_answer_valid(refined_answer_dict, list_of_main_categories, list_of_subcategories):
#         raw_string_answer = classify_record(llm, desc, categories_and_rules)
#         refined_answer = refine_answer(llm_refiner, raw_string_answer)
#         if not refined_answer:
#             return None
#
#         refined_answer_dict = string_to_dict(refined_answer)
#         if refined_answer_dict is None:
#             return None
#
#     return refined_answer_dict, raw_string_answer, refined_answer


def clean_enpara_desc(value):
    def clean_currency_info(record):
        pattern = r', \d+\.?\d* (USD|TRY), işlem kuru \d+\.\d+ TL'
        cleaned_record = re.sub(pattern, '', record)
        cleaned_desc = cleaned_record.strip()
        return cleaned_desc

    cleaned_record = clean_currency_info(value)
    return cleaned_record


def clean_descs(descs, bank_name):
    clean_values = []
    for e in tqdm(descs, desc="cleaning desc"):
        v = clean_enpara_desc(e)
        clean_values.append(v)
    return clean_values


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
    classified_by_bank_pattern = []
    classified_by_keyword_rule = []
    identifiers = []
    cleaned_descs = []
    classification_cache = {}

    raw_answers = []
    refined_answers = []

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
