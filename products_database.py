# Products database - matches frontend products.js EXACTLY
# All 60 products with correct names and prices from products.js

PRODUCTS = [
    # ========== GPUs - Budget (5 products) ==========
    {"name": "GIGABYTE Radeon RX 9060 XT Gaming OC 16GB", "priceUSD": 378.99, "priceEUR": 324.16, "category": "GPU"},
    {"name": "Gigabyte GeForce RTX 3050 8GB", "priceUSD": 319.55, "priceEUR": 273.32, "category": "GPU"},
    {"name": "Sapphire PULSE Radeon RX 6600 8GB", "priceUSD": 263.99, "priceEUR": 225.80, "category": "GPU"},
    {"name": "Sapphire Pulse Radeon RX 7600 8GB", "priceUSD": 247.99, "priceEUR": 212.11, "category": "GPU"},
    {"name": "ZOTAC Geforce RTX 5050 TWIN EDGE OC 8GB", "priceUSD": 238.99, "priceEUR": 204.41, "category": "GPU"},
    
    # ========== GPUs - Performance (7 products) ==========
    {"name": "GAINWARD GeForce RTX 5090 Phantom 32G", "priceUSD": 2780.99, "priceEUR": 2370.29, "category": "GPU"},
    {"name": "GAINWARD GeForce RTX 5080 Phoenix 16G", "priceUSD": 1199.99, "priceEUR": 1022.78, "category": "GPU"},
    {"name": "Gigabyte GeForce RTX 4080 Super WINDFORCE V2 16G", "priceUSD": 1261.99, "priceEUR": 1075.62, "category": "GPU"},
    {"name": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "priceUSD": 755.99, "priceEUR": 642.54, "category": "GPU"},
    {"name": "ASRock Radeon RX 9070 XT Taichi 16GB OC", "priceUSD": 723.99, "priceEUR": 615.34, "category": "GPU"},
    {"name": "Sapphire Nitro + Radeon RX 7800 XT 16GB", "priceUSD": 649.99, "priceEUR": 552.45, "category": "GPU"},
    {"name": "ASUS Prime GeForce RTX 5070 12GB", "priceUSD": 507.99, "priceEUR": 431.76, "category": "GPU"},
    
    # ========== CPUs - Budget (5 products) ==========
    {"name": "Intel Core i5-12400F", "priceUSD": 147.99, "priceEUR": 125.88, "category": "CPU"},
    {"name": "AMD Ryzen 5 8400F", "priceUSD": 155.17, "priceEUR": 131.99, "category": "CPU"},
    {"name": "AMD Ryzen 5 5600X", "priceUSD": 129.99, "priceEUR": 110.57, "category": "CPU"},
    {"name": "AMD Ryzen 5 5600", "priceUSD": 126.96, "priceEUR": 107.99, "category": "CPU"},
    {"name": "Intel Core i3-13100F", "priceUSD": 94.04, "priceEUR": 79.99, "category": "CPU"},
    
    # ========== CPUs - Performance (7 products) ==========
    {"name": "AMD Ryzen 9 9950X3D", "priceUSD": 679.99, "priceEUR": 578.40, "category": "CPU"},
    {"name": "AMD Ryzen 9 9900X3D", "priceUSD": 586.99, "priceEUR": 499.29, "category": "CPU"},
    {"name": "Intel Core Ultra 9 285K", "priceUSD": 568.99, "priceEUR": 483.98, "category": "CPU"},
    {"name": "Intel Core i9-14900KF", "priceUSD": 507.87, "priceEUR": 431.99, "category": "CPU"},
    {"name": "AMD Ryzen 9 7950X", "priceUSD": 485.99, "priceEUR": 413.38, "category": "CPU"},
    {"name": "AMD Ryzen 7 9800X3D", "priceUSD": 452.61, "priceEUR": 384.99, "category": "CPU"},
    {"name": "Intel Core i7-14700K", "priceUSD": 340.92, "priceEUR": 289.99, "category": "CPU"},
    
    # ========== SSDs - Budget (6 products) ==========
    {"name": "Crucial P310 500GB PCIe 4.0 NVMe", "priceUSD": 65.99, "priceEUR": 56.72, "category": "SSD"},
    {"name": "Kingston NV3 500GB PCIe 4.0 NVMe", "priceUSD": 87.59, "priceEUR": 75.28, "category": "SSD"},
    {"name": "Patriot VP4300L 500GB PCIe 4.0 NVMe", "priceUSD": 91.99, "priceEUR": 79.07, "category": "SSD"},
    {"name": "WD Blue SN5100 1TB PCIe 4.0 NVMe", "priceUSD": 136.99, "priceEUR": 117.74, "category": "SSD"},
    {"name": "Patriot Viper VP4300 Lite 1TB PCIe 4.0 NVMe", "priceUSD": 163.75, "priceEUR": 140.74, "category": "SSD"},
    {"name": "WD Blue SN5000 500GB PCIe 4.0 NVMe", "priceUSD": 127.99, "priceEUR": 109.86, "category": "SSD"},
    
    # ========== SSDs - Mainstream (7 products) ==========
    {"name": "Crucial T500 1TB PCIe 4.0 NVMe", "priceUSD": 151.28, "priceEUR": 129.83, "category": "SSD"},
    {"name": "Samsung 990 PRO 1TB PCIe 4.0 NVMe", "priceUSD": 160.55, "priceEUR": 137.79, "category": "SSD"},
    {"name": "Lexar NM790 1TB PCIe 4.0 NVMe", "priceUSD": 176.45, "priceEUR": 151.43, "category": "SSD"},
    {"name": "Samsung 990 EVO Plus 2TB PCIe 4.0 NVMe", "priceUSD": 268.45, "priceEUR": 230.39, "category": "SSD"},
    {"name": "WD SN7100 2TB PCIe 5.0 NVMe", "priceUSD": 281.99, "priceEUR": 242.00, "category": "SSD"},
    {"name": "WD_BLACK SN850X 2TB PCIe 4.0 NVMe", "priceUSD": 316.68, "priceEUR": 271.78, "category": "SSD"},
    {"name": "Silicon Power US75 4TB PCIe 4.0 NVMe", "priceUSD": 402.21, "priceEUR": 345.19, "category": "SSD"},
    
    # ========== Monitors - Budget (6 products) ==========
    {"name": 'Samsung Odyssey G3 24"', "priceUSD": 118.91, "priceEUR": 102.45, "category": "Monitor"},
    {"name": 'MSI MAG 244C 23.6"', "priceUSD": 127.66, "priceEUR": 109.99, "category": "Monitor"},
    {"name": "ASUS ROG Strix XG27WCS", "priceUSD": 235.29, "priceEUR": 202.73, "category": "Monitor"},
    {"name": "AOC MiniLED Q27G3XMN", "priceUSD": 264.99, "priceEUR": 228.32, "category": "Monitor"},
    {"name": "ASUS ROG Strix XG27WCMS", "priceUSD": 402.85, "priceEUR": 347.10, "category": "Monitor"},
    {"name": "MSI MAG 321CUPDF", "priceUSD": 604.68, "priceEUR": 520.99, "category": "Monitor"},
    
    # ========== Monitors - Premium (5 products) ==========
    {"name": "AOC AG276QZD2", "priceUSD": 387.99, "priceEUR": 330.26, "category": "Monitor"},
    {"name": "LG UltraGear 27GX704A-B", "priceUSD": 441.62, "priceEUR": 375.91, "category": "Monitor"},
    {"name": "Samsung Odyssey OLED G6 G60SD", "priceUSD": 610.70, "priceEUR": 519.83, "category": "Monitor"},
    {"name": "AOC AGON AG326UD", "priceUSD": 859.00, "priceEUR": 719.99, "category": "Monitor"},
    {"name": "ASUS ROG Swift PG32UCDP", "priceUSD": 1051.49, "priceEUR": 894.61, "category": "Monitor"},
    
    # ========== RAM - DDR4 (4 products) ==========
    {"name": "Kingston FURY Beast RGB 8GB", "priceUSD": 94.77, "priceEUR": 79.65, "category": "RAM"},
    {"name": "Kingston FURY Beast 16GB Kit", "priceUSD": 109.74, "priceEUR": 92.23, "category": "RAM"},
    {"name": "CORSAIR VENGEANCE LPX 32GB Kit", "priceUSD": 227.50, "priceEUR": 191.20, "category": "RAM"},  # 2x16GB DDR4-3600
    {"name": "CORSAIR VENGEANCE LPX 32GB Kit", "priceUSD": 281.21, "priceEUR": 236.34, "category": "RAM"},  # 4x8GB DDR4-3200
    
    # ========== RAM - DDR5 (8 products) ==========
    {"name": "Kingston FURY Beast Black 16GB", "priceUSD": 117.48, "priceEUR": 98.73, "category": "RAM"},
    {"name": "CORSAIR VENGEANCE RGB 32GB Kit", "priceUSD": 380.99, "priceEUR": 325.85, "category": "RAM"},
    {"name": "Patriot Xtreme 5 RGB 48GB Kit", "priceUSD": 680.17, "priceEUR": 571.64, "category": "RAM"},
    {"name": "Kingston FURY Beast RGB 64GB Kit", "priceUSD": 795.95, "priceEUR": 668.94, "category": "RAM"},
    {"name": "Kingston FURY Beast EXPO 64GB Kit", "priceUSD": 758.37, "priceEUR": 637.36, "category": "RAM"},
    {"name": "Kingston FURY Renegade 48GB", "priceUSD": 874.09, "priceEUR": 734.62, "category": "RAM"},
    {"name": "Kingston FURY Beast Black 64GB", "priceUSD": 886.58, "priceEUR": 745.11, "category": "RAM"},
    {"name": "CORSAIR VENGEANCE RGB 128GB Kit", "priceUSD": 1309.92, "priceEUR": 1100.90, "category": "RAM"},
]
