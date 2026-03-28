# Data Pipeline - Maju Jaya

Project ini merupakan implementasi sederhana end-to-end data pipeline mulai dari ingestion, transformasi, hingga analisis menggunakan MySQL, dbt, dan Prefect.

---

## 📌 Overview

Pipeline ini dibuat untuk mengolah data:
- Customer
- Sales
- After Sales

Data awal berasal dari file CSV dan kemudian diproses menjadi bentuk data warehouse sederhana dengan pendekatan dimensional (fact & dimension table).

---

## ⚙️ Tech Stack

- **MySQL** → sebagai data warehouse
- **dbt** → untuk transformasi data
- **Prefect** → untuk orchestration
- **Docker Compose** → untuk environment setup
- **Python (SQLAlchemy)** → untuk ingestion

---

## 📂 Struktur Pipeline

### 1. Ingestion Layer
- Data dari CSV di-load ke MySQL
- Menggunakan `LOAD DATA INFILE` untuk performa yang lebih cepat
- File di-mount ke dalam container MySQL

---

### 2. Staging Layer
- Data raw disimpan di tabel:
  - `customers_raw`
  - `sales_raw`
  - `after_sales_raw`
  - `customer_address_raw`

---

### 3. Transformation Layer (dbt)

Menggunakan dbt untuk membentuk model:

#### Dimension Table
- `dim_users`

#### Fact Table
- `fact_sales`

Fitur yang digunakan:
- Incremental load (`updated_at`)
- Deduplikasi dengan window function (`rank()`)

---

### 4. Data Warehouse
Semua data hasil transformasi disimpan di database dwh_maju_jaya


### 5. Analytics Layer

Beberapa query analisis yang dibuat:

- Top customer berdasarkan total spending
- Customer lifecycle (pembelian vs service)
- Sales per bulan

---

### 6. Orchestration

- Menggunakan Prefect untuk:
  - Menjalankan ingestion
  - Menjalankan dbt
  - Monitoring pipeline

---

## 🚀 Cara Menjalankan

### 1. Jalankan Docker

```bash
docker-compose up -d ```


