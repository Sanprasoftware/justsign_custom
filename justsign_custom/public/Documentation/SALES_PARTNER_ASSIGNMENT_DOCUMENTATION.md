# Sales Partner Assignment & Lead Management - Technical Documentation

## Overview
The **Sales Partner Assignment System** automatically matches incoming leads with the most appropriate sales partners based on specific criteria. This ensures every lead is distributed to the right team member who specializes in that lead's characteristics. The system also enables lead tracking, comments, and follow-up scheduling.

--- 

## Core System Architecture

### Main Components

1. **Assign Sales Partner** - Automatic lead-to-partner matching
2. **Lead Status Tracking** - Marks leads as "Assigned" or "Not Assigned"
3. **Sales Partner Assigned Lead Record** - Detailed tracking document
4. **Lead Comments** - Team communication and notes
5. **Follow-Up Events** - Scheduling calls and meetings

---

## How Assign Sales Partner Works

### Step 1: Trigger Point
When a lead is **created or updated**, the `assign_sales_partner()` function is automatically triggered.

### Step 2: Validation
The system checks if the Lead has THREE required fields:
- **Pincode** - Lead's location
- **Brand** - Product/service brand they're interested in
- **Lead Type** - Category of the lead (e.g., Customer, Prospect)

**If any field is missing:**
- ❌ Assignment is skipped
- Lead status remains as is
- A warning is logged

### Step 3: Sales Partner Matching Process

The system searches for Sales Partners with matching criteria:

```
FOR EACH Sales Partner:
   ├─ Check if they handle this PINCODE
   ├─ Check if they sell this BRAND
   └─ Check if they handle this LEAD TYPE

IF ALL THREE match:
   └─ Add to matched partners list
```

### Step 4: Match Results

**Case 1: Match Found ✅**
- Lead is assigned to the matching Sales Partner
- Lead status changes to **"Assigned"**
- Sales Partner Assigned Lead record is created/updated

**Case 2: No Match Found ❌**
- Lead status changes to **"Not Assigned"**
- Message: "No matching Sales Partner found"
- **Fallback:** If a Sales Partner is manually assigned, use them instead

### Step 5: Data Transfer

When a match is found, the following information is captured:

```
Lead Information → Sales Partner Assigned Lead
├─ Lead Name
├─ Lead Email
├─ Lead Mobile Number
├─ Lead City
├─ Lead Pincode
├─ Lead Status
├─ Lead Brand
├─ Lead Type
├─ Lead Comments (last 10 comments)
└─ Sales Partner Details
   ├─ Sales Partner Name
   ├─ Sales Partner Email
   ├─ Sales Partner Mobile
   ├─ Sales Partner Customer Link
   └─ Linked Customer Email
```

---

## Sales Partner Configuration

### What Sales Partners Need

Each Sales Partner must have the following information configured:

#### 1. **Pincode Table**
Lists all pincode areas they serve

| Field | Type | Example |
|-------|------|---------|
| Pincodes | Numeric | 110001, 110002, 110003 |

#### 2. **Brand Table**
Lists all brands they handle

| Field | Type | Example |
|-------|------|---------|
| Brand | Text | BMW, Ferrari, Audi |

#### 3. **Lead Type Table**
Lists lead types they accept

| Field | Type | Example |
|-------|------|---------|
| Lead Type | Select | Direct, Referral, Website |

#### 4. **Customer Link**
Linked customer record (optional)

| Field | Type | Example |
|-------|------|---------|
| Custom Customer | Link | Customer-001 |

#### 5. **Email & Mobile**
Contact information

| Field | Type | Example |
|-------|------|---------|
| Custom Email | Email | partner@company.com |
| Custom Mobile No | Phone | 9876543210 |

---

## Data Flow Diagram

