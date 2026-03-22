# EcoRoute Atlas

**EcoRoute Atlas** is a production-grade, AI-driven backend system for global supply chain management, sustainability tracking, and regulatory compliance. Built exclusively with **Python and FastAPI**, it integrates advanced AI (Atlas) to provide proactive decision support, automated regulatory audits, and carbon footprint optimization.

---

## 🌟 Core Modules
- **Identity & Access Management (IAM)**: Advanced RBAC with multi-tenancy support for global logistics organizations.
- **Intelligent Compliance (Atlas AI)**: LLM-powered regulatory assistant using RAG (Retrieval-Augmented Generation) for real-time legal audits.
- **Dynamic Sustainability Tracking**: Automated CO2 footprint calculation based on route telemetry and vehicle health.
- **Fleet & Asset Monitoring**: High-frequency IoT data ingestion for real-time diagnostics and proactive maintenance.

---

## 🏗️ Technical Architecture
The system is designed as a high-performance **FastAPI** application with a focus on asynchronous processing and modularity.

- **Stack**: Python 3.12+, FastAPI, Pydantic (v2), SQLAlchemy/asyncpg.
- **Data Layer**:
  - **PostgreSQL**: Primary store for structured shipments, assets, and user data.
  - **Qdrant**: High-dimensional vector database for Atlas AI's knowledge retrieval.
- **AI/LLM**: Integrates with OpenAI/Anthropic or local models (BGE/E5) for embeddings and inference.

---

## 🚀 API & RBAC Specification
The system implements a detailed Role-Based Access Control model across 7 distinct user roles:
- `Super Admin`, `Company Admin`, `Logistics Manager`, `Compliance Officer`, `Sustainability Lead`, `Standard Dispatcher`, `Driver`.

For the full production-grade endpoint specification, see the [API & RBAC Spec](./docs/API_RBAC_SPEC.md).

---

## 📚 Documentation
- [AI System Architecture (ATLAS.md)](./docs/ATLAS.md)
- [Vector Flow Documentation (ATLAS_INTEL_FLOW.md)](./docs/ATLAS_INTEL_FLOW.md)
- [Production Architecture (ECOROUTE_ARCHITECTURE.md)](./docs/ECOROUTE_ARCHITECTURE.md)
- [Business Requirements (ECOROUTE_BUSINESS_REQUIREMENTS.md)](./docs/ECOROUTE_BUSINESS_REQUIREMENTS.md)
- [Detailed API Specification (API_RBAC_SPEC.md)](./docs/API_RBAC_SPEC.md)

---

## 🛠️ Project Setup (Development)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/shahadathhs/ecoroute.git
    ```
2.  **Environment Setup**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Local Services**: Ensure PostgreSQL and Qdrant are running locally or reachable via network.

---

## 📄 License
MIT License - Copyright (c) 2026 EcoRoute Team
