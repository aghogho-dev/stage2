# Intelligence Query Engine - HNG Stage 2

A FastAPI-based backend service that manages a dataset of 2,026 personas. This project supports complex filtering, pagination, and natural language search functionality, deployed on Railway with a PostgreSQL database.

## 🚀 Live Demo
- **API URL**: https://stage2-production-e0cc.up.railway.app/
- **Interactive Documentation**: https://stage2-production-e0cc.up.railway.app/docs

## 🛠️ Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Railway)
- **ORM**: SQLAlchemy (Async)
- **Database Driver**: asyncpg
- **Deployment**: Railway
- **Data Handling**: Pydantic, UUID7

## 📋 Features
- **Comprehensive Filtering**: Filter by gender, age group, country (ISO code), and probability scores.
- **Natural Language Search**: Interprets queries like "young males from Nigeria" or "adult females" into structured database filters.
- **Pagination**: Standardized `page` and `limit` parameters for all endpoints.
- **Robust Error Handling**: Standardized JSON error responses for validation and server failures.
- **CORS Enabled**: Cross-Origin Resource Sharing supported via custom middleware for frontend integration.

## 🔍 Natural Language Mapping
The search endpoint (`/api/profiles/search?q=...`) uses a custom parser to map natural language to specific data ranges:
- **Youth**: 16–24 years old (Age Group: `youth`)
- **Adult**: 25–44 years old (Age Group: `adult`)
- **Senior**: 45–64 years old (Age Group: `senior`)
- **Elderly**: 65+ years old (Age Group: `elderly`)
