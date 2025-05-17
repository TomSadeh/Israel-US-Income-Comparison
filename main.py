import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
import math
import bidi.algorithm as bidi  # For RTL text handling in plots

# Set page configuration
st.set_page_config(
    page_title="Israel-US Income Position Calculator",
    page_icon="📊",
    layout="wide"
)

# Define translations
translations = {
    "en": {
        "page_title": "Israel-US Income Position Calculator",
        "intro": "This tool helps you compare where your income would position you in both the Israeli and US distributions. It can standardize income by household size to provide per-capita comparisons.",
        "config": "Configuration",
        "ppp_rate": "Purchasing Power Parity (PPP) Rate (ILS to USD)",
        "ppp_help": "The number of Israeli Shekels equivalent to 1 US Dollar in purchasing power",
        "data_loaded": "Data loaded successfully from data.csv",
        "data_error": "Error loading data.csv: ",
        "data_info": "Please make sure data.csv is in the same directory as this script with the required columns.",
        "preview_data": "Preview data (first few rows)",
        "error_processing": "Error processing data: ",
        "household_info": "Enter Your Household Information",
        "household_size": "Number of people in your household:",
        "household_help": "This is used to standardize income on a per-capita basis using the square root scale",
        "income_period": "Income period:",
        "annual": "Annual",
        "monthly": "Monthly",
        "currency": "Currency:",
        "annual_usd": "Enter your annual total household income before taxes (USD):",
        "monthly_usd": "Enter your monthly total household income before taxes (USD):",
        "annual_ils": "Enter your annual total household income before taxes (ILS):",
        "monthly_ils": "Enter your monthly total household income before taxes (ILS):",
        "standardize": "Use standardized per capita income",
        "standardize_help": "Compare using standardized income distributions (adjusted for household size)",
        "standardize_warning": "Standardized income data is not available in the uploaded file. The application will use manual standardization which may be less accurate than using pre-calculated standardized distributions.",
        "results": "Results: Your Income Position",
        "raw_income": "Raw Income",
        "annual_usd_short": "Annual USD:",
        "annual_ils_short": "Annual ILS:",
        "monthly_usd_short": "Monthly USD:",
        "monthly_ils_short": "Monthly ILS:",
        "std_income": "Standardized Income",
        "divided_by": "Divided by √{} = {:.3f}",
        "percentile_position": "Percentile Position",
        "us_dist": "US Distribution:",
        "il_dist": "Israel Distribution:",
        "difference": "Difference:",
        "points": "points",
        "using_precalc": "Using pre-calculated standardized distributions",
        "interpretation": "Interpretation",
        "similar_position": "Your income has a similar relative position in both countries.",
        "higher_in_il": "Your income puts you {:.1f} percentile points higher in Israel than in the US.",
        "higher_in_us": "Your income puts you {:.1f} percentile points higher in the US than in Israel.",
        "this_means": "This means {} annual income of ${:,.2f} would place you:",
        "standardized_a": "a standardized ",
        "an": "an ",
        "us_percentile": "At the {:.1f}th percentile in the US (higher than {:.1f}% of US households)",
        "il_percentile": "At the {:.1f}th percentile in Israel (higher than {:.1f}% of Israeli households)",
        "note_analysis": "Note: This analysis uses {} standardized income distributions that account for household size.",
        "precalculated": "pre-calculated",
        "manually_calculated": "manually calculated",
        "visual_analysis": "Visual Analysis",
        "your_position": "Your Position",
        "income_distributions": "Income Distributions",
        "chart_shows_where": "This chart shows where your{} income falls within both distributions.",
        "standardized_space": " standardized",
        "chart_shows_dist": "This chart shows the {} income distributions of both countries.",
        "key_thresholds": "Key Income Thresholds",
        "income_at_key": "{} {} Income at Key Percentiles:",
        "methodology": "Methodology and Notes",
        "data_sources": "Data Sources and Methodology",
        "data_sources_text": """- **Data Sources**: This tool uses income percentile data from the provided data.csv file.
- **PPP Conversion**: Israeli incomes are converted to USD using the selected Purchasing Power Parity (PPP) rate.
- **Income Standardization**: When selected, income is standardized by dividing by the square root of household size.
- **Distribution Type**: The tool can use either raw household income distributions or standardized per capita distributions.""",
        "square_root": "Square Root Equivalence Scale",
        "square_root_text": """The square root scale divides household income by the square root of household size to account for economies of scale:

- For a household of 1 person: divide by √1 = 1 (no change)
- For a household of 2 people: divide by √2 ≈ 1.414
- For a household of 3 people: divide by √3 ≈ 1.732
- For a household of 4 people: divide by √4 = 2

This approach, used by the OECD and many economists, recognizes that larger households benefit from economies of scale in consumption.""",
        "data_file": "Data File Format",
        "data_file_text": """For the most accurate comparisons, the data.csv file should include both raw and standardized income distributions:

- Raw income columns: `Percentile`, `US_Income_USD`, `Israel_Income_ILS`
- Standardized income columns: `US_Std_Income_USD`, `Israel_Std_Income_ILS`

If standardized columns are not available, the tool will calculate standardized incomes manually.""",
        "limitations": "Limitations",
        "limitations_text": """- This analysis does not account for differences in:
  - Tax systems
  - Benefits and social services
  - Cost of living within different regions of each country
  - Household composition (age, etc.)""",
        "interpretation_header": "Interpretation",
        "interpretation_text": """The percentile position indicates where an income falls in the distribution of each country. For example, 
being at the 75th percentile means your income is higher than 75% of households in that country.

A similar percentile position in both countries suggests that your relative economic standing would be 
similar in either country, while a substantial difference indicates that your relative position would change.""",
        "footer": "This tool is for informational purposes only. Economic comparisons between countries are complex and involve many factors beyond income distributions."
    },
    "he": {
        "page_title": "מחשבון מיקום הכנסה ישראל-ארה\"ב",
        "intro": "כלי זה עוזר לך להשוות היכן ההכנסה שלך תמקם אותך בהתפלגויות של ישראל וארה\"ב. הוא יכול לתקנן הכנסה לפי גודל משק הבית כדי לספק השוואות לנפש.",
        "config": "הגדרות",
        "ppp_rate": "שער שווי כוח קנייה (PPP) (ש\"ח לדולר)",
        "ppp_help": "מספר השקלים הישראליים שווי ערך ל-1 דולר אמריקאי בכוח קנייה",
        "data_loaded": "הנתונים נטענו בהצלחה מקובץ data.csv",
        "data_error": "שגיאה בטעינת data.csv: ",
        "data_info": "אנא ודא שקובץ data.csv נמצא באותה תיקייה כמו סקריפט זה עם העמודות הנדרשות.",
        "preview_data": "תצוגה מקדימה של הנתונים (שורות ראשונות)",
        "error_processing": "שגיאה בעיבוד הנתונים: ",
        "household_info": "הזן את פרטי משק הבית שלך",
        "household_size": "מספר האנשים במשק הבית שלך:",
        "household_help": "משמש לתקנון הכנסה על בסיס לנפש באמצעות סולם שורש ריבועי",
        "income_period": "תקופת הכנסה:",
        "annual": "שנתי",
        "monthly": "חודשי",
        "currency": "מטבע:",
        "annual_usd": "הזן את הכנסתך השנתית הכוללת של משק הבית לפני מסים (דולר):",
        "monthly_usd": "הזן את הכנסתך החודשית הכוללת של משק הבית לפני מסים (דולר):",
        "annual_ils": "הזן את הכנסתך השנתית הכוללת של משק הבית לפני מסים (ש\"ח):",
        "monthly_ils": "הזן את הכנסתך החודשית הכוללת של משק הבית לפני מסים (ש\"ח):",
        "standardize": "השתמש בהכנסה מתוקננת לנפש",
        "standardize_help": "השווה באמצעות התפלגויות הכנסה מתוקננות (מותאמות לגודל משק הבית)",
        "standardize_warning": "נתוני הכנסה מתוקננים אינם זמינים בקובץ שהועלה. האפליקציה תשתמש בתקנון ידני שעשוי להיות פחות מדויק מאשר שימוש בהתפלגויות מתוקננות שחושבו מראש.",
        "results": "תוצאות: מיקום ההכנסה שלך",
        "raw_income": "הכנסה גולמית",
        "annual_usd_short": "שנתי בדולר:",
        "annual_ils_short": "שנתי בש\"ח:",
        "monthly_usd_short": "חודשי בדולר:",
        "monthly_ils_short": "חודשי בש\"ח:",
        "std_income": "הכנסה מתוקננת",
        "divided_by": "מחולק ב-√{} = {:.3f}",
        "percentile_position": "מיקום באחוזונים",
        "us_dist": "התפלגות ארה\"ב:",
        "il_dist": "התפלגות ישראל:",
        "difference": "הפרש:",
        "points": "נקודות",
        "using_precalc": "משתמש בהתפלגויות מתוקננות שחושבו מראש",
        "interpretation": "פרשנות",
        "similar_position": "להכנסה שלך יש מיקום יחסי דומה בשתי המדינות.",
        "higher_in_il": "ההכנסה שלך ממקמת אותך {:.1f} נקודות אחוזון גבוה יותר בישראל מאשר בארה\"ב.",
        "higher_in_us": "ההכנסה שלך ממקמת אותך {:.1f} נקודות אחוזון גבוה יותר בארה\"ב מאשר בישראל.",
        "this_means": "משמעות הדבר היא שהכנסה שנתית {} של ${:,.2f} תמקם אותך:",
        "standardized_a": "מתוקננת ",
        "an": "",
        "us_percentile": "באחוזון ה-{:.1f} בארה\"ב (גבוה יותר מ-{:.1f}% ממשקי הבית בארה\"ב)",
        "il_percentile": "באחוזון ה-{:.1f} בישראל (גבוה יותר מ-{:.1f}% ממשקי הבית בישראל)",
        "note_analysis": "הערה: ניתוח זה משתמש בהתפלגויות הכנסה מתוקננות {} המתחשבות בגודל משק הבית.",
        "precalculated": "שחושבו מראש",
        "manually_calculated": "שחושבו ידנית",
        "visual_analysis": "ניתוח חזותי",
        "your_position": "המיקום שלך",
        "income_distributions": "התפלגויות הכנסה",
        "chart_shows_where": "תרשים זה מראה היכן ההכנסה{} שלך נמצאת בשתי ההתפלגויות.",
        "standardized_space": " המתוקננת",
        "chart_shows_dist": "תרשים זה מראה את התפלגויות ההכנסה {} של שתי המדינות.",
        "key_thresholds": "ספי הכנסה מרכזיים",
        "income_at_key": "הכנסה {} {} באחוזונים מרכזיים:",
        "methodology": "מתודולוגיה והערות",
        "data_sources": "מקורות נתונים ומתודולוגיה",
        "data_sources_text": """- **מקורות נתונים**: כלי זה משתמש בנתוני אחוזוני הכנסה מקובץ data.csv שסופק.
- **המרת PPP**: הכנסות ישראליות מומרות לדולר באמצעות שער שווי כוח הקנייה (PPP) שנבחר.
- **תקנון הכנסה**: כאשר נבחר, ההכנסה מתוקננת על ידי חלוקה בשורש הריבועי של גודל משק הבית.
- **סוג ההתפלגות**: הכלי יכול להשתמש בהתפלגויות הכנסה גולמיות של משקי בית או בהתפלגויות מתוקננות לנפש.""",
        "square_root": "סולם שקילות שורש ריבועי",
        "square_root_text": """סולם השורש הריבועי מחלק את הכנסת משק הבית בשורש הריבועי של גודל משק הבית כדי להתחשב ביתרונות לגודל:

- עבור משק בית של אדם אחד: לחלק ב-√1 = 1 (ללא שינוי)
- עבור משק בית של 2 אנשים: לחלק ב-√2 ≈ 1.414
- עבור משק בית של 3 אנשים: לחלק ב-√3 ≈ 1.732
- עבור משק בית של 4 אנשים: לחלק ב-√4 = 2

גישה זו, המשמשת את ה-OECD וכלכלנים רבים, מכירה בכך שמשקי בית גדולים יותר נהנים מיתרונות לגודל בצריכה.""",
        "data_file": "פורמט קובץ נתונים",
        "data_file_text": """להשוואות המדויקות ביותר, קובץ data.csv צריך לכלול הן התפלגויות הכנסה גולמיות והן מתוקננות:

- עמודות הכנסה גולמית: `Percentile`, `US_Income_USD`, `Israel_Income_ILS`
- עמודות הכנסה מתוקננת: `US_Std_Income_USD`, `Israel_Std_Income_ILS`

אם עמודות מתוקננות אינן זמינות, הכלי יחשב הכנסות מתוקננות באופן ידני.""",
        "limitations": "מגבלות",
        "limitations_text": """- ניתוח זה אינו מתחשב בהבדלים ב:
  - מערכות מס
  - הטבות ושירותים חברתיים
  - יוקר המחיה באזורים שונים של כל מדינה
  - הרכב משק הבית (גיל וכו')""",
        "interpretation_header": "פרשנות",
        "interpretation_text": """מיקום האחוזון מציין היכן הכנסה נמצאת בהתפלגות של כל מדינה. לדוגמה,
להיות באחוזון ה-75 פירושו שההכנסה שלך גבוהה יותר מ-75% ממשקי הבית באותה מדינה.

מיקום אחוזון דומה בשתי המדינות מרמז על כך שהמעמד הכלכלי היחסי שלך יהיה
דומה בכל אחת מהמדינות, בעוד שהבדל משמעותי מצביע על כך שהמיקום היחסי שלך ישתנה.""",
        "footer": "כלי זה הוא למטרות מידע בלבד. השוואות כלכליות בין מדינות הן מורכבות וכוללות גורמים רבים מעבר להתפלגויות הכנסה."
    }
}

# Custom CSS for better appearance, including RTL support
def get_custom_css(is_rtl=False):
    dir_attr = "rtl" if is_rtl else "ltr"
    text_align = "right" if is_rtl else "left"
    
    return f"""
    <style>
        .main-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 1rem;
            direction: {dir_attr};
            text-align: {text_align};
        }}
        .sub-header {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #2563EB;
            margin-top: 2rem;
            margin-bottom: 1rem;
            direction: {dir_attr};
            text-align: {text_align};
        }}
        .info-text {{
            font-size: 1rem;
            color: #4B5563;
            direction: {dir_attr};
            text-align: {text_align};
        }}
        .highlight {{
            background-color: #DBEAFE;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            direction: {dir_attr};
            text-align: {text_align};
        }}
        .tooltip {{
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted black;
        }}
        .footer {{
            font-size: 0.8rem;
            color: #6B7280;
            margin-top: 3rem;
            text-align: center;
            direction: {dir_attr};
        }}
        /* RTL specific styling */
        [dir="rtl"] {{
            unicode-bidi: embed;
        }}
        [dir="rtl"] .stButton {{
            direction: rtl;
            float: right;
        }}
        [dir="rtl"] div.row-widget.stRadio > div {{
            flex-direction: row-reverse;
        }}
        [dir="rtl"] .stCheckbox {{
            direction: rtl;
        }}
        /* Fix number input for RTL */
        [dir="rtl"] input[type="number"] {{
            direction: ltr;
            text-align: right;
        }}
    </style>
    """

