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
        /* En-tête discret et centré */
        .header-container {
            text-align: center;
            padding: 25px 20px;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
            border-radius: 10px;
            border-bottom: 2px solid #003087;
        }
        
        .header-content {
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .main-title {
            font-size: 2.2rem;
            font-weight: 600;
            margin: 0 0 10px 0;
            color: #003087;
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.2;
            text-align: center;
        }
        
        .subtitle {
            font-size: 1rem;
            margin: 0 auto;
            color: #555;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 400;
            line-height: 1.5;
            text-align: center;
            width: 100%;
            max-width: none;
            display: block;
            padding: 0;
        }
        
        /* Suppression de l'ancien style title */
        
        /* Amélioration de la sidebar */
        .stSidebar {
            background: linear-gradient(180deg, #002856 0%, #003087 100%);
        }
        
        .stSidebar > div:first-child {
            background: linear-gradient(180deg, #002856 0%, #003087 100%);
        }
        
        .sidebar .sidebar-content {
            background: transparent;
            padding: 20px 15px;
        }
        
        .stSidebar .element-container {
            background: transparent;
        }
        
        .stSidebar h3 {
            color: #FFFFFF !important;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 10px;
        }
        
        .stSidebar h4 {
            color: #FFFFFF !important;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 500;
            font-size: 1rem;
            margin: 15px 0 10px 0;
            opacity: 0.9;
        }
        
        .stSidebar hr {
            border: none;
            height: 1px;
            background: rgba(255, 255, 255, 0.2);
            margin: 15px 0;
        }
        
        .stSidebar .stButton button {
            background: linear-gradient(135deg, #004ba0, #0066cc);
            color: #FFFFFF;
            border: none;
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 500;
            width: 100%;
            margin-bottom: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-family: 'Segoe UI', sans-serif;
        }
        
        .stSidebar .stButton button:hover {
            background: linear-gradient(135deg, #CE1126, #ff1744);
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(206, 17, 38, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stSidebar .stButton button:active {
            transform: translateY(0px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Style pour la date/heure dans la sidebar */
        .sidebar-datetime {
            text-align: center;
            color: #FFFFFF;
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 8px;
            margin-top: 20px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 0.9rem;
            font-weight: 500;
            border: 1px solid rgba(255, 255, 255, 0.1);
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
            padding: 20px;
            background: linear-gradient(135deg, #E6ECEF, #d1e7dd);
            color: #2c3e50;
            font-family: 'Segoe UI', sans-serif;
            border-radius: 10px;
            margin-top: 30px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(0, 48, 135, 0.1);
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
        
        /* Amélioration du contenu principal */
        .main .block-container {
            background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin-top: 10px;
        }
        
        /* Animations et transitions */
        .stButton button {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .stSelectbox {
            font-family: 'Segoe UI', sans-serif;
        }
        
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
                letter-spacing: -0.2px;
            }
            .subtitle {
                font-size: 0.9rem;
                line-height: 1.2;
            }
            .header-content {
                padding: 25px 20px 20px;
            }
        }
        
        /* Responsive pour l'en-tête */
        @media (max-width: 768px) {
            .header-container {
                padding: 20px 15px;
                margin-bottom: 25px;
            }
            .main-title {
                font-size: 1.8rem;
            }
            .subtitle {
                font-size: 0.9rem;
                max-width: 100%;
            }
        }
        
        @media (max-width: 480px) {
            .header-container {
                padding: 15px 10px;
                margin-bottom: 20px;
            }
            .main-title {
                font-size: 1.6rem;
                line-height: 1.3;
            }
            .subtitle {
                font-size: 0.85rem;
                line-height: 1.5;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )