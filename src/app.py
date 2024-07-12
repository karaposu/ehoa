import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sample Data with Top-level Categories and Sub-categories
data = {
    'Details': [
        'Food_Source01', 'Food_Source02', 'Food_Source03',
        'Home_Source01', 'Home_Source02', 'Home_Source03',
        'Leisure_Source01', 'Leisure_Source02'
    ],
    'Category': [
        'Food', 'Food', 'Food',
        'Home', 'Home', 'Home',
        'Leisure', 'Leisure'
    ],
    'Sub-Category': [
        'Groceries', 'Dining Out', 'Snacks',
        'Rent', 'Utilities', 'Repairs',
        'Movies', 'Travel'
    ],
    '2017': [500, 700, 600, 1200, 300, 400, 200, 300],
    'Total': [500, 700, 600, 1200, 300, 400, 200, 300]
}

df = pd.DataFrame(data)

# Set page layout
st.set_page_config(layout="wide")

# Title
st.title("Total Spending")

# Create two columns
col1, col2 = st.columns([2, 3])

# Display DataFrame in the first column
with col1:
    st.header("Details")
    st.table(df)

# Display Pie Chart in the second column
with col2:
    st.header("Spending Distribution")
    fig, ax = plt.subplots()
    df.groupby('Category')['Total'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    st.pyplot(fig)

    # Display Pie Chart for Sub-categories
    st.header("Sub-category Distribution")
    fig, ax = plt.subplots()
    df.groupby('Sub-Category')['Total'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    st.pyplot(fig)

# Additional layout and styling can be added as required
