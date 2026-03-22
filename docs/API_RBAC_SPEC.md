# EcoRoute Atlas — API & RBAC Specification

This document defines the production-grade API endpoints and the Role-Based Access Control (RBAC) model for the EcoRoute Atlas backend.

---

## 👥 User Roles & Permissions Matrix

The system utilizes a granular RBAC model to ensure data security and operational integrity across the logistics ecosystem.

| Role | Access Scope | Key Responsibilities |
| :--- | :--- | :--- |
| **Super Admin** | Global | Full system management, organization creation, and global auditing. |
| **Company Admin** | Organization | User management, company settings, and asset oversight within a specific tenant. |
| **Logistics Manager** | Operational | High-level shipment tracking, fleet performance monitoring, and reporting. |
| **Compliance Officer** | Regulatory | Hazmat rule enforcement, document audits, and regulatory knowledge ingestion. |
| **Sustainability Lead** | Metrics | CO2 tracking, green route analysis, and ESG reporting. |
| **Standard Dispatcher** | Task-Based | Daily shipment creation, routing updates, and basic vehicle monitoring. |
| **Driver** | Restricted | Viewing assigned shipments, vehicle health checks, and status reporting. |

---

## 🛠️ API Modules & Endpoints

### 1. Identity & Access Management (IAM)
*Handles user lifecycle, authentication, and role-based permissions.*

- **Login / Token Exchange** (`POST /v1/auth/login`): Primary entry point for authentication. Issues secure JWT tokens for subsequent API calls.
- **Token Refresh** (`POST /v1/auth/refresh`): Extends active sessions without requiring re-authentication.
- **User Profile** (`GET /v1/users/me`): Retrieves details, organization context, and permissions for the current user.
- **User Management** (`GET /v1/users`, `POST /v1/users/invite`): Admin-level endpoints for listing and inviting members to an organization.
- **Role Assignment** (`PATCH /v1/users/{id}/role`): Used by admins to manage permissions and functional roles of team members.

### 2. Organization Management
*Manages multi-tenancy and company-wide configurations.*

- **Org Profile** (`GET /v1/orgs/profile`): Details on subscription status, billing, and resource limits.
- **Org Settings** (`PATCH /v1/orgs/settings`): Customizing operational rules, safety thresholds, and reporting defaults.

### 3. Shipment & Logistics Lifecycle
*End-to-end management of cargo movements.*

- **Shipment Search** (`GET /v1/shipments`): Advanced filtering for multi-criteria shipment tracking.
- **Shipment Initialization** (`POST /v1/shipments`): Creates new shipment records and triggers initial compliance checks.
- **Shipment Telemetry** (`GET /v1/shipments/{id}/telemetry`): Historical and real-time GPS/IoT data for a specific transit.
- **Operational Events** (`POST /v1/shipments/{id}/events`): Logging milestones such as customs clearance or delivery completion.
- **Compliance Audit** (`GET /v1/shipments/{id}/compliance`): Direct access to AI-generated legal adherence summaries.

### 4. Fleet & Asset Management
*Tracking physical assets and their operational health.*

- **Fleet Inventory** (`GET /v1/fleet`): Real-time overview of all vehicles and their availability status.
- **Asset Diagnostics** (`GET /v1/fleet/{id}/diagnostics`): Deep-dive into vehicle health metrics (battery, fuel, maintenance needs).
- **Driver Assignment** (`POST /v1/fleet/{id}/assign`): Links specific drivers and shipments to an available asset.

### 5. Atlas AI: Intelligence & Compliance
*The LLM-powered engine for regulatory support.*

- **Regulatory Q&A** (`POST /v1/atlas/ask`): Natural language interface for complex international trade and logistics queries.
- **Document Verification** (`POST /v1/atlas/verify-docs`): AI-driven cross-referencing of shipping documents against global laws.
- **Knowledge Ingestion** (`POST /v1/atlas/ingest`): Updating the system's "Intelligence" with new policy/law documents.

### 6. Sustainability & Green Analytics
*Measuring and optimizing environmental impact.*

- **Emissions Dashboard** (`GET /v1/analytics/emissions`): Aggregated CO2 metrics across the organization's operations.
- **Route Optimization** (`POST /v1/analytics/optimize-route`): Recommends routes based on carbon efficiency vs. time.
- **Sustainability Reporting** (`GET /v1/analytics/reports/sustainability`): Generates compliance reports for environmental standards.

---

## 🔒 Security & Data Scoping

- **JWT-Based RBAC**: Permissions are verified at the server layer using claims embedded within the bearer token.
- **Multi-tenant Isolation**: All data queries are automatically scoped to the user's `organization_id` to ensure strict data privacy between companies.
- **Least Privilege Access**: Drivers and standard users have constrained views, limited only to the data required for their specific assignments.
