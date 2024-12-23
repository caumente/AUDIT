import streamlit as st
import plotly.io as pio


def download_plot(fig, label="", filename="image"):
    st.download_button(
        label=f"Download {label} plot",
        data=pio.to_image(fig, format="svg"),
        file_name=f"{filename}.svg",
        mime="/image/svg"
    )