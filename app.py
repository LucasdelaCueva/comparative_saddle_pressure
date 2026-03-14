import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from analysis_functions import procesar_datos_dbld, comparar_ajustes_completo

# Ensure Google Drive is mounted for file access if running in Colab
# In a production Streamlit app, you might handle file paths differently (e.g., direct upload handling)
# For local testing, ensure files are in the expected directory or handle via st.file_uploader directly.
# This example assumes files might be in a mounted drive path or uploaded.

st.set_page_config(layout="wide")
st.title("Compare Saddle Pressure") # Changed title here

st.markdown("Upload two `.dbld` files to compare initial and post-adjustment biomechanical data.")

# File uploaders
file1 = st.file_uploader("Upload Initial State (.dbld) File", type=["dbld"], key="file1")
file2 = st.file_uploader("Upload Post-Adjustment State (.dbld) File", type=["dbld"], key="file2")

# Notes for the analysis
notes_input = st.text_input("Adjustment Notes (e.g., 'Sillín -5mm | Punta -2.5º')", 
                             "Sillín -5mm | Punta -2.5º | Calas +2mm atrás")

if st.button("Run Analysis"):
    if file1 is not None and file2 is not None:
        # No need for temporary file storage anymore
        # Pass file-like objects directly

        st.subheader("Analysis Report")
        
        # Redirect stdout to capture the printed DataFrame
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            # Execute the function, which will display the plots via plt.show()
            # and print the table to stdout. We capture stdout to display the table.
            # Pass file-like objects directly
            comparar_ajustes_completo(file1, file2, notas=notes_input) 
        
        # Capture the figure displayed by matplotlib.pyplot
        # This assumes the function creates and shows a single figure.
        if plt.get_fignums():
            fig = plt.gcf()
            st.pyplot(fig)
            plt.close(fig) # Close the figure to prevent it from showing again implicitly
        
        s = f.getvalue()
        
        # Extract the DataFrame string from the captured output
        # This is a bit hacky; ideally, the function would return the DataFrame.
        table_start_idx = s.find("--- Comparative Metrics ---")
        if table_start_idx != -1:
            table_str = s[table_start_idx:].strip()
            st.text(table_str)
        else:
            st.error("Could not extract comparative metrics table from output.")

        st.success("Analysis complete!")
        
        # No need for temporary file cleanup anymore

    else:
        st.warning("Please upload both initial and post-adjustment files to run the analysis.")

st.markdown("\n---")
st.markdown("**Note:** This Streamlit app now handles file uploads directly as file-like objects for better performance and security.")
