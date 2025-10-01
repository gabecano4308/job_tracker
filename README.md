# Job Helper

An automated job search assistant that finds, ranks, and emails relevant job postings based on your criteria.

## What it does

1. **Optimizes search queries** - LLM converts natural language job requests into effective Google boolean searches
2. **Searches the web** - Finds recent job postings from multiple pages of search results
3. **Ranks matches** - Uses AI to analyze and rank job postings based on your specific criteria
4. **Sends results** - Emails you the top job matches with summaries and links

## Quick Start

1. Set up your environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export SERPAPI_API_KEY="your-serpapi-key"
   export JOB_SEARCH_EMAIL="your-email@example.com"
   ```

2. Run the job search:
   ```bash
   python main.py
   ```

## Configuration

- `MAX_PAGES`: Number of search result pages to scan (default: 2)
- `TOP_RANK_COUNT`: Number of top jobs to return (default: 5)
- `JOB_SEARCH_EMAIL`: Email address to send results to

## Dependencies

- OpenAI API (for job analysis and ranking)
- SerpAPI (for web search)
- Gmail API (for sending results)
- Playwright (for web scraping)
