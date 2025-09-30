"""
Prompt templates for the job search workflow
"""

PROMPTS = {
    "system": (
        "# Role\n"
        "You are a specialized Google Search Query Optimizer for job searches.\n\n"
        
        "# Task\n"
        "Transform natural language job search requests into optimized Google boolean search queries.\n\n"
        
        "# Requirements\n"
        "- Generate ONLY the boolean search query\n"
        "- Target specific job postings, not job boards or career advice pages\n"
        "- Use appropriate boolean operators (AND, OR, quotes, parentheses)\n"
        "- Include relevant synonyms and variations\n"
        "- Exclude generic career sites and job aggregators\n\n"
        
        "# Output Format\n"
        "Return only the optimized search query without explanations or additional text."
    ),
    
    "user": (
        "Find Data Scientist OR Machine Learning Engineer positions in the healthcare/medical industry.\n\n"
        
        "Requirements:\n"
        "- Industries: Healthcare, Medical, Health Tech\n"
        "- Locations: New York City, Chicago, San Francisco, Philadelphia, or Remote\n\n"
        
    ),
    
    "ranking": (
        "# Original Job Search Criteria\n"
        "{user_message_content}\n\n"
        
        "# Job Postings Analysis\n"
        "Below are job postings with their summaries:\n\n"
        "{postings}\n\n"
        
        "# Task\n"
        "Analyze and rank these job postings based on how well they match the original criteria.\n\n"
        
        "# Selection Criteria (in order of importance)\n"
        "1. Relevance to job title and role requirements\n"
        "2. Industry alignment (healthcare/medical focus)\n"
        "3. Experience level match (2-5 years preferred)\n"
        "4. Geographic restriction (United States only)\n"
        "5. Location preference alignment (NYC, Chicago, SF, Philadelphia, Remote)\n"
        "6. Company reputation and role quality\n\n"
        
        "# Specific Requirements\n"
        "- MUST be located in or allow remote work within the United States\n"
        "- MUST still be accepting applications\n"
        "- Select exactly {rank} postings if there are enough to choose from\n"
        "- Do NOT select duplicate URLs or companies\n"
        "- Focus on roles that best match the specified criteria\n\n"
        
        "# Output Format\n"
        "Return a valid JSON array with the selected postings:\n"
        "[\n"
        "  {{\n"
        "    \"index\": <original_index_number>,\n"
        "    \"summary\": \"<brief_job_summary>\"\n"
        "  }}\n"
        "]\n\n"
        
        "Return ONLY the JSON array, no additional text or formatting."
    )
}