from .user_handlers import user_router
from .admin_handlers import admin_router
from .general_hanlders import general_router

__all__ = ["user_router", "admin_router", "general_router"]