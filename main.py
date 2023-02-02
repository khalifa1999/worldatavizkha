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

logo = "files/WGS-summit-logo.png"
st.sidebar.image(logo, width=200)

log = "files/WGS-summit-logo-transparency.png"
st.image(log, width=500)

st.title("World data Viz KHALIFA & YERO NIAMADIO")
st.subheader("Feel free to manipulate the interactives dashboards by pressing on Add Filter button and changing variables !!")

uploaded_f = "files/datavizII.xlsx"


# Download the 2 others static presentations
def download_ppt():
    # Specify the file path of the PowerPoint file
    file_path = ""

    # Add a download button and link it to the file path
    st.sidebar.markdown("""
    <a href="{}" download="presentation.pptx">
        <button style="background-color:#0077C9;color:white;padding:10px;">Download 1st static dashboard</button>
    </a>
    """.format(file_path), unsafe_allow_html=True)


# Call the function in your Streamlit app


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
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
    df = pd.read_excel(uploaded_f)
    return df

@st.experimental_memo
def unemployment(data):
    fig = px.scatter(data, x='gdp_perc_education', y='kids_perc_dropout', size='unemployement', color='country')
    st.plotly_chart(fig)
    st.write("The previous scatter plot represents the relationship between country, percentage of GDP dedicated to education, number of children out of school, and unemployment rate. The X-axis represents the gdp percentage for education, the Y-axis represents the percentage percentage of kids out of school, and the size of the dot represents unemployment rate. Each point on the scatter plot represents a country, with its position in the 3D space indicating its unemployment rate, percentage of GDP dedicated to education, and number of children out of school. The color of each point represents the country."\
            "This visualization provides a useful overview of the interplay between these three factors and how they vary between countries. It allows us to see which countries have higher HDI, higher investment in education, and lower numbers of children out of school, and how these factors may be related to each other. Using the filter HDI on it can help us see the trends between develped and developing countries.")

@st.experimental_memo
def plot_category_evolution(data):
    fig = px.scatter_3d(data, x=data["HDI_XXI"], y=data["gdp_perc_health"], z=data['infant_mortality'],
                        color='country')
    st.plotly_chart(fig)
    st.write("A 3D scatter plot showing the relationship between HDI (Human Development Index), percentage of GDP dedicated to health, and infant mortality, where each point represents a country. The x-axis represents HDI, the y-axis represents the percentage of GDP dedicated to health, and the z-axis represents infant mortality. ")


@st.experimental_memo
def plot_HDI_women_rep(data):
    fig = px.scatter(data, x=data['parliament_gender_equity'], y=data['HDI_XXI'], trendline='ols')
    st.plotly_chart(fig)
    st.write(
        "The scatter plot chart shows the relationship between the Human Development Index (HDI) and the percentage of women representation in parliament for different countries. The HDI is a composite measure of three dimensions of human development: health, education, and standard of living." \
        "As observed from the chart, there seems to be a positive correlation between HDI and the percentage of women representation in parliament. Countries with higher HDI values generally have a higher percentage of women representation in parliament, indicating that gender equality and human development are closely linked." \
        "The Ordinary Least Squares (OLS) line is a line of best fit that is used to model the relationship between two variables. In our case, between HDI and women representation, the OLS line represents the relationship between the two variables and how they change together.")



# Create a line chart


if uploaded_f is not None:
    df = temp()

    # Select a category to display
    zila = filter_dataframe(df)

    umpt = zila[['gdp_perc_education','country', 'kids_perc_dropout', 'unemployement']]
    unemployment(umpt)

    inf_mort_perc_gdp = zila[['HDI_XXI', 'gdp_perc_health', 'infant_mortality', 'country']]
    plot_category_evolution(inf_mort_perc_gdp)

    equity_hdi = zila[["parliament_gender_equity", "HDI_XXI"]]
    plot_HDI_women_rep(equity_hdi)
