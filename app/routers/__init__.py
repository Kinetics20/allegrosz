from app.routers.location import router as location_router
from app.routers.contact import router as contacts_router
from app.routers.products import router as products_router
from app.routers.inventory import router as inventory_router

routers = [contacts_router, products_router, location_router, inventory_router]