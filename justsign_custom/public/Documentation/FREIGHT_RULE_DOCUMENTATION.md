# Freight Rule System - User Guide

## Overview
The **Freight Rule System** is used to define and manage shipping charges for your orders. It allows you to set different freight rates based on various factors like quantity, weight, order amount, or a fixed price. This helps you automatically calculate the correct shipping cost for each order.

---

## Key Features 

✅ **Flexible Pricing Options** - Set freight charges multiple ways  
✅ **Apply to Items or Groups** - Create rules for specific products or categories  
✅ **Multiple Shipping Modes** - Support Air and Road transportation  
✅ **Different Calculation Methods** - Choose the best pricing model for your business  
✅ **Shipper Management** - Link freight rules to specific carriers  
✅ **Automatic Calculations** - System applies rules automatically to orders  

---

## How the Freight Rule Works

### Main Concepts

A **Freight Rule** defines:
- **What applies the rule** (Specific item or entire item group)
- **How shipping is calculated** (By quantity, weight, amount, or percentage)
- **The freight rates** (Pricing tiers or fixed amounts)
- **Shipping method** (Air or Road)

---

## Step-by-Step Setup Guide

### Step 1: Create a New Freight Rule
1. Give your rule a unique name (e.g., "Local Air Shipping", "Heavy Items Road")
2. This name helps you identify the rule later

### Step 2: Choose Application Type
Select **"Apply On":**
- **Item** - Rule applies to specific products only
- **Item Group** - Rule applies to an entire category of products

**Example:**
- Use "Item" for special items with different shipping rates
- Use "Item Group" for all electronics or all heavy items

### Step 3: Select Calculation Method
Choose **"Calculate Based On":**

| Method | When to Use | Example |
|--------|-----------|---------|
| **Fix Price** | Same shipping cost for all orders | ₹100 per shipment |
| **Qty Wise** | Shipping varies by quantity ordered | 5 items = ₹50, 10 items = ₹80 |
| **Amount Wise** | Shipping based on order total value | ₹0-5000 = ₹100, ₹5000+ = ₹200 |
| **Weight Wise** | Shipping based on package weight | Up to 5kg = ₹50, 5-10kg = ₹100 |
| **Percentage Wise** | Shipping as percentage of order value | 5% of order amount |

### Step 4: Optional - Select Shipper & Mode
- **Shipper** - Select which carrier/supplier delivers (optional)
- **Mode** - Choose **Air** or **Road** transportation

### Step 5: Enter Pricing Details
Based on your calculation method, add the specific rates in the table below:

**For Fix Price:**
- Just enter a single fixed amount

**For Qty Wise:**
- Define quantity ranges and their corresponding shipping costs
- Example: 1-5 items = ₹50, 6-10 items = ₹75, 10+ items = ₹100

**For Amount Wise:**
- Define order value ranges and shipping costs
- Example: ₹0-10,000 = ₹100, ₹10,001-50,000 = ₹250

**For Weight Wise:**
- Define weight ranges (in kg) and shipping costs
- Example: 0-5kg = ₹75, 5-10kg = ₹150, 10kg+ = ₹250

**For Percentage Wise:**
- Enter percentage rates applied to order totals
- Example: 2% for all orders

### Step 6: Save the Rule
Once you've entered all details, save the freight rule. The system will now use this rule automatically when processing orders.

---

## Field Explanations

| Field | Purpose | Required | Notes |
|-------|---------|----------|-------|
| **Freight Rule Name** | Unique name for the rule | ✓ Yes | Cannot be used twice |
| **Apply On** | Where the rule applies | ✓ Yes | Choose Item or Item Group |
| **Shipper** | Carrier/Supplier name | No | Link to a supplier/carrier |
| **Mode** | Transportation method | No | Air or Road |
| **Calculate Based On** | How costs are determined | ✓ Yes | Choose one method |
| **Pricing Table** | Freight rates | ✓ Yes | Fill based on calculation method |

---

## Workflow Examples

