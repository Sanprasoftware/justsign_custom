# Vehicle Entry System - User Guide

## Overview
The **Vehicle Entry System** is designed to track and manage vehicle check-ins and check-outs. It helps you maintain a record of which vehicles are entering or leaving your premises, along with the time they arrive and depart.

---

## Key Features 

✅ **Vehicle Registration** - Create and link vehicles to customer records  
✅ **Check-In/Check-Out Tracking** - Record when vehicles enter and leave  
✅ **Mobile Number Lookup** - Quickly find customer and vehicle information  
✅ **Automatic Status Updates** - System automatically tracks vehicle status  
✅ **Timestamp Recording** - Automatic recording of entry and exit times  

---

## How to Use the System

### Step 1: Enter Vehicle Number
- Enter the vehicle's license plate numb er (e.g., DL-01-AB-1234)
- Select the vehicle type: **Bike** or **Car**

### Step 2: Link to Customer (First Time Users)
**Option A - If customer exists:**
- Enter the customer's **mobile number**
- The system will automatically find and link their information

**Option B - If customer is new:**
- Enter the mobile number
- Click **"Create Lead & Vehicle"** button
- This creates a new customer record and vehicle entry in the system

### Step 3: Check-In Process
- Click the **"Check IN"** button when the vehicle arrives
- The system automatically records the exact arrival time
- Status changes to **"Check In"**

### Step 4: Check-Out Process
- Click the **"Check Out"** button when the vehicle leaves
- The system automatically records the exact departure time
- Status changes to **"Check Out"**

---

## Field Explanations

| Field | Purpose | Notes |
|-------|---------|-------|
| **Vehicle Number** | License plate of the vehicle | Cannot be left empty |
| **Vehicle Type** | Bike or Car | Must be selected (required) |
| **Mobile Number** | Customer's phone number | Used to identify the vehicle owner |
| **Check IN** | Button to mark arrival | Records arrival time automatically |
| **Check IN Time** | Arrival timestamp | Set automatically when Check IN is clicked |
| **Check Out** | Button to mark departure | Records departure time automatically |
| **Check Out Time** | Departure timestamp | Set automatically when Check Out is clicked |
| **Status** | Current state of the vehicle | Shows: Open, Check In, or Check Out |
| **Lead** | Customer/Lead reference | Auto-filled from mobile number lookup |
| **Custom Vehicle** | Link to vehicle master record | Auto-filled from database |

---

## Workflow Summary

```
New Entry
    ↓
Enter Vehicle Number & Type
    ↓
Enter Mobile Number
    ↓
System Looks Up Customer
    ↓
Click "Check IN" (Vehicle Arrives)
    ↓
System Records Arrival Time
    ↓
Click "Check Out" (Vehicle Leaves)
    ↓
System Records Departure Time
    ↓
Entry Complete
```

---

## Quick Reference

### When to Click "Create Lead & Vehicle"
- Use this **only the first time** a new customer enters a vehicle
- This button is only available when no mobile number entry exists
- After clicking, the system creates both a customer and vehicle record

### Automatic Actions
- **Vehicle lookup** - When you enter a vehicle number, all linked information loads automatically
- **Time recording** - Check-in and check-out times are recorded automatically by the system
- **Customer matching** - The system finds the customer using their mobile number

---

## Common Scenarios

### Scenario 1: Regular Customer Returning
1. Enter vehicle number
2. Mobile number auto-fills from previous records
3. Click "Check IN" to record arrival
4. Later, click "Check Out" to record departure

### Scenario 2: New Vehicle or Customer
1. Enter vehicle number and mobile number
2. Click "Create Lead & Vehicle" (system creates new records)
3. Click "Check IN" when vehicle arrives
4. Click "Check Out" when vehicle leaves

### Scenario 3: Viewing History
- All previous vehicle entries are stored in the system
- You can view check-in and check-out times for any vehicle
- Status field shows the current state (Open, Check In, Check Out)

---

## Tips for Best Results

📌 Always enter the **complete and correct vehicle number**  
📌 Ensure mobile numbers are **10 digits** (as per system requirement)  
📌 Click buttons in the correct order: **Check IN** first, then **Check Out**  
📌 The system automatically records timestamps - no need to enter manually  
📌 Once created, vehicle records are permanent and reusable  

---

## Support

If you encounter any issues:
- Verify the vehicle number is entered correctly
- Check that the mobile number format is correct (10 digits)
- Ensure you're clicking buttons in the right sequence
- Contact the technical team for any system errors

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**System:** ERPNext - Frappe Framework
