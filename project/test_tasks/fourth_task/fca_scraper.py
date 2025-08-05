"""FCA Scraper"""

import asyncio
import aiohttp
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

FCA_API_KEY = os.getenv("FCA_API_KEY")
API_EMAIL = "vitaliy.dayneko2410@gmail.com"

URL = "https://register.fca.org.uk/services/V0.1/Firm/"
PARAMS = {"page": 1, "per_page": 1}
HEADERS = {
    "x-auth-email": API_EMAIL,
    "x-auth-key": FCA_API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

MAX_CONCURRENT_REQUESTS = 3
sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def safe_get(
    session: aiohttp.ClientSession, url: str, params=None
) -> dict | None:
    """Safely fetch data from the FCA API with error handling and rate limiting."""
    async with sem:
        try:
            async with session.get(
                url, headers=HEADERS, params=params, timeout=30
            ) as response:
                if response.status == 429:
                    print(f"429 Too Many Requests at {url}, retrying after delay...")
                    await asyncio.sleep(5)
                    return await safe_get(session, url, params)
                if response.status != 200:
                    print(f"Error {response.status} fetching {url}")
                    return None
                return await response.json()
        except Exception as e:
            print(f"Exception fetching {url}: {e}")
            return None


async def get_firm_data(session: aiohttp.ClientSession, frn: str) -> dict:
    """Fetch firm data from the FCA API using the FRN."""
    json_data = await safe_get(session, URL + str(frn), params=PARAMS)
    return json_data.get("Data") if json_data else None


async def get_address_data(session: aiohttp.ClientSession, address_url: str) -> dict:
    """Fetch address data from the FCA API."""
    json_data = await safe_get(session, address_url, params=PARAMS)
    return json_data.get("Data") if json_data else None


async def process_entity(
    session: aiohttp.ClientSession,
    entity: pd.Series,
    idx: int,
    total: int,
    name_key: str,
) -> dict:
    """Process a single entity to fetch its data from the FCA API."""
    frn = entity["FRN"]
    name = entity[name_key]

    print(f"Processing {idx}/{total} ({idx/total:.2%}): (FRN: {frn})")

    if not frn:
        print("Empty FRN, skipping...")
        return None

    firm_data = await get_firm_data(session, frn)
    if not firm_data:
        print(f"No firm data found for (FRN: {frn})")
        return None
    firm_data = firm_data[0]

    address_url = firm_data.get("Address", "")
    address_data = await get_address_data(session, address_url) if address_url else [{}]
    address_data = address_data[0] if address_data else {}

    address = ", ".join(
        filter(
            None,
            [
                address_data.get("Address Line 1", ""),
                address_data.get("Address Line 2", ""),
                address_data.get("Address Line 3", ""),
                address_data.get("Address Line 4", ""),
            ],
        )
    ).strip(", ")

    print(f"Fetched data for (FRN: {frn})")

    return {
        "Organisation Name": name,
        "FRN": frn,
        "Status": firm_data.get("Status", ""),
        "Status Effective Date": firm_data.get("Status Effective Date", ""),
        "Business Type": firm_data.get("Business Type", ""),
        "Companies House Number": firm_data.get("Companies House Number", ""),
        "Client Money Permission": firm_data.get("Client Money Permission", ""),
        "Address": address,
        "Town": address_data.get("Town", ""),
        "County": address_data.get("County", ""),
        "Country": address_data.get("Country", ""),
        "Website Address": address_data.get("Website Address", ""),
        "Phone Number": address_data.get("Phone Number", ""),
        "Postcode": address_data.get("Postcode", ""),
        "Address Type": address_data.get("Address Type", ""),
    }


async def fetch_fca_data(data_path: str, output_path: str, name_key: str):
    """Fetch data from the FCA API and save it to an Excel file."""
    df = pd.read_csv(data_path, encoding="utf-8")
    results = []
    batch_size = 100

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(df), batch_size):
            batch = df[i : i + batch_size]

            tasks = [
                process_entity(session, entity, i + 1, len(df), name_key)
                for i, entity in batch.iterrows()
            ]

            for future in asyncio.as_completed(tasks):
                result = await future
                if result:
                    results.append(result)
            print(
                f"Processed batch {i // batch_size + 1}/{(len(df) // batch_size) + 1}"
            )

    pd.DataFrame(results).to_excel(output_path, index=False)
    print("Data fetching completed.")


if __name__ == "__main__":
    input_bank_path = "data/Credit Institutions (CSV).csv"
    output_bank_path = "output/fca_bank_data.xlsx"
    asyncio.run(fetch_fca_data(input_bank_path, output_bank_path, "Firm"))

    input_asset_manager_path = "data/Investment Firms Register.csv"
    output_asset_manager_path = "output/fca_asset_manager_data.xlsx"
    asyncio.run(
        fetch_fca_data(
            input_asset_manager_path, output_asset_manager_path, "Organisation Name"
        )
    )
