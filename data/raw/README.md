# Raw Data Files

This directory contains the original, immutable data files. 

## Data Sources

### Primary Sources
- Government census data
- Immigration/emigration statistics
- Population surveys

### Secondary Sources
- Economic indicators
- Geographic data
- Political stability indices

## File Naming Convention

Use the following naming convention for raw data files:
- `source_YYYY-MM-DD_description.extension`
- Example: `census_2023-01-15_population_data.csv`

## Data Quality Notes

Document any known issues with the raw data:
- Missing values
- Data collection changes
- Known errors or inconsistencies

## Processing Notes

- Never modify files in this directory
- Always create processed versions in `../processed/`
- Document all transformations and cleaning steps
