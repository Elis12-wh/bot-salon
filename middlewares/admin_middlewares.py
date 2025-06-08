from aiogram import BaseMiddleware

class AdminCheckMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: set, faq_path: str):
        self.admin_ids = admin_ids
        self.faq_path = faq_path
        super().__init__()

    async def __call__(self, handler, event, data: dict):
        user = data.get("event_from_user")
        if user:
            print("User id ", user.id)
            print("Admin ids ", self.admin_ids)
            print("Is admin ", str(user.id) in self.admin_ids)
            print(type(user.id))
            print(type(self.admin_ids[0]))
            data["is_admin"] = int(user.id) in self.admin_ids
        data["faq_path"] = self.faq_path
        return await handler(event, data)