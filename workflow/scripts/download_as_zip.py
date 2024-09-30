"""This script is temporary until the nbiatoolkit is refactored"""

from nbiatoolkit import utils
from nbiatoolkit import NBIAClient
from nbiatoolkit.dicomsort.helper_functions import sanitizeFileName, _truncateUID
from nbiatoolkit.logger import setup_logger

import requests
import time

PARAMS = snakemake.params  # type: ignore
OUTPUT = snakemake.output[0]   # type: ignore
LOG = snakemake.log[0]   # type: ignore
WILDCARDS = snakemake.wildcards  # type: ignore
logger = setup_logger(
    name="download_series_as_zip",
    log_file=LOG,
    log_level="DEBUG",
)


query_url = (
    utils.NBIA_BASE_URLS.NBIA.value + utils.NBIA_ENDPOINTS.DOWNLOAD_SERIES.value
)

client = NBIAClient(
    PARAMS.NBIA_USERNAME,
    PARAMS.NBIA_PASSWORD,
)

logger.info(f"Downloading series {WILDCARDS.SeriesInstanceUID} as zip file")
logger.info(f"Query URL: {query_url}")
logger.info(f"Output file: {OUTPUT}")

for attempt in range(PARAMS.max_retries):
  logger.debug(f"Attempt {attempt+1}/{PARAMS.max_retries}")
  response = requests.get(
      query_url,
      headers=client.headers,
      params={"SeriesInstanceUID": WILDCARDS.SeriesInstanceUID},
  )
  logger.debug(f"Response status code: {response.status_code}")
  logger.debug(f"Response headers: {response.headers}")
  try:
      response.raise_for_status()
      with open(OUTPUT, "wb") as f:
          f.write(response.content)
      break  # Exit loop if the request is successful
  except requests.exceptions.HTTPError as httperror:
      logger.error(f"ERROR: Exception Error - {httperror}")
  except requests.exceptions.ConnectionError as connerror:
      logger.error(f"ERROR: Connection Error - {connerror}. Sleeping for 5 seconds...")
      time.sleep(5)
  except requests.exceptions.Timeout as timeout:
      logger.error(f"ERROR: Timeout Error - {timeout}. Sleeping for 5 seconds...")
      time.sleep(5)
  finally:
      if attempt == PARAMS.max_retries - 1:
          logger.error(f"ERROR: Maximum number of retries ({PARAMS.max_retries}) exceeded. Giving up.")
