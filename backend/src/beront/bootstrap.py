from dataclasses import dataclass
from functools import partial

from beront.modules.cart.application.build_quote import BuildCartQuote
from beront.modules.cart.infrastructure.whatsapp import WhatsAppLinkBuilder
from beront.modules.catalog.application.manage_catalog import CatalogService
from beront.modules.catalog.application.query_catalog import CatalogQueryFacade
from beront.modules.catalog.infrastructure.images import LocalImageStorage
from beront.modules.catalog.infrastructure.repositories import SqlCatalogRepository
from beront.modules.commerce.application.manage_commerce import CommerceService
from beront.modules.commerce.infrastructure.repositories import SqlCommerceRepository
from beront.modules.identity.application.authenticate import IdentityService
from beront.modules.identity.infrastructure.passwords import WerkzeugPasswordHasher
from beront.modules.identity.infrastructure.repositories import SqlIdentityRepository
from beront.modules.inventory.application.adjust_inventory import InventoryService
from beront.modules.inventory.infrastructure.repositories import SqlStockRepository
from beront.modules.media.application.manage_media import MediaService
from beront.modules.media.infrastructure.repositories import SqlMediaRepository
from beront.modules.orders.application.manage_orders import OrderService
from beront.modules.orders.infrastructure.mailer import BackgroundMailer, SmtpMailer
from beront.modules.orders.infrastructure.repositories import SqlOrderRepository
from beront.shared.infrastructure.database import SqlUnitOfWork, make_database


@dataclass
class Container:
    engine: object
    uow_factory: object
    identity: IdentityService
    catalog: CatalogService
    queries: CatalogQueryFacade
    inventory: InventoryService
    quote: BuildCartQuote
    storage: LocalImageStorage
    media: MediaService
    commerce: CommerceService
    orders: OrderService


def build_container(settings, mailer=None):
    engine, sessions = make_database(settings.database_url)
    factory = partial(
        SqlUnitOfWork,
        sessions,
        {
            "identity": SqlIdentityRepository,
            "catalog": SqlCatalogRepository,
            "stock": SqlStockRepository,
            "media": SqlMediaRepository,
            "commerce": SqlCommerceRepository,
            "orders": SqlOrderRepository,
        },
    )
    storage = LocalImageStorage(settings.storage_root)
    queries = CatalogQueryFacade(factory)
    commerce = CommerceService(factory)
    return Container(
        engine,
        factory,
        IdentityService(factory, WerkzeugPasswordHasher()),
        CatalogService(factory, storage),
        queries,
        InventoryService(factory),
        BuildCartQuote(queries, WhatsAppLinkBuilder(commerce.whatsapp_number)),
        storage,
        MediaService(factory, storage),
        commerce,
        OrderService(
            factory,
            storage,
            settings.secret_key,
            mailer or BackgroundMailer(SmtpMailer(settings)),
            settings.frontend_origin,
        ),
    )
