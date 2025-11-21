# Multiple Devices Support - Usage Guide

## Overview
This module now supports tracking multiple devices per repair order through an integrated inventory system.

## Features

### 1. Device Inventory System
Track customer devices with complete details:
- **Category**: Lens, Smartphone, Tablet, etc.
- **Brand**: Canon, Apple, Samsung, etc.
- **Model**: HJ, iPhone 16, Galaxy S22, etc.
- **Variant**: 14x4.3, Pro Max, etc.
- **Serial Number**: Unique identifier
- **Status**: Available, In Repair, Returned

### 2. Multiple Devices per Repair Order
Each repair order can now include multiple devices with:
- Full device configuration per line
- Automatic serial number filtering
- Individual device tracking
- Flexible device management

## Usage Workflow

### Step 1: Check-in Devices to Inventory
**From Main Menu:**
1. Go to "Repair Management" → "Inventory"
2. Click "Create"
3. Fill in device details:
   - Category (e.g., Lens)
   - Brand (e.g., Canon)
   - Model (e.g., HJ)
   - Variant (e.g., 14x4.3)
   - Serial Number (e.g., CNH14X001)
4. Save

**From Repair Order (Quick Check-in):**
1. Open a repair order
2. Click "Check-in Device to Inventory" button at the top
3. Fill in device details as above
4. Save and return to repair order

### Step 2: Add Devices to Repair Order
1. Create or open a repair order
2. Scroll to "Devices" section
3. Click "Add a line"
4. Select device configuration:
   - **Category**: Select category (e.g., Lens)
   - **Brand**: Select brand (e.g., Canon)
   - **Model**: Select model from filtered list (e.g., HJ)
   - **Variant**: Enter or select variant (e.g., 14x4.3)
   - **Serial Number**: Dropdown shows ONLY matching available devices
     * Example: For Lens > Canon > HJ > 14x4.3, only shows:
       - CNH14X001
       - CNH14X002
       - CNH14X003
5. Optionally add color and condition info
6. Repeat to add more devices

### Step 3: Track Devices
- **In List View**: See device count and summary per order
- **In Search**: Search by serial number to find orders
- **In Inventory**: See which devices are in repair and their order

## Key Features

### Automatic Filtering
When you select a device configuration in a repair order:
```
Category: Lens
Brand: Canon
Model: HJ
Variant: 14x4.3

↓ Serial Number dropdown shows only: ↓

CNH14X001 - Canon HJ 14x4.3 Lens
CNH14X002 - Canon HJ 14x4.3 Lens
CNH14X003 - Canon HJ 14x4.3 Lens

(Other serial numbers for different configs are hidden)
```

### Status Management
- **Available**: Device is in inventory, ready to be added to repair
- **In Repair**: Device is currently assigned to a repair order
- **Returned**: Device has been returned to customer

Status updates automatically:
- Add device to repair → Status: In Repair
- Remove device from repair → Status: Available

### Backward Compatibility
Legacy single-device fields are still available but hidden when using the new device lines feature. Existing repairs continue to work without changes.

## Example Scenario

**Scenario**: Customer brings 3 Canon HJ14x4.3 lenses for repair

1. **Check-in to Inventory** (if not already in system):
   - Device 1: Lens > Canon > HJ > 14x4.3 > S/N: CNH14X001
   - Device 2: Lens > Canon > HJ > 14x4.3 > S/N: CNH14X002
   - Device 3: Lens > Canon > HJ > 14x4.3 > S/N: CNH14X003

2. **Create Repair Order**:
   - Customer: ABC Broadcasting Company
   - Add device line 1: Lens > Canon > HJ > 14x4.3 > CNH14X001
   - Add device line 2: Lens > Canon > HJ > 14x4.3 > CNH14X002
   - Add device line 3: Lens > Canon > HJ > 14x4.3 > CNH14X003

3. **Result**:
   - Repair order shows: "3 devices"
   - List view shows: "Lens Canon HJ 14x4.3 (S/N: CNH14X001), Lens Canon HJ 14x4.3 (S/N: CNH14X002) (+1 more)"
   - All 3 devices marked as "In Repair" in inventory
   - Linked to repair order for tracking

## Benefits

