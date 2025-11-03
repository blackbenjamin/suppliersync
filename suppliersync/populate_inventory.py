"""
Populate or update the database with a Wayfair-style inventory of 20 products.
Run with: python populate_inventory.py
"""

import os
import sqlite3

DB_PATH = os.getenv("SQLITE_PATH", "suppliersync.db")

# Wayfair-style products with realistic pricing
PRODUCTS = [
    {
        "sku": "SOF-001",
        "name": "Westwood 84\" Gray Fabric Sofa with Reversible Chaise - Transitional Modern Living Room Furniture",
        "category": "Couches",
        "wholesale_price": 520.00,
        "retail_price": 899.00,
        "supplier_id": 1,
    },
    {
        "sku": "TBL-002",
        "name": "Madison Extendable Dining Table in Weathered Oak Finish - Seats 6 to 8 People",
        "category": "Dining",
        "wholesale_price": 380.00,
        "retail_price": 649.00,
        "supplier_id": 2,
    },
    {
        "sku": "CHA-003",
        "name": "Grey Tufted Button Back Upholstered Dining Chair Set of 2 - Modern Kitchen Seating",
        "category": "Dining",
        "wholesale_price": 145.00,
        "retail_price": 249.00,
        "supplier_id": 3,
    },
    {
        "sku": "BED-004",
        "name": "Kingsley Queen Size Upholstered Platform Bed Frame with Adjustable Headboard in Charcoal Gray",
        "category": "Bedroom",
        "wholesale_price": 410.00,
        "retail_price": 699.00,
        "supplier_id": 1,
    },
    {
        "sku": "DESK-005",
        "name": "Harper 48\" Computer Desk in Espresso Brown - Home Office Writing Table",
        "category": "Office",
        "wholesale_price": 185.00,
        "retail_price": 329.00,
        "supplier_id": 2,
    },
    {
        "sku": "RUG-006",
        "name": "Safavieh Monaco Collection 8x10 Area Rug in Beige and Blue Geometric Pattern - Machine Washable",
        "category": "Living",
        "wholesale_price": 280.00,
        "retail_price": 479.00,
        "supplier_id": 3,
    },
    {
        "sku": "LAMP-007",
        "name": "Brass Adjustable Swivel Floor Lamp with USB Charging Port - Modern Reading Light",
        "category": "Living",
        "wholesale_price": 85.00,
        "retail_price": 149.00,
        "supplier_id": 4,
    },
    {
        "sku": "CAB-008",
        "name": "Bedford 5-Drawer Dresser in White Oak Finish - Bedroom Storage Furniture",
        "category": "Bedroom",
        "wholesale_price": 450.00,
        "retail_price": 799.00,
        "supplier_id": 2,
    },
    {
        "sku": "SEC-009",
        "name": "Bradford 2-Piece Sectional Sofa in Linen Gray with Pillows - Reversible Chaise Configuration",
        "category": "Couches",
        "wholesale_price": 680.00,
        "retail_price": 1199.00,
        "supplier_id": 1,
    },
    {
        "sku": "BAR-010",
        "name": "Industrial 30\" Bar Cart with Wine Glass Rack and Wood Shelf - Mobile Kitchen Island",
        "category": "Kitchen",
        "wholesale_price": 195.00,
        "retail_price": 349.00,
        "supplier_id": 4,
    },
    {
        "sku": "TVS-011",
        "name": "Modern TV Stand with Sliding Barn Doors and Media Storage Compartment - 60\" Wide",
        "category": "Living",
        "wholesale_price": 320.00,
        "retail_price": 549.00,
        "supplier_id": 2,
    },
    {
        "sku": "OTM-012",
        "name": "Verona Oversized Tufted Ottoman Bench in Navy Blue - Storage Footrest for Living Room",
        "category": "Living",
        "wholesale_price": 165.00,
        "retail_price": 289.00,
        "supplier_id": 3,
    },
    {
        "sku": "MAT-013",
        "name": "Casper Sleep Original Queen Memory Foam Mattress - Medium Firm Support with AirScape Cooling",
        "category": "Bedroom",
        "wholesale_price": 520.00,
        "retail_price": 995.00,
        "supplier_id": 5,
    },
    {
        "sku": "ACC-014",
        "name": "Coastal Farmhouse Wall Decor Set of 3 Wooden Signs - Beach Inspired Home Accents",
        "category": "Living",
        "wholesale_price": 45.00,
        "retail_price": 89.00,
        "supplier_id": 4,
    },
    {
        "sku": "CUR-015",
        "name": "Blackout Curtain Panels Set of 2 in Charcoal Gray - Thermal Insulated Window Treatment",
        "category": "Living",
        "wholesale_price": 75.00,
        "retail_price": 139.00,
        "supplier_id": 3,
    },
    {
        "sku": "OTM-016",
        "name": "Alma Dark Brown Leather Reclining Ottoman with Tray Top - Living Room Footrest",
        "category": "Seating",
        "wholesale_price": 125.00,
        "retail_price": 219.00,
        "supplier_id": 1,
    },
    {
        "sku": "BOO-017",
        "name": "Modular 6-Cube Bookshelf Organizer in Espresso Brown - Freestanding Storage System",
        "category": "Storage",
        "wholesale_price": 95.00,
        "retail_price": 179.00,
        "supplier_id": 2,
    },
    {
        "sku": "CHA-018",
        "name": "Bermuda Outdoor Patio Dining Chair Set of 4 in Teak Wood - Weather Resistant Seating",
        "category": "Outdoor",
        "wholesale_price": 220.00,
        "retail_price": 399.00,
        "supplier_id": 4,
    },
    {
        "sku": "SOF-019",
        "name": "Blake 72\" Sofa Bed with Trundle Storage in Navy Blue Microfiber - Convertible Furniture",
        "category": "Couches",
        "wholesale_price": 395.00,
        "retail_price": 679.00,
        "supplier_id": 3,
    },
    {
        "sku": "DIN-020",
        "name": "Monterey Rustic Farmhouse Rectangular Dining Table in Distressed Brown - Seats 6 People",
        "category": "Dining",
        "wholesale_price": 520.00,
        "retail_price": 899.00,
        "supplier_id": 2,
    },
]

