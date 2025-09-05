# Offline POS (Cash Register) – Python App

A complete specification and implementation guide for a modern, fully offline Point of Sale desktop app built with **Python + SQLite**.

---

## 1) Product Overview

**Goal:** A lightweight, offline cash register for PCs that looks modern, supports barcode scanners, prints receipts, handles product variants (e.g., Pishori vs Daawat rice, 1kg vs 500g), manages stock with supplier re-order functionality, and generates end-of-day and historical reports.

**Primary Users:**
- **Admin:** Manages users, settings, products, suppliers, stock, pricing, taxes, receipts layout; views all reports.
- **Cashier:** Logs in, enters opening cash, sells items, prints receipts, closes shift.

**Key Constraints:**
- Must run **fully offline**.
- Must be **easy to install** and **simple to use**.
- Data is local (SQLite).

---

## 2) Core Features

### 2.1 Sales Register
- Switch between **Grid view** (tiles) and **Table view** (list).
- Add to cart by clicking, searching, or **barcode scanning**.
- Quantity controls and variant selection.
- Discounts, tax calculation, and multiple payment methods (starting with cash).
- Receipt preview & **Print**.

### 2.2 Product & Variant Management
- Products with brands, categories, suppliers, barcodes.
- Variants per product (e.g., 1kg, 500g) with separate prices.
- Optional per-variant barcode/SKU.
- **Stock tracking** (per variant).
- **Reorder level** setting per variant.

### 2.3 Supplier Management
- Suppliers table with name, phone, email, address.
- Products linked to suppliers.
- On low stock, pressing **Re-order** displays supplier details (phone, email, name).
- Optional future feature: generate purchase order PDFs.

### 2.4 Shifts & Cash Drawer
- On login: prompt **Opening Cash**.
- On close shift: compute **Expected vs Actual** cash, and generate **End-of-Day report**.

### 2.5 Reporting
- EOD auto-generated at shift close.
- Filters: **Today**, Specific Day, **Weekly**, **Monthly**, **Annually**, **All time**.
- Summaries: revenue, items sold, top products, tax, discounts.
- Export to **CSV** and **PDF**.

### 2.6 Settings & Users
- Store profile (name, address, logo, receipt footer message).
- Currency symbol/format, tax %, date/time format.
- User management (Admin/Cashier roles).
- Printer selection and receipt preferences.

---

## 3) Tech Stack

- **DB:** SQLite (via built-in sqlite3 module)
- **PDF/Reports:** ReportLab or FPDF
- **Packaging:** PyInstaller

---

## 4) Architecture

- **Main App:** `main.py` launches QMainWindow with stacked pages (Sales, Products, Reports, Settings).
- **Modules:** Organized by feature (sales, reports, settings).
- **Database Layer:** Central `db.py` with models for CRUD operations.
- **UI Layer:** screens, modern look.

---

## 5) Data Model

### Users
- `id, username, password_hash, role (admin/cashier)`

### Settings
- `id, key, value`

### Suppliers
- `id, name, phone, email, address`

### Products
- `id, name, brand, category, barcode, supplier_id (FK)`

### Variants
- `id, product_id, name (e.g., 1kg, 500g), price, barcode, stock_qty, reorder_level`

### Shifts
- `id, user_id, opening_cash, closing_cash, start_time, end_time`

### Sales
- `id, shift_id, total, payment_method, created_at`

### Sale Items
- `id, sale_id, product_id, variant_id, qty, price, subtotal`

---

## 6) UI/UX

### Layout
- **Top bar:** Store name, user, time, quick actions.
- **Left nav:** Sales, Products, Reports, Settings.

### Sales Screen
- Search bar, toggle between grid and table view.
- Cart panel with totals, tax, discounts, payment.
- Barcode scanning support.

### Products Screen
- Table of products and variants with stock and supplier info.
- Stock indicators (green = ok, yellow = low, red = critical).
- **Re-order button** for low-stock products → pops up supplier details.

### Reports Screen
- Date filters and summaries.
- Export buttons.

### Settings Screen
- Store details, users, currency, printer, receipt message.

---

## 7) Offline Strategy

- All assets shipped with app.
- Database stored locally in user data folder.
- Backup/export features provided.

---

## 8) Barcode Scanning

- Handled as keyboard input (USB scanner emulates typing).
- Detect burst typing ending with Enter → lookup by barcode.

---

## 9) Printing Receipts

- Print receipts to connected printer (58mm or 80mm).
- Template includes store name/logo, receipt no, items, totals, and footer message.

---

## 10) Re-order Feature

- Low stock products highlighted.
- Re-order button triggers popup with supplier name, phone, email, and current stock info.
- Admin can contact supplier manually (phone/email).
- Future enhancement: auto-generate purchase orders as PDF.

---

## 11) End-of-Day & Reports

- On shift close, generate EOD report with totals, cash reconciliation, and archive.
- Reports include daily, weekly, monthly, annual, and all-time views.

---

## 12) Security

- Role-based access control (admin vs cashier).
- Passwords stored hashed.
- Database access abstracted through helper functions.

---

## 13) Packaging & Distribution

- Use **PyInstaller** for Windows `.exe` and Linux/macOS builds.
- Bundle SQLite DB and resources with installer.

---

## 14) Milestones

- **M1:** Scaffold project.
- **M2:** Core sales screen (grid/table, cart, barcode, receipt print).
- **M3:** Products with stock, supplier re-order feature.
- **M4:** Reports & settings.
- **M5:** User roles, security, backups, polish.

---

## 15) Future Enhancements

- Stock purchase orders (auto-PDF).
- MPESA/card integration.
- Multi-register sync.
- Promotions/loyalty.
- Multi-language support.

---

### Final Notes

This blueprint provides the full picture of the app with the new **Re-order feature**. All components and workflows are designed for offline use, ensuring reliability and usability in environments without internet access.
