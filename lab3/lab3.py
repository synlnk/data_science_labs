import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
df = pd.read_csv("vhi_data_clean.csv")

default_index = "VHI"
default_area = sorted(df["area"].unique())[0]
default_week = (1, 52)
default_year = (1982, 2024)

if "selected_index" not in st.session_state:
    st.session_state.selected_index = default_index
if "selected_area" not in st.session_state:
    st.session_state.selected_area = default_area
if "week_range" not in st.session_state:
    st.session_state.week_range = default_week
if "year_range" not in st.session_state:
    st.session_state.year_range = default_year
if "sort_asc" not in st.session_state:
    st.session_state.sort_asc = False
if "sort_desc" not in st.session_state:
    st.session_state.sort_desc = False
     
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("Скинути фільтри"):
        st.session_state.selected_index = default_index
        st.session_state.selected_area = default_area
        st.session_state.week_range = default_week
        st.session_state.year_range = default_year
        st.session_state.sort_asc = False
        st.session_state.sort_desc = False
        st.rerun()

    selected_index = st.selectbox(
        "Оберіть часовий ряд для аналізу:",
        ["VCI", "TCI", "VHI"],
        key="selected_index"
    )
    st.write("Ви обрали індекс:", selected_index)

    selected_area = st.selectbox(
        "Оберіть область:",
        sorted(df["area"].unique()),
        key="selected_area"
    )
    st.write("Ви обрали область:", selected_area)

    week_range = st.slider(
        "Оберіть інтервал тижнів:",
        min_value=1,
        max_value=52,
        value=st.session_state.week_range,
        key="week_range"
    )
    st.write(f"Тижні: з {week_range[0]} по {week_range[1]}")

    year_range = st.slider(
        "Оберіть інтервал років:",
        min_value=1982,
        max_value=2024,
        value=st.session_state.year_range,
        key="year_range"
    )
    st.write(f"Роки: з {year_range[0]} по {year_range[1]}")

    sort_asc = st.checkbox("Сортувати за зростанням", key="sort_asc")
    sort_desc = st.checkbox("Сортувати за спаданням", key="sort_desc")

    if sort_asc and sort_desc:
        st.warning("Увімкнені обидва сортування. Дані не будуть відсортовані.")
        sort_asc = sort_desc = False

with col2:
    tab1, tab2, tab3 = st.tabs(["Таблиця відфільтрованих даних", "Графік відфільтрованих даних", "Графік порівняння даних по областях"])

    with tab1:
        filtered_df = df[
            (df["area"] == selected_area) &
            (df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1]) &
            (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
        ][["Year", "Week", selected_index, "area"]]
        
        if sort_asc:
            filtered_df = filtered_df.sort_values(by=selected_index, ascending=True)
        elif sort_desc:
            filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)
                
        st.write("Відфільтровані дані:")
        st.dataframe(filtered_df)


    with tab2:
        st.write("Графік обраного індексу по обраній області")

        area_filtered = df[
            (df["area"] == selected_area) &
            (df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1]) &
            (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
        ]

        plt.figure(figsize=(10, 5))
        plt.plot(area_filtered["Year"] + area_filtered["Week"] / 52, area_filtered[selected_index], marker='o')
        plt.xlabel("Рік")
        plt.ylabel(selected_index)
        plt.title(f"{selected_index} для {selected_area}")
        plt.grid(True)
        st.pyplot(plt)


    with tab3:
        st.write("Порівняння обраного індексу між областями")

        comparison_df = df[
            (df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1]) &
            (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
        ]

        grouped = comparison_df.groupby(["area", "Year"])[selected_index].mean().reset_index()

        plt.figure(figsize=(12, 6))
        areas = grouped["area"].unique()

        for area in areas:
            area_data = grouped[grouped["area"] == area]
            plt.plot(area_data["Year"], area_data[selected_index],
                    label=area,
                    linewidth=2 if area == selected_area else 1,
                    alpha=1.0 if area == selected_area else 0.5)

        plt.xlabel("Рік")
        plt.ylabel(selected_index)
        plt.title(f"Порівняння {selected_index} між областями")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.grid(True)
        st.pyplot(plt)