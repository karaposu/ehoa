refiner_template2 = '''

       Here is a text: {answer_to_be_refined}. I want you to accurately extract the information by identifying the Main Category and Subcategory from the given text. 
       Provide the answer strictly in the following JSON format without any additional comments or inferred information:
       {{
          "category": "here_is_selected_category",
          "subcategory": "here_is_selected_subcategory"
        }}
    '''




refiner_template = '''
    Here is a text {answer_to_be_refined}.  i want you to extract information by searching for Main Category and Subcategory and 
    give me answer in following format
     {{ 'category': 'here_is_selected_category', 'subcategory': 'here_is_selected_subcategory' }} 
       do not output extra information and remove words like "likely"! 

         '''

template1 = '''
   
  

   Category Structure:

   {classes}

   Task Description:

   Identify the Main Category: Determine which of the main categories (e.g., Food & Dining, Utilities, etc.) the string belongs to.
   Determine the Subcategory: Once the main category is identified, determine the specific subcategory within that main category (e.g., within Food & Dining, identify whether it is Groceries, Restaurants, Coffee, or Takeout).
   Extra Information - Rules: There is additional information under each subcategory labeled as 'rules'. These rules include 'keyword' and 'text_based' but should be considered as extra information and not directly involved in the classification task.

   Instructions:
   Given the string record, first identify the main category, and then the specific subcategory within that main category (your final answer shouldnt include words like "likely").
   Use the 'rules' section for additional context. Make sure subcategory is selected from given subcategories and matches 100%

   Examples:
   Record: "Grocery shopping at Walmart"
   Main Category: Food & Dining
   Subcategory: Groceries

   Record: "Monthly electricity bill"
   Main Category: Utilities
   Subcategory: Electricity and Water and Gas
   
    String record to classify:
   {record}
   '''