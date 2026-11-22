# Healthcare Claims ELT Pipeline

An end-to-end data pipeline for U.S. Medicare claims data.
It downloads raw claims files, checks them in AWS, cleans them with PySpark,
loads them into a database, and builds a star schema with dbt.
Airflow runs all the steps in order.

> All data is synthetic (CMS DE-SynPUF). No real patient data is used.

## Status
Work in progress.

## Tools
- Python, REST APIs
- AWS S3, AWS Lambda
- PySpark
- PostgreSQL
- dbt
- Apache Airflow
- Docker
- GitHub Actions