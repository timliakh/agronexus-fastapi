from sqlalchemy.orm import Session

from app.config import config
from app.db_models import ProductRecord
from app.models import Category


def category_image(category: Category) -> str:
    return f"/static/images/{category.value}.svg"


INITIAL_PRODUCTS: list[dict] = [
    {
        "slug": "agribot-x1",
        "name": "AgriBot X1 — автономный трактор",
        "description": "Полностью автономный электротрактор с LiDAR, RTK-GPS и AI-маршрутизацией. Работает 24/7 без оператора в кабине.",
        "price": 12500.0,
        "category": Category.TRACTORS,
        "manufacturer": "NeuroField Robotics",
        "configurations": ["Level 4", "450 км", "LiDAR + RTK"],
        "in_stock": True,
        "image_url": category_image(Category.TRACTORS),
    },
    {
        "slug": "harvestai-9000",
        "name": "HarvestAI 9000 — робот-комбайн",
        "description": "Самоходный комбайн с компьютерным зрением и адаптивной жаткой. Самостоятельно оптимизирует маршрут уборки по полю.",
        "price": 34000.0,
        "category": Category.HARVESTERS,
        "manufacturer": "Cortex Harvest",
        "configurations": ["AI Vision", "Swarm Link", "9 м захват"],
        "in_stock": True,
        "image_url": category_image(Category.HARVESTERS),
    },
    {
        "slug": "autotill-matrix",
        "name": "AutoTill Matrix — робот для обработки почвы",
        "description": "Автономный агрегат глубокорыхлительной обработки с картированием плотности почвы и точной навигацией.",
        "price": 7300.0,
        "category": Category.PLOWS,
        "manufacturer": "TerraLogic",
        "configurations": ["Level 4", "6 м", "Soil Map AI"],
        "in_stock": True,
        "image_url": category_image(Category.PLOWS),
    },
    {
        "slug": "autoseed-navigator",
        "name": "AutoSeed Navigator — умная сеялка",
        "description": "Автономная сеялка с датчиками влажности и AI-подбором нормы высева для каждого участка поля.",
        "price": 9550.0,
        "category": Category.SEEDERS,
        "manufacturer": "PrecisionAg Labs",
        "configurations": ["Variable Rate", "3.6 м", "Edge AI"],
        "in_stock": True,
        "image_url": category_image(Category.SEEDERS),
    },
    {
        "slug": "cropguard-auto",
        "name": "CropGuard Auto — автономный опрыскиватель",
        "description": "Роботизированный опрыскиватель с распознаванием сорняков и точечным внесением СЗР только на целевые зоны.",
        "price": 13200.0,
        "category": Category.SPRAYERS,
        "manufacturer": "GreenVision",
        "configurations": ["Spot Spray AI", "24 м", "4000 л"],
        "in_stock": True,
        "image_url": category_image(Category.SPRAYERS),
    },
    {
        "slug": "farmos-nexus",
        "name": "FarmOS Nexus — станция управления полем",
        "description": "Центр управления автономным парком: координация техники, прогноз урожая и мониторинг поля в реальном времени.",
        "price": 4500.0,
        "category": Category.ATTACHMENTS,
        "manufacturer": "Synapse Agri",
        "configurations": ["Fleet Control", "Satellite Link", "50 машин"],
        "in_stock": True,
        "image_url": category_image(Category.ATTACHMENTS),
    },
]


def _link_existing_uploads(db: Session) -> None:
    upload_dir = config.paths.products_upload_dir
    allowed = config.image.allowed_extensions
    if not upload_dir.is_dir():
        return

    changed = False
    for path in upload_dir.iterdir():
        if not path.is_file() or not path.stem.isdigit():
            continue
        if path.suffix.lower() not in allowed:
            continue

        record = db.get(ProductRecord, int(path.stem))
        if record is None:
            continue

        url = f"/uploads/products/{path.name}"
        if record.image_url != url:
            record.image_url = url
            changed = True

    if changed:
        db.commit()


def init_db(db: Session) -> None:
    if db.query(ProductRecord).count() == 0:
        for product_data in INITIAL_PRODUCTS:
            db.add(
                ProductRecord(
                    slug=product_data["slug"],
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],
                    category=product_data["category"].value,
                    manufacturer=product_data["manufacturer"],
                    configurations=product_data["configurations"],
                    in_stock=product_data["in_stock"],
                    image_url=product_data.get("image_url"),
                )
            )
        db.commit()

    _link_existing_uploads(db)
