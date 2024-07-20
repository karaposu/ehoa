
#streamlit run app2.py


import yaml
import os
import re
from langchain_core.prompts import PromptTemplate
import ast

def load_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def extract_categories(data):
    categories = []
    subcategories = {}

    for category in data['categories']:
        for main_category, subcat in category.items():
            categories.append(main_category)
            subcat_list = []
            if isinstance(subcat, list):
                for sub_category in subcat:
                    subcat_list.append(sub_category)
            subcategories[main_category] = subcat_list

    return categories, subcategories
#
# def extract_categories(data):
#     categories = []
#     subcategories = {}
#
#     for category in data['categories']:
#         for main_category, subcat in category.items():
#             categories.append(main_category)
#             subcat_list = []
#             if isinstance(subcat, list):
#                 for item in subcat:
#                     for sub_category, sub_subcat in item.items():
#                         subcat_list.append(sub_category)
#             subcategories[main_category] = subcat_list
#
#     return categories, subcategories


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

def classify_record_with_keyword(record, categories_keywords):
    for category, subcategories in categories_keywords.items():
        for subcategory, keywords in subcategories.items():
            for keyword in keywords:
                if keyword.lower() in record.lower():
                    return {'category': category, 'subcategory': subcategory}
    return None

class ExpandedDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True
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


#
# def is_service_enabled(service_name):
#     try:
#         result = subprocess.run(['systemctl', 'is-enabled', service_name],
#                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         if result.returncode == 0:
#             return result.stdout.strip() == 'enabled'
#         else:
#             print(f"Error checking service status: {result.stderr.strip()}")
#             return False
#     except Exception as e:
#         print(f"Exception occurred: {e}")
#         return False


# def classify_a_record_using_llm(simple_chain, record, classes):
#     # Convert classes to a YAML string
#     classes_string = yaml.dump(classes, default_flow_style=False, Dumper=ExpandedDumper)
#
#     # Format the prompt manually using the existing PromptTemplate
#     formatted_prompt = simple_chain.prompt_template.format(record=record, classes=classes_string)
#
#     # Prepare variables for the chain
#     variables = {
#         "record": record,
#         "classes": classes_string
#     }
#
#     # Run the simple_chain with the formatted variables
#     result = simple_chain.run(variables)
#     output = result
#     # Assuming 'output' is the key used by SimpleChain for its results, adjust if necessary
#     #output = result['output'] if 'output' in result else result
#
#     return output, formatted_prompt

def classify_a_record_using_llm(llm, unformatted_template, record, classes):

    classes_string = yaml.dump(classes, default_flow_style=False, Dumper=ExpandedDumper)

    prompt = PromptTemplate.from_template(unformatted_template)
    formatted_prompt = prompt.format(record=record, classes=classes_string)
    # print("----")
    # print(formatted_prompt)
    r = llm.invoke(formatted_prompt)
    return r ,formatted_prompt

def refine_answer(llm, unformatted_prompt , answer_to_be_refined):
    # refiner_template = '''
    # Here is a text {answer_to_be_refined}.  i want you to extract information by searching for Main Category and Subcategory and
    # give me answer in following format
    #  {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }}
    #    do not output extra information and remove words like "likely"!
    # '''

    # refiner_template = '''Here is an answer from another LLM for my question. {answer_to_be_refined} I want you to format the answer in following format
    #  {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }}
    #  do not output extra information! '''
    prompt = PromptTemplate.from_template(unformatted_prompt)
    formatted_prompt = prompt.format(answer_to_be_refined=answer_to_be_refined)
    r = llm.invoke(formatted_prompt)
    return r

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

