# Exact Dataset Location

After extracting the uploaded ZIP files, use:

## 1. Clinical dataset
Uploaded ZIP:
`Thyroid Disease Data(1).zip`

Put the extracted file here:

`datasets/raw/clinical/thyroidDF.csv`

## 2. Ultrasound dataset
Uploaded ZIP:
`Thyroid Ultrasound(1).zip`

Put XML files here:

`datasets/raw/ultrasound/xml/`

Put JPG/PNG images here:

`datasets/raw/ultrasound/images/`

Do NOT put the ZIP archives inside the training folders after extraction.

Recommended:
- Raw data stays untouched.
- Notebook reads from `datasets/raw/`.
- Cleaned data is written to `datasets/processed/`.
- Trained models are written to `models/`.
- FastAPI loads the trained model files.
