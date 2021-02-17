from typing import List, Dict

# List of order statuses
ORDER_STATUSES: Dict[int, str] = {
    0: 'new',
    1: 'payment_pending',
    2: 'payment_canceled',
    3: 'processing',
    4: 'awaiting_shipment',
    5: 'awaiting_pickup',
    6: 'completed',
    7: 'canceled',
    8: 'refunded'
}


class _BaseModel:
    fields: tuple

    def __init__(self, **kw):
        if not kw:
            return

        [setattr(self, k, kw.get(k)) for k, types in self.fields if any(isinstance(kw.get(k), t) for t in types)]
        undefined = set(kw.keys()) - set(k for k, _ in self.fields)
        if undefined:
            raise TypeError('Fields is not found: ' + ', '.join(undefined))

    def to_json(self):
        return self.__dict__


class Client:
    """
    Client instance is smartbonus app user
    """

    def __init__(self, phone: str, balance: float, name: str):
        self.phone = phone  # phone number of client (unique)
        self.balance = balance  # amount of bonuses in smartbonus account
        self.name = name  # client name (optional)

    def __repr__(self):
        return f'{self.phone}: {self.balance}'


class Nomenclature(_BaseModel):
    """
        Nomenclature instance has to be sync to smartbonus after it created, changed or deleted.
        If you cannot trigger nomenclature events, send it by some interval: once a day for example.
    """

    fields = (
        ('description', (str,)),  # description of product
        ('photo_url', (str,)),  # image of product, if you have more than one image join them by comma
        ('is_deleted', (bool,)),  # send true if you deleted that product
        ('category', (str,)),  # unique identifier of category in your db
        ('barcode', (str,)),  # barcode of your product
        ('price', (float, int)),  # price of your product
        ('is_category', (bool,)),  # send true if current instance is category or false if it's product
        ('tags', (list, tuple)),  # list of tag identifiers
        ('can_buy', (bool,)),  # send true if this product can be buyed in smartbonus app
        ('is_hidden', (bool,))  # send false if you want to show this product in smartbonus app catalog for clients
    )

    def __init__(self, _id: str, name: str, **kw):
        self.id = _id  # unique identifier of product in your db
        self.name = name  # title of product

        super().__init__(**kw)

    def __repr__(self):
        return self.name


class NomenclatureItem(_BaseModel):
    def __init__(self, _id: str, quantity: float, price: float):
        self.nomenclature_id = _id  # your product identifier
        self.amount = quantity  # quantity of product
        self.unit_price = price  # price of product
        super().__init__()


class ReceiptDiscount(_BaseModel):
    """ Body for receipt discount method """

    def __init__(self, user_id: str, items: List[NomenclatureItem], date: int = 0, withdrawn: float = 0):
        self.user_id = user_id  # Phone or scanned key from smartbonus app
        if date:  # Date of receipt
            self.date = date
        if withdrawn:  # Amount of money that cashier want to withdraw from client account
            self.withdrawn = withdrawn

        self.receipt = []
        for item in items:
            if isinstance(item, NomenclatureItem):
                self.receipt.append(item.to_json())
            else:
                raise TypeError(f'Invalid item of items, expected {type(NomenclatureItem)} added {type(item)}')
        if not self.receipt:
            raise TypeError(f'Items is not found')
        super().__init__()

    def __repr__(self):
        return f'{self.user_id}'


class ExecutedModule:
    """ Smartbonus modules that accrued/withdrawn bonuses or added discount """

    def __init__(self, **kw):
        self.id: str = kw.get('id')
        self.type: str = kw.get('type')
        self.accrued: float = kw.get('accrued_bonus')
        self.immediate: float = kw.get('immediate_bonus')
        self.withdrawn: float = kw.get('withdrawn_bonus')
        self.module_type: str = kw.get('module_type')
        self.name: str = kw.get('name')


class AnalyticObject:
    """ List of executed modules """

    def __init__(self, modules: List[ExecutedModule]):
        self.executed_modules = modules


class ReceiptItem:
    """ Item of receipt response """

    def __init__(self, **kw):
        self.id: str = kw.get('id')
        self.accrued: float = kw.get('accrued') or 0
        self.withdrawn: float = kw.get('withdrawn') or 0
        self.immediate: float = kw.get('immediate') or 0
        self.amount: float = kw.get('amount') or 0
        self.unit_price: float = kw.get('unit_price') or 0


class ReceiptResult:
    """ Receipt response of discount and confirm methods """

    def __init__(self, **kw):
        self.discount: float = kw.get('discount') or 0
        self.info: str = kw.get('info')
        self.accrued: float = kw.get('user_add_bonus') or 0
        self.withdrawn: float = kw.get('withdrawn') or 0
        self.immediate: float = kw.get('immediate') or 0
        self.user_name: str = kw.get('user_name')
        self.items: List[ReceiptItem] = [ReceiptItem(**v) for v in kw.get('nomenclatures') or [] if isinstance(v, dict)]
        self.analytics_object: AnalyticObject = AnalyticObject([
            ExecutedModule(**v)
            for v in (kw.get('analytics_object') or {}).get('executed_modules') or [] if isinstance(v, dict)
        ])


