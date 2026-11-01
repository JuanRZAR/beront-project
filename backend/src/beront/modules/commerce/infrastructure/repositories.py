from beront.shared.infrastructure.pg_call import require_record


class SqlCommerceRepository:
    RESOURCES = {"provinces": "province", "cities": "city", "banks": "bank"}

    def __init__(self, pg):
        self.pg = pg

    def settings(self):
        return self.pg.call("commerce_settings_get")

    def save_settings(self, data):
        return self.pg.call("commerce_settings_save", data)

    def listing(self, resource, *, private=False):
        return self.pg.call("commerce_" + self.RESOURCES[resource] + "_list", {"private": private})

    def get(self, resource, identifier):
        return require_record(
            self.pg.call("commerce_" + self.RESOURCES[resource] + "_get", {"id": identifier})
        )

    def add(self, resource, data):
        return self.pg.call("commerce_" + self.RESOURCES[resource] + "_add", data)

    def save(self, resource, data):
        return self.pg.call("commerce_" + self.RESOURCES[resource] + "_save", data)

    def destination(self, city_id):
        return require_record(self.pg.call("commerce_destination", {"id": city_id}))
