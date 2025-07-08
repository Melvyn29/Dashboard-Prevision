import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        .main .block-container {
            background-color: #F5F7FA;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .title {
            color: #003087;
            font-size: 48px;
            text-align: center;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: bold;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        .sidebar .sidebar-content {
            background-color: #0A0A0A;
            padding: 15px;
        }
        .stSidebar .stButton button {
            background-color: #003087;
            color: #F5F7FA;
            border: none;
            padding: 14px 22px;
            border-radius: 8px;
            font-size: 18px;
            width: 100%;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }
        .stSidebar .stButton button:hover {
            background-color: #CE1126;
            transform: translateY(-2px);
        }
        .stMetric {
            background-color: #F8FAFC;
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #4A90E2;
            color: #333;
            font-size: 14px;
            max-width: 300px;
        }
        .trend-form {
            background-color: #F5F7FA;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #003087;
            margin-bottom: 15px;
        }
        .footer {
            text-align: center;
            padding: 10px;
            background-color: #E6ECEF;
            color: #333333;
            font-family: 'Arial', sans-serif;
            font-size: 12px;
            margin-top: 30px;
        }
        .stDataFrame tbody tr:hover {
            background-color: #E6ECEF;
        }
        .comparison-table th, .comparison-table td {
            border: 1px solid #003087;
            padding: 8px;
            text-align: center;
        }
        .highlight-best {
            background-color: #E6F3E6;
        }
        .datetime-display {
            text-align: center;
            font-size: 16px;
            color: #003087;
            font-family: 'Arial', sans-serif;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )