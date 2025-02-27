from flask import Flask
from flask import send_file
from fpdf import FPDF
import os
import yfinance as yf  # Yahoo Finance API
import matplotlib
matplotlib.use('Agg')  # Fix Tkinter error
import matplotlib.pyplot as plt
import pandas as pd


app = Flask(__name__)

def fetch_company_info(ticker):
    """Fetches company details from Yahoo Finance API."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        company_data = {
            "Company Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Market Cap": format_large_number(info.get("marketCap", "N/A")),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "52-Week High": format_large_number(info.get("fiftyTwoWeekHigh", "N/A")),
            "52-Week Low": format_large_number(info.get("fiftyTwoWeekLow", "N/A"))
        }

        valuation_metrics = {
            "Price/Earnings (P/E)": info.get("trailingPE", "N/A"),
            "Price/Book (P/B)": info.get("priceToBook", "N/A"),
            "EV/EBITDA": format_large_number(info.get("enterpriseToEbitda", "N/A")),
            "Debt/Equity Ratio": info.get("debtToEquity", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
        }

        return company_data, valuation_metrics
    except Exception as e:
        return {"Error": f"Failed to fetch data: {str(e)}"}
    

def fetch_financials(ticker):
    stock = yf.Ticker(ticker)

    # Extract Income Statement
    income_stmt = stock.financials
    revenue = income_stmt.loc["Total Revenue"].iloc[0] if "Total Revenue" in income_stmt.index else "N/A"
    net_income = income_stmt.loc["Net Income"].iloc[0] if "Net Income" in income_stmt.index else "N/A"
    ebitda = income_stmt.loc["EBITDA"].iloc[0] if "EBITDA" in income_stmt.index else "N/A"

    # Extract Balance Sheet
    balance_sheet = stock.balance_sheet
    total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else "N/A"
    total_liabilities = balance_sheet.loc["Total Liabilities"].iloc[0] if "Total Liabilities" in balance_sheet.index else "N/A"
    shareholder_equity = balance_sheet.loc["Total Shareholder Equity"].iloc[0] if "Total Shareholder Equity" in balance_sheet.index else "N/A"

    # Extract Cash Flow Statement
    cash_flow = stock.cashflow
    operating_cash_flow = cash_flow.loc["Total Cash From Operating Activities"].iloc[0] if "Total Cash From Operating Activities" in cash_flow.index else "N/A"
    investing_cash_flow = cash_flow.loc["Total Cashflows From Investing Activities"].iloc[0] if "Total Cashflows From Investing Activities" in cash_flow.index else "N/A"
    financing_cash_flow = cash_flow.loc["Total Cash From Financing Activities"].iloc[0] if "Total Cash From Financing Activities" in cash_flow.index else "N/A"

    financial_data = {
        "Revenue": format_large_number(revenue),
        "Net Income": format_large_number(net_income),
        "EBITDA": format_large_number(ebitda),
        "Total Assets": format_large_number(total_assets),
        "Total Liabilities": format_large_number(total_liabilities),
        "Shareholder Equity": format_large_number(shareholder_equity),
        "Operating Cash Flow": format_large_number(operating_cash_flow),
        "Investing Cash Flow": format_large_number(investing_cash_flow),
        "Financing Cash Flow": format_large_number(financing_cash_flow)
    }

    return financial_data


def generate_stock_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")  # Get 1 year of data. For future, make this editable by the user

    # Calculate Moving Averages
    hist["50-day MA"] = hist["Close"].rolling(window=50).mean()
    hist["200-day MA"] = hist["Close"].rolling(window=200).mean()

    # Stock Price Chart (with Moving Averages)
    plt.figure(figsize=(8, 4))
    plt.plot(hist.index, hist["Close"], label="Closing Price", color="blue")
    plt.plot(hist.index, hist["50-day MA"], label="50-Day MA", linestyle="--", color="orange")
    plt.plot(hist.index, hist["200-day MA"], label="200-Day MA", linestyle="--", color="red")
    plt.title(f"Stock Price Chart: {ticker.upper()}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid()

    # Ensure directory exists
    os.makedirs("static/charts", exist_ok=True)

# Save images in static/charts/
    stock_chart_path = f"static/charts/{ticker}_stock_chart.png"
    volume_chart_path = f"static/charts/{ticker}_volume_chart.png"
    plt.savefig(stock_chart_path)
    plt.close() 

    # Trading Volume Chart
    plt.figure(figsize=(8, 4))
    plt.bar(hist.index, hist["Volume"], color="purple", alpha=0.6)
    plt.title(f"Trading Volume: {ticker.upper()}")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.grid()

    plt.savefig(volume_chart_path)
    plt.close() 

    return stock_chart_path, volume_chart_path  




@app.route('/generate_pdf', methods=['GET'])
def generate_pdf(ticker):
    if not ticker:
        return "Ticker is required", 400
    
    # Fetch company data
    stock = yf.Ticker(ticker)
    info = stock.info


    company_data, valuation_metrics = fetch_company_info(ticker)
    financial_data = fetch_financials(ticker)
    stock_chart_path, volume_chart_path = generate_stock_chart(ticker)
    
    class PDF(FPDF):
        def header(self):
            self.image('images.png', 18, 6, 30, 30)
            self.set_font('Arial', 'B', 20)
            self.cell(190, 20, f"Company Overview: {ticker.upper()}", ln=True, align="C", border=False)
            self.ln(10)
        
        def footer(self):
            self.set_y(-13)
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
    
    # Create PDF
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set font for content
    pdf.set_font("Arial", size=14)

    currency_keys = {"Market Cap", "52-Week High", "52-Week Low", "Revenue", "Net Income", "EBITDA", 
                 "Total Assets", "Total Liabilities", "Shareholder Equity", "Operating Cash Flow", 
                 "Investing Cash Flow", "Financing Cash Flow"}

    # Add company details to PDF
    for key, value in company_data.items():
        if key in currency_keys:
            pdf.cell(0, 10, f"{key}: ${value}", ln=True)  # Add $ for monetary values
        else:
            pdf.cell(0, 10, f"{key}: {value}", ln=True)   # Keep it normal for non-monetary values

    pdf.add_page()

    pdf.ln(5)
    # Financial Statements Summary
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Financial Statements Summary", ln=True)
    pdf.set_font("Arial", size=14)

    for key, value in financial_data.items():
        if key in currency_keys:
            pdf.cell(0, 10, f"{key}: ${value}", ln=True)  # Add $ for monetary values
        else:
            pdf.cell(0, 10, f"{key}: {value}", ln=True)   # Keep it normal for non-monetary values

    



    pdf.ln(5)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Valuation Metrics", ln=True, align="L")
    pdf.set_font("Arial", size=14)

    for key, value in valuation_metrics.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)


    # Add stock price chart
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Stock Price Chart", ln=True, align="C")
    pdf.image(stock_chart_path, x=20, y=None, w=170) 

    # Add trading volume chart
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Trading Volume Chart", ln=True, align="C")
    pdf.image(volume_chart_path, x=20, y=None, w=170)  


    
    filename = f"{ticker}_report.pdf"
    pdf.output(filename)

    return send_file(filename, as_attachment=True)

def format_large_number(value):
    """Converts large numbers to a human-readable format (K, M, B, T)."""
    if value == "N/A" or value is None:
        return "N/A"
    
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000_000:  # Trillions
            return f"{value / 1_000_000_000_000:.2f}T"
        elif abs(value) >= 1_000_000_000:  # Billions
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:  # Millions
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:  # Thousands
            return f"{value / 1_000:.2f}K"
        else:
            return str(round(value, 2))
    except ValueError:
        return str(value)  # If conversion fails, return original value


if __name__ == '__main__':
    app.run(debug=True)                                      