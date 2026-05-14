import asyncio
import os
from playwright.async_api import async_playwright

async def test_fetch():
    async with async_playwright() as p:
        # Use chrome channel as requested
        print("Launching Chrome...")
        browser = await p.chromium.launch(channel="chrome", headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test with CS.AI and a recent date
        subject = "cs.AI"
        date = "2026-05-13"
        url = f"https://arxiv.org/catchup?subject={subject}&date={date}&include_abs=True"
        
        print(f"Navigating to {url}")
        await page.goto(url)
        
        # Wait for content
        await page.wait_for_selector("dl")
        
        papers = await page.query_selector_all("dl > dt")
        print(f"Found {len(papers)} papers")
        
        results = []
        for dt in papers[:5]: # Just test the first 5
            pdf_link_el = await dt.query_selector('a[title="Download PDF"]')
            if not pdf_link_el:
                continue
            
            pdf_url = await pdf_link_el.get_attribute("href")
            if not pdf_url.startswith("http"):
                pdf_url = "https://arxiv.org" + pdf_url
            
            paper_id_el = await dt.query_selector('a[id^="pdf-"]')
            paper_id = await paper_id_el.inner_text() if paper_id_el else "Unknown"
            
            print(f"Paper: {paper_id} -> {pdf_url}")
            results.append({"id": paper_id, "url": pdf_url})
        
        # Test download of one paper
        if results:
            paper = results[0]
            print(f"Testing download for {paper['id']}")
            
            # Using context.request.get to download the file using the browser's context
            response = await context.request.get(paper['url'])
            if response.status == 200:
                filepath = os.path.join(os.getcwd(), f"test_{paper['id'].replace(':', '_')}.pdf")
                with open(filepath, "wb") as f:
                    f.write(await response.body())
                print(f"Downloaded to {filepath}")
                
                if os.path.exists(filepath):
                    print("Download successful!")
                    os.remove(filepath)
                else:
                    print("Download failed!")
            else:
                print(f"Download failed with status {response.status}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fetch())