```
Lead Created/Updated
        ↓
Check Required Fields (Pincode, Brand, Lead Type)
        ↓
    ├─ Missing? → Skip & Return
    └─ Present? → Continue
        ↓
Loop Through All Sales Partners
        ↓
    For Each Partner:
    ├─ Check Pincode Match?
    ├─ Check Brand Match?
    └─ Check Lead Type Match?
        ↓
    ├─ All Match? → Add to Matched List
    └─ Any Mismatch? → Skip to Next Partner
        ↓
Matched List Result:
    ├─ Has Matches? → Assign to First Match
    │  ├─ Create "Sales Partner Assigned Lead" Record
    │  ├─ Update Lead Status to "Assigned"
    │  ├─ Populate Lead Information
    │  └─ Transfer Sales Partner Details
    │
    └─ No Matches? → Mark as "Not Assigned"
       ├─ Update Lead Status to "Not Assigned"
       ├─ Show Message to User
       └─ If Manual Partner Exists → Use Fallback
```

---

## Lead Status Field

### What It Means

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **Assigned** | ✅ Matched to a Sales Partner | Sales Partner can now work on the lead |
| **Not Assigned** | ❌ No matching Sales Partner found | Manual assignment needed or follow up |

---

## Sales Partner Assigned Lead Record

### What Gets Created

When a lead is successfully assigned, a new document type **"Sales Partner Assigned Lead"** is created with:

#### Lead Information Section
- Lead's name, email, phone
- Lead's city, pincode, status
- Brand they're interested in
- All comments from lead discussions

#### Sales Partner Section
- Sales Partner name
- Sales Partner's email and phone
- Linked customer (if available)
- Customer's email (if available)

#### Purpose
- **Central tracking** of all lead-partner relationships
- **Quick reference** for lead history
- **Reporting** on lead distribution
- **Future reference** for similar leads

### Update vs. Create Logic

**If lead already has an assignment:**
- Existing record is **updated** with new information
- Previous history is preserved
- Message: "Updated existing Sales Partner Assigned Lead"

**If lead is new or unassigned:**
- New record is **created**
- All current lead information is captured

---

## Comment System

### Add Comment Feature

Users can add comments to a lead using the **"Add Comment"** button.

**Function:** `add_comments(comment, name, email)`

**What Happens:**
1. User enters their comment
2. System creates a Comment record linked to the Lead
3. Comments are stored in the database
4. Comments appear in lead's timeline
5. Recent comments (last 10) are included in assignment records

**Comment Storage:**
- Reference: Linked to the Lead document
- Type: "Comment" type (not system notes)
- Visibility: All team members can see
- Used for: Context when assigning to partners

---

## Follow-Up Event System

### Type 1: Standard Follow-Up

**Function:** `create_event_with_todos(data)`

**What It Does:**
- Creates an Event record in the system
- Creates corresponding ToDo items for assigned users
- Automatically links to the lead

**Information Captured:**
- Subject of the meeting/call
- Start and end time
- Duration (in minutes)
- Event category (Call, Meeting, Email, etc.)
- Assigned to multiple users
- Description/notes

**Multiple User Assignment:**
- Can assign one event to multiple team members
- Each person gets their own ToDo
- Helps with collaborative follow-up

**Automatic Calculations:**
- System calculates end time = start time + duration

### Type 2: RNR Follow-Up (Review & Revert)

**Function:** `create_event_with_todos_rnr(data)`

**What It Does:**
- Creates a special "RNR" follow-up event
- Auto-scheduled for 2 days from today
- Assigned to the current user only
- Marked as "Follow Up" category

**Purpose:**
- Quick follow-ups for leads not yet contacted
- Automatic scheduling (no date selection needed)
- Fast to create with minimal input

**Auto-Scheduling Logic:**
```
Today = April 25, 2026
RNR Due Date = April 27, 2026 (Today + 2 days)
Category = "Follow Up"
Assigned To = Current User
```

---

## Code Functions Reference

### 1. assign_sales_partner(doc, method)

**Trigger:** Automatically when Lead is saved

**Parameters:**
- `doc` - The Lead document being saved
- `method` - Frappe hook method

**Logic:**
1. Validates required fields
2. Fetches all Sales Partners
3. Matches based on pincode, brand, lead type
4. Creates or updates assignment record
5. Updates lead status

**Returns:** None (updates database directly)

---

### 2. add_comments(comment, name, email)

**Trigger:** Manual button click by user

**Parameters:**
- `comment` - Text of the comment
- `name` - Lead document name/ID
- `email` - Commenter's email (optional)

**Logic:**
1. Creates new Comment document
2. Links to Lead reference
3. Stores in database
4. Returns "Success" or error

**Returns:** "Success" or error message

