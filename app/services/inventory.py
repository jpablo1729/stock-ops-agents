from sqlalchemy.orm import Session
from app.database import Product

class InventoryService:
    @staticmethod
    def get_all(db: Session) -> list[Product]:
        """Retrieves all products from the inventory."""
        return db.query(Product).all()

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Product | None:
        """Retrieves a single product by its SKU. Case-insensitive and trims spaces."""
        return db.query(Product).filter(Product.sku == sku.upper().strip()).first()

    @staticmethod
    def reserve_stock(db: Session, sku: str, quantity: int) -> tuple[bool, str]:
        """
        Attempts to reserve a specific quantity of a product.
        Returns a tuple: (success_boolean, message).
        """
        if quantity <= 0:
            return False, "Quantity to reserve must be greater than zero."

        product = InventoryService.get_by_sku(db, sku)
        if not product:
            return False, f"No product found with SKU {sku}."

        if product.stock < quantity:
            return False, f"Insufficient stock for {product.name}. Available: {product.stock}."

        # Deduct the stock and commit the change
        product.stock -= quantity
        db.commit()
        db.refresh(product)

        return True, f"Reservation confirmed: {quantity}x {product.name}. Remaining stock: {product.stock}."