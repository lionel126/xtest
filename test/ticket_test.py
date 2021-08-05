from utils import MallV2, Data, MallV2DB
from config import STORE1, USER_ID
import pytest
import math

class TestTicketCreate():
    def test_create(self):
        r = MallV2.manage_create_ticket(promotionTag="csgtest")
        assert r.status_code == 200
        self.ticket = r.json()['data']

    
    @pytest.mark.parametrize('json', [
        {
            # "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        },
        # {
        #     "name": "test ticket name",
        #     # "brief": "test ticket brief",
        #     "storeCode": STORE1,
        #     "promotionTag": "test-ticket-tag",
        #     "ticketType": "package",
        #     "ticketValue": 100,
        #     "duration": 3600 * 24 * 30 * 1000
        # },
        {
            "name": "test ticket name",
            "brief": "test ticket brief",
            # "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        },
        {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            # "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        },
        {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            # "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        },
        {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            # "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        },
        {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            # "duration": 3600 * 24 * 30 * 1000
        },
    ])
    def test_missing_required_params(self, json):
        r = MallV2.manage_create_ticket(json=json)
        assert r.status_code == 400
        assert r.json()['status'] == 400

    @pytest.mark.parametrize('json', [
        {
            "name": "test ticket name",
            # "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        },
    ])
    def test_missing_optional_params(self, json):
        r = MallV2.manage_create_ticket(json=json)
        assert r.status_code == 200
        assert r.json()['status'] == 0
        for k, v in json.items():
            assert r.json()['data'][k] == v

class TestTicketOffer():
    def test_1(self):
        tc = TestTicketCreate()
        tc.test_create()
        r = MallV2.offer_ticket(ticketId=tc.ticket['id'])
    
    @pytest.mark.parametrize('json', [
        {"receives": [{"userId": USER_ID, "count": 1}]},
        {"ticketId": 0, "receives": [{"userId": USER_ID, "count": 1}]},
    ])
    def test_missing_required_params_1(self, json):
        tc = TestTicketCreate()
        tc.test_create()
        # r = MallV2.offer_ticket(json={"receives": [{"userId": USER_ID, "count": 1}]})
        r = MallV2.offer_ticket(json=json)
        assert r.status_code == 400
        assert r.json()['status'] == 400

    @pytest.mark.parametrize('json', [
        {"ticketId": 1, "receives": []},
        {"ticketId": 1},
        {"ticketId": 1, "receives": [{"count": 1}]},
        {"ticketId": 1, "receives": [{"userId": USER_ID, "count": 0}]},
        {"ticketId": 1, "receives": [{"userId": USER_ID}]},
    ])
    def test_missing_required_params_2(self, json):
        """没校验"""
        # tc = TestTicketCreate()
        # tc.test_create()
        # r = MallV2.offer_ticket(json={"receives": [{"userId": USER_ID, "count": 1}]})
        r = MallV2.offer_ticket(json=json)
        assert r.status_code == 200
        assert r.json()['status'] == 400

    def test_not_existed_ticket(self):
        '''bug 发放不存在的ticket'''
        tc = TestTicketCreate()
        tc.test_create()
        MallV2DB.delete_tickets(tickets=[tc.ticket['id']])
        r = MallV2.offer_ticket(ticketId=tc.ticket['id'])
        MallV2.ticket_list()
        assert r.status_code == 200
        assert r.json()['status'] != 0
        
    def test_re_offer(self):
        '''todo'''
        tc = TestTicketCreate()
        tc.test_create()
        r = MallV2.offer_ticket(ticketId=tc.ticket['id'])
        r = MallV2.offer_ticket(ticketId=tc.ticket['id'])
        MallV2.ticket_list()

    @pytest.mark.parametrize('count', [
        2
    ])
    def test_offer_multiple(self, count):
        '''一次发放<count>个
        '''
        total = MallV2.ticket_list().json()['data']['pagination']['total']
        tc = TestTicketCreate()
        tc.test_create()
        r = MallV2.offer_ticket(ticketId=tc.ticket['id'], receives=[{"userId": USER_ID, "count": count}])
        
        total2 = MallV2.ticket_list().json()['data']['pagination']['total']
        assert total2 == total + count
        

class TestTicketUpdate():
    '''todo 更新后 发放原来的ticketid？'''  


class TestTicketList():

    def test_paginate(self):
        '''
        pageSize 
        列表排序
        '''
        if total := MallV2.ticket_list().json()['data']['pagination']['total'] < 10:
            TestTicketOffer().test_offer_multiple(10)

        total = MallV2.ticket_list().json()['data']['pagination']['total']
        total_pages = math.ceil(total/3)
        tickets = MallV2.ticket_list(page=total_pages, pageSize=3).json()['data']['list']
        assert len(tickets) == total - 3 * (total_pages - 1)

        tickets2 = MallV2.ticket_list(page=total_pages+1, pageSize=3).json()['data']['list']
        assert len(tickets2) == 0