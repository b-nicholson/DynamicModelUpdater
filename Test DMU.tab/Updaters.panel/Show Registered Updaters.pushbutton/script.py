import Autodesk.Revit.DB as DB

updaters = DB.UpdaterRegistry.GetRegisteredUpdaterInfos()
for u in updaters:
    print(u.UpdaterName)
