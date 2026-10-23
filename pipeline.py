import time
import asyncio
import aiohttp
import pandas as pd
from scraper import extract_website_content
from enricher import generate_outreach_pitch

INPUT_FILE = "leads.csv"
OUTPUT_FILE = "enriched_leads.csv"

async def process_lead(idx, row, total_leads, session):
    company = row.get("company_name", "Unknown Company")
    website = row.get("website", "")
    contact = row.get("contact_name", "Founder")

    print(f"[{idx + 1}/{total_leads}] Processing: {company} ({website})")

    # 1. Scrape content
    site_content = await extract_website_content(website, session)

    # 2. Generate customized pitch with LLM
    enrichment = await generate_outreach_pitch(company, site_content)

    print(f"    ✔ Hook generated for {company} ({contact}): \"{enrichment.personalized_hook[:70]}...\"\n")
    return enrichment

async def run_pipeline():
    print("=" * 60)
    print("🚀 STARTING B2B LEAD ENRICHMENT & OUTREACH PIPELINE")
    print("=" * 60)

    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"[!] Error: {INPUT_FILE} not found. Make sure it exists.")
        return

    print(f"[+] Loaded {len(df)} leads from {INPUT_FILE}\n")

    start_time = time.time()
    
    semaphore = asyncio.Semaphore(10) # limit to 10 concurrent requests
    
    async def bounded_process_lead(idx, row, total_leads, session):
        async with semaphore:
            return await process_lead(idx, row, total_leads, session)

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_process_lead(idx, row, len(df), session) for idx, row in df.iterrows()]
        results = await asyncio.gather(*tasks)

    # Collect outputs
    df["company_one_liner"] = [res.company_one_liner for res in results]
    df["target_audience"] = [res.target_audience for res in results]
    df["personalized_outreach_hook"] = [res.personalized_hook for res in results]

    # Save final enriched dataset
    df.to_csv(OUTPUT_FILE, index=False)

    elapsed = round(time.time() - start_time, 2)
    print("=" * 60)
    print(f"✅ PIPELINE COMPLETE in {elapsed}s")
    print(f"📁 Enriched file saved: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_pipeline())