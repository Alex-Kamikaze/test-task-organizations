from fastapi import FastAPI, Depends
import uvicorn
from sqlalchemy import event
from app.core.settings import app_settings
from app.api.views.building_views import building_router
from app.api.views.organization_views import organizations_router
from app.api.views.auth_views import auth_router
from app.api.dependencies.auth_dependency import require_bearer_auth
from app.db.models.activity_models import Activity
from app.db.events.activity_indentation_checker import (
    check_activity_indentation_level,
)


if not hasattr(Activity, "_indentation_event_registered"):
    event.listen(Activity, "before_insert", check_activity_indentation_level)
    event.listen(Activity, "before_update", check_activity_indentation_level)
    setattr(Activity, "_indentation_event_registered", True)

app = FastAPI(debug=app_settings.DEBUG, title="Organizations")

app.include_router(auth_router, prefix="/auth")

app.include_router(
    building_router, prefix="/buildings", dependencies=[Depends(require_bearer_auth)]
)
app.include_router(
    organizations_router,
    prefix="/organizations",
    dependencies=[Depends(require_bearer_auth)],
)

if __name__ == "__main__":
    uvicorn.run(app=app, host=app_settings.HOST, port=app_settings.PORT, reload=app_settings.DEBUG)
