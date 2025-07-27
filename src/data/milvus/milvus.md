# 📂 Folder: milvus

This folder contains the logic for **Milvus vector database integration**, handling:

* **Collection management** (create, drop, connect)
* **Dynamic schema generation** based on data
* **Dense & sparse vector indexing** for hybrid search
* **Hybrid search queries with reranking**

It includes two main files:

* **`indexing.py`** → `MilvusIndexer` for dynamically creating collections and indexing FAQ data
* **`milvus_client.py`** → `MilvusClient` for generic indexing & hybrid search functionality

---

## 📄 File: `indexing.py`

### ✅ Purpose

* Dynamically loads FAQ data (CSV/XLSX)
* Creates Milvus collections with **dynamic fields**
* Generates **dense embeddings** for each category using `EmbeddingEngine`
* Inserts data and creates **dense & sparse indexes** for hybrid retrieval

---

## 📌 `class MilvusIndexer`

Handles **data ingestion & indexing** into Milvus.

### Attributes

* `collection_name` → Name of the Milvus collection.
* `faq_file` → Path to the CSV/XLSX file containing FAQ data.
* `file_type` → Detected file type (`csv` or `xlsx`).
* `milvus_client` → Instance of `MilvusClient`.
* `collection` → The Milvus collection reference.

---

### **`connect()`**

* Connects to Milvus server via `MilvusClient._connect()`.

### **`create_collection(data_sample=None)`**

* Creates a Milvus collection **with dynamic schema** based on FAQ data columns.
* Drops existing collection if already present.
* For each category:

  * Creates a **VARCHAR field** for text.
  * Creates **dense (FLOAT\_VECTOR)** and **sparse (SPARSE\_FLOAT\_VECTOR)** embedding fields.
  * Adds a BM25 function for sparse search.

### **`load_faq_data_from_csv()`**

* Loads FAQ data from CSV into a list of dictionaries.

### **`load_faq_data_from_xlsx()`**

* Loads FAQ data from Excel, supports multiple sheet engines (`openpyxl`, `xlrd`, `calamine`).

### **`generate_embeddings(data)`**

* Dynamically generates **dense embeddings** for all FAQ categories.
* Uses `EmbeddingEngine` with MiniLM model.
* Returns `category_texts` and `category_embeddings`.

### **`insert_data(data)`**

* Inserts FAQ data (both text + embeddings) into the collection.
* Flushes collection after insertion.

### **`create_index(categories=None)`**

* Creates indexes for **dense (IVF\_FLAT)** and **sparse (BM25)** embeddings.
* Loads the collection after indexing.

### **`run()`**

* Main pipeline:

  1. Connects to Milvus
  2. Loads FAQ data
  3. Creates collection & indexes
  4. Inserts data

---

## 📄 File: `milvus_client.py`

### ✅ Purpose

* Provides a **generic client** for Milvus operations.
* Ensures connection & collection existence.
* Supports **indexing**, **hybrid search**, and **fallback strategies**.

---

## 📌 `class MilvusClient`

Handles **connection**, **collection management**, and **search queries**.

### Attributes

* `collection_name` → Milvus collection name.
* `collection` → `pymilvus.Collection` object.

---

### **`_connect()`**

* Establishes connection using `MILVUS_URI` & `MILVUS_TOKEN` from env.
* Verifies connection.

### **`_ensure_connection()`**

* Checks if connection is still alive, reconnects if needed.

### **`_ensure_collection_exists()`**

* Creates a default FAQ schema if the collection does not exist:

  * `Question`, `Answer`
  * Dense/sparse embeddings for both fields

---

### **`index_data(Questions, Answers, Question_embeddings, Answer_embeddings, ...)`**

* Inserts **questions, answers, dense embeddings, and optional sparse embeddings** into the collection.
* Calls `create_index()` after insertion.

### **`create_index()`**

* Creates IVF\_FLAT index for **dense embeddings**.
* Supports BM25 indexing for sparse embeddings.

---

### **`hybrid_search(query_text, query_dense_embedding, limit=5, search_answers=False, ranker_weights=None)`**

* Performs **hybrid search** combining:

  * Dense vector search (semantic similarity)
  * Sparse BM25 keyword search
* Uses `WeightedRanker` to rerank results.
* Fallback to **simple vector search** if hybrid search fails.

---

### **`generic_hybrid_search(query_text, query_dense_embedding, limit=10, fields_to_search=None, dense_weight=0.7, sparse_weight=0.3, output_fields=None)`**

* **Multi-field hybrid search**
* Auto-discovers searchable text fields with `_dense_embedding` & `_sparse_embedding`
* Prepares multiple `AnnSearchRequest` for each field
* Uses `WeightedRanker` for scoring & reranking
* Fallback to simple dense search on first available field if hybrid search fails.

---

## 🔄 Typical Flow

1. **Data Indexing** (dynamic)

   ```python
   indexer = MilvusIndexer(collection_name="workshop_faq", faq_file="faq_data.xlsx")
   indexer.run()
   ```

2. **Direct Indexing** (manual)

   ```python
   client = MilvusClient("workshop_faq")
   client.index_data(Questions, Answers, Question_embeddings, Answer_embeddings)
   ```

3. **Hybrid Search**

   ```python
   results = client.hybrid_search(
       query_text="How to apply for the workshop?",
       query_dense_embedding=embedding_engine.get_query_embedding("How to apply for the workshop?"),
       limit=5
   )
   ```

4. **Generic Multi-Field Hybrid Search**

   ```python
   results = client.generic_hybrid_search(
       query_text="scholarship deadline",
       query_dense_embedding=embedding_engine.get_query_embedding("scholarship deadline"),
       limit=10
   )
   ```


