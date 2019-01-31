from Database.DbClass import DbClass

mc = DbClass()
uitvoer = mc.executeQuery("Select * from db_weerstation.meting")
print(uitvoer)
