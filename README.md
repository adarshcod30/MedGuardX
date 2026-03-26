<div align="center">

# 🛡️ MedGuardX
### *Healthcare Data Protection & Context-Aware Masking System*

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-05998b?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

🚀 **Live Deployment**: [med-guard-x.vercel.app](https://med-guard-x.vercel.app/)

</div>

---

## 📖 Overview

MedGuardX is a complete healthcare data protection system designed to fundamentally change how sensitive medical data is ingested, stored, and shared. It functions as an **intelligent data vault** and **context-aware masking engine**, detecting PII/PHI (Personally Identifiable Information / Protected Health Information) and dynamically applying security policies.

### ✨ Key Differentiators
- **Dynamic Context-Aware Masking**: Evaluates the `(Role × Purpose × Patient Consent)` matrix in real-time.
- **Multi-Format Ingestion**: Supports raw text, HL7 messages, PDFs, and scanned images (Tesseract OCR).
- **AI-PII Detection**: Powered by Microsoft Presidio & spaCy with native support for Indian identifiers (Aadhaar/PAN).
- **Indelible Audit Trails**: Chronological tracking of every access attempt for complete accountability.

---

## 📸 Core Capabilities & Showcase

### 1. Intelligent Dashboard
Real-time security telemetry and high-level statistics for your healthcare data ecosystem.
![Dashboard Overview](docs/screenshots/dashboard.png)

### 2. Multi-Format Secure Upload
Supports HL7, PDF, PNG, JPG, and TXT. Tesseract OCR processes images to extract and protect clinical data.
![Upload Screen](docs/screenshots/upload.png)

### 3. Contextual Data Retrieval
Paste a Patient UUID and define your context. Masking is applied instantly based on user roles and patient consent.
![Retrieve Screen](docs/screenshots/retrieve.png)

### 4. Immutable Access Audit
A transparent chain of accountability tracking every denied and permitted access event.
![Audit Screen](docs/screenshots/audit.png)

---

## 📂 Project Structure

```text
.
├── backend
│   ├── app
│   │   ├── auth.py          # JWT & Authentication logic
│   │   ├── database.py      # SQLAlchemy/SQLite session mgmt
│   │   ├── main.py          # FastAPI application entry
│   │   ├── models.py        # Database schema definitions
│   │   ├── routes/          # API endpoint controllers
│   │   └── services/        # PII Detection & Encryption logic
│   ├── medguardx.db         # Local encrypted store
│   └── requirements.txt     # Python dependencies
├── docs
│   └── screenshots/         # UI visual assets
├── frontend
│   ├── public/              # Static assets
│   ├── src
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # Reusable UI components
│   │   └── lib/             # API clients & utilities
│   ├── tailwind.config.ts   # UI Theme configurations
│   └── tsconfig.json        # TypeScript configuration
└── README.md                # Project documentation
```

---

## 🏗️ System Architecture

### High-Level Flow
```mermaid
graph TD
    UI[Frontend: Next.js + Tailwind UI]
    API[Backend: FastAPI Routes]
    Auth[JWT Authentication]
    Ingest[Ingestion Engine: OCR, PDF, HL7]
    PII[Presidio PII Detector + spaCy NLP]
    StorageLayer[AES Encrypted DB Storage]
    Policy[Context-Aware Policy Engine]
    Mask[Presidio Anonymizer Engine]
    Audit[Audit/Access Logger]

    UI -->|1. Upload File| API
    UI -->|2. Request Data \nRole + Purpose| API
    API <--> Auth
    
    subgraph "Upload Flow"
    API --> Ingest
    Ingest --> PII
    PII --> StorageLayer
    end
    
    subgraph "Retrieval Flow"
    API --> StorageLayer
    StorageLayer --> Policy
    Policy --> Mask
    Mask --> Audit
    Audit --> UI
    end
```

### Retrieval Sequence Logic
```mermaid
sequenceDiagram
    participant User
    participant Retrieve Route
    participant DB
    participant Policy Engine
    participant PII Masking Engine
    
    User->>Retrieve Route: POST /retrieve (Patient ID, Role, Purpose, Consent)
    Retrieve Route->>DB: Fetch encrypted records & PII Metadata
    DB-->>Retrieve Route: Decrypted Raw Text & JSON Entities
    Retrieve Route->>Policy Engine: evaluate_policy(Role, Purpose, Consent)
    
    alt Unauthorized Combination
        Policy Engine-->>Retrieve Route: DENY Strategy + Professional Fallback Msg
        Retrieve Route->>DB: Log "ACCESS_DENIED" to Audit
        Retrieve Route-->>User: 403 Forbidden
    else Authorized Combination
        Policy Engine-->>Retrieve Route: ALLOW or PARTIAL_MASK
        Retrieve Route->>PII Masking Engine: mask_text(Record Text, PII Metadata, Strategy)
        PII Masking Engine-->>Retrieve Route: Safe Redacted Text
        Retrieve Route->>DB: Log Access Event to Audit
        Retrieve Route-->>User: 200 OK + Masked Output
    end
```

---

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- `tesseract` binary (`brew install tesseract` on macOS)

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_lg
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Compliance & Standards
MedGuardX is built with a **Privacy-by-Design** philosophy, adhering to global and local healthcare regulations:
- ✅ **DPDP Act (India)**: Native PII/PHI detection for Aadhaar/PAN cards.
- ✅ **GDPR**: Implements data minimization and purpose-based access.
- ✅ **IT Act 2000**: Robust encryption for data at rest (AES-256).

---

## 📄 License
MedGuardX is licensed under the MIT License. See `LICENSE` for more details.

---
*Built with ❤️ for secure healthcare by Adarsh.*
