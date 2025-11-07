"""
Enhanced financial data fetching from multiple open-source APIs
"""
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
# from rag_chatbot.src.config import Config
import time


class FinancialDataFetcher:
    """Fetch real-time and historical financial data from free APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # API endpoints
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.fmp_base = "https://financialmodelingprep.com/api/v3"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
    
    def get_stock_quote(self, ticker: str) -> Dict:
        """
        Get current stock price and metrics using yfinance (FREE, no key needed)
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL', 'MSFT')
        
        Returns:
            Dictionary with current stock information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get current trading data
            current_data = stock.history(period='1d', interval='1m')
            current_price = current_data['Close'].iloc[-1] if not current_data.empty else info.get('currentPrice')
            
            return {
                "ticker": ticker.upper(),
                "current_price": current_price,
                "previous_close": info.get('previousClose'),
                "open": info.get('open'),
                "day_high": info.get('dayHigh'),
                "day_low": info.get('dayLow'),
                "volume": info.get('volume'),
                "avg_volume": info.get('averageVolume'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "forward_pe": info.get('forwardPE'),
                "dividend_yield": info.get('dividendYield'),
                "beta": info.get('beta'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "50_day_avg": info.get('fiftyDayAverage'),
                "200_day_avg": info.get('twoHundredDayAverage'),
                "timestamp": datetime.now().isoformat(),
                "source": "Yahoo Finance"
            }
        except Exception as e:
            return {"error": f"Failed to fetch data for {ticker}: {str(e)}"}
    
    def get_historical_data(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical stock data (FREE)
        
        Args:
            ticker: Stock symbol
            period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
        Returns:
            DataFrame with historical data
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            hist['ticker'] = ticker.upper()
            return hist
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def get_company_info(self, ticker: str) -> Dict:
        """
        Get detailed company information (FREE)
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Dictionary with company details
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker.upper(),
                "company_name": info.get('longName'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "description": info.get('longBusinessSummary'),
                "website": info.get('website'),
                "employees": info.get('fullTimeEmployees'),
                "headquarters": f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(', '),
                "founded": info.get('founded'),
                "exchange": info.get('exchange'),
                "currency": info.get('currency'),
                "source": "Yahoo Finance"
            }
        except Exception as e:
            return {"error": f"Failed to fetch company info: {str(e)}"}
    
    def get_financial_statements(self, ticker: str) -> Dict:
        """
        Get income statement, balance sheet, and cash flow (FREE)
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Dictionary with financial statements as DataFrames
        """
        try:
            stock = yf.Ticker(ticker)
            
            return {
                "income_statement": stock.financials,
                "balance_sheet": stock.balance_sheet,
                "cash_flow": stock.cashflow,
                "quarterly_financials": stock.quarterly_financials,
                "quarterly_balance_sheet": stock.quarterly_balance_sheet,
                "quarterly_cashflow": stock.quarterly_cashflow,
                "source": "Yahoo Finance"
            }
        except Exception as e:
            return {"error": f"Failed to fetch financial statements: {str(e)}"}
    
    # ==================== FINNHUB (Free tier: 60 calls/min) ====================
    
    def get_finnhub_quote(self, ticker: str) -> Dict:
        """
        Get real-time quote from Finnhub
        Requires free API key from: https://finnhub.io/register
        """
        if not Config.FINNHUB_API_KEY:
            return {"error": "Finnhub API key not configured"}
        
        try:
            url = f"{self.finnhub_base}/quote"
            params = {
                'symbol': ticker.upper(),
                'token': Config.FINNHUB_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "ticker": ticker.upper(),
                "current_price": data.get('c'),  # Current price
                "change": data.get('d'),  # Change
                "percent_change": data.get('dp'),  # Percent change
                "high": data.get('h'),  # High price of day
                "low": data.get('l'),  # Low price of day
                "open": data.get('o'),  # Open price
                "previous_close": data.get('pc'),  # Previous close
                "timestamp": datetime.fromtimestamp(data.get('t', 0)).isoformat(),
                "source": "Finnhub"
            }
        except Exception as e:
            return {"error": f"Finnhub API error: {str(e)}"}
    
    def get_company_news(self, ticker: str, days_back: int = 7) -> List[Dict]:
        """
        Get recent company news from Finnhub (FREE)
        """
        if not Config.FINNHUB_API_KEY:
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.finnhub_base}/company-news"
            params = {
                'symbol': ticker.upper(),
                'from': from_date,
                'to': to_date,
                'token': Config.FINNHUB_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            news = response.json()
            
            # Format news items
            formatted_news = []
            for item in news[:10]:  # Limit to 10 most recent
                formatted_news.append({
                    "headline": item.get('headline'),
                    "summary": item.get('summary'),
                    "source": item.get('source'),
                    "url": item.get('url'),
                    "datetime": datetime.fromtimestamp(item.get('datetime', 0)).isoformat()
                })
            
            return formatted_news
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    # ==================== FINANCIAL MODELING PREP (Free: 250 calls/day) ====================
    
    def get_fmp_quote(self, ticker: str) -> Dict:
        """
        Get quote from Financial Modeling Prep
        Free API key from: https://financialmodelingprep.com/developer/docs/
        """
        if not Config.FMP_API_KEY:
            return {"error": "FMP API key not configured"}
        
        try:
            url = f"{self.fmp_base}/quote/{ticker.upper()}"
            params = {'apikey': Config.FMP_API_KEY}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return {"error": "No data returned"}
            
            quote = data[0]
            return {
                "ticker": ticker.upper(),
                "current_price": quote.get('price'),
                "change": quote.get('change'),
                "percent_change": quote.get('changesPercentage'),
                "day_high": quote.get('dayHigh'),
                "day_low": quote.get('dayLow'),
                "open": quote.get('open'),
                "previous_close": quote.get('previousClose'),
                "volume": quote.get('volume'),
                "avg_volume": quote.get('avgVolume'),
                "market_cap": quote.get('marketCap'),
                "pe": quote.get('pe'),
                "eps": quote.get('eps'),
                "timestamp": datetime.now().isoformat(),
                "source": "Financial Modeling Prep"
            }
        except Exception as e:
            return {"error": f"FMP API error: {str(e)}"}
    
    # ==================== COINGECKO (Crypto - FREE, no key) ====================
    
    def get_crypto_price(self, crypto_id: str = "bitcoin") -> Dict:
        """
        Get cryptocurrency data from CoinGecko (FREE, no API key)
        
        Args:
            crypto_id: Coin ID (bitcoin, ethereum, cardano, etc.)
        
        Returns:
            Dictionary with crypto data
        """
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if crypto_id not in data:
                return {"error": f"Crypto {crypto_id} not found"}
            
            coin_data = data[crypto_id]
            
            return {
                "crypto_id": crypto_id,
                "current_price": coin_data.get('usd'),
                "market_cap": coin_data.get('usd_market_cap'),
                "24h_volume": coin_data.get('usd_24h_vol'),
                "24h_change": coin_data.get('usd_24h_change'),
                "last_updated": datetime.fromtimestamp(coin_data.get('last_updated_at', 0)).isoformat(),
                "source": "CoinGecko"
            }
        except Exception as e:
            return {"error": f"CoinGecko API error: {str(e)}"}
    
    # ==================== AGGREGATED DATA METHODS ====================
    
    def get_comprehensive_quote(self, ticker: str) -> Dict:
        """
        Get quote from multiple sources and merge (fallback strategy)
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Best available quote data
        """
        # Try Yahoo Finance first (most reliable, no key needed)
        yf_quote = self.get_stock_quote(ticker)
        if "error" not in yf_quote:
            return yf_quote
        
        # Fallback to Finnhub
        if Config.FINNHUB_API_KEY:
            finnhub_quote = self.get_finnhub_quote(ticker)
            if "error" not in finnhub_quote:
                return finnhub_quote
        
        # Fallback to FMP
        if Config.FMP_API_KEY:
            fmp_quote = self.get_fmp_quote(ticker)
            if "error" not in fmp_quote:
                return fmp_quote
        
        return {"error": f"Unable to fetch quote for {ticker} from any source"}
    
    def format_for_context(self, ticker: str, include_news: bool = False) -> str:
        """
        Format financial data as text for RAG context
        
        Args:
            ticker: Stock symbol
            include_news: Whether to include recent news
        
        Returns:
            Formatted string for LLM context
        """
        quote = self.get_comprehensive_quote(ticker)
        company = self.get_company_info(ticker)
        
        if "error" in quote:
            return f"Unable to retrieve real-time data for {ticker}: {quote['error']}"
        
        # Format main quote
        context_parts = [
            f"=== REAL-TIME DATA FOR {ticker} ===",
            f"Retrieved: {quote.get('timestamp', 'N/A')}",
            f"Source: {quote.get('source', 'Multiple sources')}",
            "",
            f"Company: {company.get('company_name', 'N/A')}",
            f"Sector: {company.get('sector', 'N/A')} | Industry: {company.get('industry', 'N/A')}",
            "",
            "CURRENT TRADING DATA:",
            f"  Price: ${quote.get('current_price', 'N/A'):.2f}" if quote.get('current_price') else "  Price: N/A",
            f"  Change: {quote.get('change', 'N/A')} ({quote.get('percent_change', 'N/A')}%)" if quote.get('change') else "",
            f"  Day Range: ${quote.get('day_low', 'N/A'):.2f} - ${quote.get('day_high', 'N/A'):.2f}" if quote.get('day_low') else "",
            f"  Volume: {quote.get('volume', 'N/A'):,}" if quote.get('volume') else "",
            "",
            "KEY METRICS:",
            f"  Market Cap: ${quote.get('market_cap', 0):,.0f}" if quote.get('market_cap') else "",
            f"  P/E Ratio: {quote.get('pe_ratio', 'N/A'):.2f}" if quote.get('pe_ratio') else "",
            f"  52-Week Range: ${quote.get('52_week_low', 'N/A')} - ${quote.get('52_week_high', 'N/A')}" if quote.get('52_week_low') else "",
        ]
        
        # Add company description
        if company.get('description'):
            context_parts.extend([
                "",
                "COMPANY OVERVIEW:",
                company['description'][:400] + "..." if len(company['description']) > 400 else company['description']
            ])
        
        # Add recent news if requested
        if include_news and Config.FINNHUB_API_KEY:
            news = self.get_company_news(ticker, days_back=7)
            if news:
                context_parts.extend([
                    "",
                    "RECENT NEWS:",
                ])
                for i, item in enumerate(news[:5], 1):
                    context_parts.append(f"  {i}. {item['headline']} ({item['source']})")
        
        return "\n".join(context_parts)
    
    def get_market_overview(self) -> Dict:
        """
        Get overview of major market indices (FREE)
        """
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT"
        }
        
        overview = {}
        for name, symbol in indices.items():
            try:
                quote = self.get_stock_quote(symbol)
                if "error" not in quote:
                    overview[name] = {
                        "price": quote.get('current_price'),
                        "change": quote.get('change'),
                        "change_percent": quote.get('percent_change')
                    }
            except:
                continue
        
        return overview


# Example usage and testing
if __name__ == "__main__":
    fetcher = FinancialDataFetcher()
    
    print("=" * 60)
    print("Testing Yahoo Finance (No API key needed)")
    print("=" * 60)
    print(fetcher.format_for_context("AAPL"))
    
    print("\n" + "=" * 60)
    print("Testing Market Overview")
    print("=" * 60)
    overview = fetcher.get_market_overview()
    for index, data in overview.items():
    #     print(f"{index}: ${data['price']:.2f} ({data.get('change_percent', 0):.2f}%)")
        price= data.get("price") or 0
        change= data.get("change_percent") or 0
        
        print ({"price": price, "change":change})
        # print(f"{index}: ${ (data.get('price') or 0):.2f } ({ (data.get('change_percent') or 0):.2f}%)")

    
    print("\n" + "=" * 60)
    print("Testing Crypto (CoinGecko - No API key)")
    print("=" * 60)
    crypto = fetcher.get_crypto_price("bitcoin")
    if "error" not in crypto:
        print(f"Bitcoin: ${crypto['current_price']:,.2f}")
        print(f"24h Change: {crypto['24h_change']:.2f}%")