import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from collections import deque

async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_main_content_links(session, url, visited, depth, found):
    if found['status']:  # Check the flag before processing
        return "Skipped", []

    print(f"Processing {url} at depth {depth}")
    start_time = time.time()
    content = await fetch_page(session, url)

    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find("div", {"id": "bodyContent"})

    status = "Not found"
    if "Hitler" in main_content.text:
        status = "Found"

    links = []
    for link in main_content.find_all("a"):
        href = link.get("href", "")
        if href.startswith("/wiki/") and ":" not in href:
            full_url = "https://en.wikipedia.org" + href
            if full_url not in visited:
                links.append(full_url)
                visited.add(full_url)

    return status, links

async def producer(queue, visited, found):
    start_url = "https://en.wikipedia.org/wiki/Superconducting_magnet"
    visited.add(start_url)
    queue.append((start_url, 0))

    async with aiohttp.ClientSession() as session:
        while queue:
            url, depth = queue.popleft()
            if found['status']:  # Check the flag before processing
                break
            status, links = await fetch_main_content_links(session, url, visited, depth, found)
            if status == "Found":
                print(f"Found Hitler at depth {depth+1}")
                found['status'] = True  # Set the flag
                break
            for link in links:
                queue.append((link, depth + 1))

async def main_async():
    visited = set()
    queue = deque()
    found = {'status': False}
    await producer(queue, visited, found)
