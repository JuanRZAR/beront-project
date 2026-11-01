from beront.shared.infrastructure.modelos.base import Base as Base
from beront.shared.infrastructure.modelos.catalog import tables as catalog
from beront.shared.infrastructure.modelos.commerce import tables as commerce
from beront.shared.infrastructure.modelos.comunes import tables as comunes
from beront.shared.infrastructure.modelos.identity import tables as identity
from beront.shared.infrastructure.modelos.inventory import tables as inventory
from beront.shared.infrastructure.modelos.media import tables as media
from beront.shared.infrastructure.modelos.orders import tables as orders

REGISTERED_MODELS = (catalog, comunes, commerce, identity, inventory, media, orders)
