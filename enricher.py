import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Groq uses the exact same OpenAI client with a custom base_url
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY") or "DUMMY_KEY_FOR_TESTS",
    base_url="https://api.groq.com/openai/v1"
)

class EnrichedLeadData(BaseModel):
    company_one_liner: str
    target_audience: str
    personalized_hook: str

async def generate_outreach_pitch(company_name: str, site_text: str) -> EnrichedLeadData:
    """Takes scraped content and generates a targeted 2-sentence cold outreach hook."""
    if not site_text or "[SCRAPE_ERROR]" in site_text:
        return EnrichedLeadData(
            company_one_liner="Technology company",
            target_audience="B2B buyers",
            personalized_hook="Noticed your company's growth in the tech space and wanted to connect."
        )

    system_prompt = (
        "You are an elite B2B sales development representative (SDR) writing 1-to-1 cold outreach. "
        "Analyze the provided scraped website text and return a valid JSON object matching this schema:\n"
        "{\n"
        '  "company_one_liner": "What they do in 6 words or less",\n'
        '  "target_audience": "Who their primary customer is",\n'
        '  "personalized_hook": "A natural, conversational 2-sentence opening hook for a cold email. '
        'Sentence 1 must mention a specific product feature, claim, or tagline from their website. '
        'Sentence 2 must bridge into solving email deliverability, sales pipeline, or infrastructure growth. '
        'Never sound robotic. Never start with I hope this email finds you well."\n'
        "}\n"
        "Respond ONLY with valid raw JSON."
    )

    user_prompt = f"Company: {company_name}\nWebsite Content:\n{site_text}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_llm():
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        data = json.loads(response.choices[0].message.content)
        return EnrichedLeadData(**data)

    try:
        return await _call_llm()
    except Exception as e:
        print(f"[-] LLM Error for {company_name}: {e}")
        return EnrichedLeadData(
            company_one_liner="Tech platform",
            target_audience="Engineers & Founders",
            personalized_hook="Loved what your team is building and wanted to introduce an easier pipeline solution."
        )

async def main():
    from scraper import extract_website_content

    test_company = "Resend"
    test_url = "https://resend.com"

    print(f"Scraping & enriching test lead: {test_company}...")
    async with aiohttp.ClientSession() as session:
        scraped = await extract_website_content(test_url, session)
    result = await generate_outreach_pitch(test_company, scraped)

    print("\n--- LLM RESULT ---")
    print(f"One-Liner:     {result.company_one_liner}")
    print(f"Audience:      {result.target_audience}")
    print(f"Outreach Hook: {result.personalized_hook}")

if __name__ == "__main__":
    asyncio.run(main())
