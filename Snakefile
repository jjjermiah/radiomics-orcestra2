# lookup(
#     dpath: Optional[str | Callable] = None,
#     query: Optional[str | Callable] = None,
#     cols: Optional[List[str]] = None,
#     is_nrows: Optional[int],
#     within=None,
#     default=NODEFAULT
# )
# conda: "pipeline.yaml"

import pandas as pd
from pathlib import Path

dataset = "Head-Neck-Radiomics-HN1"

series_df = pd.read_csv(f"metadata2/{dataset}/series_df.csv")

# subset patientids if a row has Modality == "RTSTRUCT"
PATIENT_IDS = series_df[series_df["Modality"] == "RTSTRUCT"]["PatientID"].unique()
PATIENT_IDS=PATIENT_IDS[:1]

envvars:
    "NBIA_USERNAME",
    "NBIA_PASSWORD",


rule all:
    input:
        expand(
            "rawdata/{dataset}/images/unzipped/{PatientID}",
            dataset=dataset,
            PatientID=PATIENT_IDS,
        ),


rule eval_zip:
    input:
        collect(
            Path("rawdata")
            / dataset
            / "images/zipped/{series.PatientID}/{series.SeriesInstanceUID}.zip",
            series=lookup(
                query="(Modality == 'RTSTRUCT' or Modality == 'CT') & PatientID == '{PatientID}'",
                within=series_df,
            ),
        ),
    output:
        directory("rawdata/{dataset}/images/unzipped/{PatientID}"),


rule download_zip:
    output:
        zip_file="rawdata/{dataset}/images/zipped/{PatientID}/{SeriesInstanceUID}.zip",
    params:
        NBIA_PASSWORD=os.environ["NBIA_PASSWORD"],
        NBIA_USERNAME=os.environ["NBIA_USERNAME"],
        max_retries=3,
    script:
        "workflow/scripts/download_as_zip.py"
