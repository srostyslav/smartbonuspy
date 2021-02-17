import requests
from .utils import catch_error
from .models import Client, Nomenclature, ReceiptDiscount, ReceiptResult, ReceiptConfirm, RefundItemResult, \
    ReceiptRefund, Tag, StatusBody, ORDER_STATUSES
from typing import List


class SmartBonus:
    root_path: str = ''

    def __init__(self, store: str):
        self.store = store

    @catch_error
    def get_client(self, user_id: str, **_) -> (Client, bool):
        """
        :param user_id: phone or scanned key from smartbonus app
        :return: If client exists in smartbonus app return its instance
        """

        return self._send_get('user/phone', Client, **self._get_params(user_id=user_id))

    @catch_error
    def sync_nomenclatures(self, nomes: List[Nomenclature], **_) -> (str, bool):
        """
        Sync your catalog to smartbonus app
        warning: ensure that count of elements has to be less than or equal 500 in a request
        :param nomes: list of nomenclatures
        :return: object, bool
        """

        if not isinstance(nomes, list) or not nomes:
            raise ValueError('Nomes must be list of nomenclatures')
        if len(nomes) > 500:
            raise ValueError('Length of nomenclatures must be less or equal than 500 elements')

        response = self._send_post('sync/nomenclature', str,
                                   **self._get_params(elements=[nom.to_json() for nom in nomes]))
        if isinstance(response, str) and response.startswith('Sync success'):
            return response
        raise ValueError(str(response))

    @catch_error
    def discount_receipt(self, receipt: ReceiptDiscount, **_) -> (ReceiptResult, bool):
        """ Get discount of receipt """

        return self._send_post('receipt/discount', ReceiptResult, **self._get_params(**receipt.to_json()))

    @catch_error
    def confirm_receipt(self, receipt: ReceiptConfirm, **_) -> (ReceiptResult, bool):
        """ Confirmation of receipt """

        return self._send_post('receipt/confirm', ReceiptResult, **self._get_params(**receipt.to_json()))

    @catch_error
    def delete_receipts(self, receipts: List[str], **_) -> (str, bool):
        """
        Delete previous confirmed receipts
        warning: ensure that count of elements has to be less than or equal 100 in a request
        :param receipts: list of receipts
        :return: str, bool
        """

        if not isinstance(receipts, list) or not receipts:
            raise ValueError('No element found')
        if len(receipts) > 500:
            raise ValueError('Length of receipts must be less or equal than 100 elements')

        response = self._send_post('delete/receipt', str,
                                   **self._get_params(elements=[dict(remote_id=r) for r in receipts]))
        if isinstance(response, str) and response.startswith('Delete success'):
            return response
        raise ValueError(str(response))

    @catch_error
    def refund_receipt(self, receipt: ReceiptRefund, **_) -> (List[RefundItemResult], bool):
        """ Refund products of receipt """

        resp = self._send_post('refund/receipt', list, **self._get_params(**receipt.to_json()))
        if resp:
            resp = [RefundItemResult(**v) for v in resp]
        return resp

    @catch_error
    def sync_receipts(self, receipts: List[ReceiptConfirm], **_) -> (str, bool):
        """
        Sync your catalog to smartbonus app
        warning: ensure that count of elements has to be less than or equal 100 in a request
        :param receipts: list of receipts
        """

        if not isinstance(receipts, list) or not receipts:
            raise ValueError('No element found')
        if len(receipts) > 100:
            raise ValueError('Length of receipts must be less or equal than 100 elements')

        response = self._send_post('sync/receipt', str,
                                   **self._get_params(elements=[r.to_json() for r in receipts]))
        if isinstance(response, str) and response.startswith('Sync success'):
            return response
        raise ValueError(str(response))

    @catch_error
    def sync_tags(self, tags: List[Tag], **_) -> (str, bool):
        """
        Sync list of tags
        warning: ensure that count of elements has to be less than or equal 500 in a request
        :param tags: list of tags
        """

        if not isinstance(tags, list) or not tags:
            raise ValueError('No element found')
        if len(tags) > 500:
            raise ValueError('"Length of tags must be less or equal than 500 elements')

        response = self._send_post('sync/tag', str, **self._get_params(elements=[r.to_json() for r in tags]))
        if isinstance(response, str) and response.startswith('Sync success'):
            return response
        raise ValueError(str(response))

    @catch_error
    def config_order(self, order_url: str, status_url: str, token: str) -> (object, bool):
        """
        Config order hook:
        when user created order in smartbonus we send it to your api orderUrl with body Order class.
        :param order_url: your api that wait new order from smartbonus app
        :param status_url: your api that wait new status of order: receive body StatusBody
        :param token: your unique identifier of store: your receive it in orderUrl & statusUrl hooks in field "store"
        """

        return self._send_post('order/config', None,
                               **self._get_params(order_url=order_url, status_url=status_url, token=token))

    @catch_error
    def change_order_status(self, body: StatusBody) -> (object, bool):
        """
        Change status of order that created in smartbonus app
        If status changed client receive push notification about it
        """

        if not ORDER_STATUSES.get(body.status):
            raise ValueError(f'Status {body.status} does not exist')

        return self._send_post('order/status', None, **self._get_params(**body.to_json()))

    def _send_post(self, path: str, obj: object, **params):
        body = requests.post(self.root_path + path, json=params).json()
        return self._decode_response(body, obj)

    def _send_get(self, path: str, obj: object, **params):
        body = requests.get(self.root_path + path, params=params).json()
        return self._decode_response(body, obj)

    def _get_params(self, **params) -> dict:
        params['store'] = self.store
        return params

    @staticmethod
    def _decode_response(body: object, obj: object):
        if isinstance(body, dict) and 'message' in body:
            if body.get('status') != 200:
                raise ValueError(str(body['message']))

            if not callable(obj):
                return body['message']

            return obj(**body['message']) if isinstance(body['message'], dict) else obj(body['message'])
        raise AttributeError(str(body))


def set_root_path(root_path: str):
    SmartBonus.root_path = root_path
