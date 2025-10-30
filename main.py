from fastapi import FastAPI
import uvicorn
from app.core.settings import app_settings
from app.api.views.building_views import building_router
from app.api.views.organization_views import organizations_router

app = FastAPI(debug=app_settings.DEBUG, title="Organizations")
app.include_router(building_router, prefix="/buildings")
app.include_router(organizations_router, prefix="/organizations")

if __name__ == "__main__":
    uvicorn.run(app=app)