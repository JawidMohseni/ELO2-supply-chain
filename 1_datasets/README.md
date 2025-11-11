# Datasets

This folder contains the **original/raw dataset** used for our supply chain
analysis project.

---

## 1. Source

**Original Dataset Repository:**  
[Supply Chain Analytic — Just In Time Company](https://github.com/hoshigan/Supply-Chain-Analytic---Just-In-Time-Company?utm_source=chatgpt.com)

**Access:** Publicly available for educational and research purposes.

**Notes:** The dataset is stored in its original form and has
**not been cleaned or modified**.
 Cleaning and preprocessing steps are documented separately
 in the `2_data_preparation` folder.

---

## 2. Raw Dataset Overview

**File:** [***`orders_and_shipments_raw.csv`***](../1_datasets/orders_and_shipments.raw.csv).

**Description:**  
The dataset provides detailed information on orders and shipments across
 multiple countries. It captures order details, product information, customer
demographics, shipment data, and financial metrics. This data is essential for
analyzing supply chain performance, shipment delays, and sales patterns.

---

## 3. Columns / Features

- **Order ID**: Unique identifier for each order.  
- **Order Item ID**: Identifier for individual items within an order.  
- **Order YearMonth**: Year and month of the order (e.g., 201502).  
- **Order Year**: Year of the order.  
- **Order Month**: Month of the order.  
- **Order Day**: Day of the order.  
- **Order Time**: Time when the order was placed.  
- **Order Quantity**: Quantity of each product in the order.  
- **Product Department**: Main department the product belongs to.  
- **Product Category**: Subcategory of the product.  
- **Product Name**: Name of the product.  
- **Customer ID**: Unique identifier for the customer.  
- **Customer Market**: Market segment of the customer.  
- **Customer Region**: Geographic region of the customer.  
- **Customer Country**: Country of the customer.  
- **Warehouse Country**: Country of the warehouse fulfilling the order.  
- **Shipment Year**: Year the shipment occurred.  
- **Shipment Month**: Month of the shipment.  
- **Shipment Day**: Day of the shipment.  
- **Shipment Mode**: Mode of shipment (e.g., air, sea, road).  
- **Shipment Days - Scheduled**: Scheduled number of days for shipment.  
- **Gross Sales**: Total sales amount for the order before discounts.  
- **Discount %**: Discount applied to the order.  
- **Profit**: Profit from the order after costs and discounts.  

---

## Data Collection

The dataset is from
[Supply Chain Analytics – Just In Time Company](https://github.com/hoshigan/Supply-Chain-Analytic---Just-In-Time-Company?utm_source=chatgpt.com).

It contains global order and shipment data including customer country, warehouse
 country, products, orders, shipments, and financial metrics. The dataset
 provides a broad view of supply chain operations for analysis purposes.

---

## 4. Notes

- This is the **raw dataset**, so it may contain **inconsistent country names,
  special characters, missing values, or duplicates**. These issues are handled
  in the data preparation step.  
- All columns are preserved exactly as they were in the original source to
  maintain reproducibility.  
- The dataset can be used to analyze supply chain operations, shipment delays,
- sales performance, and regional trends.

---

## 5. Recreating / Accessing the Data

To access the dataset:

1. Visit the source repository: [Supply Chain Analytic — Just In Time Company](https://github.com/hoshigan/Supply-Chain-Analytic---Just-In-Time-Company?utm_source=chatgpt.com)
2. Download the dataset file `orders_and_shipments_raw.csv`.  
3. Place it in the `0_datasets` folder for use in analysis or preprocessing.

---

## Possible Limitations

- Some countries or regions may have fewer records than others.  
- Certain details about business context or data collection methods are not provided.
  
---
**Relevance to Our Project:**  
This dataset allows analysis of delivery performance, regional shipment patterns,
 and supply chain efficiency. It provides essential features for
 exploring delays and comparing regions.
