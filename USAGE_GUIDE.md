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
