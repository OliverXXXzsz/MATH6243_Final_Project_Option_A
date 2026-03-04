# MATH6243_Final_Project_Option_A
# Group Members: Shize Zong, Nguyen Bao, Zhenyu Xie

## Project title 
Predicting Residential Assessed Value and Simulating a Simplified Property Tax Shift in Cook County

## Short project overview
This project studies a simplified version of a property-tax policy question in Cook County. We examine what may happen under a revenue-neutral shift in tax burden away from improvements and toward land value. Our goal is to estimate whether a meaningful share of residential parcels would experience a lower simulated tax burden under this policy change.

This project is based on Option A of the course final project and combines supervised learning with a simplified counterfactual policy simulation.

## Research Questions / Objective
Our project focuses on two main questions:

1. Under a simplified revenue-neutral shift from improvement-based taxation toward land-based taxation, what fraction of residential parcels would experience a lower simulated tax burden?
2. How do the simulated effects vary across geographic groups and across property-value deciles?

Our main objective is to build a transparent and reproducible workflow that first predicts residential assessed value, then uses the assessment components to study the distributional impact of a stylized property-tax shift.

## Data Sources and Links
We currently plan to use the following Cook County Assessor datasets:

1. **Assessed Values**  
   Main parcel-level dataset containing:
   - Land Assessed Value (Land AV)
   - Improvement Assessed Value (Improvement AV)
   - Total Assessed Value (Total AV)
   - Tax year

   Link: https://catalog.data.gov/dataset/assessor-historic-assessed-values

2. **Single and Multi-Family Improvement Characteristics**  
   Residential structural and physical characteristics, such as:
   - building square footage
   - lot size
   - year built
   - number of units
   - construction class
   - exterior wall type
   - selected structural indicators

   Link: https://catalog.data.gov/dataset/assessor-single-and-multi-family-improvement-characteristics

3. **Parcel Universe**  
   Parcel-level administrative and geographic identifiers, including municipality and related location fields.

   Link: https://catalog.data.gov/dataset/assessor-parcel-universe-current-year-only

4. (Optional for now) **Property Tax-Exempt Parcels**  
   Used for sample restriction so the analysis focuses on taxable residential parcels.

   Link: https://datacatalog.cookcountyil.gov/Property-Taxation/Assessor-Property-Tax-Exempt-Parcels/vgzx-68gb/about_data

5. (Optional for now) **Neighborhood Boundaries**
   May be used later for more detailed subgroup analysis and visualization.

   Link: http://catalog.data.gov/dataset/assessor-neighborhood-boundaries

In addition, we use the CCAO GitHub wiki as a documentation starting point for identifying and understanding the public data ecosystem:

- CCAO Data Wiki: https://github.com/ccao-data/wiki
- Open Data Guide: https://github.com/ccao-data/wiki/blob/master/SOPs/Open-Data.md

## Planned Methods
Our two primary methods are:

- **Ridge Regression**
- **Elastic Net**

These models will be used to predict **Total Assessed Value** using structural and geographic predictors.

After the prediction stage, we will run a **simplified counterfactual tax-shift simulation** using **Land AV** and **Improvement AV** to study how the simulated tax burden changes when the burden is shifted away from improvements and toward land.

## Unit of Analysis
The main unit of analysis is **parcel-year**.

This is the most appropriate level because assessment values are tied to tax year, and it gives us a consistent unit for merging parcel-level and improvement-level information.

## Repository Structure (following the suggestions from the Project Guide)
This repository is organized as follows:

- `data_raw/` — raw downloaded source data (not committed if too large)
- `data_processed/` — cleaned and merged analysis-ready data
- `src/` — preprocessing, modeling, and simulation scripts
- `reports/` — proposal, notes, and final write-ups
- `docs/` — additional documentation
- `figures/` — generated plots, charts, and visual outputs

## Data Sharing / Responsible Use Note (Statement)
This project uses public administrative datasets. We will not upload restricted, private, or personally identifiable data to this repository.

## Repository Link
Repository URL: https://github.com/OliverXXXzsz/MATH6243_Final_Project_Option_A

## Project Status
Phase I repository setup in progress.
