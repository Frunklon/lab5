from src.models import Apartment
from src.manager import Manager
from src.models import Parameters, Bill, ApartmentSettlement, Tenant, TenantSettlement


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key

def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names

def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True

    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False

def test_apartment_total_cost():
    parameters = Parameters()
    manager = Manager(parameters)

    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910
    assert manager.get_apartment_costs('A1', 2000, 3) == None
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0.0

def test_create_apartment_settlement():
    manager = Manager(Parameters())

    manager.apartments = {'apart-1': 'dummy', 'apart-2': 'dummy'}
    manager.bills = []

    manager.bills.append(Bill(
        amount_pln=150.0, date_due='2024-04-10', apartment='apart-1', 
        settlement_year=2024, settlement_month=4, type='electricity'
    ))
    manager.bills.append(Bill(
        amount_pln=200.0, date_due='2024-04-15', apartment='apart-1', 
        settlement_year=2024, settlement_month=4, type='water'
    ))
    manager.bills.append(Bill(
        amount_pln=300.0, date_due='2024-05-10', apartment='apart-1', 
        settlement_year=2024, settlement_month=5, type='water'
    ))

    settlement_with_bills = manager.create_apartment_settlement('apart-1', 2024, 4)
    assert settlement_with_bills is not None
    assert isinstance(settlement_with_bills, ApartmentSettlement)
    assert settlement_with_bills.apartment == 'apart-1'
    assert settlement_with_bills.year == 2024
    assert settlement_with_bills.month == 4
    assert settlement_with_bills.total_bills_pln == 350.0
    assert settlement_with_bills.total_rent_pln == 0.0
    assert settlement_with_bills.total_due_pln == 0.0

    settlement_empty = manager.create_apartment_settlement('apart-2', 2024, 4)
    assert settlement_empty is not None
    assert settlement_empty.apartment == 'apart-2'
    assert settlement_empty.total_bills_pln == 0.0

    settlement_none = manager.create_apartment_settlement('invalid-key', 2024, 4)
    assert settlement_none is None

def test_create_tenant_settlements():
    manager = Manager( Parameters())

    manager.tenants={
        'tenant-1': Tenant(name='Jan Kowalski', apartment='apart-2-tenants', room='1', rent_pln=1000.0, deposit_pln=0.0, date_agreement_from='2024-01-01', date_agreement_to='2025-01-01'),
        'tenant-2': Tenant(name='Anna Nowak', apartment='apart-2-tenants', room='2', rent_pln=1000.0, deposit_pln=0.0, date_agreement_from='2024-01-01', date_agreement_to='2025-01-01'),
        'tenant-3': Tenant(name='Piotr Wiśniewski', apartment='apart-1-tenant', room='1', rent_pln=1500.0, deposit_pln=0.0, date_agreement_from='2024-01-01', date_agreement_to='2025-01-01')
    }

    settlement_2_tenants = ApartmentSettlement(apartment='apart-2-tenants', month=5, year=2024, total_rent_pln=0.0, total_bills_pln=300.0, total_due_pln=0.0)
    settlement_1_tenant = ApartmentSettlement(apartment='apart-1-tenant', month=5, year=2024, total_rent_pln=0.0, total_bills_pln=150.0, total_due_pln=0.0)
    settlement_0_tenants = ApartmentSettlement(apartment='apart-empty', month=5, year=2024, total_rent_pln=0.0, total_bills_pln=500.0, total_due_pln=0.0)

    result_2 = manager.create_tenant_settlements(settlement_2_tenants)
    assert result_2 is not None
    assert isinstance(result_2, list)
    assert len(result_2) == 2
    assert result_2[0].bills_pln == 150.0
    assert result_2[1].bills_pln == 150.0
    assert result_2[0].apartment_settlement == 'apart-2-tenants'
    assert result_2[0].month == 5

    result_1 = manager.create_tenant_settlements(settlement_1_tenant)
    assert len(result_1) == 1
    assert result_1[0].bills_pln == 150.0
    assert result_1[0].tenant == 'tenant-3'
    assert result_1[0].balance_pln == -150.0

    result_0 = manager.create_tenant_settlements(settlement_0_tenants)
    assert isinstance(result_0, list)
    assert len(result_0) == 0
