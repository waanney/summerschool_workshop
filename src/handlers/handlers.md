
# 📂 Folder: handlers

This folder contains **utility classes for handling runtime events** like errors, logging, or other operational concerns.

It currently includes:

* `error_handler.py` → Defines a centralized **ErrorHandler** for logging and managing exceptions.

---

## 📄 File: `error_handler.py`

### ✅ Purpose

* Provides a **centralized exception handling mechanism**.
* Logs errors consistently using a shared logger.
* Returns user-friendly error messages when exceptions occur.

---

## 📌 `class ErrorHandler`

A simple class for handling and logging exceptions.

### Attributes

* `logger` → A logger instance configured via `setup_logger`.

---

### **`__init__(log_file="app.log")`**

* **Purpose:** Initializes the error handler with a log file.
* **Parameters:**

  * `log_file` → Path/name of the log file where errors will be recorded.
* **Behavior:**

  * Calls `setup_logger` from `utils.logger` to get a configured logger.

---

### **`handle_exception(exception: Exception)`**

* **Purpose:** Handles and logs an exception, then returns a generic safe message.
* **Parameters:**

  * `exception` → Any Python `Exception` instance.
* **Returns:**

  * A safe string message like: `"An error occurred: <ExceptionType>. Please try again later."`
* **Behavior:**

  1. Extracts the exception type name.
  2. Logs the error with stack details.
  3. Returns a generic error message for user-facing responses.

---

## ✅ Usage Example

```python
try:
    risky_operation()
except Exception as e:
    handler = ErrorHandler()
    user_message = handler.handle_exception(e)
    print(user_message)
    # Logs the error in app.log
```

---

