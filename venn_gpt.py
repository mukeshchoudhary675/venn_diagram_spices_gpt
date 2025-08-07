import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from io import StringIO

st.title("Venn Diagram Generator for FSSR Classifications")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Filter out fully compliant rows
    df_filtered = df[df["Overall Compliance"] != "Compliant as per FSSR"]

    # Define flags
    df_filtered["Unsafe"] = df_filtered["Overall Safety Classification"].str.strip().str.lower() == "unsafe"
    df_filtered["Sub-Standard"] = df_filtered["Overall Quality Classification"].str.strip().str.lower() == "sub-standard"
    df_filtered["Mis-labelled"] = df_filtered["Overall Labelling Complaince"].str.strip().str.lower() == "mis-labelled"

    def plot_venn(data, title):
        set_unsafe = set(data[data["Unsafe"]]["Order ID"])
        set_substandard = set(data[data["Sub-Standard"]]["Order ID"])
        set_mislabelled = set(data[data["Mis-labelled"]]["Order ID"])

        plt.figure(figsize=(4, 4))
        venn3([set_unsafe, set_substandard, set_mislabelled],
              set_labels=("Unsafe", "Sub-Standard", "Mis-labelled"))
        plt.title(title)
        st.pyplot(plt.gcf())
        plt.close()

    st.subheader("Overall Venn Diagram")
    plot_venn(df_filtered, "Overall")

    st.subheader("Per Commodity Venn Diagrams")

    for commodity in sorted(df_filtered["Commodity"].unique()):
        st.markdown(f"### {commodity}")
        df_commodity = df_filtered[df_filtered["Commodity"] == commodity]
        if len(df_commodity) > 0:
            plot_venn(df_commodity, commodity)
        else:
            st.write("No data for this commodity.")
