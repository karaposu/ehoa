import plotly.express as px
import streamlit as st
import yaml
from utils import extract_categories
import pandas as pd
from langchain_community.llms import Ollama
from analysis import do_analysis

# Load the YAML file
with open('categories.yaml', 'r') as file:
    data = yaml.safe_load(file)

pdf_document = "./sample_pdfs/sample1.pdf"
llm = Ollama(model="gemma2")
# result_df = do_analysis(llm, pdf_document, "")
result_df = pd.read_csv("results_all.csv")

category_totals = result_df.groupby("category")["Tutar"].sum().reset_index()
category_totals.columns = ["Category", "Value"]

# Group by "category" and "subcategory" and sum the "Tutar" column
subcategory_totals = result_df.groupby(["category", "subcategory"])["Tutar"].sum().reset_index()
subcategory_totals.columns = ["Category", "Subcategory", "Value"]

# Extract categories and subcategories
categories, subcategories = extract_categories(data)

# # Example dollar values for each category (replace with real data)
# category_values = {
#     'Food & Dining': 1500,
#     'Accommodation & Utilities': 2000,
#     'Money Transfers': 800,
#     'Cash Withdrawal': 600,
#     'Transportation': 1200,
#     'Healthcare': 900,
#     'Shopping': 700,
#     'Personal Care': 400,
#     'Entertainment': 500,
#     'Subscriptions': 300,
#     'Business & Services': 450,
#     'Miscellaneous': 250
# }
#
# # Example dollar values for each subcategory (replace with real data)
# subcategory_values = {
#     'Groceries': 500,
#     'Restaurants': 700,
#     'Coffee': 150,
#     'Takeout': 150,
#     'Utilities': 1000,
#     'Accommodation': 1000,
#     'Fuel': 300,
#     'Taxi': 200,
#     'Travel Tickets': 400,
#     'Public Transportation': 100,
#     'Vehicle Maintenance': 100,
#     'Car Payments': 100,
#     'Medical Bills': 600,
#     'Health Insurance': 300,
#     'Clothes': 300,
#     'Technology Items': 400,
#     'Personal Grooming': 200,
#     'Fitness': 200,
#     'Movies': 200,
#     'Concerts': 300,
#     'Cloud Server Payments': 450
# }
#
# # Create a DataFrame for the main categories with dollar values
# category_totals = pd.DataFrame({
#     'Category': list(category_values.keys()),
#     'Value': list(category_values.values())
# })
#
# # Create a DataFrame for subcategories with dollar values
# subcategory_list = []
# for category, subs in subcategories.items():
#     for sub in subs:
#         value = subcategory_values.get(sub, 0)  # Use 0 as the default value if subcategory is missing
#         subcategory_list.append({'Category': category, 'Subcategory': sub, 'Value': value})
#
# subcategory_totals = pd.DataFrame(subcategory_list)


def create_dashboard(df_categories, df_subcategories):
    # Initialize session state
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = df_categories['Category'].iloc[0]

    # Function to update selected category
    def update_selected_category(selected_category):
        st.session_state.selected_category = selected_category

    # Streamlit UI
    st.set_page_config(layout="wide")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Main Categories")
        total_spent = df_categories['Value'].sum()
        st.markdown(f"**Total Spent: ${total_spent}**")
        fig_categories = px.pie(df_categories, names='Category', values='Value', title='Main Categories',
                                labels={'Value': 'Dollar Value'}, hole=0.3)
        fig_categories.update_traces(textinfo='value', texttemplate='$%{value}')
        st.plotly_chart(fig_categories, use_container_width=True)

    with col2:
        # Dropdown to select category
        selected_category = st.selectbox('Select a Category:', df_categories['Category'].tolist(),
                                         index=df_categories['Category'].tolist().index(st.session_state.selected_category))
        update_selected_category(selected_category)

        # Filter subcategories based on selected category
        filtered_subcategories = df_subcategories[df_subcategories['Category'] == st.session_state.selected_category]

        st.subheader(f"Subcategories of {st.session_state.selected_category}")
        total_sub_spent = filtered_subcategories['Value'].sum()
        st.markdown(f"**Total Spent on {st.session_state.selected_category}: ${total_sub_spent}**")
        fig_subcategories = px.pie(filtered_subcategories, names='Subcategory', values='Value',
                                   title=f'Subcategories of {st.session_state.selected_category}',
                                   labels={'Value': 'Dollar Value'}, hole=0.3)
        fig_subcategories.update_traces(textinfo='value', texttemplate='$%{value}')
        st.plotly_chart(fig_subcategories, use_container_width=True)



create_dashboard(category_totals, subcategory_totals)



#
# # Streamlit UI
# st.set_page_config(layout="wide")
# col1, col2 = st.columns(2)
#
# with col1:
#     st.subheader("Main Categories")
#     total_spent = df_categories['Value'].sum()
#     st.markdown(f"**Total Spent: ${total_spent}**")
#     fig_categories = px.pie(df_categories, names='Category', values='Value', title='Main Categories',
#                             labels={'Value': 'Dollar Value'}, hole=0.3)
#     fig_categories.update_traces(textinfo='value', texttemplate='$%{value}')
#     st.plotly_chart(fig_categories, use_container_width=True)
#
# with col2:
#     # Dropdown to select category
#     selected_category = st.selectbox('Select a Category:', list(category_values.keys()),
#                                      index=list(category_values.keys()).index(st.session_state.selected_category))
#     update_selected_category(selected_category)
#
#     # Filter subcategories based on selected category
#     filtered_subcategories = df_subcategories[df_subcategories['Category'] == st.session_state.selected_category]
#
#     st.subheader(f"Subcategories of {st.session_state.selected_category}")
#     total_sub_spent = filtered_subcategories['Value'].sum()
#     st.markdown(f"**Total Spent on {st.session_state.selected_category}: ${total_sub_spent}**")
#     fig_subcategories = px.pie(filtered_subcategories, names='Subcategory', values='Value',
#                                title=f'Subcategories of {st.session_state.selected_category}',
#                                labels={'Value': 'Dollar Value'}, hole=0.3)
#     fig_subcategories.update_traces(textinfo='value', texttemplate='$%{value}')
#     st.plotly_chart(fig_subcategories, use_container_width=True)
