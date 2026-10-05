# Project Structure

```text
MultiModalCancerTherapy/
|
+-- backend/                         # FastAPI backend
|   +-- app/
|       +-- main.py                  # FastAPI entry point
|       +-- core/                    # config, security, RBAC
|       +-- db/                      # PostgreSQL connection/session
|       +-- models/                  # SQLAlchemy models
|       +-- schemas/                 # Pydantic request/response schemas
|       +-- api/routes/              # patient, AI, reports, workflow, audit APIs
|       +-- services/                # business logic + AI integration
|       +-- utils/
|   +-- tests/
|
+-- frontend/                        # AngularJS 1.8.x + Bootstrap 5
|   +-- index.html
|   +-- css/
|   +-- js/
|       +-- app.module.js
|       +-- controllers/
|       +-- services/
|   +-- views/
|   +-- assets/                      # optional logo/background files
|
+-- database/                        # SQL/schema scripts only
|   +-- schema.sql
|   +-- seed.sql
|
+-- datasets/
|   +-- raw/
|       +-- clinical/                # Thyroid Disease Data
|       +-- ultrasound/
|           +-- images/              # JPG/PNG images
|           +-- xml/                 # XML annotations/patient metadata
|   +-- processed/                   # cleaned/feature-ready data
|
+-- models/
|   +-- clinical/                    # trained clinical model artifacts
|   +-- image/                       # trained ultrasound model artifacts
|
+-- notebooks/                       # Jupyter notebooks for ML/analysis
|
+-- docs/                            # architecture, workflow, API notes
|
+-- .env.example
+-- .gitignore
+-- requirements.txt
+-- package.json
```

Important:
- The actual PostgreSQL database is NOT stored inside this folder.
- The two uploaded ZIP files are DATASETS, not separate databases.
- Keep raw datasets under `datasets/raw/`.
- Store ultrasound images on the file system and their metadata/report links in PostgreSQL for a simple implementation.