class IncomeDistributionComparator:
    """Class to compare income positions between US and Israel"""
    
    def __init__(self, percentile_data, ppp_rate=3.7, is_rtl=False):
        """
        Initialize the comparator with the percentile data and PPP rate
        
        Parameters:
        -----------
        percentile_data : pandas.DataFrame
            DataFrame with percentile data for both countries
        ppp_rate : float
            Purchasing Power Parity rate (ILS to USD)
        is_rtl : bool
            Whether to use RTL layout for plots
        """
        self.ppp_rate = ppp_rate
        self.percentile_data = percentile_data
        self.is_rtl = is_rtl
        
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
    
    def plot_income_distributions(self, standardized=False, lang="en"):
        """
        Plot the income distributions of both countries
        
        Parameters:
        -----------
        standardized : bool
            Whether to use standardized income distributions
        lang : str
            Language code for plot text
            
        Returns:
        --------
        matplotlib.figure.Figure
            The generated figure
        """
        # Get translation for labels
        texts = {
            "en": {
                "percentile": "Percentile",
                "annual_income": "Annual {} Income (USD)",
                "distributions_title": "US vs Israel {} Income Distributions",
                "us_dist": "US {} Income Distribution",
                "il_dist": "Israel {} Income Distribution (USD PPP)",
                "raw": "Household",
                "standardized": "Standardized per Capita"
            },
            "he": {
                "percentile": "אחוזון",
                "annual_income": "הכנסה שנתית {} (USD)",
                "distributions_title": "התפלגויות הכנסה {} ארה\"ב לעומת ישראל",
                "us_dist": "התפלגות הכנסה {} ארה\"ב",
                "il_dist": "התפלגות הכנסה {} ישראל (USD PPP)",
                "raw": "משק בית",
                "standardized": "מתוקננת לנפש"
            }
        }[lang]
        
        # Set matplotlib parameters for RTL support
        if self.is_rtl:
            plt.rcParams['axes.titlepad'] = 10
            plt.rcParams['font.family'] = 'DejaVu Sans'  # A font that supports Hebrew
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if standardized and self.has_standardized_data:
            # Plotting standardized percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Std_Income_USD'], 
                    label=texts["us_dist"].format(texts["standardized"]), 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Std_Income_USD'], 
                    label=texts["il_dist"].format(texts["standardized"]), 
                    linewidth=3)
            
            title_suffix = texts["standardized"]
        else:
            # Plotting raw percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Income_USD'], 
                    label=texts["us_dist"].format(texts["raw"]), 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Income_USD'], 
                    label=texts["il_dist"].format(texts["raw"]), 
                    linewidth=3)
            
            title_suffix = texts["raw"]
        
        # Handle RTL for labels and titles
        if self.is_rtl:
            ax.set_xlabel(bidi.get_display(texts["percentile"]))
            ax.set_ylabel(bidi.get_display(texts["annual_income"].format(title_suffix)))
            ax.set_title(bidi.get_display(texts["distributions_title"].format(title_suffix)))
            
            # RTL labels for legend
            handles, labels = ax.get_legend_handles_labels()
            rtl_labels = [bidi.get_display(label) for label in labels]
            ax.legend(handles, rtl_labels)
        else:
            ax.set_xlabel(texts["percentile"])
            ax.set_ylabel(texts["annual_income"].format(title_suffix))
            ax.set_title(texts["distributions_title"].format(title_suffix))
            ax.legend()
        
        ax.grid(True)
        
        # Format y-axis as currency
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
        
        # Flip x-axis for RTL layout
        if self.is_rtl:
            ax.invert_xaxis()
        
        plt.tight_layout()
        return fig
    
    def plot_income_comparison(self, income_usd, period="annual", standardized=False, lang="en"):
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
        lang : str
            Language code for plot text
            
        Returns:
        --------
        matplotlib.figure.Figure
            The generated figure
        """
        # Get translation for labels
        texts = {
            "en": {
                "percentile": "Percentile",
                "annual_income": "Annual {} Income (USD)",
                "monthly_income": "Monthly {} Income (USD)",
                "income_title": "Income of ${:,.0f} in US vs Israel Distributions",
                "us_dist": "US {} Income Distribution",
                "il_dist": "Israel {} Income Distribution (USD PPP)",
                "raw": "Household",
                "standardized": "Standardized per Capita",
                "us_label": "US: {:.1f}%",
                "il_label": "Israel: {:.1f}%"
            },
            "he": {
                "percentile": "אחוזון",
                "annual_income": "הכנסה שנתית {} (USD)",
                "monthly_income": "הכנסה חודשית {} (USD)",
                "income_title": "הכנסה של ${:,.0f} בהתפלגויות ארה\"ב וישראל",
                "us_dist": "התפלגות הכנסה {} ארה\"ב",
                "il_dist": "התפלגות הכנסה {} ישראל (USD PPP)",
                "raw": "משק בית",
                "standardized": "מתוקננת לנפש",
                "us_label": "ארה\"ב: {:.1f}%",
                "il_label": "ישראל: {:.1f}%"
            }
        }[lang]
        
        # Calculate percentiles
        result = self.compare_income(income_usd, standardized)
        
        # Set matplotlib parameters for RTL support
        if self.is_rtl:
            plt.rcParams['axes.titlepad'] = 10
            plt.rcParams['font.family'] = 'DejaVu Sans'  # A font that supports Hebrew
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if standardized and self.has_standardized_data:
            # Plotting standardized percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Std_Income_USD'], 
                    label=texts["us_dist"].format(texts["standardized"]), 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Std_Income_USD'], 
                    label=texts["il_dist"].format(texts["standardized"]), 
                    linewidth=3)
            
            title_suffix = texts["standardized"]
        else:
            # Plotting raw percentiles
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['US_Income_USD'], 
                    label=texts["us_dist"].format(texts["raw"]), 
                    linewidth=3)
            
            ax.plot(self.percentile_data['Percentile'], 
                    self.percentile_data['Israel_Income_USD'], 
                    label=texts["il_dist"].format(texts["raw"]), 
                    linewidth=3)
            
            title_suffix = texts["raw"]
        
        # Adding points for the specified income
        us_perc = result['us_percentile']
        israel_perc = result['israel_percentile']
        income = result['income_usd']
        
        # Plot horizontal line at the income level
        ax.axhline(y=income, color='gray', linestyle='--', alpha=0.7)
        
        # Plot points on the distributions
        ax.plot(us_perc, income, 'o', color='blue', markersize=10)
        ax.plot(israel_perc, income, 'o', color='orange', markersize=10)
        
        # Add annotations with RTL support if needed
        us_label = texts["us_label"].format(us_perc)
        il_label = texts["il_label"].format(israel_perc)
        
        if self.is_rtl:
            us_label = bidi.get_display(us_label)
            il_label = bidi.get_display(il_label)
        
        ax.annotate(us_label, 
                  xy=(us_perc, income), 
                  xytext=(us_perc - 5, income * 1.1),
                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                  fontsize=10)
        
        ax.annotate(il_label, 
                  xy=(israel_perc, income), 
                  xytext=(israel_perc + 5, income * 1.1),
                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                  fontsize=10)
        
        # Create title and labels based on period and standardization
        period_str = "annual" if period == "annual" else "monthly"
        income_label = texts["annual_income"] if period_str == "annual" else texts["monthly_income"]
        
        # Handle RTL for labels and titles
        if self.is_rtl:
            ax.set_xlabel(bidi.get_display(texts["percentile"]))
            ax.set_ylabel(bidi.get_display(income_label.format(title_suffix)))
            ax.set_title(bidi.get_display(texts["income_title"].format(income)))
            
            # RTL labels for legend
            handles, labels = ax.get_legend_handles_labels()
            rtl_labels = [bidi.get_display(label) for label in labels]
            ax.legend(handles, rtl_labels)
            
            # Flip x-axis for RTL layout
            ax.invert_xaxis()
        else:
            ax.set_xlabel(texts["percentile"])
            ax.set_ylabel(income_label.format(title_suffix))
            ax.set_title(texts["income_title"].format(income))
            ax.legend()
        
        ax.grid(True)
        
        # Format y-axis as currency
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
        
        plt.tight_layout()
        return fig
    
    def create_percentile_table(self, selected_percentiles=[10, 25, 50, 75, 90, 95], period="annual", standardized=False, lang="en"):
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
        lang : str
            Language code for table headers
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with percentile comparisons
        """
        # Get translations for column headers
        texts = {
            "en": {
                "percentile": "Percentile",
                "us_income": "{} US Income (USD)",
                "il_income_ils": "{} Israel Income (ILS)",
                "il_income_usd": "{} Israel Income (USD PPP)",
                "ratio": "Ratio (US/Israel)",
                "standardized": "Standardized ",
                "raw": ""
            },
            "he": {
                "percentile": "אחוזון",
                "us_income": "הכנסה {} ארה\"ב (USD)",
                "il_income_ils": "הכנסה {} ישראל (ILS)",
                "il_income_usd": "הכנסה {} ישראל (USD PPP)",
                "ratio": "יחס (ארה\"ב/ישראל)",
                "standardized": "מתוקננת ",
                "raw": ""
            }
        }[lang]
        
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
            title_prefix = texts["standardized"]
        else:
            us_col = 'US_Income_USD'
            ils_col = 'Israel_Income_ILS'
            usd_ppp_col = 'Israel_Income_USD'
            title_prefix = texts["raw"]
        
        # Create the output table with annual or monthly values
        divider = 1 if period == "annual" else 12
        
        # Handle RTL for column headers - only for display
        if self.is_rtl:
            # Use python-bidi to handle RTL text
            column_names = {
                'Percentile': bidi.get_display(texts["percentile"]),
                f'{title_prefix}US Income (USD)': bidi.get_display(texts["us_income"].format(title_prefix)),
                f'{title_prefix}Israel Income (ILS)': bidi.get_display(texts["il_income_ils"].format(title_prefix)),
                f'{title_prefix}Israel Income (USD PPP)': bidi.get_display(texts["il_income_usd"].format(title_prefix)),
                'Ratio (US/Israel)': bidi.get_display(texts["ratio"])
            }
        else:
            column_names = {
                'Percentile': texts["percentile"],
                f'{title_prefix}US Income (USD)': texts["us_income"].format(title_prefix),
                f'{title_prefix}Israel Income (ILS)': texts["il_income_ils"].format(title_prefix),
                f'{title_prefix}Israel Income (USD PPP)': texts["il_income_usd"].format(title_prefix),
                'Ratio (US/Israel)': texts["ratio"]
            }
        
        # Create the table with original column names first (for data processing)
        table = pd.DataFrame({
            'Percentile': filtered_data['Percentile'],
            f'{title_prefix}US Income (USD)': filtered_data[us_col] / divider,
            f'{title_prefix}Israel Income (ILS)': filtered_data[ils_col] / divider,
            f'{title_prefix}Israel Income (USD PPP)': filtered_data[usd_ppp_col] / divider,
            'Ratio (US/Israel)': filtered_data[us_col] / filtered_data[usd_ppp_col]
        })
        
        # Rename the columns for display only
        table = table.rename(columns=column_names)
        
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
    
    # Language selection
    available_languages = {
        "English": "en",
        "עברית": "he"  # Hebrew
    }
    
    # Add a language selector to the sidebar
    lang_options = list(available_languages.keys())
    selected_lang_name = st.sidebar.selectbox("Language / שפה", lang_options, index=0)
    selected_lang = available_languages[selected_lang_name]
    
    # Set RTL mode based on language selection
    is_rtl = (selected_lang == "he")
    
    # Get translations for the selected language
    t = translations[selected_lang]
    
    # Apply custom CSS based on RTL setting
    st.markdown(get_custom_css(is_rtl), unsafe_allow_html=True)
    
    # Title and introduction with RTL support
    if is_rtl:
        st.markdown(f'<div class="main-header" dir="rtl">{t["page_title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-text" dir="rtl">{t["intro"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="main-header">{t["page_title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-text">{t["intro"]}</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    st.sidebar.header(t["config"])
    
    # PPP Rate
    ppp_rate = st.sidebar.number_input(
        t["ppp_rate"],
        min_value=1.0,
        max_value=10.0,
        value=3.7,
        step=0.1,
        help=t["ppp_help"]
    )
    
    # Read the data.csv file directly
    try:
        percentile_data = pd.read_csv("data.csv")
        st.sidebar.success(t["data_loaded"])
    except Exception as e:
        st.error(f"{t['data_error']}{e}")
        st.info(t["data_info"])
        st.stop()
    
    # Show data preview in sidebar
    with st.sidebar.expander(t["preview_data"]):
        st.dataframe(percentile_data.head())
    
    # Initialize our comparator
    try:
        comparator = IncomeDistributionComparator(percentile_data, ppp_rate, is_rtl)
    except Exception as e:
        st.error(f"{t['error_processing']}{e}")
        st.stop()
    
    # Check if standardized data is available
    has_standardized_data = comparator.has_standardized_data
    
    # Income Input Section with RTL support
    if is_rtl:
        st.markdown(f'<div class="sub-header" dir="rtl">{t["household_info"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sub-header">{t["household_info"]}</div>', unsafe_allow_html=True)
    
    # Household size
    household_size = st.number_input(
        t["household_size"],
        min_value=1,
        max_value=20,
        value=1,
        step=1,
        help=t["household_help"]
    )
    
    # Period selection (Annual/Monthly)
    income_period = st.radio(
        t["income_period"],
        (t["annual"], t["monthly"]),
        index=0,
        horizontal=True
    )
    
    # Currency selection
    currency_option = st.radio(
        t["currency"],
        ("USD", "ILS"),
        index=0,
        horizontal=True
    )
    
    # Income input
    if currency_option == "USD":
        if income_period == t["annual"]:
            income_usd = st.number_input(
                t["annual_usd"],
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
                t["monthly_usd"],
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
        if income_period == t["annual"]:
            income_ils = st.number_input(
                t["annual_ils"],
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
                t["monthly_ils"],
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
        t["standardize"], 
        value=False,
        help=t["standardize_help"]
    )
    
    # Alert user if standardized data is requested but not available
    if standardize and not has_standardized_data:
        st.warning(t["standardize_warning"])
    
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
    if is_rtl:
        st.markdown(f'<div class="sub-header" dir="rtl">{t["results"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sub-header">{t["results"]}</div>', unsafe_allow_html=True)
    
    # Calculate the income position using selected income and distribution
    result = comparator.compare_income(calculation_income_usd, standardize)
    
    # Create columns for results
    col1, col2, col3 = st.columns([2, 2, 3])
    
    # Set direction attribute for RTL support
    dir_attr = 'dir="rtl"' if is_rtl else ''
    
    with col1:
        st.markdown(f"""
        <div class="highlight" {dir_attr}>
        <h3>{t["raw_income"]}</h3>
        <p>{t["annual_usd_short"]} <b>${annual_income_usd:,.2f}</b></p>
        <p>{t["annual_ils_short"]} <b>₪{annual_income_ils:,.2f}</b></p>
        <p>{t["monthly_usd_short"]} <b>${monthly_income_usd:,.2f}</b></p>
        <p>{t["monthly_ils_short"]} <b>₪{monthly_income_ils:,.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="highlight" {dir_attr}>
        <h3>{t["std_income"]}</h3>
        <p>{t["annual_usd_short"]} <b>${std_annual_income_usd:,.2f}</b></p>
        <p>{t["annual_ils_short"]} <b>₪{std_annual_income_ils:,.2f}</b></p>
        <p>{t["monthly_usd_short"]} <b>${std_monthly_income_usd:,.2f}</b></p>
        <p>{t["monthly_ils_short"]} <b>₪{std_monthly_income_ils:,.2f}</b></p>
        <p><em>{t["divided_by"].format(household_size, math.sqrt(household_size))}</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        using_precalc_text = t["using_precalc"] if (standardize and has_standardized_data) else ""
        st.markdown(f"""
        <div class="highlight" {dir_attr}>
        <h3>{t["percentile_position"]}</h3>
        <p>{t["us_dist"]} <b>{result['us_percentile']:.1f}%</b></p>
        <p>{t["il_dist"]} <b>{result['israel_percentile']:.1f}%</b></p>
        <p>{t["difference"]} <b>{result['percentile_difference']:.1f} {t["points"]}</b></p>
        <p><em>{using_precalc_text}</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Interpretation
    if abs(result['percentile_difference']) < 3:
        interpretation = t["similar_position"]
    elif result['percentile_difference'] > 0:
        interpretation = t["higher_in_il"].format(result['percentile_difference'])
    else:
        interpretation = t["higher_in_us"].format(abs(result['percentile_difference']))
    
    std_text = t["standardized_a"] if standardize else t["an"]
    
    st.markdown(f"""
    <div class="highlight" {dir_attr}>
    <h3>{t["interpretation"]}</h3>
    <p>{interpretation}</p>
    <p>{t["this_means"].format(std_text, calculation_income_usd)}</p>
    <ul>
        <li>{t["us_percentile"].format(result['us_percentile'], result['us_percentile'])}</li>
        <li>{t["il_percentile"].format(result['israel_percentile'], result['israel_percentile'])}</li>
    </ul>
    {f"<p><em>{t['note_analysis'].format(t['precalculated'] if has_standardized_data else t['manually_calculated'])}</em></p>" if standardize else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizations
    if is_rtl:
        st.markdown(f'<div class="sub-header" dir="rtl">{t["visual_analysis"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sub-header">{t["visual_analysis"]}</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([t["your_position"], t["income_distributions"]])
    
    with tab1:
        st.pyplot(comparator.plot_income_comparison(
            calculation_income_usd, 
            period=income_period.lower(), 
            standardized=standardize,
            lang=selected_lang
        ))
        std_text = t["standardized_space"] if standardize else ""
        st.caption(t["chart_shows_where"].format(std_text))
    
    with tab2:
        st.pyplot(comparator.plot_income_distributions(standardize, selected_lang))
        std_text = t["standardized_space"].strip() + " " if standardize else ""
        st.caption(t["chart_shows_dist"].format(std_text))
    
    
    # Additional Context
    if is_rtl:
        st.markdown(f'<div class="sub-header" dir="rtl">{t["key_thresholds"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sub-header">{t["key_thresholds"]}</div>', unsafe_allow_html=True)
    
    # Create a table of key percentiles based on the selected period and standardization
    percentile_table = comparator.create_percentile_table(
        period=income_period.lower(),
        standardized=standardize,
        lang=selected_lang
    )
    
    # Format the table for display
    display_table = percentile_table.copy()
    # Find the column names dynamically since they might include 'Standardized' prefix or be translated
    for col in display_table.columns:
        if 'USD' in col:
            display_table[col] = display_table[col].apply(lambda x: f"${x:,.0f}")
        elif 'ILS' in col:
            display_table[col] = display_table[col].apply(lambda x: f"₪{x:,.0f}")
        elif 'Ratio' in col or 'יחס' in col:  # Handle both English and Hebrew column names
            display_table[col] = display_table[col].apply(lambda x: f"{x:.2f}")
    
    period_label = t["monthly"] if income_period == t["monthly"] else t["annual"]
    standardized_label = t["standardized_a"] if standardize else ""
    
    if is_rtl:
        st.write(f"**{t['income_at_key'].format(period_label, standardized_label)}**")
    else:
        st.write(f"**{t['income_at_key'].format(period_label, standardized_label)}**")
    
    st.table(display_table)
    
    # Methodology and Notes
    with st.expander(t["methodology"]):
        st.markdown(f"""
        ### {t["data_sources"]}
        
        {t["data_sources_text"]}
        
        ### {t["square_root"]}
        
        {t["square_root_text"]}
        
        ### {t["data_file"]}
        
        {t["data_file_text"]}
        
        ### {t["limitations"]}
        
        {t["limitations_text"]}
        
        ### {t["interpretation_header"]}
        
        {t["interpretation_text"]}
        """)
    
    # Footer
    st.markdown(f"""
    <div class="footer" {dir_attr}>
    {t["footer"]}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()