# Suppliers
SUPPLIERS = [
    {"id": 1, "name": "Coastal Home Co", "sla_days": 3},
    {"id": 2, "name": "Urban Loft Inc", "sla_days": 4},
    {"id": 3, "name": "Modern Living Essentials", "sla_days": 2},
    {"id": 4, "name": "Designer Home Accents", "sla_days": 3},
    {"id": 5, "name": "Sleep Innovations Inc", "sla_days": 5},
]


def populate_database():
    """Populate or update the database with new inventory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print(f"Populating database: {DB_PATH}")
    print(f"Products: {len(PRODUCTS)}")
    print(f"Suppliers: {len(SUPPLIERS)}")
    
    # Ensure suppliers exist
    for supplier in SUPPLIERS:
        cursor = conn.execute("SELECT id FROM suppliers WHERE id = ?", (supplier["id"],))
        if cursor.fetchone():
            conn.execute(
                "UPDATE suppliers SET name = ?, sla_days = ? WHERE id = ?",
                (supplier["name"], supplier["sla_days"], supplier["id"])
            )
            print(f"  Updated supplier: {supplier['name']}")
        else:
            conn.execute(
                "INSERT INTO suppliers(id, name, sla_days) VALUES (?, ?, ?)",
                (supplier["id"], supplier["name"], supplier["sla_days"])
            )
            print(f"  Added supplier: {supplier['name']}")
    
    # Update or insert products
    for product in PRODUCTS:
        cursor = conn.execute("SELECT sku FROM products WHERE sku = ?", (product["sku"],))
        if cursor.fetchone():
            conn.execute(
                """UPDATE products 
                   SET name = ?, category = ?, wholesale_price = ?, retail_price = ?, supplier_id = ?, is_active = 1
                   WHERE sku = ?""",
                (
                    product["name"],
                    product["category"],
                    product["wholesale_price"],
                    product["retail_price"],
                    product["supplier_id"],
                    product["sku"],
                )
            )
            print(f"  Updated product: {product['sku']} - {product['name'][:50]}...")
        else:
            conn.execute(
                """INSERT INTO products(sku, name, category, wholesale_price, retail_price, supplier_id, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, 1)""",
                (
                    product["sku"],
                    product["name"],
                    product["category"],
                    product["wholesale_price"],
                    product["retail_price"],
                    product["supplier_id"],
                )
            )
            print(f"  Added product: {product['sku']} - {product['name'][:50]}...")
    
    # Deactivate any products not in the new inventory list
    valid_skus = {p["sku"] for p in PRODUCTS}
    cursor = conn.execute("SELECT sku FROM products WHERE is_active = 1")
    all_skus = {row["sku"] for row in cursor.fetchall()}
    deactivated = all_skus - valid_skus
    if deactivated:
        placeholders = ",".join(["?"] * len(deactivated))
        conn.execute(f"UPDATE products SET is_active = 0 WHERE sku IN ({placeholders})", list(deactivated))
        print(f"\n  Deactivated {len(deactivated)} old products not in new inventory")
    
    conn.commit()
    conn.close()
    print("\n✅ Database populated successfully!")
    print(f"Total active products: {len(PRODUCTS)}")


if __name__ == "__main__":
    populate_database()

