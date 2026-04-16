# 🚀 SQL Server RAG Application

SQL Server database se data lekar RAG (Retrieval-Augmented Generation) application banata hai.
Natural language mein sawaal poochho — AI database se jawab dhundh ke dega!

---

## 📁 Project Structure

```
rag_sql_app/
├── main.py              ← Entry point — yahan se run karo
├── db_connector.py      ← SQL Server connection
├── data_processor.py    ← SQL data → Documents
├── vector_store.py      ← ChromaDB embeddings
├── rag_chain.py         ← RAG pipeline (retrieval + generation)
├── text_to_sql.py       ← Text-to-SQL (numerical data ke liye)
├── requirements.txt     ← Python dependencies
├── .env.example         ← Environment variables template
└── README.md
```

---

## ⚙️ Setup

### Step 1: Dependencies install karo
```bash
pip install -r requirements.txt
```

### Step 2: Environment variables set karo
```bash
# .env.example copy karo
cp .env.example .env

# .env file mein apni details bharо:
OPENAI_API_KEY=sk-...
SQL_SERVER=your_server
SQL_DATABASE=your_db
SQL_USERNAME=your_user
SQL_PASSWORD=your_pass
```

### Step 3: main.py mein apni table configure karo
```python
# main.py mein yeh lines edit karo:
TABLE_NAME = "your_actual_table"
TEXT_COLUMNS = ["col1", "col2"]      # Text wale columns
METADATA_COLUMNS = ["id", "date"]    # ID/filter columns
```

---

## ▶️ Run Karo

### Demo Mode (SQL Server ke bina — test ke liye)
```bash
python main.py --demo
```

### Real Mode (SQL Server se)
```bash
python main.py
```

### Text-to-SQL Mode (numerical data ke liye)
```python
from text_to_sql import create_sql_agent_chain, query_with_natural_language

agent = create_sql_agent_chain()
query_with_natural_language(agent, "Last month ki total sales kya thi?")
```

---

## 🔄 Kab Kya Use Karein?

| Data Type | Method | File |
|-----------|--------|------|
| Text, descriptions, comments | Vector RAG | `main.py` |
| Numbers, dates, counts | Text-to-SQL | `text_to_sql.py` |
| Dono | Dono combine karo | Dono files |

---

## 💡 Example Sawaal

```
"Product X ki description kya hai?"
"Customer Rahul ke baare mein kya information hai?"
"Electronics category mein kaunse items hain?"
"Order ORD001 ka status kya hai?"
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| ODBC Driver error | Install: `ODBC Driver 17 for SQL Server` |
| OpenAI key error | `.env` mein sahi key daalo |
| Table not found | `TABLE_NAME` sahi check karo |
| Empty results | `TEXT_COLUMNS` check karo |
