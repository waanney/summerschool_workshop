import requests
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, description="Maximum number of results to return")

class SearchOutput(BaseModel):
    results: list = Field(..., description="Search results containing titles and links")


def search_web(input: SearchInput) -> SearchOutput:
    url = "https://duckduckgo.com/html/"
    params = {"q": input.query}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for result in soup.select(".result__title a")[:input.max_results]:
        title = result.get_text()
        link = result["href"]
        results.append({"title": title, "link": link})
    
    return results
