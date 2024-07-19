import yaml
import os

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
                for item in subcat:
                    for sub_category, sub_subcat in item.items():
                        subcat_list.append(sub_category)
            subcategories[main_category] = subcat_list

    return categories, subcategories


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