---

### 3. create_event_with_todos(data)

**Trigger:** Manual "Add Follow Up" button

**Parameters:**
```
data = {
    subject: "Meeting subject",
    starts_on: "2026-04-25 14:00:00",
    ends_on: "2026-04-25 15:00:00",
    duration: 60,
    description: "meeting details",
    event_category: "Call/Meeting/Email/etc",
    lead_name: "LEAD-001",
    assign_users: ["user1@company.com", "user2@company.com"]
}
```

**Logic:**
1. Creates Event document
2. Links to Lead as participant
3. Creates ToDo for each assigned user
4. If ToDo exists, updates it
5. If ToDo doesn't exist, creates new

**Returns:** Event name/ID

---

### 4. create_event_with_todos_rnr(data)

**Trigger:** Manual "RNR Follow Up" button

**Parameters:**
```
data = {
    lead_name: "LEAD-001",
    created_from_button: 1
}
```

**Logic:**
1. Auto-calculates start date = Today + 2 days
2. Creates Event with RNR flag
3. Assigns to current user only
4. Creates corresponding ToDo
5. Marks as "Follow Up" category

**Returns:** Event name/ID

---

## UI Components (JavaScript)

### Buttons Added to Lead Form

1. **Add Comment** - Opens dialog to add notes
2. **Add Follow Up** - Opens event creation dialog
3. **RNR Follow Up** - Quick 2-day follow-up event

### Form Behavior

**Vehicle Type Selection:**
- When "Car" selected → Clear bike-related fields
- When "Bike" selected → Clear car-related fields
- Prevents data confusion

**Button Visibility:**
- All buttons hidden until lead is saved
- Prevents operations on unsaved leads
- Ensures lead ID exists for linking

---

## Matching Algorithm - Step by Step

### Pseudo Code

```
function assign_sales_partner(lead_doc):
    
    // Step 1: Validate
    if NOT (lead_doc.pincode AND lead_doc.brand AND lead_doc.type):
        return "Missing required fields"
    
    // Step 2: Get all partners
    all_partners = get_all_sales_partners()
    matched_partners = []
    
    // Step 3: Match each partner
    for each partner in all_partners:
        partner_doc = fetch_partner_data(partner)
        
        // Check pincode
        pincode_match = FALSE
        for each row in partner_doc.pincode_table:
            if row.pincode == lead_doc.pincode:
                pincode_match = TRUE
        
        // Check brand
        brand_match = FALSE
        for each row in partner_doc.brand_table:
            if row.brand == lead_doc.brand:
                brand_match = TRUE
        
        // Check lead type
        type_match = FALSE
        for each row in partner_doc.lead_type_table:
            if row.lead_type == lead_doc.type:
                type_match = TRUE
        
        // Add if ALL match
        if (pincode_match AND brand_match AND type_match):
            matched_partners.add(partner)
    
    // Step 4: Process matches
    if matched_partners.count > 0:
        for each partner in matched_partners:
            create_or_update_assignment(partner, lead_doc)
            update_lead_status("Assigned")
    else:
        update_lead_status("Not Assigned")
        show_message("No matching partner")
```

---

## Error Handling

### Scenario 1: Missing Sales Partner Fields
**Error:** Sales Partner missing pincode/brand/lead_type columns

**Handling:**
- System logs warning
- Assignment skipped
- No error shown to user
- Lead remains unaffected

### Scenario 2: Multiple Matches
**What Happens:** First matching partner is used

**Behavior:**
- System doesn't create duplicate assignments
- Existing assignment is preserved
- New assignments update the existing record

### Scenario 3: Duplicate Assignments
**Check:** `frappe.db.exists("Sales Partner Assigned Lead", {...})`

**If Exists:**
- Update existing record
- Preserve history
- Show: "Updated existing assignment"

**If New:**
- Create new record
- Include comment history (last 10)
- Show confirmation message

---

## Performance Considerations

### What Gets Optimized

1. **Duplicate Check**
   - Prevents creating multiple records for same lead
   - Single database query

2. **Batch Operations**
   - All database updates are bundled
   - Reduces round trips

3. **Comment Extraction**
   - Fetches last 10 comments only
   - HTML tags removed for clean text
   - Reduces data size

### Query Counts