class ReceiptConfirm(_BaseModel):
    """ Body for receipt confirmation """

    def __init__(self, _id: str, user_id: str, items: List[NomenclatureItem], discount: float = 0, date: int = 0,
                 change: float = 0):
        self.remote_id = _id
        self.user_id = user_id  # Phone or scanned key from smartbonus app
        if date:  # Date of receipt
            self.date = date
        if discount:  # Amount of discount that received from DiscountReceipt method.
            self.discount = discount
        if change:  # Rest of money that will accrue to smartbonus account
            self.accrued = change

        self.list = []
        for item in items:
            if isinstance(item, NomenclatureItem):
                self.list.append(item.to_json())
            else:
                raise TypeError(f'Invalid item of items, expected {type(NomenclatureItem)} added {type(item)}')
        if not self.list:
            raise TypeError(f'Items is not found')
        super().__init__()

    def __repr__(self):
        return f'{self.user_id}'


class RefundItemResult:
    """
        Item response of refund receipt request
        rest = price * quantity - withdrawn - immediate
    """

    def __init__(self, **kw):
        self.id: str = kw.get('id')  # your product identifier
        self.accrued: float = kw.get('accrued') or 0  # amount of accrued bonuses
        self.withdrawn: float = kw.get('withdrawn') or 0  # amount of withdrawn bonuses
        self.immediate: float = kw.get('immediate') or 0  # amount of immediate discount


class RefundItem(_BaseModel):
    """ Item of receipt refund request """

    def __init__(self, _id: str, quantity: float):
        """
        :param _id: your product identifier
        :param quantity: quantity of product
        """
        self.nomenclature_id = _id
        self.amount = quantity
        super().__init__()


class ReceiptRefund(_BaseModel):
    """ Receipt refund request body """

    def __init__(self, _id: str, receipt_id: str, items: List[RefundItem]):
        """
        :param _id: identifier of your refund receipt
        :param receipt_id: identifier of your sell receipt
        :param items: list of refund products
        """
        self.refund_id = _id
        self.remote_id = receipt_id
        self.list = [item.to_json() for item in items]
        super().__init__()


class Tag(_BaseModel):
    """ Tag is smartbonus filter, used in smartbonus app catalog """

    def __init__(self, _id: str, name: str, group_id: str = None, is_group: bool = False):
        self.id = _id
        self.name = name
        self.group_id = group_id
        self.is_group = is_group
        super().__init__()


class OrderProduct:
    """ OrderProduct instance - element of products in Order """

    def __init__(self, **kw):
        self.id: str = kw.get('id')  # your nomenclature identifier
        self.price: float = kw.get('amount')  # price of product
        self.quantity: float = kw.get('quantity')  # quantity of product


class OrderStatus:
    """ OrderStatus instance - element of statuses in Order """

    def __init__(self, **kw):
        self.date: int = kw.get('date_unix')  # date of status creation
        self.status: int = kw.get('status')  # one of OrderStatuses


class Order:
    """ Order instance - send new order that created in smartbonus to your api after webhook is configured """

    def __init__(self, **kw):
        self.store: str = kw.get('store')  # your StoreId token that configured
        self.id: str = kw.get('remote_id')  # unique identifier of order in smartbonus
        self.code: str = kw.get('code')  # number of order for client
        self.user_id: str = kw.get('user_id')  # client identifier that has to be used to sync receipt
        self.phone: str = kw.get('phone')  # phone number of client
        self.user_name: str = kw.get('user_name')  # name of client
        self.amount: float = kw.get('amount')  # amount for pay
        self.currency: str = kw.get('currency')  # ISO 4217: UAH, USD, EUR
        self.date: int = kw.get('date_unix')  # date of order
        self.is_paid: bool = kw.get('is_paid')  # order paid online by client
        self.products_amount: float = kw.get('products_amount')  # amount of products
        self.delivery_cost: float = kw.get('delivery_cost')  # cost of delivery
        self.discount: float = kw.get('discount')  # amount of discount
        self.products: List[OrderProduct] = [OrderProduct(**v) for v in kw.get('products') or []]
        self.statuses: List[OrderStatus] = [OrderStatus(**v) for v in kw.get('statuses') or []]
        self.comment: str = kw.get('comment')  # client comment
        self.delivery_type: str = kw.get('delivery')  # type of delivery
        self.delivery_address: str = kw.get('deliveryAddress')
        self.delivery_time: str = kw.get('deliveryTime')


class StatusBody(_BaseModel):
    """ Body of status """

    def __init__(self, order_id: str, status: int):
        """
        :param order_id: identifier of order in smartbonus
        :param status: one of OrderStatuses
        """
        self.order_id = order_id
        self.status = status
        super().__init__()
