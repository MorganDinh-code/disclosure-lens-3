"""The lists the Database uses. Edit these two lists to add a sector or a document type."""

# The 11 GICS sectors (the standard used by S&P / MSCI). NVIDIA, for example, is "Information Technology".
SECTORS = [
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Health Care",
    "Industrials",
    "Information Technology",
    "Materials",
    "Real Estate",
    "Utilities",
]

# What kind of document it is. Disclosure Lens works best on short narrative documents.
FILING_TYPES = [
    "Earnings press release",
    "10-K (annual report)",
    "10-Q (quarterly report)",
    "8-K (current report)",
    "Earnings call transcript",
    "Shareholder letter",
    "Other",
]
