import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Library Budget Explorer", layout="wide")

# Strong CSS for large graph captions
st.markdown("""
    <style>
    .stCaption, .stCaption p {
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        line-height: 1.8 !important;
        margin-top: 25px !important;
        margin-bottom: 35px !important;
        color: #f0f0f0 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Nassau Library Budget Comparator — FY 2026")


# Load the data
@st.cache_data
def load_data():
    df = pd.read_excel("Nasau Budget Comparisons DS.xlsx", sheet_name="Sheet1")
    return df


df = load_data()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Libraries", f"{len(df):,}")
col2.metric("Total FY 2026 Budget", f"${df['FY 2026 Budget'].sum():,}")
col3.metric("Avg Cost per Resident", f"${df['Cost per resident'].mean():.2f}")
col4.metric("Highest Cost per Resident",
            f"{df.loc[df['Cost per resident'].idxmax(), 'Library Name']} (${df['Cost per resident'].max():.2f})")

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar Filters with clear label
st.sidebar.header("🔍 Filters")

st.sidebar.subheader("Library Type")

selected_types = []
for lib_type in sorted(df["Library Type"].unique()):
    if st.sidebar.checkbox(lib_type, value=True, key=lib_type):
        selected_types.append(lib_type)

pop_col = "Population (ACS 2024-5 year estimate)"

min_pop = st.sidebar.slider(
    "Minimum Population",
    min_value=int(df[pop_col].min()),
    max_value=int(df[pop_col].max()),
    value=int(df[pop_col].min()),
    format="%,d"
)

min_budget = st.sidebar.slider(
    "Minimum Budget ($)",
    min_value=0,
    max_value=int(df["FY 2026 Budget"].max()),
    value=0,
    format="%,d"
)

# Apply filters
filtered_df = df[
    (df["Library Type"].isin(selected_types)) &
    (df[pop_col] >= min_pop) &
    (df["FY 2026 Budget"] >= min_budget)
    ]

st.subheader(f"Showing {len(filtered_df):,} of {len(df):,} libraries")

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs(["Budget vs Population", "Cost per Resident", "Full Table", "Download"])

with tab1:
    st.markdown("### Budget vs Population")
    fig_scatter = px.scatter(
        filtered_df,
        x=pop_col,
        y="FY 2026 Budget",
        size="Cost per resident",
        color="Library Type",
        hover_name="Library Name",
        title="",
        labels={"FY 2026 Budget": "FY 2026 Budget ($)"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption(
        "This scatter plot shows each library’s population size on the x-axis and its FY 2026 budget on the y-axis. The size of each bubble represents the cost per resident. Larger bubbles mean a higher cost per person.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### Top 10 Libraries by FY 2026 Budget")
    top10 = filtered_df.nlargest(10, "FY 2026 Budget")
    fig_bar = px.bar(top10, x="Library Name", y="FY 2026 Budget", color="Library Type")
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("This bar chart shows the 10 libraries with the largest total budgets.")

with tab2:
    st.markdown("### Libraries Ranked by Cost per Resident")
    cost_sorted = filtered_df.sort_values("Cost per resident", ascending=False)
    fig_cost = px.bar(cost_sorted.head(15), x="Library Name", y="Cost per resident",
                      color="Library Type", title="")
    st.plotly_chart(fig_cost, use_container_width=True)
    st.caption("This bar chart ranks the libraries from highest to lowest cost per resident.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### Cost per Resident by Library Type")
    fig_box = px.box(filtered_df, x="Library Type", y="Cost per resident",
                     title="")
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption(
        "This chart shows how the cost per resident compares across the different library types. For each type, the box represents the typical range of spending per resident. The line inside the box shows the usual (typical) cost for libraries in that group. If the box is wide or spread out, it means there is a lot of variation in how much libraries of that type spend per resident. If the box sits higher up on the chart, it means that library type generally has higher costs per resident than the others.")

with tab3:
    st.markdown("### Detailed Data Table")
    display_df = filtered_df.copy()
    display_df["FY 2026 Budget"] = display_df["FY 2026 Budget"].apply(lambda x: f"${x:,.0f}")
    display_df["Population (ACS 2024-5 year estimate)"] = display_df["Population (ACS 2024-5 year estimate)"].apply(
        lambda x: f"{x:,.0f}")
    display_df["Cost per resident"] = display_df["Cost per resident"].apply(lambda x: f"${x:.2f}")

    st.dataframe(display_df.sort_values("Cost per resident", ascending=False),
                 use_container_width=True, hide_index=True)

with tab4:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download filtered data as CSV",
        csv,
        "nassau_filtered_libraries.csv",
        "text/csv"
    )

# ==================== KEY INSIGHTS AT THE BOTTOM ====================
st.markdown("---")
st.markdown("### Key Insights")

if len(filtered_df) > 0:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Budget vs Population View**")
        st.write(
            f"• Largest budget: **{filtered_df.loc[filtered_df['FY 2026 Budget'].idxmax(), 'Library Name']}** (${filtered_df['FY 2026 Budget'].max():,})")
        st.write(
            f"• Smallest budget: **{filtered_df.loc[filtered_df['FY 2026 Budget'].idxmin(), 'Library Name']}** (${filtered_df['FY 2026 Budget'].min():,})")

    with col_b:
        st.markdown("**Cost per Resident View**")
        st.write(
            f"• Highest cost per resident: **{filtered_df.loc[filtered_df['Cost per resident'].idxmax(), 'Library Name']}** (${filtered_df['Cost per resident'].max():.2f})")
        st.write(
            f"• Lowest cost per resident: **{filtered_df.loc[filtered_df['Cost per resident'].idxmin(), 'Library Name']}** (${filtered_df['Cost per resident'].min():.2f})")

# Credit
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Dashboard built by Rafael Hernandez")