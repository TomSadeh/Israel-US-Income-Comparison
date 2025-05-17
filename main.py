import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import interpolate
import io
import base64
import math

# Set page configuration
st.set_page_config(
    page_title="Israel-US Income Position Calculator",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-text {
        font-size: 1rem;
        color: #4B5563;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }
    .footer {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class IncomeDistributionComparator:
    """Class to compare income positions between US and Israel"""
    
    def __init__(self, percentile_data, ppp_rate=3.7):
        """
        Initialize the comparator with the percentile data and PPP rate
        
        Parameters:
        -----------
        percentile_data : pandas.DataFrame
            DataFrame with percentile data for both countries
        ppp_rate : float
            Purchasing Power Parity rate (ILS to USD)
        """
        self.ppp_rate = ppp_rate
        self.percentile_data = percentile_data
        
        # Prepare the data
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare and validate the data for analysis"""
        # Check for both regular and standardized columns
        required_raw_columns = ['Percentile', 'US_Income_USD', 'Israel_Income_ILS']
        required_std_columns = ['Percentile', 'US_Std_Income_USD', 'Israel_Std_Income_ILS']
        
        # Flag to track if we have standardized data
        self.has_standardized_data = all(col in self.percentile_data.columns for col in required_std_columns)
        
        # Validate required columns
        for col in required_raw_columns:
            if col not in self.percentile_data.columns:
                raise ValueError(f"Required column {col} missing from the data")
        
        # Convert Israeli incomes to USD for easier comparison
        self.percentile_data['Israel_Income_USD'] = self.percentile_data['Israel_Income_ILS'] / self.ppp_rate
        
        # Create interpolation functions for raw income
        self.us_percentile_func = interpolate.interp1d(
            self.percentile_data['US_Income_USD'], 
            self.percentile_data['Percentile'],
            bounds_error=False,
            fill_value=(1, 99)
        )
        
        self.israel_percentile_func = interpolate.interp1d(
            self.percentile_data['Israel_Income_USD'], 
            self.percentile_data['Percentile'],
            bounds_error=False,
            fill_value=(1, 99)
        )
        
        # Create interpolation functions for standardized income if available
        if self.has_standardized_data:
            # Convert Israeli standardized incomes to USD
            self.percentile_data['Israel_Std_Income_USD'] = self.percentile_data['Israel_Std_Income_ILS'] / self.ppp_rate
            
            self.us_std_percentile_func = interpolate.interp1d(
                self.percentile_data['US_Std_Income_USD'], 
                self.percentile_data['Percentile'],
                bounds_error=False,
                fill_value=(1, 99)
            )
            
            self.israel_std_percentile_func = interpolate.interp1d(
                self.percentile_data['Israel_Std_Income_USD'], 
                self.percentile_data['Percentile'],
                bounds_error=False,
                fill_value=(1, 99)
            )
    
    def compare_income(self, income_usd, standardized=False):
        """
        Compare where a given income falls in both distributions
        
        Parameters:
        -----------
        income_usd : float
            Income in USD to compare
        standardized : bool
            Whether to use standardized income distributions
        
        Returns:
        --------
        dict
            Dictionary with comparison results
        """
        # Convert USD to ILS
        income_ils = income_usd * self.ppp_rate
        
        # Find percentiles
        if standardized and self.has_standardized_data:
            us_percentile = float(self.us_std_percentile_func(income_usd))
            israel_percentile = float(self.israel_std_percentile_func(income_usd))
        else:
            us_percentile = float(self.us_percentile_func(income_usd))
            israel_percentile = float(self.israel_percentile_func(income_usd))
        
        return {
            'income_usd': income_usd,
            'income_ils': income_ils,
            'us_percentile': us_percentile,
            'israel_percentile': israel_percentile,
            'percentile_difference': israel_percentile - us_percentile
        }
    
    def plot_income_distributions(self, standardized=False):
        """
        Plot the income distributions of both countries
        
        Parameters:
        -----------
        standardized : bool
            Whether to use standardized income distributions
            
        Returns:
        --------
        matplotlib.figure.Figure
            The generated figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if standardized and self.has_standardized_data:
            # Plotting standardized percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Std_Income_USD'], 
                    label='US Standardized Income Distribution', 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Std_Income_USD'], 
                    label='Israel Standardized Income Distribution (USD PPP)', 
                    linewidth=3)
            
            title_suffix = "Standardized per Capita"
        else:
            # Plotting raw percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Income_USD'], 
                    label='US Income Distribution', 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Income_USD'], 
                    label='Israel Income Distribution (USD PPP)', 
                    linewidth=3)
            
            title_suffix = "Raw Household"
        
        ax.set_xlabel('Percentile')
        ax.set_ylabel(f'Annual {title_suffix} Income (USD)')
        ax.set_title(f'US vs Israel {title_suffix} Income Distributions')
        ax.legend()
        ax.grid(True)
        
        # Format y-axis as currency
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
        
        plt.tight_layout()
        return fig
    
    def plot_income_comparison(self, income_usd, period="annual", standardized=False):
        """
        Plot where a specific income falls in both distributions
        
        Parameters:
        -----------
        income_usd : float
            Income in USD to compare
        period : str
            Period of income ('annual' or 'monthly')
        standardized : bool
            Whether to use standardized income distributions
            
        Returns:
        --------
        matplotlib.figure.Figure
            The generated figure
        """
        # Calculate percentiles
        result = self.compare_income(income_usd, standardized)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if standardized and self.has_standardized_data:
            # Plotting standardized percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Std_Income_USD'], 
                    label='US Standardized Income Distribution', 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Std_Income_USD'], 
                    label='Israel Standardized Income Distribution (USD PPP)', 
                    linewidth=3)
            
            title_suffix = "Standardized per Capita"
        else:
            # Plotting raw percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Income_USD'], 
                    label='US Income Distribution', 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Income_USD'], 
                    label='Israel Income Distribution (USD PPP)', 
                    linewidth=3)
            
            title_suffix = "Household"
        
        # Adding points for the specified income
        us_perc = result['us_percentile']
        israel_perc = result['israel_percentile']
        income = result['income_usd']
        
        # Plot horizontal line at the income level
        ax.axhline(y=income, color='gray', linestyle='--', alpha=0.7)
        
        # Plot points on the distributions
        ax.plot(us_perc, income, 'o', color='blue', markersize=10)
        ax.plot(israel_perc, income, 'o', color='orange', markersize=10)
        
        # Add annotations
        ax.annotate(f"US: {us_perc:.1f}%", 
                  xy=(us_perc, income), 
                  xytext=(us_perc - 5, income * 1.1),
                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                  fontsize=10)
        
        ax.annotate(f"Israel: {israel_perc:.1f}%", 
                  xy=(israel_perc, income), 
                  xytext=(israel_perc + 5, income * 1.1),
                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                  fontsize=10)
        
        # Create title and labels based on period and standardization
        period_str = "Annual" if period == "annual" else "Monthly"
        
        ax.set_xlabel('Percentile')
        ax.set_ylabel(f'{period_str} {title_suffix} Income (USD)')
        ax.set_title(f'Income of ${income:,.0f} in US vs Israel Distributions')
        ax.legend()
        ax.grid(True)
        
        # Format y-axis as currency
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
        
        plt.tight_layout()
        return fig
    
    def create_percentile_table(self, selected_percentiles=[10, 25, 50, 75, 90, 95], period="annual", standardized=False):
        """
        Create a table of key percentiles for comparison
        
        Parameters:
        -----------
        selected_percentiles : list
            List of percentiles to include
        period : str
            Period of income ('annual' or 'monthly')
        standardized : bool
            Whether to use standardized income distributions
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with percentile comparisons
        """
        # Find the closest percentiles in our data
        closest_percentiles = []
        for target in selected_percentiles:
            closest = self.percentile_data['Percentile'].iloc[
                (self.percentile_data['Percentile'] - target).abs().argsort()[0]
            ]
            closest_percentiles.append(closest)
        
        # Filter the data to the selected percentiles
        filtered_data = self.percentile_data[self.percentile_data['Percentile'].isin(closest_percentiles)]
        
        # Select the appropriate columns based on standardization
        if standardized and self.has_standardized_data:
            us_col = 'US_Std_Income_USD'
            ils_col = 'Israel_Std_Income_ILS'
            usd_ppp_col = 'Israel_Std_Income_USD'
            title_prefix = "Standardized "
        else:
            us_col = 'US_Income_USD'
            ils_col = 'Israel_Income_ILS'
            usd_ppp_col = 'Israel_Income_USD'
            title_prefix = ""
        
        # Create the output table with annual or monthly values
        divider = 1 if period == "annual" else 12
        
        table = pd.DataFrame({
            'Percentile': filtered_data['Percentile'],
            f'{title_prefix}US Income (USD)': filtered_data[us_col] / divider,
            f'{title_prefix}Israel Income (ILS)': filtered_data[ils_col] / divider,
            f'{title_prefix}Israel Income (USD PPP)': filtered_data[usd_ppp_col] / divider,
            'Ratio (US/Israel)': filtered_data[us_col] / filtered_data[usd_ppp_col]
        })
        
        return table

