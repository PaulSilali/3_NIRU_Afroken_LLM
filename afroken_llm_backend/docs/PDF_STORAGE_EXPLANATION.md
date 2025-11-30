# PDF Upload Storage: Folders vs MinIO

## 📁 Where PDFs Go When Uploaded

When you upload a PDF through the admin panel, here's the complete flow:

### 1. **Temporary Storage** (Initial Upload)
- **Location**: `afroken_llm_backend/data/temp/`
- **Format**: `{uuid}_{original_filename}.pdf`
- **Purpose**: Temporary storage while processing
- **Example**: `a1b2c3d4-5678-90ab-cdef-1234567890ab_handbook.pdf`

### 2. **Permanent Storage** (After Processing)

The system uses **TWO storage methods**:

#### A. **Local Folder Storage** (Always Used)
- **Location**: `afroken_llm_backend/data/pdfs/`
- **Format**: Original PDF filename
- **Status**: ✅ **Always saved here**
- **Example**: `afroken_llm_backend/data/pdfs/NPS_And_KPS_HandBook.pdf`

#### B. **MinIO Object Storage** (Optional)
- **Bucket**: `documents`
- **Path**: `pdfs/{original_filename}`
- **Status**: ⚠️ **Only if MinIO is configured**
- **Requires**: Environment variables set:
  ```bash
  MINIO_ENDPOINT=localhost:9000
  MINIO_ACCESS_KEY=minioadmin
  MINIO_SECRET_KEY=minioadmin
  MINIO_SECURE=false
  ```

### 3. **Processed Content Storage**

#### Markdown Conversion
- **Location**: `afroken_llm_backend/data/docs/`
- **Format**: `{filename}.md` (converted from PDF)
- **Purpose**: Text content extracted and formatted for RAG

#### Database Storage
- **PostgreSQL**: Document metadata, text content (truncated), and embeddings
- **Purpose**: Vector search and retrieval

---

## 🔄 Complete Upload Flow

```
1. User uploads PDF
   ↓
2. PDF saved to: data/temp/{uuid}_{filename}.pdf
   ↓
3. Background processing starts:
   ├─ Extract text from PDF
   ├─ Convert to Markdown → data/docs/{filename}.md
   ├─ Upload to MinIO (if configured) → documents/pdfs/{filename}
   ├─ Store in PostgreSQL with embedding
   └─ Original PDF kept in: data/pdfs/{filename}
   ↓
4. Temporary file can be cleaned up
```

---

## 📊 Folder Storage vs MinIO: Key Differences

### **Local Folder Storage** (`data/pdfs/`)

#### ✅ Advantages:
- **Simple**: No setup required, works immediately
- **Fast**: Direct file system access
- **No Dependencies**: Works without external services
- **Easy Debugging**: Files visible in file explorer
- **Free**: No additional infrastructure costs

#### ❌ Disadvantages:
- **Not Scalable**: Limited by server disk space
- **No Redundancy**: Single point of failure
- **No Access Control**: Files accessible to anyone with server access
- **Backup Required**: Manual backup needed
- **Not Cloud-Ready**: Hard to distribute across servers

#### **Best For:**
- Development/testing
- Small deployments
- Single-server setups
- When simplicity is priority

---

### **MinIO Object Storage**

#### ✅ Advantages:
- **Scalable**: Handles large amounts of data
- **S3-Compatible**: Works with AWS S3, DigitalOcean Spaces, etc.
- **Distributed**: Can run across multiple servers
- **Access Control**: Built-in authentication and permissions
- **Versioning**: Can track file versions
- **Cloud-Ready**: Easy to migrate to cloud storage
- **Production-Ready**: Industry standard for object storage

#### ❌ Disadvantages:
- **Setup Required**: Need to install and configure MinIO
- **Additional Service**: Another service to manage
- **Network Dependency**: Requires network access
- **Learning Curve**: Need to understand buckets and objects

#### **Best For:**
- Production deployments
- Multi-server environments
- Large-scale applications
- When you need redundancy and scalability
- Cloud deployments

---

## 🔧 Current Implementation

### How It Works Now:

```python
# From admin.py - process_pdf_background()

# 1. Always saves to local folder
temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"

# 2. Tries to upload to MinIO (if configured)
if os.getenv("MINIO_ENDPOINT"):
    minio_path = upload_bytes(
        "documents",
        f"pdfs/{filename}",
        file_data,
        content_type="application/pdf"
    )

# 3. Always creates markdown in data/docs/
md_filename = create_markdown_from_pdf(...)

# 4. Stores in database
doc = Document(
    source_url=minio_path or str(file_path),  # Uses MinIO path if available
    ...
)
```

### Current Behavior:
- ✅ **Local folder storage**: Always works
- ⚠️ **MinIO storage**: Only if `MINIO_ENDPOINT` is set
- ✅ **Both can work together**: System uses MinIO if available, falls back to local path

---

## 🚀 When to Use Each

### Use **Folder Storage** When:
- Developing locally
- Testing the application
- Small-scale deployment (< 1000 PDFs)
- Single server setup
- Budget constraints (no additional infrastructure)

### Use **MinIO** When:
- Production deployment
- Multiple servers/instances
- Need redundancy and backup
- Planning to scale
- Want cloud storage compatibility
- Need access control and security

### Use **Both** When:
- Want redundancy (local + cloud backup)
- Gradual migration path
- Development + production environments

---

## 📝 Configuration

### To Enable MinIO:

1. **Install MinIO** (or use cloud S3):
   ```bash
   # Local MinIO
   docker run -p 9000:9000 -p 9001:9001 \
     -e "MINIO_ROOT_USER=minioadmin" \
     -e "MINIO_ROOT_PASSWORD=minioadmin" \
     minio/minio server /data --console-address ":9001"
   ```

2. **Set Environment Variables**:
   ```bash
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_SECURE=false
   ```

3. **Restart Backend**: The system will automatically start using MinIO

### To Use Only Folder Storage:
- Simply **don't set** `MINIO_ENDPOINT` environment variable
- System will work perfectly with just local folder storage

---

## 🎯 Summary

| Feature | Folder Storage | MinIO |
|---------|---------------|-------|
| **Setup** | None | Requires installation |
| **Scalability** | Limited | High |
| **Redundancy** | None | Built-in |
| **Access Control** | File system | Built-in |
| **Cloud Ready** | No | Yes |
| **Cost** | Free | Free (self-hosted) |
| **Best For** | Dev/Testing | Production |

**Current System**: Supports both! Uses MinIO if configured, otherwise uses folder storage seamlessly.