1. **Accurate Tracking**: Know exactly which serial numbers are in which repair
2. **Filtered Selection**: Only see relevant serial numbers for your device config
3. **Multiple Devices**: Handle complex repairs with multiple items
4. **Inventory Management**: Full visibility of all devices in your system
5. **Status Tracking**: Automatic status updates prevent confusion
6. **Search**: Find repairs by serial number quickly
7. **Reporting**: See device counts and summaries at a glance

---

# Flight Case Management - Usage Guide

## Overview
The module now supports tracking flight cases containing multiple devices, streamlining the check-in process for bulk device arrivals.

## Features

### 1. Flight Case System
Track flight cases with complete details:
- **Case Number**: Automatically generated (CASE#####)
- **Colour**: Aluminium, Black, or Custom
- **Corner Colour**: Yellow, Red, Blue, Black, or Custom (optional)
- **Company**: Link to the customer/company that owns the case
- **Audit Trail**: Track when cases were checked in and by whom

### 2. Device-Case Integration
- Devices can be assigned to flight cases during check-in
- Automatic customer linking from case to device
- Bulk device addition to repair orders from cases

## Usage Workflow

### Step 1: Check-in a Flight Case
**From Main Menu:**
1. Go to "Repair Management" → "Cases"
2. Click "Create"
3. Fill in case details:
   - **Colour**: Select Aluminium, Black, or Custom
     - If Custom: Enter custom colour name
   - **Corner Colour** (optional): Select or enter custom
   - **Company**: Select the customer/company
4. Save - a case number will be automatically generated (e.g., CASE00001)

### Step 2: Check-in Devices to the Case
**From Main Menu:**
1. Go to "Repair Management" → "Inventory"
2. Click "Create"
3. Fill in device details:
   - Category, Brand, Model, Variant, Serial Number (as usual)
   - **Case**: Select the case number (e.g., CASE00001)
   - **Customer**: Will auto-populate from case's company
4. Repeat for all devices in the case
5. Save each device

### Step 3: Create Repair Order with Case Devices
**Method 1: Bulk Addition**
1. Create or open a repair order
2. Scroll to "Devices" section
3. Under "Add Devices from Case":
   - Select a case from the dropdown
   - Click "Add All Devices" button
4. All available devices from the case will be added automatically
5. The customer field will be updated to match the case's company

**Method 2: Manual Addition**
1. Follow the standard device addition process described in the Multiple Devices guide
2. Devices from the case will be available in the serial number dropdown

## Example Scenario: Broadcasting Equipment Case

**Scenario**: ABC Broadcasting sends 5 lenses in a black case with yellow corners

**Step-by-step:**

1. **Check-in the Case**:
   - Colour: Black
   - Corner Colour: Yellow
   - Company: ABC Broadcasting Company
   - Result: CASE00001 created

2. **Check-in Devices**:
   - Device 1: Lens > Canon > HJ > 14x4.3 > CNH14X001 > CASE00001
   - Device 2: Lens > Canon > HJ > 14x4.3 > CNH14X002 > CASE00001
   - Device 3: Lens > Canon > HJ > 14x4.3 > CNH14X003 > CASE00001
   - Device 4: Lens > Canon > HJ > 14x4.3 > CNH14X004 > CASE00001
   - Device 5: Lens > Canon > HJ > 14x4.3 > CNH14X005 > CASE00001
   - Customer auto-populated for all devices

3. **Create Repair Order**:
   - Open new repair order
   - Under "Add Devices from Case", select "CASE00001"
   - Click "Add All Devices"
   - Customer automatically set to ABC Broadcasting Company
   - All 5 devices added in one click

4. **Result**:
   - Repair order shows: "5 devices"
   - All devices linked and marked as "In Repair"
   - Complete tracking from case to devices to repair

## Additional Features

### Searching and Filtering
- Search for cases by case number or company
- Group cases by colour or company
- Filter inventory by case number
- View all devices in a specific case

### Case Information Display
- Inventory list shows case number for each device
- Customer field visible in inventory for quick reference
- Case details include audit trail (check-in date and user)

## Benefits

1. **Efficiency**: Check-in multiple devices faster with case grouping
2. **Traceability**: Track which case devices arrived in
3. **Accuracy**: Automatic customer linking reduces data entry errors
4. **Bulk Operations**: Add all case devices to repair orders in one click
5. **Organization**: Keep related devices grouped by their physical container
6. **Professional**: Match physical case identification (colour, corner colour) to digital records
