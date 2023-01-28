import requests
import smtplib, ssl
import sqlite3
import time
from datetime import datetime
from email.message import EmailMessage
from requests_html import HTMLSession
from requests.exceptions import ConnectionError
from sqlite3 import Error
from util import divider

# =============================================================================

class DB:
    def __init__(self):
        self.name = ''
        self.conn = None
        # print(sqlite3.version)
        # print(sqlite3.sqlite_version)

    def connect(self, dbName):
        self.conn = None

        try:
            self.conn = sqlite3.connect(dbName)
        except Error as e:
            print(e)

        return self.conn

    def createTables(self):
        if self.conn is not None:
            try:
                c = self.conn.cursor()
                sqlCommand = """
                CREATE TABLE IF NOT EXISTS report(
                    `position`             INTEGER PRIMARY KEY AUTOINCREMENT,
                    `service`              TEXT NOT NULL UNIQUE,
                    `latest_product_url`   TEXT,
                    `updated_at`           DATETIME
                );
                """
                c.execute(sqlCommand)
                print('Table `report` has been successfully created.')
            except Error as e:
                print(e)

    def installSingleData(self, serviceName, serviceValue, serviceTimestamp):
        if self.conn is not None:
            sqlCommand = """
                INSERT INTO `report` (`service`, `latest_product_url`, `updated_at`) VALUES ('{a}', '{b}', '{c}')
                ON CONFLICT(`service`) DO UPDATE SET `service` = '{a}';
                """.format(
                    a = serviceName,
                    b = serviceValue,
                    c = serviceTimestamp
                )

            self.conn.execute(sqlCommand)
            self.conn.commit()

    def installAllData(self):
        if self.conn is not None:
            now = datetime.now() # current date and time
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

            try:
                # Anticariat Doamnei
                self.installSingleData('anticariatdoamnei', '#anticariatdoamnei', timestamp)

                # Targul Cartii
                self.installSingleData('targulcartii', '#targulcartii', timestamp)

                print("Data for `report` table has been successfully installed.")
            except Error as e:
                print(e)

    def getLatestProductUrl(self, service):
        if self.conn is not None:
            try:
                sqlCommand = """
                    SELECT `latest_product_url` FROM `report`
                    WHERE `service` = '{a}'
                    LIMIT 1
                """.format(
                    a = service
                )

                # print(sqlCommand)

                cursor = self.conn.execute(sqlCommand)
                firstRow = cursor.fetchone()

                if (firstRow is not None):
                    return str(firstRow[0])
            except Error as e:
                print(e)

        return "#"

    def updateLatestProductUrl(self, service, productUrl):
        if self.conn is not None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                sqlCommand = """
                    UPDATE `report` SET `latest_product_url` = '{b}', 'updated_at' = '{c}'
                    WHERE `service` = '{a}'
                """.format(
                    a = service,
                    b = productUrl,
                    c = timestamp
                )

                # print(sqlCommand)

                self.conn.execute(sqlCommand)
                self.conn.commit()
            except Error as e:
                print(e)

# =============================================================================

class Service:
    def __init__(self, key, name, url, productLinkSelector, productTitleSelector):
        self.key = key
        self.name = name
        self.url = url
        self.productLinkSelector = productLinkSelector
        self.productTitleSelector = productTitleSelector

    def getKey(self):
        return self.key

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def getProductLinkSelector(self):
        return self.productLinkSelector

    def getProductTitleSelector(self):
        return self.productTitleSelector

# =============================================================================

class Catalog:
    def __init__(self, db, service, dt):
        divider()
        print(f"\n%s -  Catalog initializing... \n" % service.getName())

        self.db = db
        self.service = service
        self.dt = dt
        self.latestProductTitle = ""
        self.latestProductUrl = ""

    def searchNewProducts(self):
        divider()
        print(f"\n%s - Search new products \n" % self.service.getName())

        divider()
        latestProductUrl = self.db.getLatestProductUrl(self.service.getKey())
        print("Latest product URL from database: %s" % latestProductUrl)

        session = HTMLSession()

        for i in range(5):
            try:
                r = session.get(self.service.getUrl(), timeout=5)

                # ------------------------------------------------------------------------------------------------------

                firstProductTitleElement = r.html.find(self.service.getProductTitleSelector(), first=True)

                if (firstProductTitleElement):
                    if ("title" in firstProductTitleElement.attrs) and (firstProductTitleElement.attrs['title'] != ''):
                        firstProductTitle = firstProductTitleElement.attrs['title']
                    else:
                        firstProductTitle = firstProductTitleElement.text
                else:
                    firstProductTitle = ""

                # ------------------------------------------------------------------------------------------------------

                firstProductLinkElement = r.html.find(self.service.getProductLinkSelector(), first=True)

                if (firstProductLinkElement):
                    firstProductUrl = firstProductLinkElement.attrs['href']
                    print("Latest product URL from website:  %s" % firstProductUrl)

                    if (firstProductUrl != latestProductUrl):
                        print(f"\n" + "This product is new!" + "\n")
                        self.latestProductTitle = firstProductTitle
                        self.latestProductUrl = firstProductUrl
                        self.db.updateLatestProductUrl(self.service.getKey(), firstProductUrl)
                        self.pushNotification()
                        self.sendMail()

                break
            except ConnectionError as error:
                divider()
                print(":cyclone: Connection error! Retrying to get: " + self.service.getUrl() + " [" + str(i) + "]")
                time.sleep(5)

    def pushNotification(self):
        requests.post("https://ntfy.sh/gheoltanconstantin",
            data = self.latestProductTitle.encode(encoding='utf-8'),
            headers = {
                "Title": self.dt + " " + self.service.getName(),
                "Priority": "urgent",
                "Click": self.service.getUrl()
            })

    def sendMail(self):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "constantin.python@gmail.com"
        receiver_email = ["gheoltan.constantin@gmail.com", "constantin_gheoltan@yahoo.com"]
        password = "suzxpadxbevmqovb" # important

        msg = EmailMessage()
        msg.set_content('Salut! Au aparut produse noi pe site-ul' + self.service.getName())

        msg.add_alternative("""\
            <html>
                <head>
                    <style type="text/css">
                        .link {{
                            background-color: #c00; 
                            color: #fff;
                            display: inline-block;
                            font-weight: bold;
                            padding: 7px 12px;
                            text-decoration: none;
                        }}
                    </style>
                </head>
                <body>
                    <p>Salut!</p>
                    <p>Au aparut produse noi pe site-ul <b>{serviceName}</b>.</p>
                    <p><a href="{serviceUrl}" class="link">Vezi produsele</a></p>
                </body>
            </html>
            """.format(
                serviceName = self.service.getName(),
                serviceUrl = self.service.getUrl()
           ), subtype='html')

        msg['Subject'] = "Noutati!"
        msg['From'] = "Python <" + sender_email + ">"
        msg['To'] = receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg, from_addr = sender_email, to_addrs = receiver_email)
