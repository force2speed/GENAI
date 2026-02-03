# BigQuery Setup Instructions

You're currently in the BigQuery console. Follow these steps:

## Create Dataset

1. **Look at the left sidebar** (Explorer panel)
2. **Find your project**: `genai-486310`
3. **Click the three dots (⋮)** next to your project name
4. **Click "Create dataset"**

5. **Fill in the form:**
   - **Dataset ID:** `misinfo_logs`
   - **Data location:** Select `US (multiple regions in United States)`
   - **Default table expiration:** Leave as "Never"
   - **Encryption:** Google-managed encryption key (default)

6. **Click "CREATE DATASET"**

---

## Create Table

After the dataset is created:

1. **Click on the `misinfo_logs` dataset** in the Explorer
2. **Click the three dots (⋮)** next to `misinfo_logs`
3. **Click "Create table"**

4. **Fill in the form:**
   - **Source:** 
     - Select "Empty table"
   
   - **Destination:**
     - Project: `genai-486310` (auto-filled)
     - Dataset: `misinfo_logs` (auto-filled)
     - Table: `analysis`
     - Table type: Native table
   
   - **Schema:** Click "+ ADD FIELD" for each field below:

   | Field name | Type | Mode | Description (optional) |
   |------------|------|------|------------------------|
   | timestamp | TIMESTAMP | NULLABLE | When the analysis was performed |
   | type | STRING | NULLABLE | Type of content (document/image/audio/video) |
   | file | STRING | NULLABLE | Filename of analyzed content |
   | verdict | STRING | NULLABLE | Analysis verdict |
   | text | STRING | NULLABLE | Extracted text content |
   | id | STRING | NULLABLE | Unique identifier |

5. **Click "CREATE TABLE"**

---

## Verify Creation

After creating the table, you should see:
- ✅ Dataset: `genai-486310.misinfo_logs`
- ✅ Table: `genai-486310.misinfo_logs.analysis`
- ✅ Schema showing 6 fields

You can test it by running this query:

```sql
SELECT * FROM `genai-486310.misinfo_logs.analysis` LIMIT 10;
```

It should return "This statement returned successfully with 0 rows" since the table is empty.

---

## Update Your Code

After creating the BigQuery resources, update your `bigquery.js` file to use the correct project ID:

Current project ID in your files: `genai-486310` ✓ (This is correct!)

No code changes needed - your project ID is already correct!

---

## Next Steps

Once BigQuery is set up:
1. ✅ Check off items 4.4-4.11 in SETUP_CHECKLIST.md
2. Continue with Phase 5 (Gemini API Setup)
3. Then configure your environment variables
