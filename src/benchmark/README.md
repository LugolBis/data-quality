# 📊 Yago Data Acquisition & Setup

The scripts in this project rely on the **YAGO3** knowledge base, specifically the date facts dataset. Due to its large size, the raw data is not included in this repository and must be downloaded before running the scripts.

## 🗃️ Data Source Details
* **Source:** [YAGO Knowledge Base](https://yago-knowledge.org/)
* **Archive URL:** `https://yago-knowledge.org/data/yago3/yago-3.0.2-native.7z`
* **Target File Used:** `yagoDateFacts.tsv`

---

## 💻 Automated Download Script

You can use the following bash script to automatically download and extract the required dataset.
> [!WARNING]
> **⚠️ Attention:** This process involves a **10GB** download. Please ensure you have sufficient disk space and a stable network connection before proceeding.

### Bash Script (`download_data.sh`)
*Requirements: `wget` and `p7zip` (`7z`) must be installed on your system.*

```bash
#!/bin/bash

URL="[https://yago-knowledge.org/data/yago3/yago-3.0.2-native.7z](https://yago-knowledge.org/data/yago3/yago-3.0.2-native.7z)"
ARCHIVE_NAME="yago-3.0.2-native.7z"
TARGET_FILE="yagoDateFacts.tsv"

echo "📥 Downloading YAGO3 data (this may take a while depending on your connection)..."
wget -O "$ARCHIVE_NAME" "$URL"

echo "📦 Extracting $TARGET_FILE from the archive..."
# Extracts only the specific target file, ignoring the full folder structure (-r searches recursively)
7z e "$ARCHIVE_NAME" "*$TARGET_FILE" -r

echo "🧹 Cleaning up the archive..."
rm "$ARCHIVE_NAME"

echo "✅ Done! $TARGET_FILE is ready to use."
```

---

## 🧹 Data Processing & Transformation

Once the raw `yagoDateFacts.tsv` file is downloaded, it must be processed. We provide a Python script (`yago_data_sampler.py`) that samples, cleans, and artificially injects noise into the dataset for testing purposes.

**Specifically, the script performs the following operations:**
1. **Truncation:** Limits the output to the first 50,000 records.
2. **Data Cleaning:** Removes YAGO type identifiers (e.g., stripping values after `^^`) and clears surrounding quotation marks.
3. **Anomaly Injection:** Introduces a 1% probability of altering the date field (column 5) to `"3000-01-01"`, creating an ideal dataset for testing data validation and error-handling pipelines.

### Usage

Ensure that `yagoDateFacts.tsv` is in your working directory, then run the following command:

```bash
python3 yago_data_sampler.py
```

---
---

# 📊 Northwind Data Acquisition & Setup

The scripts in this project rely on the **Northwind** knowledge base, specifically focusing on orders, products, and customers. Because this requires a live graph environment, the raw data is not included in this repository and must be loaded directly into your Neo4j instance.

---

## 🗄️ Database Population (Cypher)

Run the following streamlined Cypher queries sequentially in your Neo4j Browser to fully populate the Northwind graph:

```cypher
CREATE INDEX FOR (p:Product) ON (p.productID);
CREATE INDEX FOR (c:Category) ON (c.categoryID);
CREATE INDEX FOR (s:Supplier) ON (s.supplierID);
CREATE INDEX FOR (cu:Customer) ON (cu.customerID);
CREATE INDEX FOR (o:Order) ON (o.orderID);

LOAD CSV WITH HEADERS FROM "[https://data.neo4j.com/northwind/products.csv](https://data.neo4j.com/northwind/products.csv)" AS row
CREATE (n:Product) 
SET n = row, 
    n.unitPrice = toFloat(row.unitPrice), 
    n.unitsInStock = toInteger(row.unitsInStock), 
    n.unitsOnOrder = toInteger(row.unitsOnOrder), 
    n.reorderLevel = toInteger(row.reorderLevel), 
    n.discontinued = (row.discontinued <> "0");

LOAD CSV WITH HEADERS FROM "[https://data.neo4j.com/northwind/categories.csv](https://data.neo4j.com/northwind/categories.csv)" AS row CREATE (n:Category) SET n = row;
LOAD CSV WITH HEADERS FROM "[https://data.neo4j.com/northwind/suppliers.csv](https://data.neo4j.com/northwind/suppliers.csv)" AS row CREATE (n:Supplier) SET n = row;
LOAD CSV WITH HEADERS FROM "[https://data.neo4j.com/northwind/customers.csv](https://data.neo4j.com/northwind/customers.csv)" AS row CREATE (n:Customer) SET n = row;
LOAD CSV WITH HEADERS FROM "[https://data.neo4j.com/northwind/orders.csv](https://data.neo4j.com/northwind/orders.csv)" AS row CREATE (n:Order) SET n = row;

MATCH (p:Product),(c:Category) WHERE p.categoryID = c.categoryID CREATE (p)-[:PART_OF]->(c);
MATCH (p:Product),(s:Supplier) WHERE p.supplierID = s.supplierID CREATE (s)-[:SUPPLIES]->(p);
MATCH (cu:Customer),(o:Order) WHERE cu.customerID = o.customerID CREATE (cu)-[:PURCHASED]->(o);

LOAD CSV WITH HEADERS FROM "[https://data.neo4j.com/northwind/order-details.csv](https://data.neo4j.com/northwind/order-details.csv)" AS row
MATCH (p:Product), (o:Order) 
WHERE p.productID = row.productID AND o.orderID = row.orderID
CREATE (o)-[details:ORDERS]->(p) 
SET details = row, 
    details.quantity = toInteger(row.quantity), 
    details.unitPrice = toFloat(row.unitPrice), 
    details.discount = toFloat(row.discount);
```

---

## 🐒 Data Chaos Monkey (Testing)

Once your Neo4j database is populated, you can run the Chaos Monkey script to simulate data anomalies and test your graph's resilience.

### Usage

Ensure you have a `.env` file configured in your working directory with your Neo4j credentials (`URI`, `DB_USER`, `DB_PW`, `DB_NAME`). Then, execute the script:

```bash
python3 data_chaos_monkey.py
```