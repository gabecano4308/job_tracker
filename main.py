import os
import asyncio
import logging
from typing import TypedDict, List, Dict, Union
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langgraph.graph import END, StateGraph
from utils import fetch_page_content, parse_ranked_posts, extract_user_message_content

from gmail_sender import GmailService
from prompts import PROMPTS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_search.log')
    ]
)


class JobState(TypedDict):
    """
    State object for the job search workflow - tracks data flow between nodes
    """
    prompt: List[BaseMessage]  # Original user request and system instructions
    optimized_query: str  # Google search query optimized by LLM
    urls: List[str]  # Job posting URLs found by search
    ranked_posts: List[Dict[str, Union[str, int]]]  # Top 5 ranked job matches


class JobSearchWorkflow:
    """
    Main workflow class for automated job searching and ranking
    """
    
    def __init__(self, llm=None, prompts=None, config=None):
        """
        Initialize the JobSearchWorkflow
        
        Args:
            llm: Language model instance (defaults to GPT-4o-mini)
            prompts: Prompt templates dictionary
            config: Configuration dictionary for workflow settings
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.prompts = prompts or PROMPTS
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.graph = self._build_graph()

    
    def _build_graph(self):
        """
        Build the LangGraph workflow
        """
        graph_builder = StateGraph(JobState)
        
        # Add workflow nodes
        graph_builder.add_node("optimize_prompt", self.optimize_prompt)
        graph_builder.add_node("scan_web", self.scan_web)
        graph_builder.add_node("grab_top_rank", self.grab_top_rank)
        graph_builder.add_node("send_email", self.send_email)
        
        # Define the workflow sequence
        graph_builder.set_entry_point("optimize_prompt")
        graph_builder.add_edge("optimize_prompt", "scan_web")
        graph_builder.add_edge("scan_web", "grab_top_rank")
        graph_builder.add_edge("grab_top_rank", "send_email")
        graph_builder.add_edge("send_email", END)
        
        return graph_builder.compile()

    
    def optimize_prompt(self, state: JobState) -> JobState:
        """
        Step 1: Creates an optimal google boolean search according to a natural language request
        """
        self.logger.info("Starting prompt optimization...")
        
        prompt = state["prompt"]  # Get system + user messages
        response = self.llm.invoke(prompt)  # Ask LLM to optimize the search query
        
        self.logger.info(f"Generated optimized search query: {response.content}")
        return {"optimized_query": response.content}

    
    def scan_web(self, state: JobState) -> JobState:
        """
        Step 2: Scan the internet for job posting URLs using the optimized search query
        """
        max_pages = self.config.get('max_pages', 2)
        self.logger.info("Starting web search...")
        
        prompt = state["optimized_query"]
        page = 0
        start = 0
        all_urls = []
        search = SerpAPIWrapper()

        # Search multiple pages of results
        while page < max_pages:
            self.logger.info(f"   Searching page {page + 1} of {max_pages}...")

            # Pagination parameter + restrict results to past 72 hours
            search.params = {"start": start, "tbs": "qdr:d3"}  
            search_results = search.results(prompt)
            
            # Extract URLs
            all_urls.extend(
                [dic["link"] for dic in search_results.get("organic_results", [])]
            )
            start += 10  # Next page 
            page += 1

        self.logger.info(f"Web search completed. Found {len(all_urls)} URLs")
        return {"urls": all_urls}

    
    async def summarize_job_postings(self, urls: List[str]) -> List[Dict[str, Union[str, int]]]:
        """
        Helper method: Fetch and summarize job postings from URLs
        Each job gets a brief one-sentence summary for ranking
        """
        summaries, ix = [], 0

        for url in urls:
            self.logger.info(f"   Processing job posting {ix + 1}/{len(urls)}...")
            
            # Fetch the full job posting content
            text = await fetch_page_content(url)
            
            # Skip this URL if content couldn't be fetched
            if text is None:
                self.logger.warning(f"   Skipping job posting {ix + 1} - could not fetch content")
                ix += 1
                continue
            
            # Ask LLM to create a brief summary
            prompt = f"Summarize the following job posting in 1 brief sentence:\n\n{text}"
            summary = self.llm.invoke(prompt)
            summaries.append({"ix": ix, "summary": summary.content})
            ix += 1

        return summaries

    
    async def grab_top_rank(self, state: JobState) -> JobState:
        """
        Step 3: Analyze job postings and rank the top matches based on user criteria
        """
        rank = self.config.get('top_rank_count', 5)
        self.logger.info("Starting job analysis and ranking...")
        
        urls = state["urls"]
        prompt = state["prompt"]

        # Extract the original user request for ranking context
        user_message_content = extract_user_message_content(prompt)

        # Get summaries for all job postings
        summaries = await self.summarize_job_postings(urls)
        
        # Format summaries for LLM ranking prompt
        postings = "\n\n".join(
            [f"INDEX: {entry['ix']}. SUMMARY: {entry['summary']}" for entry in summaries]
        )

        # Use the ranking prompt template with dynamic values
        rank_prompt = self.prompts["ranking"].format(
            user_message_content=user_message_content,postings=postings, 
            rank=min(rank, len(summaries)))
        
        response = self.llm.invoke(rank_prompt)
        ranked_posts = parse_ranked_posts(response.content)

        # Add the original URLs back to the ranked results
        for x in ranked_posts:
            x["url"] = urls[x["index"]]

        self.logger.info(f"Job ranking completed. Selected top {len(ranked_posts)} matches")
        return {"ranked_posts": ranked_posts}

    
    def send_email(self, state: JobState) -> JobState:
        """
        Step 4: Send the top job matches via email
        """
        self.logger.info("Sending email with job results...")
        
        email = self.config.get("email", "example@example.com")

        # Format job results into readable email content
        message_text = "\n\n".join(
            [
                f"Job Summary: {x['summary']}\nJob URL: {x['url']}"
                for x in state["ranked_posts"]
            ]
        )

        # Send email
        gmail_service = GmailService(to=email, message_text=message_text)
        gmail_service.create_and_send_message()
        
        self.logger.info("Email sent successfully!")
        return {}

    
    async def run(self, user_message: str = None) -> dict:
        """
        Run the complete job search workflow
        
        Args:
            user_message: Custom user message (optional, uses default from prompts if not provided)
            
        Returns:
            Dictionary with workflow results including ranked_posts
        """
        self.logger.info("Starting job search workflow...")
        
        # Use provided user message or default from prompts
        user_msg_content = user_message or self.prompts["user"]
        
        # Create initial state
        system_message = SystemMessage(self.prompts["system"])
        user_msg = HumanMessage(user_msg_content)
        initial_state = {"prompt": [system_message, user_msg]}
        
        try:
            result = await self.graph.ainvoke(initial_state)
            self.logger.info("Job search workflow completed successfully!")
            return result
        except Exception as e:
            self.logger.error(f"Job search workflow failed: {str(e)}")
            raise


async def main():
    """
    Main function - creates and runs the job search workflow
    """    
    config = {
        'max_pages': int(os.environ.get("MAX_PAGES", "2")),
        'top_rank_count': int(os.environ.get("TOP_RANK_COUNT", "5")),
        'email': os.environ.get("JOB_SEARCH_EMAIL", "example@example.com"),
    }
    
    # Create and run the workflow
    workflow = JobSearchWorkflow(config=config)
    result = await workflow.run()
    
    return result


if __name__ == "__main__":
    asyncio.run(main())