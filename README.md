Notes:
- small scope to start
- every morning, kick off a script that sends me relevant jobs posted during the prior 24 hours
- have it send to my email address
- limit to top 5 matches per day
- start with preferences hardcoded into the prompt, later can make a UI settings page to set preferences
- check serpAPI metrics: https://serpapi.com/searches/reports
- check OpenAI metrics: 

For next time:
- add capability to check only for jobs posted in the last 3 days. Start with including it in prompt and see how it changes the optimized query...
- see if it's better to use langchain requests wrapper instead of playwright, which specialized with dynamic interaction (you are only working with static webpages pretty sure)
- implement some monitoring to see how it's working at each step, identify improvement areas
