import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3_unweighted
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🔍 FSSR Classification Venn Diagram Generator")

uploaded_file = st.file_uploader("📤 Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Filter out fully compliant rows
    df = df[df["Overall Compliance"] != "Compliant as per FSSR"]

    # Create flag columns
    df["Unsafe"] = df["Overall Safety Classification"].str.strip().str.lower() == "unsafe"
    df["Sub-Standard"] = df["Overall Quality Classification"].str.strip().str.lower() == "sub-standard"
    df["Mis-labelled"] = df["Overall Labelling Complaince"].str.strip().str.lower() == "mis-labelled"

    # Sidebar controls
    st.sidebar.header("🎛 Customize Venn Diagram")
    selected_commodity = st.sidebar.selectbox(
        "Select Commodity", ["Overall"] + sorted(df["Commodity"].unique())
    )
    show_all = st.sidebar.checkbox("Show All 14 Venn Diagrams", value=False)

    figure_width = st.sidebar.slider("Figure Width", 4, 10, 6)
    figure_height = st.sidebar.slider("Figure Height", 4, 10, 6)
    label_fontsize = st.sidebar.slider("Label Font Size", 8, 24, 14)
    value_fontsize = st.sidebar.slider("Value Font Size", 8, 24, 10)

    def plot_venn(data, title):
        set_unsafe = set(data[data["Unsafe"]]["Order ID"])
        set_substandard = set(data[data["Sub-Standard"]]["Order ID"])
        set_mislabelled = set(data[data["Mis-labelled"]]["Order ID"])
    
        fig, ax = plt.subplots(figsize=(figure_width, figure_height))
        v = venn3_unweighted([set_unsafe, set_substandard, set_mislabelled],
                             set_labels=("Unsafe", "Sub-Standard", "Mis-labelled"))
    
        # Fix: apply font size to set labels safely
        if v.set_labels:
            for lbl in v.set_labels:
                if lbl:
                    lbl.set_fontsize(label_fontsize)
    
        # Font size for intersection values
        for subset in v.subset_labels:
            if subset:
                subset.set_fontsize(value_fontsize)
    
        plt.title(title, fontsize=label_fontsize + 2)
        return fig

    # Show diagrams
    if show_all:
        st.subheader("📊 All 14 Venn Diagrams")
        all_commodities = ["Overall"] + sorted(df["Commodity"].unique())
        for com in all_commodities:
            st.markdown(f"### {com}")
            data = df if com == "Overall" else df[df["Commodity"] == com]
            fig = plot_venn(data, com)
            st.pyplot(fig)
    else:
        st.subheader(f"📈 Venn Diagram: {selected_commodity}")
        data = df if selected_commodity == "Overall" else df[df["Commodity"] == selected_commodity]
        fig = plot_venn(data, selected_commodity)
        st.pyplot(fig)

        # Download PNG
        buffer = BytesIO()
        fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        st.download_button(
            label="📥 Download Venn as PNG",
            data=buffer.getvalue(),
            file_name=f"{selected_commodity}_venn.png",
            mime="image/png"
        )
