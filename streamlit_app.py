import pandas as pd     
import streamlit as st 

# st.set_page_config(layout="wide")

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #F2F0EF;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="BBC News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


exploration_page = st.Page(
    "exploration.py",
    title = "Geographical Analysis Dashboard",
    icon = ":material/explore:",
)

prediction_page = st.Page(
    "prediction.py",
    title="Prediction Insights",
    icon=":material/farsight_digital:",
)


# selected_page = st.navigation([exploration_page, prediction_page])
selected_page = st.navigation([exploration_page, prediction_page])
selected_page.run()