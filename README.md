# Business Crawler

This project is a modular and extensible pipeline that automates web research at scale. It performs live searches, scrapes readable content, summarizes insights, and exports structured data for analysis or downstream applications.

## Features

*   **Live Search**: Uses DuckDuckGo to fetch the latest search results.
*   **Robust Scraping**: Leverages `trafilatura` and falls back to `BeautifulSoup` for content extraction.
*   **Data Export**: Saves results in per-topic `.csv` and `.json` files.
*   **Error Logging**: Logs failed URLs for each search query.
*   **Domain Analytics**: Tracks success and failure rates for each domain.
*   **Unified Dataset**: Merges all results into a single `.csv` and `.json` file.

## Folder Structure

```
business-crawler/
├── main.py                 # CLI interface for scraping
├── requirements.txt        # Project dependencies
├── business_crawler.ipynb  # (optional) Visualization dashboard
├── blacklist.txt           # Domains to skip during scraping
├── config.py               # Configuration settings
├── pyproject.toml          # Project configuration for tools like Black and Ruff
├── setup.py                # Package setup file for pip installation
├── streamlit_app.py        # Streamlit web application for data visualization
├── output/                   # Generated CSV/JSON logs
│   ├── <query_name>.csv      # Scraped data for each specific query (e.g., AI_in_healthcare.csv)
│   ├── _all_queries_merged.csv # Merged dataset of all scraped content
│   ├── _all_queries_merged.json # Merged dataset of all scraped content (JSON format)
│   ├── _domain_stats_summary.csv # Summary of domain success and failure rates
│   └── <query_name>_failed.txt # Log of failed URLs for each query (e.g., AI_in_healthcare_failed.txt)
└── README.md
└── tests/                  # Unit and integration tests
```

## Installation

You can install the `business-crawler` package directly from this repository using `pip`:

```bash
pip install .
```

Alternatively, you can clone the repository and install in editable mode for development:

```bash
git clone https://github.com/gbadrain/business-crawler.git
cd business-crawler
pip install -e .
```

## Usage

Once installed, you can run the crawler from your command line using the `business-crawler` command with one or more search queries:

```bash
business-crawler "AI in healthcare" "Natural Language Processing"
```

You can also specify a blacklist file to skip certain domains:

```bash
business-crawler "AI in healthcare" --blacklist my_blacklist.txt
```

This will:

1.  Scrape the top 10 URLs for each topic.
2.  Skip domains listed in the blacklist file.
3.  Save the results to the `output/` directory.
4.  Merge all results into combined `.csv` and `.json` files.
5.  Generate a domain performance summary.

### Output Columns

| Column     | Description                                     |
| :--------- | :---------------------------------------------- |
| `topic`      | Original search query                           |
| `title`      | Article title from the search result            |
| `url`        | Source URL                                      |
| `domain`     | Extracted domain from URL                       |
| `snippet`    | First 300 characters of scraped content         |
| `content`    | Full scraped main content                       |
| `scraped_at` | UTC timestamp when content was fetched          |
| `entities`   | Extracted entities (e.g., persons, organizations) |
| `keywords`   | Extracted keywords (placeholder for future use) |

## Testing

To run the tests, ensure you have `pytest` installed (it's included in `requirements.txt`). Then, navigate to the project root and run:

```bash
pytest
```



## Getting Started

This section guides you through setting up, running, and exploring the Business Crawler project.

### 1. Installation

First, clone the repository and install the necessary dependencies.

```bash
git clone https://github.com/gbadrain/business-crawler.git
cd business-crawler
pip install -e .
```

### 2. Running the Crawler

Execute the crawler from your command line with your desired search queries.

```bash
business-crawler "AI in healthcare" "Natural Language Processing"
```

You can also specify a custom blacklist file to skip certain domains:

```bash
business-crawler "AI in healthcare" --blacklist my_blacklist.txt
```

The crawler will:
*   Perform live searches using DuckDuckGo.
*   Scrape content from the top URLs.
*   Extract entities from the scraped content.
*   Save results in the `output/` directory.

### 3. Exploring Results and Visualizations

After running the crawler, you can explore the generated data and visualizations:

*   **Raw Data**: Check the `output/` directory for `_all_queries_merged.csv` (and `.json`) for the combined dataset, and individual CSVs for each query.
*   **Domain Statistics**: Review `output/_domain_stats_summary.csv` for success/failure rates per domain.
*   **Interactive Dashboard (Streamlit)**: For a more interactive and user-friendly experience, run the Streamlit application:

    ```bash
    streamlit run streamlit_app.py
    ```

    This will open a web browser with the dashboard, allowing you to explore the data with key performance indicators (KPIs), interactive Plotly doughnut charts, and detailed data tables.

### 4. Running Tests

To ensure the project's functionality and code quality, run the automated tests:

```bash
pytest
```

This will execute all unit and integration tests, providing feedback on the project's stability.

## Future Enhancements

*   [x] Standalone Web-based Dashboard (Streamlit)

---

## Contact & Support

**Gurpreet Singh Badrain**
Market Research Analyst & Aspiring Data Analyst

*   **My portfolio**: [Data Guru](https://your-portfolio-link.com) (Replace with actual link)
*   **GitHub**: [gbadrain](https://github.com/gbadrain)
*   **LinkedIn**: [gurpreet-badrain](https://www.linkedin.com/in/gurpreet-badrain)
*   **Email**: gbadrain@gmail.com
*   **Streamlit**: [gbadrain-Machine Learnning](https://share.streamlit.io/gbadrain/your-streamlit-app) (Replace with actual link)
