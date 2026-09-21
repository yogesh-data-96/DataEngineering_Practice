# Healthcare Encounter Data Quality Pipeline

A Python-based data quality pipeline that demonstrates how healthcare encounter data can be ingested, transformed, validated, and separated into valid and rejected records.

> **Note:** All data in this project is synthetic and contains no real patient information.

## Project Overview

Data quality is critical in healthcare data engineering because incorrect dates, missing identifiers, invalid departments, and incorrect financial values can affect downstream analytics and reporting.

This project implements a small end-to-end validation pipeline that:

1. Loads encounter data from CSV.
2. Validates the expected schema.
3. Normalizes dates, numeric values, and text fields.
4. Applies business validation rules.
5. Separates valid and rejected records.
6. Records the reason for rejected records.
7. Calculates data quality metrics.
8. Writes the processed results to output files.

## Architecture

```text
Synthetic CSV Data
       |
       v
   Load Data
       |
       v
Schema Validation
       |
       v
Data Transformation
       |
       v
Business Rule Validation
       |
       +-------------------+
       |                   |
       v                   v
 Valid Records       Rejected Records
       |                   |
       +---------+---------+
                 |
                 v
        Quality Summary
