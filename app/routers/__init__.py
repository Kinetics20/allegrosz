from app.routers.location import router as location_router
from app.routers.contact import router as contacts_router
from app.routers.products import router as products_router

routers = [contacts_router, products_router, location_router]