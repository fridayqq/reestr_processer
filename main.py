import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime  # Add this import at the top

def luhn_checksum(iccid):
    # Преобразуем строку в список цифр
    digits = [int(d) for d in iccid]
    # Перевернем список для удобства
    digits.reverse()
    # Проходим по цифрам, удваивая каждую вторую
    for i in range(len(digits)):
        if i % 2 == 0:
            digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    # Вычисляем сумму
    total_sum = sum(digits)
    # Вычисляем контрольное число
    checksum = (10 - (total_sum % 10)) % 10
    return checksum

# Initialize session states
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'prev_id_column' not in st.session_state:
    st.session_state.prev_id_column = None
if 'prev_phone_column' not in st.session_state:
    st.session_state.prev_phone_column = None

st.title('🔄 Data Processing App')
st.markdown('---')

# File uploader section
st.header('📁 Upload File')
uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            
        # Display original dataframe
        st.header('📊 Original Data')
        st.write("First 2 rows of uploaded file:")
        st.write(df.head(2).to_html(index=False), unsafe_allow_html=True)
        st.markdown('---')
        
        # Column selection section
        st.header('🎯 Select Columns')
        col1, col2 = st.columns(2)
        with col1:
            id_column = st.selectbox('Select ID column:', df.columns)
        with col2:
            phone_column = st.selectbox('Select Phone Number column:', df.columns)
        
        # Reset filtered_df if columns changed
        if (id_column != st.session_state.prev_id_column or 
            phone_column != st.session_state.prev_phone_column):
            st.session_state.filtered_df = None
            st.session_state.prev_id_column = id_column
            st.session_state.prev_phone_column = phone_column

        # Display filtered DataFrame if both columns are selected
        if id_column and phone_column:
            # Initialize filtered_df in session state if it's None
            if st.session_state.filtered_df is None:
                st.session_state.filtered_df = df[[id_column, phone_column]].copy()
            
            st.markdown('---')
            st.header('🛠️ Data Operations')
            
            # Phone number operations
            st.subheader('📱 Phone Number Operations')
            if st.button('Добавить "+7" к номеру телефона', use_container_width=True):
                st.session_state.filtered_df[phone_column] = '+7' + st.session_state.filtered_df[phone_column].astype(str)
            
            st.markdown('##')  # Vertical spacing
            
            # ID operations
            st.subheader('🔢 ID Operations')
            if st.button('Удалить 1 символ из ID слева', use_container_width=True):
                st.session_state.filtered_df[id_column] = st.session_state.filtered_df[id_column].astype(str).str[1:]
            
            if st.button('Удалить 1 символ из ID справа', use_container_width=True):
                st.session_state.filtered_df[id_column] = st.session_state.filtered_df[id_column].astype(str).str[:-1]
            
            if st.button('Удалить лишние символы из ID', use_container_width=True):
                st.session_state.filtered_df[id_column] = st.session_state.filtered_df[id_column].astype(str).apply(lambda x: re.sub(r'\D', '', x))
            
            if st.button('Добавить контрольное число в столбец ID', use_container_width=True):
                st.session_state.filtered_df[id_column] = st.session_state.filtered_df[id_column].astype(str).apply(
                    lambda x: x + str(luhn_checksum(re.sub(r'\D', '', x)))
                )

            st.markdown('---')
            
            # Results section
            st.header('📋 Results')
            st.write("Processed data (first 10 rows):")
            st.write(st.session_state.filtered_df.head(10).to_html(index=False), unsafe_allow_html=True)
            
            st.markdown('##')
            
            # Download section
            st.header('💾 Download')
            # Add download button with custom styling
            download_df = st.session_state.filtered_df.copy()
            # Rename columns
            download_df.columns = ['ZSIM_ID' if col == id_column else 'ZSIM_PHNR' if col == phone_column else col 
                                 for col in download_df.columns]
            
            # Generate filename with record count and current date
            record_count = len(download_df)
            current_date = datetime.now().strftime("%d%m%Y")
            filename = f"reestr_{record_count}_{current_date}.csv"
            
            # Convert DataFrame to CSV with specific encoding and delimiter
            csv_data = download_df.to_csv(index=False, sep=';', encoding='cp1251')
            
            st.download_button(
                label="📥 Скачать реестр",
                data=csv_data,
                file_name=filename,  # Use dynamic filename
                mime="text/csv",
                key='download-csv',
                help="Скачать данные в формате CSV",
                type="primary",
                use_container_width=True
            )

        else:
            # Reset filtered_df if no columns selected
            st.session_state.filtered_df = None
            
    except Exception as e:
        st.error(f"Error: {e}")

st.write()