### Example 1: Fixed Shipping Rate
```
Rule Name: Standard Domestic Shipping
Apply On: Item Group (All Items)
Mode: Road
Calculate Based On: Fix Price
Price: ₹200 per shipment
Result: Every order costs ₹200 to ship
```

### Example 2: Quantity-Based Shipping
```
Rule Name: Bulk Item Shipping
Apply On: Item Group (Bulk Products)
Mode: Road
Calculate Based On: Qty Wise

Pricing Tiers:
- 1-10 units   = ₹100
- 11-25 units  = ₹200
- 26+ units    = ₹350

Result: Shipping cost increases with order quantity
```

### Example 3: Weight-Based Shipping
```
Rule Name: Heavy Item Air Shipping
Apply On: Item Group (Heavy Electronics)
Mode: Air
Calculate Based On: Weight Wise

Pricing Tiers:
- Up to 5 kg    = ₹500
- 5-15 kg       = ₹900
- 15-30 kg      = ₹1500
- 30+ kg        = ₹2500

Result: Shipping cost depends on package weight
```

### Example 4: Percentage-Based Shipping
```
Rule Name: Premium Items Shipping
Apply On: Item Group (Premium Products)
Calculate Based On: Percentage Wise

Rate: 3% of order value

Result: If customer orders ₹10,000 worth of goods, shipping = ₹300
```

---

## When to Use Each Method

### Use **Fix Price** When:
- All items cost the same to ship
- Shipping rate doesn't vary by volume or weight
- Simple, uniform shipping policy

### Use **Qty Wise** When:
- You offer bulk discounts on shipping
- Heavier orders should cost more
- Quantity is the main factor

### Use **Amount Wise** When:
- Large orders get better shipping rates
- You want to incentivize bigger purchases
- Order value determines shipping cost

### Use **Weight Wise** When:
- Items vary significantly in weight
- Heavier items carry higher shipping cost
- Weight is the accurate measure

### Use **Percentage Wise** When:
- Shipping cost should scale with product value
- Premium products need premium shipping
- Fair pricing based on order value

---

## Common Scenarios

### Scenario 1: Standard Domestic Shipping
- Single fixed rate for all local orders
- Use "Fix Price" method
- Easy to manage and explain to customers

### Scenario 2: International Shipping
- Create separate rules for different countries
- Use "Weight Wise" for accurate costing
- Different rates for Air vs. Road

### Scenario 3: B2B Bulk Orders
- Offer volume discounts on shipping
- Use "Qty Wise" method
- Encourage larger orders with better rates

### Scenario 4: Premium vs. Standard Products
- Premium items have different shipping rules
- Apply to specific Item Groups
- Use "Percentage Wise" for fair pricing

---

## Important Notes

📌 **Rule Names Must Be Unique** - Each freight rule must have a different name  
📌 **Select Calculation Method First** - Then fill in the pricing table  
📌 **Test Your Rules** - Verify freight calculations work correctly on orders  
📌 **Keep Rules Simple** - Fewer rules are easier to manage  
📌 **Document Your Rules** - Keep notes on why each rule exists  

---

## Tips for Best Results

✓ Create a naming convention (e.g., "SHIPPING_LOCAL_AIR")  
✓ Group similar items together for easier management  
✓ Review and update rates quarterly based on carrier costs  
✓ Test with sample orders before going live  
✓ Keep customer communications clear about shipping charges  
✓ Archive old rules instead of deleting them  

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Wrong shipping calculated | Check if correct rule is assigned to the item/group |
| Rule not applying | Verify "Apply On" matches item type correctly |
| Multiple rules conflict | Ensure each rule has unique scope (different item groups) |
| Customers confused about shipping | Review and simplify your pricing structure |

---

## Quick Reference 

### Calculation Methods Comparison

| Method | Best For | Complexity | Accuracy |
|--------|----------|-----------|----------|
| Fix Price | Standard items | Very Low | Medium |
| Qty Wise | Volume-based | Low | High |
| Amount Wise | Order value-based | Medium | High |
| Weight Wise | Heavy items | Medium | Very High |
| Percentage Wise | Premium items | Low | High |

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**System:** ERPNext - Frappe Framework