def classify_and_refine(llm, llm_template,  llm_refiner, refiner_prompt_template,  desc, categories_and_rules, list_of_main_categories, list_of_subcategories,
                        retries=2):
    def attempt_classification_and_refinement():
        raw_string_answer, formatted_prompt = classify_a_record_using_llm(llm,llm_template, desc, categories_and_rules)
        refined_answer = refine_answer(llm_refiner, refiner_prompt_template,  raw_string_answer)
        return raw_string_answer, refined_answer, formatted_prompt

    for _ in range(retries):
        raw_string_answer, refined_answer, formatted_prompt = attempt_classification_and_refinement()

        print("raw_string_answer_:", raw_string_answer)
        print("refined_answer:", refined_answer)

        if not refined_answer:
            continue

        refined_answer_dict = string_to_dict(refined_answer)
        if refined_answer_dict is None:
            continue

        if is_answer_valid(refined_answer_dict, list_of_main_categories, list_of_subcategories):

            return refined_answer_dict, raw_string_answer, refined_answer

    # # Final attempt to return in case of failure
    # raw_string_answer, refined_answer,  = attempt_classification_and_refinement()
    return None, raw_string_answer, refined_answer


def get_hierarchical_categories(yaml_file):
    yaml_data = load_yaml(yaml_file)

    # main_categories = [list(cat.keys())[0] for cat in category]


    print("categories",  yaml_data["categories"])
    print("")
    print("rules", yaml_data["rules"])

    categories_data = yaml_data['categories']
    list_of_main_categories = [list(category.keys())[0] for category in categories_data]
    list_of_subcategories = []
    for category in categories_data:
        for subcat in category.values():
            if isinstance(subcat, list):
                list_of_subcategories.extend(subcat)
            else:
                list_of_subcategories.append(subcat)

    rules_data = yaml_data['rules']


    def merge_categories_and_rules(data, rules):
        categories_and_rules = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        subcategories = []
                        if isinstance(value, list):
                            for sub in value:
                                sub_rule_details = rules.get(key, {}).get(sub, {})
                                subcategories.append({sub: {"subcategories": [], "rules": sub_rule_details}})
                        rule_details = rules.get(key, {})
                        categories_and_rules.append({key: {"subcategories": subcategories, "rules": rule_details}})
                elif isinstance(item, str):  # Simple categories without subcategories
                    rule_details = rules.get(item, {})
                    categories_and_rules.append({item: {"subcategories": [], "rules": rule_details}})
        return categories_and_rules


    categories_and_rules = merge_categories_and_rules(categories_data, rules_data)
    print(" >>")
    print("categories_and_rules", categories_and_rules)
    return categories_and_rules,  list_of_main_categories , list_of_subcategories


# def get_hierarchical_categories(yaml_file):
#     yaml_data = load_yaml(yaml_file)
#
#     def extract_categories(data, rules):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories, _ = extract_categories(value, rules.get(key, {}))
#                         rule_details = rules.get(key, {})
#                         categories.append({key: {"subcategories": subcategories, **rule_details}})
#         elif isinstance(data, dict):
#             subcategories = []
#             rules_details = {}
#             for key, value in data.items():
#                 if isinstance(value, (dict, list)):
#                     nested_subcategories, nested_rules = extract_categories(value, rules.get(key, {}))
#                     subcategories.append({key: {"subcategories": nested_subcategories, **nested_rules}})
#                 else:
#                     subcategories.append({key: {"subcategories": []}})
#             return subcategories, rules_details
#         return categories, {}
#
#     categories_data = yaml_data['categories']
#     rules_data = {list(item.keys())[0]: list(item.values())[0] for item in yaml_data['rules']}
#
#     categories, _ = extract_categories(categories_data, rules_data)
#     return categories

# categories, subcategories = extract_categories(data)

# def get_hierarchical_categories(yaml_data):
#     yaml_data = load_yaml(yaml_data)
#     def extract_categories(data, rules):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories, subrules = extract_categories(value, rules.get(key, {}))
#                         rule_details = rules.get(key, {})
#                         categories.append({key: {"subcategories": subcategories, **rule_details}})
#         elif isinstance(data, dict):
#             subcategories = []
#             rules_details = {}
#             for key, value in data.items():
#                 nested_subcategories, nested_rules = extract_categories(value, rules.get(key, {}))
#                 subcategories.append({key: {"subcategories": nested_subcategories, **nested_rules}})
#             return subcategories, rules_details
#         return categories, {}
#
#     categories_data = yaml_data['categories']
#     rules_data = {list(item.keys())[0]: list(item.values())[0] for item in yaml_data['rules']}
#
#     categories, _ = extract_categories(categories_data, rules_data)
#     return categories