def standardize_income(income, household_size):
    """
    Standardize household income by household size using the square root scale
    
    Parameters:
    -----------
    income : float
        Household income
    household_size : int
        Number of people in the household
        
    Returns:
    --------
    float
        Standardized income
    """
    if household_size <= 0:
        return income
    
    # Square root equivalence scale
    return income / math.sqrt(household_size)

def main():
    """Main Streamlit application function"""
    
    # Title and introduction
    st.markdown('<div class="main-header">Israel-US Income Position Calculator</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-text">
    This tool helps you compare where your income would position you in both the Israeli and US distributions.
    It can standardize income by household size to provide per-capita comparisons.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # PPP Rate
    ppp_rate = st.sidebar.number_input(
        "Purchasing Power Parity (PPP) Rate (ILS to USD)",
        min_value=1.0,
        max_value=10.0,
        value=3.7,
        step=0.1,
        help="The number of Israeli Shekels equivalent to 1 US Dollar in purchasing power"
    )
    
    # Read the data.csv file directly
    try:
        percentile_data = pd.read_csv("data.csv")
        st.sidebar.success("Data loaded successfully from data.csv")
    except Exception as e:
        st.error(f"Error loading data.csv: {e}")
        st.info("Please make sure data.csv is in the same directory as this script with the required columns.")
        st.stop()
    
    # Show data preview in sidebar
    with st.sidebar.expander("Preview data (first few rows)"):
        st.dataframe(percentile_data.head())
    
    # Initialize our comparator
    try:
        comparator = IncomeDistributionComparator(percentile_data, ppp_rate)
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.stop()
    
    # Check if standardized data is available
    has_standardized_data = comparator.has_standardized_data
    
    # Income Input Section
    st.markdown('<div class="sub-header">Enter Your Household Information</div>', unsafe_allow_html=True)
    
    # Household size
    household_size = st.number_input(
        "Number of people in your household:",
        min_value=1,
        max_value=20,
        value=1,
        step=1,
        help="This is used to standardize income on a per-capita basis using the square root scale"
    )
    
    # Period selection (Annual/Monthly)
    income_period = st.radio(
        "Income period:",
        ("Annual", "Monthly"),
        index=0,
        horizontal=True
    )
    
    # Currency selection
    currency_option = st.radio(
        "Currency:",
        ("USD", "ILS"),
        index=0,
        horizontal=True
    )
    
    # Income input
    if currency_option == "USD":
        if income_period == "Annual":
            income_usd = st.number_input(
                "Enter your annual household income (USD):",
                min_value=0,
                max_value=10000000,
                value=50000,
                step=1000
            )
            income_ils = income_usd * ppp_rate
            # We store the annual income for calculations
            annual_income_usd = income_usd
            annual_income_ils = income_ils
            # For display purposes
            monthly_income_usd = income_usd / 12
            monthly_income_ils = income_ils / 12
        else:  # Monthly
            income_usd = st.number_input(
                "Enter your monthly household income (USD):",
                min_value=0,
                max_value=1000000,
                value=4000,
                step=100
            )
            income_ils = income_usd * ppp_rate
            # Convert to annual for calculations
            annual_income_usd = income_usd * 12
            annual_income_ils = income_ils * 12
            # For display purposes
            monthly_income_usd = income_usd
            monthly_income_ils = income_ils
    else:  # ILS
        if income_period == "Annual":
            income_ils = st.number_input(
                "Enter your annual household income (ILS):",
                min_value=0,
                max_value=30000000,
                value=int(50000 * ppp_rate),
                step=5000
            )
            income_usd = income_ils / ppp_rate
            # We store the annual income for calculations
            annual_income_usd = income_usd
            annual_income_ils = income_ils
            # For display purposes
            monthly_income_usd = income_usd / 12
            monthly_income_ils = income_ils / 12
        else:  # Monthly
            income_ils = st.number_input(
                "Enter your monthly household income (ILS):",
                min_value=0,
                max_value=2500000,
                value=int(4000 * ppp_rate),
                step=500
            )
            income_usd = income_ils / ppp_rate
            # Convert to annual for calculations
            annual_income_usd = income_usd * 12
            annual_income_ils = income_ils * 12
            # For display purposes
            monthly_income_usd = income_usd
            monthly_income_ils = income_ils
    
    # Standardization selection
    standardize = st.checkbox(
        "Use standardized per capita income", 
        value=False,
        help="Compare using standardized income distributions (adjusted for household size)"
    )
    
    # Alert user if standardized data is requested but not available
    if standardize and not has_standardized_data:
        st.warning("Standardized income data is not available in the uploaded file. The application will use manual standardization which may be less accurate than using pre-calculated standardized distributions.")
    
    # Calculate standardized income if selected
    if standardize:
        std_annual_income_usd = standardize_income(annual_income_usd, household_size)
        std_annual_income_ils = standardize_income(annual_income_ils, household_size)
        std_monthly_income_usd = std_annual_income_usd / 12
        std_monthly_income_ils = std_annual_income_ils / 12
        
        # Use standardized income for calculations
        calculation_income_usd = std_annual_income_usd
    else:
        # Use raw income for calculations
        calculation_income_usd = annual_income_usd
        
        # Set these for display purposes
        std_annual_income_usd = standardize_income(annual_income_usd, household_size)
        std_annual_income_ils = standardize_income(annual_income_ils, household_size)
        std_monthly_income_usd = std_annual_income_usd / 12
        std_monthly_income_ils = std_annual_income_ils / 12
    
    # Results Section
    st.markdown('<div class="sub-header">Results: Your Income Position</div>', unsafe_allow_html=True)
    
    # Calculate the income position using selected income and distribution
    result = comparator.compare_income(calculation_income_usd, standardize)
    
    # Create columns for results
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        st.markdown(f"""
        <div class="highlight">
        <h3>Raw Income</h3>
        <p>Annual USD: <b>${annual_income_usd:,.2f}</b></p>
        <p>Annual ILS: <b>₪{annual_income_ils:,.2f}</b></p>
        <p>Monthly USD: <b>${monthly_income_usd:,.2f}</b></p>
        <p>Monthly ILS: <b>₪{monthly_income_ils:,.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="highlight">
        <h3>Standardized Income</h3>
        <p>Annual USD: <b>${std_annual_income_usd:,.2f}</b></p>
        <p>Annual ILS: <b>₪{std_annual_income_ils:,.2f}</b></p>
        <p>Monthly USD: <b>${std_monthly_income_usd:,.2f}</b></p>
        <p>Monthly ILS: <b>₪{std_monthly_income_ils:,.2f}</b></p>
        <p><em>Divided by √{household_size} = {math.sqrt(household_size):.3f}</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="highlight">
        <h3>Percentile Position</h3>
        <p>US Distribution: <b>{result['us_percentile']:.1f}%</b></p>
        <p>Israel Distribution: <b>{result['israel_percentile']:.1f}%</b></p>
        <p>Difference: <b>{result['percentile_difference']:.1f} points</b></p>
        <p>{"<em>Using pre-calculated standardized distributions</em>" if standardize and has_standardized_data else ""}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Interpretation
    if abs(result['percentile_difference']) < 3:
        interpretation = "Your income has a similar relative position in both countries."
    elif result['percentile_difference'] > 0:
        interpretation = f"Your income puts you {result['percentile_difference']:.1f} percentile points higher in Israel than in the US."
    else:
        interpretation = f"Your income puts you {abs(result['percentile_difference']):.1f} percentile points higher in the US than in Israel."
    
    st.markdown(f"""
    <div class="highlight">
    <h3>Interpretation</h3>
    <p>{interpretation}</p>
    <p>This means {f"a standardized " if standardize else "an "}annual income of ${calculation_income_usd:,.2f} would place you:</p>
    <ul>
        <li>At the {result['us_percentile']:.1f}th percentile in the US (higher than {result['us_percentile']:.1f}% of US households)</li>
        <li>At the {result['israel_percentile']:.1f}th percentile in Israel (higher than {result['israel_percentile']:.1f}% of Israeli households)</li>
    </ul>
    {f"<p><em>Note: This analysis uses {'pre-calculated' if has_standardized_data else 'manually calculated'} standardized income distributions that account for household size.</em></p>" if standardize else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<div class="sub-header">Visual Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Your Position", "Income Distributions"])
    
    with tab1:
        st.pyplot(comparator.plot_income_comparison(
            calculation_income_usd, 
            period=income_period.lower(), 
            standardized=standardize
        ))
        st.caption(f"This chart shows where your{' standardized' if standardize else ''} income falls within both distributions.")
    
    with tab2:
        st.pyplot(comparator.plot_income_distributions(standardize))
        st.caption(f"This chart shows the {'standardized ' if standardize else ''}income distributions of both countries.")
    
    
    # Additional Context
    st.markdown('<div class="sub-header">Key Income Thresholds</div>', unsafe_allow_html=True)
    
    # Create a table of key percentiles based on the selected period and standardization
    percentile_table = comparator.create_percentile_table(
        period=income_period.lower(),
        standardized=standardize
    )
    
    # Format the table for display
    display_table = percentile_table.copy()
    # Find the column names dynamically since they might include 'Standardized' prefix
    for col in display_table.columns:
        if 'USD' in col:
            display_table[col] = display_table[col].apply(lambda x: f"${x:,.0f}")
        elif 'ILS' in col:
            display_table[col] = display_table[col].apply(lambda x: f"₪{x:,.0f}")
        elif 'Ratio' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:.2f}")
    
    period_label = "Monthly" if income_period == "Monthly" else "Annual"
    standardized_label = "Standardized " if standardize else ""
    st.write(f"**{period_label} {standardized_label}Income at Key Percentiles:**")
    st.table(display_table)
    
    # Methodology and Notes
    with st.expander("Methodology and Notes"):
        st.markdown("""
        ### Data Sources and Methodology
        
        - **Data Sources**: This tool uses income percentile data from the provided data.csv file.
        - **PPP Conversion**: Israeli incomes are converted to USD using the selected Purchasing Power Parity (PPP) rate.
        - **Income Standardization**: When selected, income is standardized by dividing by the square root of household size.
        - **Distribution Type**: The tool can use either raw household income distributions or standardized per capita distributions.
        
        ### Square Root Equivalence Scale
        
        The square root scale divides household income by the square root of household size to account for economies of scale:
        
        - For a household of 1 person: divide by √1 = 1 (no change)
        - For a household of 2 people: divide by √2 ≈ 1.414
        - For a household of 3 people: divide by √3 ≈ 1.732
        - For a household of 4 people: divide by √4 = 2
        
        This approach, used by the OECD and many economists, recognizes that larger households benefit from economies of scale in consumption.
        
        ### Data File Format
        
        For the most accurate comparisons, the data.csv file should include both raw and standardized income distributions:
        
        - Raw income columns: `Percentile`, `US_Income_USD`, `Israel_Income_ILS`
        - Standardized income columns: `US_Std_Income_USD`, `Israel_Std_Income_ILS`
        
        If standardized columns are not available, the tool will calculate standardized incomes manually.
        
        ### Limitations
        
        - This analysis does not account for differences in:
          - Tax systems
          - Benefits and social services
          - Cost of living within different regions of each country
          - Household composition (age, etc.)
        
        ### Interpretation
        
        The percentile position indicates where an income falls in the distribution of each country. For example, 
        being at the 75th percentile means your income is higher than 75% of households in that country.
        
        A similar percentile position in both countries suggests that your relative economic standing would be 
        similar in either country, while a substantial difference indicates that your relative position would change.
        """)
    
    # Footer
    st.markdown("""
    <div class="footer">
    This tool is for informational purposes only. Economic comparisons between countries are complex and involve many factors beyond income distributions.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()