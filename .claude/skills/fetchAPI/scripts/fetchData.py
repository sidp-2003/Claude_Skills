"""
Fetch CSV data from remote APIs using async httpx and save to dated folder.
Logs each API call result to a timestamped log file.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import httpx

API_URLS = [
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_customer.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_store.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_date.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_product.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_sales.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_returns.csv",
]

BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"


def buildDataDir(currentDate: str) -> Path:
    dataFolder = DATA_DIR / currentDate
    dataFolder.mkdir(parents=True, exist_ok=True)
    return dataFolder


def buildLogDir(currentTimestamp: str) -> Path:
    logFolder = LOGS_DIR / currentTimestamp
    logFolder.mkdir(parents=True, exist_ok=True)
    return logFolder


def extractFileName(url: str) -> str:
    return url.split("/")[-1]


async def fetchSingleUrl(client: httpx.AsyncClient, url: str) -> dict:
    fileName = extractFileName(url)
    try:
        response = await client.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        return {
            "url": url,
            "fileName": fileName,
            "status": "success",
            "httpStatus": response.status_code,
            "contentLength": len(response.content),
            "content": response.text,
            "error": None,
        }
    except httpx.HTTPStatusError as e:
        return {
            "url": url,
            "fileName": fileName,
            "status": "failure",
            "httpStatus": e.response.status_code,
            "contentLength": 0,
            "content": None,
            "error": str(e),
        }
    except Exception as e:
        return {
            "url": url,
            "fileName": fileName,
            "status": "failure",
            "httpStatus": None,
            "contentLength": 0,
            "content": None,
            "error": str(e),
        }


async def fetchAllUrls(urls: list) -> list:
    async with httpx.AsyncClient() as client:
        tasks = [fetchSingleUrl(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results


def saveCsvFiles(results: list, dataFolder: Path) -> None:
    for result in results:
        if result["status"] == "success" and result["content"]:
            outputPath = dataFolder / result["fileName"]
            outputPath.write_text(result["content"], encoding="utf-8")
            print(f"  Saved: {result['fileName']} ({result['contentLength']} bytes)")


def writeLogFile(results: list, logFolder: Path, startTime: datetime, endTime: datetime) -> None:
    logPath = logFolder / "fetchAPI.log"
    logLines = []
    logLines.append(f"fetchAPI Log")
    logLines.append(f"Start Time : {startTime.isoformat()}")
    logLines.append(f"End Time   : {endTime.isoformat()}")
    logLines.append(f"Duration   : {(endTime - startTime).total_seconds():.2f}s")
    logLines.append("")
    logLines.append(f"Total URLs : {len(results)}")
    successCount = sum(1 for r in results if r["status"] == "success")
    failureCount = len(results) - successCount
    logLines.append(f"Successes  : {successCount}")
    logLines.append(f"Failures   : {failureCount}")
    logLines.append("")
    logLines.append("--- Detail ---")
    for result in results:
        logLines.append(f"URL        : {result['url']}")
        logLines.append(f"File       : {result['fileName']}")
        logLines.append(f"Status     : {result['status'].upper()}")
        if result["httpStatus"]:
            logLines.append(f"HTTP Code  : {result['httpStatus']}")
        if result["contentLength"]:
            logLines.append(f"Bytes      : {result['contentLength']}")
        if result["error"]:
            logLines.append(f"Error      : {result['error']}")
        logLines.append("")

    logPath.write_text("\n".join(logLines), encoding="utf-8")
    print(f"  Log written: {logPath}")


def main() -> None:
    currentDate = datetime.now().strftime("%Y-%m-%d")
    currentTimestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    dataFolder = buildDataDir(currentDate)
    logFolder = buildLogDir(currentTimestamp)

    print(f"Fetching {len(API_URLS)} URLs...")
    startTime = datetime.now()
    results = asyncio.run(fetchAllUrls(API_URLS))
    endTime = datetime.now()

    print(f"Saving CSVs to: {dataFolder}")
    saveCsvFiles(results, dataFolder)

    print(f"Writing log to: {logFolder}")
    writeLogFile(results, logFolder, startTime, endTime)

    successCount = sum(1 for r in results if r["status"] == "success")
    print(f"\nDone. {successCount}/{len(results)} files fetched successfully.")


if __name__ == "__main__":
    main()
