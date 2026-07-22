"""Single source of truth for the service version.

Consumed by the FastAPI app metadata, GET /api/health, and GET /api/architecture
so the three can never drift apart.
"""

API_VERSION = "1.0.0"