from app.repositories.feedback_repository import SqlAlchemyFeedbackRepository
from app.repositories.order_repository import SqlAlchemyOrderRepository
from app.repositories.product_repository import SqlAlchemyProductRepository
from app.services.admin_service import AdminService
from app.services.feedback_service import FeedbackService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.storage.local_image_storage import LocalImageStorage

_product_repo = SqlAlchemyProductRepository()
_order_repo = SqlAlchemyOrderRepository()
_feedback_repo = SqlAlchemyFeedbackRepository()
_image_storage = LocalImageStorage()

_product_service = ProductService(_product_repo, _image_storage)
_order_service = OrderService(_product_repo, _order_repo)
_feedback_service = FeedbackService(_feedback_repo)
_admin_service = AdminService(_product_repo, _order_repo, _feedback_repo)


def get_image_storage() -> LocalImageStorage:
    return _image_storage


def get_product_service() -> ProductService:
    return _product_service


def get_order_service() -> OrderService:
    return _order_service


def get_feedback_service() -> FeedbackService:
    return _feedback_service


def get_admin_service() -> AdminService:
    return _admin_service
