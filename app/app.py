import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional


def page_config() -> None:
    st.set_page_config(
        page_title="Bank Statement Analysis",
        page_icon=":money_with_wings:",
        layout="centered",
        initial_sidebar_state="expanded",
    )


def select_bank():
    options = ["Nubank", "Banco do Brasil", "Caixa Economica", "Sicoob"]
    choice = st.selectbox("Select your bank", options)
    return choice


def upload_statement() -> Optional[pd.DataFrame]:
    uploaded_file = st.file_uploader("", type="csv")
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return None


def selected_menu() -> str:
    return option_menu(
        menu_title=None,
        options=["Dia", "Categoria", "Table"],
        icons=[" ", " ", " "],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"width": "100%"},
            "nav-link": {"font-size": "12px", "text-align": "center", "margin": "0px"},
        },
    )


def clean_statement(df: pd.DataFrame, option) -> pd.DataFrame:
    if option == "Nubank":
        df = df[df["title"] != "Pagamento recebido"]
        df["date"] = pd.to_datetime(df["date"])

        category_mapping = {
            "Supermercado": [
                "mercado",
                "supermercado",
                "hortifruti",
                "atacado",
                "atacadista",
            ],
            "Delivery": ["ifood", "delivery", "ifd"],
            "Serviços": ["conta", "energia", "água", "internet", "telefone"],
        }

        def assign_category(title):
            title_lower = title.lower()
            for category, keywords in category_mapping.items():
                if any(keyword in title_lower for keyword in keywords):
                    return category
            return "Outros"

        df["category"] = df["title"].apply(assign_category)
        return df
    else:
        st.warning("In construction!")
        return None


def plot_chart(df: pd.DataFrame, kind: str) -> None:
    try:
        height = 750
        width = 800

        fig = go.Figure()

        fig_sub = make_subplots(
            rows=2,
            cols=1,
            vertical_spacing=0.2,
            subplot_titles=("Daily Expenses", "Cumulative Expenses"),
        )

        if kind == "Dia":
            daily_totals = df.groupby("date")["amount"].sum().reset_index()
            cumulative_totals = daily_totals["amount"].cumsum()

            fig_sub.add_trace(
                go.Bar(
                    x=daily_totals["date"],
                    y=daily_totals["amount"],
                    text=daily_totals["amount"],
                    texttemplate="%{text:.0f}",
                    textposition="outside",
                    textangle=0,
                    textfont=dict(size=12, color="white", family="Segoe UI"),
                    marker_color="#ff4b4b",
                    hovertemplate="%{x}<br>Amount: %{y:.2f}",
                    # showlegend=False,
                    name="",
                )
            )

            fig_sub.add_trace(
                go.Bar(
                    x=daily_totals["date"],
                    y=cumulative_totals,
                    text=cumulative_totals,
                    texttemplate="%{text:.0f}",
                    textposition="outside",
                    textangle=0,
                    textfont=dict(size=12, color="white", family="Segoe UI"),
                    marker_color="#4b4bff",
                    hovertemplate="%{x}<br>Cumulative Amount: %{y:.2f}",
                    # showlegend=False,
                    name="",
                ),
                row=2,
                col=1,
            )

            fig_sub.update_layout(
                title=dict(
                    text="Daily Total Statement Analysis",
                    font=dict(size=20),
                ),
                xaxis=dict(
                    title=None,
                    tickfont=dict(size=12, family="Segoe UI"),
                    tickformat="%d/%m/%y",
                    showgrid=False,
                    zeroline=False,
                    showticklabels=True,
                    ticks="outside",
                    linecolor="white",
                    tickcolor="white",
                ),
                yaxis=dict(
                    showticklabels=False,
                    title=None,
                    showgrid=False,
                    zeroline=False,
                ),
                xaxis2=dict(
                    title=None,
                    tickfont=dict(size=12, family="Segoe UI"),
                    tickformat="%d/%m/%y",
                    showgrid=False,
                    zeroline=False,
                    showticklabels=True,
                    ticks="outside",
                    linecolor="white",
                    tickcolor="white",
                ),
                yaxis2=dict(
                    showticklabels=False,
                    title=None,
                    showgrid=False,
                    zeroline=False,
                ),
                autosize=True,
                height=height,
                width=width,
                uniformtext_minsize=8,
                showlegend=False,
            )
            st.plotly_chart(fig_sub, use_container_width=True)

        elif kind == "Categoria":
            category_totals = (
                df.groupby(["category", "title"])["amount"].sum().reset_index()
            )

            fig.add_trace(
                go.Pie(
                    labels=category_totals["category"],
                    values=category_totals["amount"],
                    textinfo="label+percent+value",
                    hoverinfo="label+percent+value",
                    textposition="inside",
                    textfont=dict(size=12, family="Segoe UI"),
                    # marker=dict(colors=["#ff4b4b", "white", "#ffa6a6"]),
                    # pull=[0.2, 0, 0],
                    # marker=dict(line=dict(color="#0e1117", width=1)),
                )
            )

            fig.update_layout(
                title=dict(
                    text="Category Total Statement Analysis",
                    font=dict(size=20),
                ),
                showlegend=False,
                height=height,
                width=width,
                # margin=dict(l=50, r=50, t=50, b=50),
            )
            st.plotly_chart(fig, use_container_width=True, use_container_height=True)

        elif kind == "Table":
            grouped_df = (
                df.groupby(["date", "title", "category"])["amount"].sum().reset_index()
            )

            st.dataframe(grouped_df, use_container_width=True, height=height)
    except AttributeError as e:
        st.error("Error: The selected statement and uploaded statement do not match.")


def display_selected_chart(menu: str, clean_df: pd.DataFrame) -> None:
    if menu in ["Dia", "Categoria", "Table"]:
        plot_chart(clean_df, menu)


def header() -> None:
    st.title("Bank Statement Analysis")
    st.write("This app allows you to analyze your bank statement data.")


def main() -> None:
    page_config()

    header()

    option = select_bank()

    df = upload_statement()
    if df is not None:
        clean_df = clean_statement(df, option)
        menu = selected_menu()
        display_selected_chart(menu, clean_df)
    else:
        st.warning("Please upload a CSV file to begin analysis.")


if __name__ == "__main__":
    main()
