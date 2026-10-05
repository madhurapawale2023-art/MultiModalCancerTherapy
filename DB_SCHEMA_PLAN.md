# PostgreSQL Database Plan

Use ONE PostgreSQL database for the application.

Suggested database name:
`multimodal_cancer`

Main tables:
1. users
2. roles
3. patients
4. patient_assignments
5. clinical_records
6. lab_reports
7. pathology_reports
8. imaging_reports
9. imaging_files
10. molecular_records
11. treatment_history
12. workflow_status
13. ai_analysis
14. ai_recommendations
15. specialist_opinions
16. missing_information
17. notifications
18. audit_logs
19. final_treatment_plans

No DNA-testing table, endpoint, page, or route.

Simple storage rule:
- PostgreSQL: application records, metadata, status, findings, AI result, audit data.
- File system: ultrasound images and uploaded report files.
