from mysql import connector

from Database.pswd import password

class DbClass:
    # constructor
    def __init__(self):
        import mysql.connector as connector

        self.__dsn = {
            'host': 'localhost',
            'user': 'adminWS',
            'passwd': password(),
            'db': 'db_weerstation'
        }

        # ** om een dictionary te kunnen doorgeven
        self.__connection = connector.connect(**self.__dsn)
        self.__cursor = self.__connection.cursor()

    def __query(self, query: str, data: dict = None, dictionary=False):
        try:
            cursor = self.__connection.cursor(dictionary=dictionary)
        except TypeError:
            # print("De optie 'dictionary vereist mysql-connector v2.x.x, kan je installeren met: \n "
            #       "sudo pip3 install mysql-connector==2.1.4")
            cursor = self.__connection.cursor()
        cursor.execute(query, data)
        result = cursor.fetchall()
        cursor.close()
        return result

        # voor schrijven (INSERT, UPDATE, ...)

    def __execute(self, query: str, data: dict = None):
        cursor = self.__connection.cursor()
        cursor.execute(query, data)
        result = cursor.lastrowid
        self.__connection.commit()
        cursor.close()
        return result


    def getPlaatsIDByWeestationID(self, pID):
        try:
            query = "SELECT id FROM  db_weerstation.plaats WHERE ID = (SELECT id FROM  db_weerstation.weerstation WHERE plaats.ID = '" + str(
                pID) + "');"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()[0]
            return result
        except:
            print("Error, kon de plaatsID niet ophalen.")
            return None

    def getPlaatsIDFromWeerstation(self, pID):
        try:
            query = "SELECT weerstation.plaats_ID FROM db_weerstation.weerstation WHERE weerstation.id = " + str(pID)
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()[0]
            return result
        except:
            print("Error, kon de plaatsID niet ophalen.")
            return None

    def insertSample(self, pTemperatuur, pVochtigheid, pLuchtdruk, pWindsnelheid, pLichtinval, pWeerstation_ID,
                     pWeerstation_plaats_ID):
        query = "INSERT INTO db_weerstation.meting (Tijd, Temperatuur, Vochtigheid, Luchtdruk, Windsnelheid, Lichtinval, weerstation_ID, weerstation_plaats_ID) VALUES (current_timestamp(), %f, %f, %f, %f, %f, %i, %i)" % (
            pTemperatuur, pVochtigheid, pLuchtdruk, pWindsnelheid, pLichtinval, pWeerstation_ID, pWeerstation_plaats_ID)
        try:
            result = self.__cursor.execute(query)
            self.__connection.commit()
            return result
        except:
            print("Error, meting is niet toegevoegd.")
            return None

    def checkActive(self, pId):
        try:
            query = "SELECT Actief FROM db_weerstation.weerstation WHERE weerstation.id = " + str(pId)
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()[0]
            return result
        except:
            print("Error, kon de weerstation actief niet ophalen.")
            return None


    def getRawSamples(self):
        try:
            query = "SELECT * FROM db_weerstation.meting"
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            # self.__cursor.close()
            return result
        except:
            print("Error, metingen niet kunnen ophalen.")
            return None

    def getGegevens(self):
        try:
            queryJaren = "SELECT DISTINCT year(Tijd) FROM db_weerstation.meting"
            self.__cursor.execute(queryJaren)
            resultJaren = self.__cursor.fetchall()

            queryWeken = "SELECT DISTINCT weekofyear(Tijd) FROM db_weerstation.meting"
            self.__cursor.execute(queryWeken)
            resultWeken = self.__cursor.fetchall()

            queryDagen = "SELECT DISTINCT  dayname(Tijd) FROM db_weerstation.meting"
            self.__cursor.execute(queryDagen)
            resultDagen = self.__cursor.fetchall()

            queryGegevens = "SELECT *, dayname(Tijd) AS 'Weekdag', weekofyear(Tijd) AS 'Week' FROM db_weerstation.meting"
            self.__cursor.execute(queryGegevens)
            resultGegevens = self.__cursor.fetchall()

            return {'jaren': resultJaren, 'weken': resultWeken, 'dagen': resultDagen, 'gegevens': resultGegevens}
        except:
            print('Gegevens niet kunnen opghalen')
            return None

    def getGegevensBetweenDates(self, begin, eind):
        try:
            queryGegevens = "SELECT  *,  dayname(Tijd)    AS 'Weekdag',  weekofyear(Tijd) AS 'Week'FROM db_weerstation.meting WHERE (DATE(Tijd) BETWEEN '%s' AND '%s')" % (
            begin, eind)
            self.__cursor.execute(queryGegevens)
            resultGegevens = self.__cursor.fetchall()
            return resultGegevens
        except:
            print("Error, gegevens niet kunnen ophalen.")
            return None

    def gemiddeldeGegevensPerDag(self):
        try:
            query = "SELECT DISTINCT DATE(Tijd),AVG(Temperatuur), AVG(Vochtigheid), AVG(Luchtdruk), AVG(Windsnelheid), AVG(Lichtinval) AS AvgValue FROM db_weerstation.meting GROUP BY DATE (Tijd)"
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return result
        except:
            print("Error, metingen niet kunnen ophalen.")
            return None

    def getUserLoginByName(self, name):
        try:
            query = "SELECT * FROM db_weerstation.gebruiker WHERE username = '" + name + "';"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            return result
        except:
            print("Error, kon gebruiker niet ophalen.")
            return None

    def changePasswordByName(self, pUserName, pNew):
        try:
            query = "UPDATE db_weerstation.gebruiker SET Wachtwoord = '" + pNew + "' WHERE username = '" + pUserName + "';"
            self.__cursor.execute(query)
            self.__connection.commit()
        except:
            print("Error, wachtwoord kon niet worden gewijzigd.")

    def getColors(self):
        try:
            query = "SELECT * FROM db_weerstation.kleur ORDER BY kleur.Naam ASC"
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return result
        except:
            print("Error, kleuren niet kunnen ophalen.")
            return None

    def newColor(self, pCode, pName):
        try:
            query = "INSERT INTO db_weerstation.kleur " \
                    "(kleurCode, Naam) " \
                    "VALUES (%s , %s)" % (pCode, pName)
            result = self.__cursor.execute(query)
            self.__connection.commit()
            return result
        except:
            print("Error, kleur is niet toegevoegd.")
            return None

    def updateSettingsColor(self, pCode, pNaam):
        try:
            query = "UPDATE db_weerstation.instellingen SET LaatstAangepast = current_timestamp(), kleur_kleurCode = '" + pCode + "' WHERE gebruiker_Login = '" + pNaam + "' ;"
            result = self.__cursor.execute(query)
            self.__connection.commit()
            return result
        except:
            print("Error, instellingen zijn aangepast.")
            return None

    def getColorByLogin(self, pLogin):
        try:
            query = "SELECT kleur_kleurCode FROM db_weerstation.instellingen WHERE gebruiker_Login = '" + pLogin + "';"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            return result
        except:
            print("Error, kleur van de gebruiker niet kunnen ophalen.")
            return None

    def getUsers(self):
        try:
            query = "SELECT * FROM db_weerstation.gebruiker"
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return result
        except:
            print("Error, user kon niet worden opgehaald.")
            return None

    def getWeerstations(self):
        try:
            query = "SELECT weerstation.id, weerstation.naam, plaats.Plaats, DATE(weerstation.DatumActief), TIME(weerstation.DatumActief), CASE weerstation.Actief WHEN 0 THEN 'Neen'  WHEN 1 THEN 'Ja' END FROM db_weerstation.weerstation JOIN plaats ON weerstation.plaats_ID = plaats.ID"
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            return result
        except:
            print("Error, weerstation kon niet worden opgehaald.")
            return None

    def getWeerstationByID(self, pID):
        try:
            query = 'SELECT Naam FROM db_weerstation.weerstation WHERE ID = ' + pID
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            return result
        except:
            print("Error, weerstation kon niet worden opgehaald.")
            return None

    def updateWeerstationActiveByID(self, pID):
        try:
            query = 'UPDATE db_weerstation.weerstation SET Actief = 1, DatumActief = current_timestamp() WHERE id = ' + pID
            self.__cursor.execute(query)
            self.__connection.commit()
        except:
            print("Error, weerstation kon niet worden geactiveerd.")

    def updateWeerstationInactiveByID(self, pID):
        try:
            query = 'UPDATE db_weerstation.weerstation SET Actief = 0 WHERE id = ' + pID
            self.__cursor.execute(query)
            self.__connection.commit()
        except:
            print("Error, weerstation kon niet worden gedeactiveerd.")

    def getMinMaxDatumZoekGegevens(self):
        try:
            query = "SELECT min(date(Tijd)), max(date(Tijd)) FROM db_weerstation.meting;"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            return result
        except:
            print("Error, kon de minimum en maximum datums niet ophalen.")
            return None

    def newAlert(self):
        pass

    def closeCursor(self):
        self.__cursor.close()

    # def insertHashPswd(self, username, pwd_hash, pwd_salt):
    #     query = "UPDATE db_weerstation.gebruiker SET pwd_hash = '" + pwd_hash + "', pwd_salt ='" + pwd_salt + "' WHERE Login = 'Lander'"
    #     print(query)
    #     self.__cursor.execute(query)
    #     self.__connection.commit()

    # connectie aflsuiten wanneer object verwijderd wordt
    def __del__(self):
        self.__connection.close()