```
Sales Partner Assignment:
├─ Query 1: Validate Sales Partner fields
├─ Query 2: Get all Sales Partners list
├─ Query N: For each partner, fetch pincode/brand/type rows
├─ Query N+1: Check if assignment exists
└─ Query N+2: Create or Update assignment record
```

---

## Workflow Examples

### Example 1: New Lead - Perfect Match

```
Lead Created:
├─ Pincode: 110001
├─ Brand: BMW
└─ Type: Direct

Match Process:
├─ Partner A: Serves 110001 ✓, Sells BMW ✓, Takes Direct ✓
└─ Result: MATCH!

Output:
├─ Lead Status → "Assigned"
├─ Sales Partner Assigned Lead → Created
├─ Partner Notified → Ready to work
└─ Success Message → Shown to User
```

### Example 2: New Lead - No Match

```
Lead Created:
├─ Pincode: 110099
├─ Brand: Ferrari
└─ Type: Referral

Match Process:
├─ Partner A: Doesn't serve 110099 ✗
├─ Partner B: Doesn't sell Ferrari ✗
└─ Result: NO MATCH

Output:
├─ Lead Status → "Not Assigned"
├─ Warning → "No matching partner found"
├─ Manual Assignment → Fallback option available
└─ Message → Shown to User
```

### Example 3: Lead Update - Status Change

```
Existing Lead Updated:
├─ Old Brand: BMW
├─ New Brand: Audi
└─ Pincode: 110001 (unchanged)

Re-matching:
├─ Previous Partner: No longer matches (sells BMW, not Audi)
├─ New Partner: Matches (serves 110001, sells Audi, takes Direct)
└─ Result: REASSIGN

Output:
├─ Existing Assignment → Updated with new partner
├─ Lead Status → "Assigned" (to new partner)
├─ History → Preserved
└─ Message → "Updated existing assignment"
```

### Example 4: Follow-Up Creation

```
User Clicks "Add Follow Up":
├─ Opens Dialog
├─ User Enters:
│  ├─ Subject: "Initial Discussion"
│  ├─ Start: April 25, 2:00 PM
│  ├─ End: April 25, 3:00 PM
│  ├─ Category: "Call"
│  ├─ Assign To: ["user1@company", "user2@company"]
│  └─ Description: "Discuss requirements"
│
└─ System Creates:
   ├─ Event record with all details
   ├─ ToFo for user1 - "Initial Discussion"
   ├─ ToDo for user2 - "Initial Discussion"
   ├─ All linked to the Lead
   └─ Notification sent to both users
```

---

## Best Practices

### For Sales Partner Setup

✓ **Be Specific with Pincodes**
  - Don't create overlapping zones
  - Clear boundaries reduce conflicts

✓ **Update Brands Regularly**
  - Add new brands as you take them on
  - Remove discontinued ones

✓ **Clear Lead Type Definitions**
  - Define what each type means
  - Consistent categorization

✓ **Maintain Contact Information**
  - Keep email and phone current
  - Enables notifications

### For Lead Management

✓ **Complete All Lead Fields**
  - Pincode, brand, type must be filled
  - Triggers automatic assignment

✓ **Add Comments During Discussions**
  - Keeps team informed
  - Helps future context

✓ **Schedule Follow-ups Promptly**
  - Create events immediately
  - Prevents leads from going cold

✓ **Review Unassigned Leads**
  - Check "Not Assigned" leads regularly
  - Manually assign or update criteria

---

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Lead not assigned | Missing pincode/brand/type | Fill all required fields |
| Wrong partner assigned | Criteria too broad | Refine partner criteria |
| Duplicate assignments | Bug or manual retry | Check assignment record |
| Comments not visible | Not added to lead | Use "Add Comment" button |
| Follow-up not created | Permissions issue | Check user permissions |
| Event not linked | System error | Recreate with correct lead name |

---

## Summary

The **Sales Partner Assignment System** automatically routes leads to appropriate partners based on:
1. Geographic coverage (pincode)
2. Product expertise (brand)
3. Lead category (type)

It maintains a complete audit trail, enables team communication, and provides comprehensive follow-up scheduling capabilities.

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**System:** ERPNext - Frappe Framework  
**Developer:** Sanpra Softwares
