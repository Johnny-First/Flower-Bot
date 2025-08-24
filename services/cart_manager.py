import json
from ..database.models import UserManager

class CartManager:
    @staticmethod
    async def add_to_cart(user_id: int, new_item: dict):
        await UserManager.to_cart(user_id, {
            'id': new_item['id'],
                'quantity': new_item["quantity"]
        })

    # @staticmethod
    # async def check_cart(user_id: int):
    #     all = await UserManager.get_cart(user_id=user_id)
    #     items, price = all[0], all[1]
    #     return items, price