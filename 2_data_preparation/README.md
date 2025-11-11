<!-- markdownlint-disable MD013 -->

# 🧼 Data Cleaning Script

**Main file for cleaning  data**: as **Main file for cleaning data:** [***`cleaning_data_script.ipynb`***](./cleaning_data_script.ipynb).

Cleaning data contains the Python scripts used to **clean, merge, and organize**
the  [***`original datasets`***](../1_datasets/orders_and_shipments.raw.csv).
 before analysis.  
The purpose of this stage is to create a reliable and consistent dataset ready
for exploration and visualization.

---

## 🔧 Overview of Data Cleaning Process

1. **Data Cleaning**  
   - Removed duplicates, missing values, and inconsistent records.  
   - Standardized column names and formatting for readability.  
   - Fixed special characters in country names to ensure uniformity.

2. **Merging Datasets**  
   - Combined multiple columns (Orders data and Shipments data,) into one
   unified dataset.  
   - Ensured records matched accurately across datasets using common identifiers.

3. **Adding Region Information**  
   - Added a new **Region** column to classify countries by geographic area
   (e.g., Asia, Europe, Africa).  
   - This required careful correction of country names to ensure proper region mapping.

---

## 💾 Output

- The final cleaned dataset is saved as:  
   [***`orders_and_shipments_final_cleaned.csv`***](../1_datasets/orders_and_shipments_final_cleaned.csv)  
  (located inside the `1_cleaned_data` folder)

- The original unmodified datasets remain in the `0_datasets` folder for
  transparency and reproducibility as [***`original datasets`***](../1_datasets/orders_and_shipments.raw.csv).

---
