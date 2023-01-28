import math
import sys
import time
from datetime import datetime
from util import (
    clear,
    divider,
    formatSeconds
)
from classes import (
    Catalog,
    DB,
    Service
)

# =============================================================================

try:
    clear()
    now = datetime.now() # current date and time
    dt = now.strftime('%H:%M')

    # BEGIN -------------------------------------------------------------------

    divider()
    p1 = "python " + (" ".join(sys.argv))
    p2 = now.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Command was: %s" % p1)
    print(f"Datetime:    %s" % p2)
    divider()

    start = time.time()

    objDB = DB()
    objDB.connect('book_shops.db')
    objDB.createTables()
    objDB.installAllData()

    # Anticariat Doamnei ......................................................
    objService1 = Service(
        "anticariatdoamnei",
        "Anticariat Doamnei",
        "https://anticariat-doamnei.com/toate?sort=p.date_added&order=DESC",
        "#content .product-item h4 a", # URL
        "#content .product-item h4 a" # text
    )
    objCatalog1 = Catalog(objDB, objService1, dt)
    objCatalog1.searchNewProducts()

    # Targul Cartii ...........................................................
    objService2 = Service(
        "targulcartii",
        "Targul Cartii",
        "https://www.targulcartii.ro/noutati",
        "#display-product-list .product-list-row .name a", # URL
        "#display-product-list .product-list-row .name a" # text
    )
    objCatalog2 = Catalog(objDB, objService2, dt)
    objCatalog2.searchNewProducts()

    end = time.time()

    # END ---------------------------------------------------------------------
    # BEGIN CLI REPORT --------------------------------------------------------

    elapsedTime = formatSeconds(math.floor(end - start))

    divider()
    print()
    print(f"Elapsed Time: %s" % elapsedTime)
    print()
    divider()

    # END CLI REPORT ----------------------------------------------------------

except Exception as error:
    print(error)
