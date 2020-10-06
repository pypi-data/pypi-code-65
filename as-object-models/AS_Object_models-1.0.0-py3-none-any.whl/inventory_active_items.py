###############################################################################################################################
# Licensed to the part of the ownership of Analytics Supply LLC.
#  All updates to this file should only be done at the sole discretion of the 
#  officers of Analytics Supply:
#  
##################################
##  Module Name:  inventory_active_items.py
##################################
#
#  Description:
#  --  This module will have all recipe items by item type and will have a "tracked" attribute to tell us wether or not this is an item to track for inventory
#
##################################
#
#  Created:  ???  Somewhere around July 2020
#
##################################
#  UPDATES:
#  Date, Issue #, Name of Developer, Short description of bug
#  9/11/2020, ct:85, Jason Bowles, Update to stop tracking items by type and name:  https://gitlab.com/AnalyticsSupply/customer-tracking/-/issues/85
#
#
#
#################################################################################################################################
from .sales_inv_utils import SalesInvBase
from .utils import FSObjSummary
from datetime import datetime
import jmespath

from . import GetInstance
from . import DataNumber, DataNumberLookup
from .item_week import ItemWeek

'''
In order to make the production view screen return relatively quickly.. I needed a way to identify when a new item was entered and needed tracked
... 

This adds an extra step for the user, that they have to add it as a "recipe item"... and also add it here to configure it to be tracked.

However, this also allows more control on how items in a recipe are tracked... by turning some off (cleaning up the view) or remapping on the fly
'''
class InventoryActiveItems(SalesInvBase):
    """ This is the class represents all items that are available during a specific week """

    ext_fields = ['item_type', 'items','soft_delete','inventory_type','parent_path','path']
    COLLECTION_NAME = 'application_data'

    DefaultFieldValues = {'tracked':False, 'order':99, 'id': 'None', 'id':'NoIdGiven', 'path':'NoPathGiven'}
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.item_type = kwargs.get('item_type','')
        self.items = kwargs.get('items',{})
        self.inventory_type = kwargs.get('inventory_type','week')
    
        super(InventoryActiveItems, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return InventoryActiveItems.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return InventoryActiveItems.__basePath(InventoryActiveItems.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return InventoryActiveItems.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/InventoryActiveItems'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = InventoryActiveItems.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return InventoryActiveItems(InventoryActiveItems.get_firestore_client(),**docDict)
  
    def get_schema(self):
        schema = self.get_bq_schema()
        return schema

    def get_values_dict(self):
        values = self.get_dict()
        return values

    def get_inventory_type(self):
        return self.inventory_type
    
    def set_inventory_type(self,typeInv):
        self.inventory_type = typeInv
    
    def set_inventory_monthly(self):
        self.set_inventory_type('month')
    
    def set_inventory_weekly(self):
        self.set_inventory_type('week') 

    @classmethod
    def __clean_item_type(cls,item_type):
        return ItemWeek.CleanItemType(item_type)

    @classmethod
    def display_recipe_items(cls,item_type):
        #recipeItems = InventoryActiveItems.get_active_recipe_items(item_type,fldKey='data_number_lookup')
        #productionViewItems = InventoryActiveItems.get_all_active_dict(item_type)
        productionViewItems = InventoryActiveItems.get_all_dict(item_type)
        #entries = {}
        #prefix = cls.__clean_item_type(item_type)
        #for rp in list(recipeItems.values()):
        #    pvp = productionViewItems.get(rp.data_number_lookup,None)
        #    if pvp:
        #        pvp['tracked'] = True
        #        pvp[prefix+'_id'] = pvp['id']
        #        pvp[prefix+'_path'] = pvp['path']
        #        pvp[prefix+'_name'] = pvp['name']
        #        entries[pvp['id']] = pvp
        #    else:
        #        d = {prefix+'_name':rp.name}
        #        d[prefix+'_id'] = rp.id
        #        d[prefix+'_path'] = rp.path
        #        d['tracked'] = False
        #        entries[d[prefix+'_id']] = d
            
        return {'item_type':item_type,'items':productionViewItems}


    @classmethod
    def get_active_recipe_items(cls,item_type, fldKey='name'):
        path = 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/recipe_costing'
        colRef = InventoryActiveItems.get_firestore_client().collection(path)
        q = colRef.where('item_type','==',item_type)
        q = q.where('status','==','Active')
        snaps = q.stream()
        plts = {x.get(fldKey):InventoryActiveItems.GetStorageBlobInstance(x) for x in snaps if x.get('name') != 'N/A'}
        return plts

    @classmethod
    def remove_item(cls,activeItemId):
        recipeItem = InventoryActiveItems.GetSBObjByDNL(activeItemId)
        return InventoryActiveItems.AddItem(recipeItem,doTrack=False)

    @classmethod
    def add_item_by_id(cls, recipe_id):
        recipeItem = InventoryActiveItems.GetSBObjByDNL(recipe_id)
        return InventoryActiveItems.AddItem(recipeItem,doTrack=True)

    @classmethod
    def add_item_order(cls, recipe_id, order):
        recipeItem = InventoryActiveItems.GetSBObjByDNL(recipe_id)
        return InventoryActiveItems.AddItem(recipeItem,itemOrder=order)

    @classmethod
    def _setup_entry(self,item_type):
        doc_path = InventoryActiveItems.basePath()+"/"+item_type
        sap = InventoryActiveItems.getInstance(InventoryActiveItems.get_firestore_client().document(doc_path))
        sap.item_type = item_type
        recipeItems = InventoryActiveItems.get_active_recipe_items(item_type,fldKey='data_number_lookup')
        recipes = list(recipeItems.values())
        for recipeEntry in recipes:
            sap.add_item(recipeEntry,doTrack=False)
        sap.update_ndb()
        return sap

    #@classmethod
    #def GetItemByName(cls, itemType, itemName):
    #    items = InventoryActiveItems.get_all(itemType)
    #    for item_key in items.keys():
    #        item = items[item_key]
    #        name = item.name
    #        cleanName = ItemWeek.CleanItemName(name)
    #        if itemName == name or itemName == cleanName:
    #            return item
    #    return None
    
    @classmethod
    def GetItemById(cls,itemType,itemId):
        '''
        Updates are now going to be by item_id: (ct:85)
        '''
        items = InventoryActiveItems.get_all_active(itemType)
        return items.get(itemId,None)

    @classmethod
    def AddItem(cls, recipe_entry,doTrack=None, itemOrder=None):
        sap = cls.get_entry(recipe_entry.item_type)
        return sap.add_item(recipe_entry,doTrack,itemOrder)

    def add_item(self, recipe_entry,doTrack=None, itemOrder=None):
        itemD = self.items.get(recipe_entry.id,{})
        itemD['id'] = recipe_entry.id
        itemD['name'] = recipe_entry.name
        itemD['clean_name'] = ItemWeek.CleanItemName(recipe_entry.name)
        itemD['item_type'] = recipe_entry.item_type
        itemD['image'] = recipe_entry.image
        itemD['path'] = recipe_entry.path
        
        currentTracked = itemD.get('tracked',None)
        if doTrack is not None:
            itemD['tracked'] = doTrack
            currentTracked = doTrack
            
        if currentTracked is None:
            itemD['tracked'] = False # Default value for tracking
        
        currentOrder = itemD.get('order',None)
        if itemOrder is not None:
            itemD['order'] = itemOrder
            currentOrder = itemOrder

        if currentOrder is None:
            itemD['order'] = 99 # Default value for order

        self.items[recipe_entry.id] = itemD
        
        self.update_ndb()
        return itemD

    @classmethod
    def get_entry(cls, item_type):
        docRef = InventoryActiveItems.get_firestore_client().document(InventoryActiveItems.basePath()+'/'+item_type)
        activeItem = InventoryActiveItems.getInstance(docRef)
        if activeItem.exists:
            return activeItem
        return cls._setup_entry(item_type)
    
    @classmethod
    def _getActiveEntries(cls,itemType):
        aps = InventoryActiveItems.get_entry(itemType)
        return jmespath.search("* | [?tracked == `true`]",aps.items)
    
    @classmethod
    def get_all_active(cls,item_type):
        '''
        return all active entries
        '''
        activeEntries = InventoryActiveItems._getActiveEntries(item_type)
        return {x['id']:FSObjSummary(**cls._get_item_entry(x,fields=['id','path','name'])) for x in activeEntries}
        #for key in aps.items.keys():
        #    if aps.items[key]['tracked']:
        #        objDict[key] = FSObjSummary(**aps.items[key])
       # 
        #return objDict
    
    @classmethod
    def get_all_active_dict(cls,item_type):
        activeEntries = InventoryActiveItems._getActiveEntries(item_type)
        return {x['id']:cls._get_item_entry(x) for x in activeEntries}
    
    @classmethod
    def _get_item_entry(cls, itemEntry, fields=None):
        if fields is None:
            entry = {}
            defKeys = list(cls.DefaultFieldValues.keys())
            for key in defKeys:
                entry[key] = itemEntry.get(key,cls.DefaultFieldValues[key])
            for key in list(itemEntry.keys()):
                if key not in defKeys:
                    entry[key] = itemEntry[key]
            return entry

        if fields[0] == 'all':
            return itemEntry

        return {k:v for k,v in itemEntry.items() if k in fields}


    @classmethod
    def get_all_dict(cls,item_type):
        aps = InventoryActiveItems.get_entry(item_type)
        #return aps.items
        return {x['id']:cls._get_item_entry(x) for x in jmespath.search("* | [*]",aps.items)}


class InventoryItems(SalesInvBase):
    """ This is the class represents all items that are available during a specific week """

    ext_fields = ['tracked_items','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.tracked_items = kwargs.get('tracked_items',[])
        super(InventoryItems, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return InventoryItems.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return InventoryItems.__basePath(InventoryItems.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return InventoryItems.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/InventoryItems'


    @classmethod
    def getInstance(cls):
        fsDocument = InventoryItems.get_firestore_client().document(cls.basePath()+'/InventoryItems')
        ref,snap = InventoryItems.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        ii = InventoryItems(InventoryItems.get_firestore_client(),**docDict)
        if not ii.exists:
            ii.update_ndb(True)
        return ii
  