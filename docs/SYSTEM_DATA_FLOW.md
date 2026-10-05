# System Data Flow

```text
AngularJS Frontend
       |
       v
FastAPI REST API
       |
       +----> PostgreSQL
       |        |
       |        +--> Patients
       |        +--> Reports
       |        +--> Workflow
       |        +--> AI results
       |        +--> Audit trail
       |
       +----> Model Service
                  |
                  +--> Clinical model
                  +--> Ultrasound model
                  +--> Multimodal fusion
                           |
                           v
                    Decision Support
                           |
                           v
                 Senior Doctor Review
                           |
                           v
                 Final Treatment Plan
```

Jupyter is used for:
- data cleaning
- feature engineering
- clinical model training
- ultrasound model training
- model evaluation
- saving model artifacts to `models/`

The website/backend then loads those saved models.
