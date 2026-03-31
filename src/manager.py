from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 
        
        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self,apartment_key, year=None, month=None):
        apartment = self.apartments.get(apartment_key)

        if not apartment:
            return None
        
        cost = 0.0

        
        for bill in self.bills:
            if bill.apartment != apartment_key: continue
            
            
            
            
            if bill.settlement_year != year and year is not None: continue
            
            
            if bill.settlement_month != month and month is not None: continue
                
                
                
            cost += bill.amount_pln

        
        return cost
    
    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):

        apartment = self.apartments.get(apartment_key)
        if not apartment:
            return None
        
        total_bills = self.get_apartment_costs(apartment_key, year, month)

        total_rent = 0.0
        total_due = 0.0

        return ApartmentSettlement(
            apartment = apartment_key, month = month, year = year, total_rent_pln = total_rent, total_bills_pln = total_bills, total_due_pln=total_due
        )

    def create_tenant_settlements(self, apartment_settlement: 'ApartmentSettlement'):

        apartment_tenants = []
        for tenant_key, tenant in self.tenants.items():
            if tenant.apartment == apartment_settlement.apartment:
                apartment_tenants.append(tenant_key)

        if not apartment_tenants:
            return []
        
        split_bills = apartment_settlement.total_bills_pln / len(apartment_tenants)

        tenant_settlements = []
        for tenant_key in apartment_tenants:
            rent = 0.0
            total_due = rent + split_bills
            balance = 0.0 - total_due

            settlement = TenantSettlement(
                tenant=tenant_key,
                apartment_settlement=apartment_settlement.apartment,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=rent,
                bills_pln=split_bills,
                total_due_pln=total_due,
                balance_pln=balance
            )
            tenant_settlements.append(settlement)

        return tenant_settlements
