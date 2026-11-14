# Procurement Purchase Orders: Data Dictionary and Business Rules

## 1. Overview
Table: `purchase_orders`. One row per purchase order (PO) placed with a
supplier. Use this document to understand column meanings, allowed values,
KPI formulas and known data quirks. For actual numbers, query the database.

## 2. Column Definitions

### PO_ID
Unique identifier of the purchase order. Format: `PO-00001`. Primary key.

### Supplier
Name of the supplier fulfilling the order. Values seen: Alpha_Inc,
Beta_Supplies, Delta_Logistics, Epsilon_Group, Gamma_Co.

### Order_Date
Date the PO was placed. Format: DD/MM/YYYY (day first).

### Delivery_Date
Date associated with delivery of the PO. Format: DD/MM/YYYY.
Open question: it is unclear whether this is the actual or the promised
delivery date. Confirm before computing on-time delivery.

### Item_Category
Type of goods ordered. Values seen:
- Office Supplies: general office consumables
- MRO: Maintenance, Repair and Operations items
- Packaging: packaging materials
- Raw Materials: inputs used for production

### Order_Status
Current state of the PO. Values seen:
- Delivered: fully received
- Partially Delivered: only part of the quantity received
- Pending: not yet delivered
- Cancelled: order cancelled; no goods expected

### Quantity
Number of units ordered.

### Unit_Price
List price per unit before negotiation. Currency is not specified in the
data. Confirm before reporting money values.

### Negotiated_Price
Final agreed price per unit after negotiation. In the sample it is always
lower than Unit_Price.

### Defective_Units
Number of received units that were defective. Can be empty (NULL), for
example on cancelled orders where nothing was received.

### Compliance
Whether the order complied with procurement policy. Values: Yes, No.
The specific policy is not defined in the data. *(assumption)* It may cover
approved suppliers, required approvals or contract terms.

### load_date
Timestamp when the row was loaded into the database (ETL load time).
Not a business date. Do not use it for order or delivery analysis.

## 3. KPI Definitions *(proposed, edit to match your business)*

### Negotiation savings
Savings per order = (Unit_Price - Negotiated_Price) x Quantity.
Savings % = (Unit_Price - Negotiated_Price) / Unit_Price.

### Total spend
Spend = Negotiated_Price x Quantity.
Exclude Cancelled orders from spend.

### Defect rate
Defect rate = Defective_Units / Quantity.
Calculate only for orders with Order_Status in (Delivered, Partially
Delivered). Treat NULL defects on Cancelled orders as not applicable,
not as zero.

### Lead time (days)
Lead time = Delivery_Date - Order_Date.
Meaningful only if Delivery_Date is the actual delivery date.

### Compliance rate
Compliance rate = count of orders with Compliance = 'Yes' / total orders.

### Fulfilment rate
Fulfilment rate = Delivered orders / (all orders excluding Cancelled).

## 4. Business Rules and Interpretation Guidance
- Cancelled orders should be excluded from spend, defect rate and
  lead time analysis.
- When comparing suppliers, compare within the same Item_Category,
  because price levels differ by category.
- A supplier with a high defect rate and Compliance = 'No' orders is a
  higher-risk supplier.
- A large gap between Unit_Price and Negotiated_Price on a single order
  may indicate strong negotiation, or a list price set too high. Compare
  with other orders in the same category before concluding.

## 5. Known Data Quirks (observed in the sample)
- Defective_Units is empty for Cancelled orders.
- A Pending order can still show a Delivery_Date and Defective_Units. This
  may mean partial receipt or a data entry issue. Flag it, do not assume.
- Dates use DD/MM/YYYY. Parse with day first to avoid swapping day and
  month.
- load_date is the same for all rows in a batch and reflects the load
  time only.

## 6. Example Questions This Data Can Answer
- Which supplier has the highest defect rate in Raw Materials?
- How much did negotiation save by item category?
- What share of orders is non-compliant, and which suppliers cause it?
- Which suppliers have the longest average lead time?
- How many orders are still Pending, and since when?

## 7. When to Use SQL vs This Document
- Use SQL for counts, sums, averages and trends.
- Use this document for column meanings, KPI formulas, status definitions
  and data quirks.
- If a KPI is not defined here, say so instead of guessing.