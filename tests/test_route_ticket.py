"""Comprobantes temporales firmados, sin llamadas a APIs externas."""
import pytest
from backend.app.route_ticket import InvalidRouteTicket, RouteTicketSigner


def test_issue_validate_and_reject_tampering():
    now = [1000]
    s = RouteTicketSigner(secret=b'k' * 32, ttl=20, clock=lambda: now[0])
    token = s.issue(faculty='FISI', ids=['DEMO-BIENESTAR'], source='primary')
    assert s.verify(token)['i'] == ['DEMO-BIENESTAR']
    assert 'Quiero ayuda' not in token
    with pytest.raises(InvalidRouteTicket):
        s.verify(token + 'x')
    now[0] = 1021
    with pytest.raises(InvalidRouteTicket):
        s.verify(token)


def test_invalid_issued_route_and_invalid_receipt():
    s = RouteTicketSigner(secret=b'k' * 32)
    with pytest.raises(InvalidRouteTicket):
        s.issue(faculty='FISI', ids=['A', 'A'], source='primary')
    with pytest.raises(InvalidRouteTicket):
        s.issue(faculty='FISI', ids=[], source='primary')
    for data in ('abc', '*.*', ' ' * 3000):
        with pytest.raises(InvalidRouteTicket):
            s.verify(data)
