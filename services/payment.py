
class PaymentService():
    def __init__(self):
        self.amount = 11

    def create_paylink(self):
        link = (f"https://yoomoney.ru/quickpay/shop-widget"
                "?writer=seller"
                "&targets=Flowers"
                "&default-sum=11"
                "&button-text=11"
                "&payment-type-choice=on"
                "&successURL=https://web.telegram.org/a/#8089817622"
                "&account=4100118022895931")
        return link
ps = PaymentService()
print(ps.create_paylink())