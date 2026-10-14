# Cost of Living Tracker 🇨🇦

An automated, serverless architecture that tracks the Canadian cost of living over time using GitHub Actions, Statistics Canada, and the Bank of Canada APIs.

## Architecture
- **Crawler**: `scraper.py` polls APIs daily.
- **Database**: `data/prices.json` stores time-series data locally.
- **Automation**: `.github/workflows/scraper.yml` triggers the crawler daily.
- **Frontend**: `index.html` visualizes data using ECharts via GitHub Pages.
