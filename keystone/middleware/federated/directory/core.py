from keystone import catalog
def getProviderList():
   list = []
        self.catalog = catalog.ServiceController()
        services = self.catalog.get_services({"is_admin":"True"})
        for service in services["OS-KSADM:services"]:
                if "idp" in service["type"]:
                        list.append({'name':service["description"], 'service_id':service["id"]})
        return {'realms':list}
