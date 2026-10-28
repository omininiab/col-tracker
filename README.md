# Cost of Living Tracker 🇨🇦

An automated, serverless architecture that tracks the Canadian cost of living over time using GitHub Actions, Statistics Canada, and the Bank of Canada APIs.

## Architecture
- **Crawler**: `scraper.py` polls APIs monthly.
- **Database**: `data/prices.json` stores time-series data locally.
- **Automation**: `.github/workflows/scraper.yml` runs the crawler monthly, commits changed data, and deploys the site.
- **Frontend**: `index.html` visualizes data using ECharts via GitHub Pages.

The shared Ominini navbar, typography, buttons, newsletter/footer styling, quote, and scroll-to-top behavior are served from `https://www.ominini.com/assets/`. The source of truth is the `omininiab.github.io` repository; the tracker intentionally retains only dashboard-specific styles in `css/style.css`. Deploy the homepage repository before this tracker so those shared asset URLs are available.

## GitHub Actions setup

The workflow runs on the first day of each month at 14:17 UTC, runs when tracker code or data changes on `main`, and can also be started from the Actions tab with **Run workflow**. It commits changed data with the built-in `GITHUB_TOKEN` and deploys the site to GitHub Pages; no personal access token or API secrets are required.

To enable deployment once, open **Settings → Pages** and set **Build and deployment → Source** to **GitHub Actions**. The workflow declares the required `contents`, `pages`, and `id-token` permissions. Repository or organization policy must allow these permissions and scheduled workflows. If `main` is protected, allow the Actions bot to push data commits; also ensure the `github-pages` environment does not require manual approval.

Scheduled runs use UTC and can be delayed by GitHub. GitHub may disable scheduled workflows in inactive public repositories, so the repository must remain active for fully unattended updates.
