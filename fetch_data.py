import yfinance as yf

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
        return str(value)

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
