import pandas as pd
import plotly.express as px
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(page_title="World data Viz KHALIFA & YERO NIAMADIO",
                   page_icon=None, layout="centered", initial_sidebar_state="auto"
                   )

st.title("World data Viz KHALIFA & YERO NIAMADIO")
st.subheader("Welcome !!")

uploaded_f = st.sidebar.file_uploader("Choose xlsx file", type=['xlsx', 'xlsb'])

# Download the 2 others static presentations
def download_ppt():
    # Specify the file path of the PowerPoint file
    file_path = "path/to/presentation.pptx"

    # Add a download button and link it to the file path
    st.markdown("""
    <a href="{}" download="presentation.pptx">
        <button style="background-color:#0077C9;color:white;padding:10px;">Download PowerPoint Presentation</button>
    </a>
    """.format(file_path), unsafe_allow_html=True)

# Call the function in your Streamlit app
download_ppt()

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    Args:
        df (pd.DataFrame): Original dataframe
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], format="%Y/%m/%d %H:%m:%s")
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]
    st.write(len(df.index.unique()))
    return df


@st.experimental_memo
def temp():
    df = pd.read_excel(uploaded_f, engine='openpyxl')
    return df


def plot_category_evolution(data):
    fig = px.scatter_3d(data, x=data["HDI_XXI"], y=data["gdp_perc_health"], z=data['infant_mortality'],
                        color='indicator')
    st.plotly_chart(fig)


def plot_HDI_women_rep(data):
    fig = px.scatter(data, x=data['parliament_gender_equity'], y=data['HDI_XXI'], trendline='ols')
    st.plotly_chart(fig)


# Create a line chart


if uploaded_f is not None:
    df = temp()

    # Select a category to display
    zila = filter_dataframe(df)
    st.dataframe(zila)

    inf_mort_perc_gdp = zila[['HDI_XXI', 'gdp_perc_health', 'infant_mortality', 'indicator']]
    plot_category_evolution(inf_mort_perc_gdp)

    equity_hdi = zila[["parliament_gender_equity", "HDI_XXI"]]
    st.dataframe(equity_hdi)
    plot_HDI_women_rep(equity_hdi)