#
# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data, rules, base_path=os.path.dirname(yaml_file)):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories, subrules = extract_categories(value, rules.get(key, {}), base_path)
#                         rule_details = rules.get(key, {})
#                         categories.append({key: {"subcategories": subcategories, **rule_details}})
#         elif isinstance(data, dict):
#             subcategories = []
#             rules_details = {}
#             for key, value in data.items():
#                 nested_subcategories, nested_rules = extract_categories(value, rules.get(key, {}), base_path)
#                 subcategories.append({key: {"subcategories": nested_subcategories, **nested_rules}})
#             return subcategories, rules_details
#         return categories, {}
#
#     categories_data = data['categories']
#     rules_data = {item.popitem()[0]: item.popitem()[1] for item in data['rules']}
#
#     categories, _ = extract_categories(categories_data, rules_data)
#     return categories

# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data, base_path=os.path.dirname(yaml_file)):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories, rules = extract_categories(value, base_path)
#                         if isinstance(value, dict) and "rules" in value:
#                             rules_path = os.path.join(base_path, value["rules"])
#                             with open(rules_path, 'r') as rf:
#                                 rules_data = yaml.safe_load(rf)
#                             categories.append({key: {"subcategories": subcategories, **rules_data}})
#                         else:
#                             categories.append({key: {"subcategories": subcategories}})
#         elif isinstance(data, dict):
#             subcategories = []
#             rules = {}
#             for key, value in data.items():
#                 if key == "rules":
#                     rules_path = os.path.join(base_path, value)
#                     with open(rules_path, 'r') as rf:
#                         rules = yaml.safe_load(rf)
#                 else:
#                     nested_subcategories, nested_rules = extract_categories(value, base_path)
#                     subcategories.append({key: {"subcategories": nested_subcategories, **nested_rules}})
#             return subcategories, rules
#         return categories, {}
#
#     categories, _ = extract_categories(data['categories'])
#     return categories



# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories = extract_categories(value)
#                         category = {"subcategories": subcategories}
#                         if isinstance(value, dict) and "rules" in value:
#                             rules_file = value["rules"]
#                             rules_path = os.path.join(os.path.dirname(yaml_file), rules_file)
#                             with open(rules_path, 'r') as rf:
#                                 rules_data = yaml.safe_load(rf)
#                             category.update(rules_data)
#                         categories.append({key: category})
#                 else:
#                     categories.append(item)
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 categories.append({key: extract_categories(value)})
#         return categories
#
#     return extract_categories(data['categories'])


# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories = extract_categories(value)
#                         category = {"subcategories": subcategories}
#                         if isinstance(value, dict) and "rules" in value:
#                             rules_file = value["rules"]
#                             rules_path = os.path.join(os.path.dirname(yaml_file), rules_file)
#                             with open(rules_path, 'r') as rf:
#                                 rules_data = yaml.safe_load(rf)
#                             category.update(rules_data)
#                         categories.append({key: category})
#                 else:
#                     categories.append(item)
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 categories.append({key: extract_categories(value)})
#         return categories
#
#     return extract_categories(data['categories'])
#


# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories = extract_categories(value)
#                         if isinstance(value, dict) and "rules" in value:
#                             rules_file = value["rules"]
#                             rules_path = os.path.join(os.path.dirname(yaml_file), rules_file)
#                             with open(rules_path, 'r') as rf:
#                                 rules_data = yaml.safe_load(rf)
#                             categories.append({key: {"subcategories": subcategories, **rules_data}})
#                         else:
#                             categories.append({key: {"subcategories": subcategories}})
#                 else:
#                     categories.append(item)
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 categories.append({key: extract_categories(value)})
#         return categories
#
#     return extract_categories(data['categories'])

# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories = extract_categories(value)
#                         if isinstance(value, dict) and "rules" in value:
#                             rules_file = value["rules"]
#                             rules_path = os.path.join(os.path.dirname(yaml_file), rules_file)
#                             with open(rules_path, 'r') as rf:
#                                 rules_data = yaml.safe_load(rf)
#                             categories.append({key: {"subcategories": subcategories, "rules": rules_data}})
#                         else:
#                             categories.append({key: {"subcategories": subcategories}})
#                 else:
#                     categories.append(item)
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 categories.append({key: extract_categories(value)})
#         return categories
#
#     return extract_categories(data['categories'])


def extract_rules(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    rules = {}

    def extract_rules_recursive(data, path=""):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, dict) and "rules" in value:
                            rules_file = value["rules"]
                            # Mock rules for the example. In real scenario, read actual rules from the file.
                            keywords = []
                            text_rules = []
                            if "groceries" in rules_file:
                                keywords = ["supermarket", "grocery store"]
                            elif "restaurants" in rules_file:
                                keywords = ["restaurant", "dine-in"]
                            elif "coffee" in rules_file:
                                keywords = ["coffee shop", "cafe"]
                            elif "takeout" in rules_file:
                                keywords = ["yemeksepeti", "getir"]
                                text_rules = [
                                    "if bill is from getir and cost is more than 50$, it is an item, it should be classify as shopping"
                                ]
                            # Add more mock rules as needed.
                            rules[path + "/" + key] = {"keywords": keywords, "text_rules": text_rules}
                        extract_rules_recursive(value, path + "/" + key)
                else:
                    continue
        elif isinstance(data, dict):
            for key, value in data.items():
                extract_rules_recursive(value, path + "/" + key)

    extract_rules_recursive(data['categories'])
    return rules

# def get_hierarchical_categories(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     def extract_categories(data):
#         categories = []
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         subcategories = extract_categories(value)
#                         categories.append({key: subcategories})
#                 else:
#                     categories.append(item)
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 categories.append({key: extract_categories(value)})
#         return categories
#
#     return extract_categories(data['categories'])
#
#
# categories = get_hierarchical_categories('categories.yaml')

# def extract_categories(data):
#     categories = []
#     if isinstance(data, list):
#         for item in data:
#             if isinstance(item, dict):
#                 for key, value in item.items():
#                     subcategories = extract_categories(value)
#                     categories.append({key: subcategories})
#             else:
#                 categories.append(item)
#     elif isinstance(data, dict):
#         for key, value in data.items():
#             categories.append({key: extract_categories(value)})
#     return categories


# def extract_rules(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)
#
#     rules = {}
#
#     def extract_rules_recursive(data, path=""):
#         if isinstance(data, list):
#             for item in data:
#                 if isinstance(item, dict):
#                     for key, value in item.items():
#                         if isinstance(value, dict) and "rules" in value:
#                             rules_file = value["rules"]
#                             rules[path + "/" + key] = rules_file
#                         extract_rules_recursive(value, path + "/" + key)
#                 else:
#                     continue
#         elif isinstance(data, dict):
#             for key, value in data.items():
#                 extract_rules_recursive(value, path + "/" + key)
#
#     extract_rules_recursive(data['categories'])
#     return rules


def create_rules_yaml(rules, output_file):
    structured_rules = {}

    for category, rule_file in rules.items():
        parts = category.strip('/').split('/')
        current = structured_rules
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        current['rules'] = rule_file

    with open(output_file, 'w') as file:
        yaml.dump(structured_rules, file, default_flow_style=False)


def get_categories(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    categories = []

    def extract_categories(data):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        categories.append(key)
                        extract_categories(value)
        elif isinstance(data, dict):
            for key, value in data.items():
                extract_categories(value)

    extract_categories(data['categories'])
    return categories


# categories = get_categories('categories.yaml')
# print(categories)
