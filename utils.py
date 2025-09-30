from playwright.async_api import async_playwright
import json
import logging
from typing import List, Dict, Union, Optional
from langchain_core.messages import BaseMessage, HumanMessage

logger = logging.getLogger(__name__)

async def fetch_page_content(url: str) -> Optional[str]:
    """
    Fetch the content of a web page using Playwright
    Returns None if the page fails to load (timeout, error, etc.)
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            content = await page.inner_text("body")
            await browser.close()
        return content
    except Exception as e:
        logger.warning(f"Failed to fetch content from {url}: {str(e)}")
        return None

def parse_ranked_posts(response_content: str) -> List[Dict[str, Union[str, int]]]:
    """
    Parse the LLM response content to extract the ranked posts as a list of dicts.
    Handles code block formatting and JSON parsing.
    """
    ranked_posts = response_content.strip()

    # Remove markdown code block formatting if present
    if ranked_posts.startswith("```json"):
        ranked_posts = ranked_posts[len("```json") :].strip()

    if ranked_posts.endswith("```"):
        ranked_posts = ranked_posts[:-3].strip()

    return json.loads(ranked_posts)

def extract_user_message_content(prompt: List[BaseMessage]) -> str:
    """
    Extract the user message content from the prompt list
    """
    try:
        user_message_content = next(
            msg.content for msg in prompt if isinstance(msg, HumanMessage)
        )
    except StopIteration:
        user_message_content = "No user message found"
    
    return user_message_content