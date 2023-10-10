# -*- coding: UTF-8 -*-

from pyrevit import forms
import Autodesk.Revit.DB as DB
from System import Guid
from System.Collections.Generic import List

class FrrUpdater(DB.IUpdater):

    def __init__(self, addinId):
        '''type UpdaterId, mix of Addin ID and updater GUID
           choose a different GUID for each updater !!! '''
        self.updaterID = DB.UpdaterId(addinId, Guid("85429c94-dd75-4e97-9594-7b1d9784269c"))

    def GetUpdaterId(self):
        return self.updaterID

    def GetUpdaterName(self):
        return 'Instance Based FRR & STC Checker'

    def GetAdditionalInformation(self):
        return 'Instance Based FRR & STC Checker (explanation, details, warnings)'

    def GetChangePriority(self):
        return DB.ChangePriority.Structure

    def Execute(self, updaterData):
        up_doc = updaterData.GetDocument()
        ids = updaterData.GetModifiedElementIds()


        def fix_instance_param(param_1_name, param_2_name, abbreviation):
            t = DB.SubTransaction(up_doc)
            t.Start()

            alert_user_exceed_max = False
            alert_user_bad_data = False

            try:
                if ids:
                    for id in ids:
                        elem = up_doc.GetElement(id)
                        wall_type = up_doc.GetElement(elem.GetTypeId())
                        type_frr = wall_type.LookupParameter(param_1_name).AsString()
                        instance_frr = elem.LookupParameter(param_2_name)
                        instance_frr_string = instance_frr.AsString()
                        instance_frr_string_original = instance_frr_string
                        if instance_frr_string != "":
                            if not instance_frr_string.isnumeric():
                                alert_user_bad_data = True
                                instance_frr_string = "".join(c for c in instance_frr_string if c.isdigit())

                        if instance_frr_string != "" and type_frr != "":
                            if int(instance_frr_string) > int(type_frr):
                                instance_frr_string = str(type_frr)
                                alert_user_exceed_max = True

                        if instance_frr_string != instance_frr_string_original:
                            instance_frr.Set(instance_frr_string)


                    if alert_user_bad_data:
                        msg = abbreviation + " must be inputted as an integer. Illegal characters have been removed."
                        forms.alert(msg)

                    if alert_user_exceed_max:
                        msg2 = "Element has " + abbreviation + " exceeding what the Type allows. The " + abbreviation + " will be automatically corrected. Feel free to undo your change if this is not desired."

                        forms.alert(msg2)

                t.Commit()
            except:
                t.RollBack()

        fix_instance_param("Max FRR", "Desired FRR", "FRR")
        fix_instance_param("Max STC", "Desired STC", "STC")

app = __revit__.Application


def register_frr_updater():
    frr_updater = FrrUpdater(app.ActiveAddInId)
    if DB.UpdaterRegistry.IsUpdaterRegistered(frr_updater.GetUpdaterId()):
        DB.UpdaterRegistry.UnregisterUpdater(frr_updater.GetUpdaterId())

    DB.UpdaterRegistry.RegisterUpdater(frr_updater)
    cats = List[DB.BuiltInCategory]()
    categories = [DB.BuiltInCategory.OST_Walls, DB.BuiltInCategory.OST_Ceilings,DB.BuiltInCategory.OST_Floors]
    for c in categories:
        cats.Add(c)
    
    filter = DB.ElementMulticategoryFilter(cats)

    DB.UpdaterRegistry.AddTrigger(frr_updater.GetUpdaterId(), filter,
        DB.Element.GetChangeTypeAny())


def unregister_frr_updater():
    frr_updater = FrrUpdater(app.ActiveAddInId)
    if DB.UpdaterRegistry.IsUpdaterRegistered(frr_updater.GetUpdaterId()):
        DB.UpdaterRegistry.UnregisterUpdater(frr_updater.GetUpdaterId())



