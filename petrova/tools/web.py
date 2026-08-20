"""
Internet & GitHub Repository Inspector for PETROVA.
Enables fetching web pages, inspecting GitHub repositories, and searching without API keys.
"""

import re
import json
import urllib.parse
from typing import Optional, Dict, Any

import requests
from petrova.ui.console import console

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 PETROVA/0.1"


def clean_html(html_text: str) -> str:
    """Strip HTML tags, scripts, and extra whitespace to extract readable text."""
    # Remove script and style elements
    text = re.sub(r"<(script|style).*?>.*?</\1>", "", html_text, flags=re.DOTALL | re.IGNORECASE)
    # Convert headings and linebreaks
    text = re.sub(r"<(?:h[1-6]|p|div|li)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    # Remove all other tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode basic entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    # Collapse multiple blank lines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def fetch_github_repo(url: str) -> Optional[str]:
    """
    Fetch repository summary, README, stars, and description from a GitHub URL.
    Example: https://github.com/Priyanshukumar2904/PETROVA
    """
    match = re.search(r"github\.com/([^/]+)/([^/#?]+)", url)
    if not match:
        return None

    owner, repo = match.group(1), match.group(2)
    repo = repo.removesuffix(".git")

    console.print(f"[dim]🌐 Fetching GitHub repository: [cyan]{owner}/{repo}[/cyan]...[/dim]")

    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}
    summary_parts = [f"# GitHub Repository: {owner}/{repo}\n"]

    # 1. Fetch Repo Metadata from GitHub API
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        res = requests.get(api_url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            desc = data.get("description") or "No description provided."
            stars = data.get("stargazers_count", 0)
            forks = data.get("forks_count", 0)
            lang = data.get("language") or "Various"
            default_branch = data.get("default_branch", "main")
            summary_parts.append(f"• Description: {desc}")
            summary_parts.append(f"• Primary Language: {lang} | Stars: {stars} | Forks: {forks}\n")
        else:
            default_branch = "main"
    except Exception:
        default_branch = "main"

    # 2. Fetch README content
    for branch in [default_branch, "main", "master"]:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
        try:
            res = requests.get(readme_url, headers=headers, timeout=8)
            if res.status_code == 200 and res.text:
                summary_parts.append(f"## README.md (Excerpt):\n{res.text[:4000]}")
                break
        except Exception:
            continue

    return "\n".join(summary_parts)


def fetch_web_page(url: str, max_chars: int = 3500) -> Optional[str]:
    """Fetch and extract readable text from any HTTP/HTTPS URL."""
    # Check if it is a GitHub repo link
    if "github.com" in url:
        gh_data = fetch_github_repo(url)
        if gh_data:
            return gh_data

    console.print(f"[dim]🌐 Fetching web content from: [cyan]{url}[/cyan]...[/dim]")

    try:
        headers = {"User-Agent": USER_AGENT}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        cleaned = clean_html(res.text)
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + "\n\n...[content truncated]..."

        return f"# Web Content from {url}\n\n{cleaned}"

    except Exception as e:
        console.print(f"[yellow]Failed to fetch web content from {url}: {e}[/yellow]")
        return None


def search_duckduckgo(query: str, max_results: int = 4) -> str:
    """Perform a lightweight web search without API keys."""
    console.print(f"[dim]🔍 Searching web for: [cyan]{query}[/cyan]...[/dim]")

    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {"User-Agent": USER_AGENT}
        res = requests.get(url, headers=headers, timeout=8)

        if res.status_code != 200:
            return f"Search returned status {res.status_code}"

        # Extract snippets using regex
        results = []
        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', res.text, re.DOTALL)
        titles = re.findall(r'<a class="result__url[^>]*href="([^"]+)"[^>]*>(.*?)</a>', res.text, re.DOTALL)

        for i, snippet in enumerate(snippets[:max_results]):
            clean_snip = clean_html(snippet)
            if clean_snip:
                results.append(f"• Result {i+1}: {clean_snip}")

        if results:
            return "\n".join(results)
        return "No clear search snippets found."

    except Exception as e:
        return f"Search failed: {e}"
