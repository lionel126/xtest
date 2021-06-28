from utils import MallV2, Data, MallV2DB


class TestTicket():
    def test_create_ticket(self):
        ticket = MallV2.create_ticket(promotionTag="csgtest").json()['data']
        MallV2.offer_ticket(ticket['id'])
        MallV2.ticket_list()

        # MallV2.trade_confirmation()
