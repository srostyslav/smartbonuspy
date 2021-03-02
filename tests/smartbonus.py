from smartbonus import set_root_path, SmartBonus, Client, Nomenclature, ReceiptDiscount, NomenclatureItem, \
    ReceiptResult, ReceiptConfirm, ReceiptRefund, RefundItem, Tag, StatusBody
from datetime import datetime
import unittest
import uuid
import os


class TestSmartBonus(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        path = os.getenv('SB_ROUTE')
        self.assertTrue(path, 'env variable "SB_ROUTE" is missing')
        set_root_path(path)

        store = os.getenv('SB_STORE')
        self.assertTrue(store, 'env variable "SB_STORE" is missing')
        self.sb = SmartBonus(store)

        self.user_id = os.getenv('SB_USER_ID')
        self.assertTrue(self.user_id, 'env variable "SB_USER_ID" is missing')

        super().__init__(*args, **kwargs)

    def test_client(self):
        # self.assertRaises(ValueError, self.sb.get_client, 'incorrect key')

        client = self.sb.get_client(self.user_id)
        self.assertIsInstance(client, Client, 'Your env variable "SB_USER_ID" is incorrect')

    def test_nomenclatures(self):
        nomes = [
            Nomenclature('1', 'Shirts', is_category=True),
            Nomenclature('2', 'Yellow shirt', description='Best quality', tags=['3', '7'],  # List of tags
                         photo_url='https://yoursite.com/products/yellow-shift.png', category='1',  # Category reference
                         price=699.99),
            Nomenclature('3', 'Blue shirt',
                         tags=['3', '6'],  # List of tags
                         photo_url='https://yoursite.com/products/blue-shift-back.png,'
                                   'https://yoursite.com/products/blue-shift-front.png',
                         category='1',  # Category reference
                         price=699.99),
            Nomenclature('4', 'black hat', can_buy=True, is_hidden=False),
        ]

        self.assertEqual(self.sb.sync_nomenclatures(nomes), 'Sync success')

    def test_discount_receipt(self):
        receipt = ReceiptDiscount(self.user_id, items=[
            NomenclatureItem('1', 10, 89.65),
            NomenclatureItem('3', 0.245, 23.9),
        ], date=int(datetime.now().timestamp()))

        result = self.sb.discount_receipt(receipt)
        self.assertIsInstance(result, ReceiptResult)

    def test_confirm_receipt(self):
        # If client pay 900 change 2.36 you can accrued to smartbonus account
        receipt = ReceiptConfirm(str(uuid.uuid4()), self.user_id, [
            NomenclatureItem('1', 10, 89.65),
            NomenclatureItem('3', 0.245, 23.9),
        ], change=2.36)

        result = self.sb.confirm_receipt(receipt)
        self.assertIsInstance(result, ReceiptResult)

        receipt = ReceiptConfirm(str(uuid.uuid4()), self.user_id, [
            NomenclatureItem('1', 10, 89.65),
            NomenclatureItem('3', 0.245, 23.9),
        ], discount=24)  # amount of discount received from DiscountReceipt method.

        result = self.sb.confirm_receipt(receipt)
        self.assertIsInstance(result, ReceiptResult)

    def test_delete_receipts(self):
        receipt = ReceiptConfirm(str(uuid.uuid4()), self.user_id, [
            NomenclatureItem('1', 10, 89.65),
            NomenclatureItem('3', 0.245, 23.9),
        ])

        result = self.sb.confirm_receipt(receipt)
        self.assertIsInstance(result, ReceiptResult)

        self.assertEqual(self.sb.delete_receipts([receipt.remote_id]), 'Delete success')
        resp = self.sb.delete_receipts([receipt.remote_id])
        self.assertIn('Delete success', resp)

    def test_refund_receipt(self):
        receipt = ReceiptConfirm(str(uuid.uuid4()), self.user_id, [
            NomenclatureItem('1', 10, 89.65),
            NomenclatureItem('3', 0.245, 23.9),
        ])

        result = self.sb.confirm_receipt(receipt)
        self.assertIsInstance(result, ReceiptResult)

        refund = ReceiptRefund(str(uuid.uuid4()), receipt.remote_id, [RefundItem('1', 8)])
        result = self.sb.refund_receipt(refund)
        self.assertIsInstance(result, list)

    def test_sync_receipts(self):
        receipts = [
            ReceiptConfirm(str(uuid.uuid4()), self.user_id, [
                NomenclatureItem('1', 10, 89.65),
                NomenclatureItem('3', 0.245, 23.9),
            ]),
            ReceiptConfirm(str(uuid.uuid4()), self.user_id, [
                NomenclatureItem('1', 10, 89.65),
                NomenclatureItem('3', 0.245, 23.9),
            ], discount=24),
        ]

        self.assertTrue(self.sb.sync_receipts(receipts), 'Sync success')

    def test_sync_tags(self):
        tags = [
            Tag('1', 'Size', is_group=True),
            Tag('2', 'M', '1'),
            Tag('3', 'S', '1'),
            Tag('5', 'Red', '4'),
            Tag('4', 'Color', is_group=True),
            Tag('6', 'Blue', '4'),
            Tag('7', 'Yellow', '4')
        ]

        self.assertEqual(self.sb.sync_tags(tags), 'Sync success')

    def test_config_order(self):
        order_url, status_url = 'https://domain:port/api/order', 'https://domain:port/api/status'
        resp = self.sb.config_order(order_url, status_url, 'really strong token of your store')
        self.assertIsNone(resp)

    def test_change_order_status(self):
        status = StatusBody('fce887b6-b307-cc0f-309d-933db16e406b', 3)
        resp = self.sb.change_order_status(status)
        self.assertIsNone(resp)

        self.assertRaises(Exception, self.sb.change_order_status, status.order_id, 12)
        self.assertRaises(Exception, self.sb.change_order_status, status.order_id + '1', 3)


if __name__ == '__main__':
    unittest.main()
