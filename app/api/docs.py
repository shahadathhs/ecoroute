"""
Documentation Routes - RapiDoc
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(
    tags=["Documentation"],
    responses={
        200: {
            "description": "Documentation page",
            "content": {"text/html": {"example": "<!DOCTYPE html>..."}},
        }
    },
)


@router.get(
    "/rapidoc",
    response_class=HTMLResponse,
    summary="RapiDoc Documentation Viewer",
    description="Modern, responsive API documentation viewer with beautiful UI and excellent mobile support. Provides interactive API exploration with a cleaner interface than traditional Swagger UI.",
)
async def rapidoc() -> str:
    """
    RapiDoc Documentation Viewer

    Returns the RapiDoc interface - a modern, responsive alternative to Swagger UI.

    **Features:**
    - Beautiful, modern UI with dark theme
    - Excellent mobile responsiveness
    - Interactive API exploration
    - Try-it-out functionality
    - Better search and filtering
    - Schema visualization

    **Access:** Visit /rapidoc in your browser to view the documentation.
    """
    return """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>EcoRoute Atlas - API Documentation</title>
        <script type="module" src="https://unpkg.com/rapidoc@9.3.3/dist/rapidoc-min.js"></script>
        <style>
          body {
            margin: 0;
            padding: 0;
          }
          rapi-doc {
            height: 100vh;
            width: 100%;
          }
        </style>
      </head>
      <body>
        <rapi-doc
          spec-url="/openapi.json"
          theme="dark"
          header-color="#667eea"
          primary-color="#764ba2"
          sort-tags="true"
          sort-endpoints-by="method"
          allow-search="true"
          allow-server-selection="true"
          allow-authentication="true"
          show-header="true"
          show-info="true"
          allow-spec-url-load="true"
          allow-spec-file-load="false"
          render-style="read"
          schema-expand-level="1"
          schema-description-expanded="true"
          default-schema-tab="example"
          nav-item-spacing="compact"
          font-size="large"
          show-components="true">
          <img
            slot="logo"
            src="https://raw.githubusercontent.com/shahadathhs/ecoroute/main/docs/assets/logo.png"
            alt="EcoRoute Atlas"
            style="height: 40px; width: 40px; border-radius: 8px;"
          />
        </rapi-doc>
      </body>
    </html>
    """


@router.get(
    "/docs-hub",
    response_class=HTMLResponse,
    summary="Documentation Hub",
    description="Landing page for choosing your preferred API documentation viewer. Compare RapiDoc, Swagger UI, and ReDoc side by side and choose the one that fits your needs.",
)
async def docs_hub() -> str:
    """
    Documentation Hub - Choose your documentation viewer.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EcoRoute Atlas - Documentation Hub</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                max-width: 1000px;
                width: 100%;
            }

            .header {
                text-align: center;
                color: white;
                margin-bottom: 50px;
            }

            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }

            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }

            .version-badge {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                margin-top: 15px;
                font-size: 0.9em;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
            }

            .card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                cursor: pointer;
                text-decoration: none;
                color: inherit;
                display: block;
            }

            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }

            .card-icon {
                font-size: 3em;
                margin-bottom: 15px;
            }

            .card h3 {
                font-size: 1.5em;
                margin-bottom: 10px;
                color: #667eea;
            }

            .card p {
                color: #666;
                line-height: 1.6;
                margin-bottom: 15px;
            }

            .card .tag {
                display: inline-block;
                background: #f0f0f0;
                padding: 5px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                color: #888;
            }

            .card.featured {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .card.featured h3 {
                color: white;
            }

            .card.featured p {
                color: rgba(255,255,255,0.9);
            }

            .card.featured .tag {
                background: rgba(255,255,255,0.2);
                color: white;
            }

            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2em;
                }
                .grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌍 EcoRoute Atlas</h1>
                <p>API Documentation - Choose Your Viewer</p>
                <div class="version-badge">Version 1.0.0</div>
            </div>

            <div class="grid">
                <a href="/rapidoc" class="card featured">
                    <div class="card-icon">🚀</div>
                    <h3>RapiDoc (Recommended)</h3>
                    <p>Modern, responsive API documentation with beautiful UI and great mobile support.</p>
                    <span class="tag">⭐ Best Experience</span>
                </a>

                <a href="/docs" class="card">
                    <div class="card-icon">📚</div>
                    <h3>Swagger UI</h3>
                    <p>Classic interactive API documentation with try-it-out functionality.</p>
                    <span class="tag">Interactive</span>
                </a>

                <a href="/redoc" class="card">
                    <div class="card-icon">📖</div>
                    <h3>ReDoc</h3>
                    <p>Beautiful, responsive documentation with detailed schemas and examples.</p>
                    <span class="tag">Reference</span>
                </a>
            </div>
        </div>
    </body>
    </html>
    """
