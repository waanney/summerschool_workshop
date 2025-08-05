#  Folder: embeddings

This folder provides functionality for **text embedding generation and management** using pre-trained **Sentence-Transformers** models. It supports:

* **Batch text embedding**
* **Single query embedding** (for search and retrieval)
* **Model state and metadata management**

---

##  File: `embedding_engine.py`

###  Purpose

This module wraps **Sentence-Transformers** models to generate embeddings for text. It allows you to:

* Use different pre-trained embedding models (via `EmbeddingModel` enum)
* Generate embeddings for a **list of texts** or a **single query**
* Handle errors gracefully with logging
* Retrieve **metadata** about the loaded model

---

##  Enumerations

### `EmbeddingModel`

Defines supported embedding models:

* `MINI_LM_L6_V2` → `"all-MiniLM-L6-v2"` (lightweight, fast)
* `MULTILINGUAL_MINI_LM_L12_V2` → `"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"` (multilingual support)

### `EmbeddingStatus`

Defines status labels for embedding operations:

* `SUCCESS` → Embedding generated successfully
* `FAILED` → General failure
* `EMPTY_TEXT` → Invalid or empty input
* `MODEL_ERROR` → Model initialization or runtime error

---

##  `class EmbeddingEngine`

The main class that manages embedding generation using **Sentence-Transformers**.

### Attributes

* **`model`** → The loaded `SentenceTransformer` instance.
* **`model_name`** → The name of the model being used.
* **`corpus`** → List of corpus texts (optional for future use).
* **`corpus_embeddings`** → Precomputed embeddings for corpus texts (optional).
* **`save_path`** → Path for saving/loading embedding state (default: `embedding_state.json`).

---

### **`__init__(model_name=EmbeddingModel.MINI_LM_L6_V2, save_path="embedding_state.json")`**

* **Purpose:** Initializes the embedding engine by loading the specified Sentence-Transformer model.
* **Parameters:**

  * `model_name` → Model Enum specifying which pre-trained model to load.
  * `save_path` → Path for saving/loading embedding state.
* **Behavior:**

  * Loads the specified model.
  * Initializes corpus and embeddings attributes.
  * Logs the model initialization.
* **Raises:**

  * `ValueError` if an invalid model is provided.
  * `Exception` if model loading fails.

---

### **`get_embeddings(texts: List[str]) -> List[List[float]]`**

* **Purpose:** Generates embeddings for a **list of texts**.
* **Parameters:**

  * `texts` → List of text strings.
* **Returns:**

  * A list of embeddings (one embedding per valid text).
* **Behavior:**

  * Skips invalid or empty strings.
  * Uses `_generate_embedding()` internally for each text.
  * Logs warnings for invalid inputs or failed embeddings.
* **Raises:**

  * `ValueError` if the list is empty or invalid.

---

### **`get_query_embedding(query: str) -> List[float]`**

* **Purpose:** Generates an embedding for a **single query** (typically for search or retrieval).
* **Parameters:**

  * `query` → A single string query.
* **Returns:**

  * A single embedding vector as a list of floats.
* **Behavior:**

  * Skips empty or invalid queries.
  * Calls `_generate_embedding()` internally.

---

### **`_generate_embedding(text: str) -> List[float]`**

* **Purpose:** Core embedding generation logic using Sentence-Transformers.
* **Parameters:**

  * `text` → A single text string.
* **Returns:**

  * Embedding vector (`List[float]`) or an empty list if an error occurs.
* **Behavior:**

  * Calls `self.model.encode(text)`.
  * Converts NumPy array output to a Python list for JSON serializability.
  * Logs debug info if successful, otherwise logs the error.

---

### **`get_model_info() -> dict[str, str | int]`**

* **Purpose:** Retrieves metadata about the loaded model.
* **Returns:**

  ```python
  {
      "model_name": <str>,
      "embedding_dimension": <int>,
      "save_path": <str>
  }
  ```

  * `embedding_dimension` is derived by generating a dummy embedding for the text `"test"`.

---

##  Typical Usage Flow

1. **Initialize the engine**

   ```python
   from embeddings.embedding_engine import EmbeddingEngine, EmbeddingModel

   engine = EmbeddingEngine(EmbeddingModel.MINI_LM_L6_V2)
   ```

2. **Generate a single query embedding**

   ```python
   embedding = engine.get_query_embedding("What is AI?")
   ```

3. **Generate batch embeddings**

   ```python
   batch_embeddings = engine.get_embeddings([
       "Artificial Intelligence",
       "Machine Learning",
       "Deep Learning"
   ])
   ```

4. **Retrieve model info**

   ```python
   info = engine.get_model_info()
   print(info)
   # Example:
   # {'model_name': 'all-MiniLM-L6-v2', 'embedding_dimension': 384, 'save_path': 'embedding_state.json'}
   ```


