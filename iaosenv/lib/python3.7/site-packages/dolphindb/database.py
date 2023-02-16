from dolphindb.table import Table
import uuid

def _generate_handle():
    return "TMP_TBL_" + uuid.uuid4().hex[:8]

##
#@if english
#DolphinDB database objects
#@endif
class Database(object):
    ##
    #@if english
    #constructor
    #@param[in] dbName: database name. The default value is None
    #@param[in] s: connected session object. The default value is None
    #@endif
    def __init__(self, dbName=None, s=None):
        self.__dbName = dbName
        self.__session = s
    
    def _getDbName(self):
        return self.__dbName

    ##
    #@if english
    #Create an empty dimension table based on the given schema
    #@param[in] table: a table. DolphinDB server will create an empty dimension table based on the schema of the passed table. The default value is None.
    #@param[in] tableName: name of the dimension table. The default value is None.
    #@param[in] sortColumns: string or a list of strings, indicating the sort column of a table. The default value is None. If specified, data with the same key are stored together in a partition in order.
    #@return DolphinDB Table object
    #@endif
    def createTable(self, table=None, tableName=None, sortColumns=None):
        if not isinstance(table, Table):
            raise RuntimeError("Only DolphinDB Table object is accepted")
        
        tHandle = table._getTableName()
        ctHandle = _generate_handle()
        runstr = ctHandle + "=" + self.__dbName + ".createTable(" + tHandle + "," + "`" + tableName

        if sortColumns is not None:
            if type(sortColumns) == str:
                runstr += ",sortColumns=`"+sortColumns
            elif type(sortColumns) == list:
                runstr += ",sortColumns="
                for key in sortColumns:
                    runstr += "`"+key

        runstr += ");"

        self.__session.run(runstr)
        return self.__session.loadTable(ctHandle)

    ##
    #@if english
    #Create an empty dimension table based on the given schema
    #@param[in] table: a table. DolphinDB server will create an empty dimension table based on the schema of the passed table. The default value is None.
    #@param[in] tableName: name of the dimension table. The default value is None.
    #@param[in] partitionColumns: string or list of strings indicating the partition columns. For a compo domain database, it is a string; for non-sequential domain, this parameter is required.
    #@param[in] compressMethods: a list of the compression methods used for each column. If unspecified, the columns are not compressed.
    #@param[in] sortColumns: string or a list of strings, indicating the sort column of a table. The default value is None. If specified, data with the same key are stored together in a partition in order.
    #@param[in] keepDuplicates: how to deal with records with duplicate sortColumns values. It can have the following values:
    #"ALL": keep all records; "LAST": only keep the last record; "FIRST": only keep the first record
    #@return DolphinDB Table object
    #@endif
    def createPartitionedTable(self, table=None, tableName=None, partitionColumns=None, compressMethods={}, sortColumns=None, keepDuplicates=""):
        if not isinstance(table, Table):
            raise RuntimeError("Only DolphinDB Table object is accepted")
        
        tHandle = table._getTableName()
        cptHandle = _generate_handle()

        partitionColumns_str = ''
        if type(partitionColumns) == str:
            partitionColumns_str =  "`" + partitionColumns
        elif type(partitionColumns) == list:
            for col in partitionColumns:
                partitionColumns_str += '`'
                partitionColumns_str += col
        else:
            raise RuntimeError("Only String or List of String is accepted for partitionColumns")

        runstr = cptHandle + "=" + self.__dbName + ".createPartitionedTable(" + tHandle + "," + "`" + tableName + ","  + partitionColumns_str

        if len(compressMethods) > 0 :
            runstr += ",compressMethods={"
            for key, value in compressMethods.items():
                runstr += key+":'"+value+"',"
            runstr = runstr[:-1]+"}"
        if sortColumns is not None:
            if type(sortColumns) == str:
                runstr += ",sortColumns=`"+sortColumns
            elif type(sortColumns) == list:
                runstr += ",sortColumns="
                for key in sortColumns:
                    runstr += "`"+key

        # if len(compressMethods) > 0 :
        #     runstr += ",compressMethods=["
        #     for key in compressMethods:
        #         runstr += "'"+key+"',"
        #     runstr = runstr[:-1]+"]"
        # if sortColumns is not None :
        #     if type(sortColumns) == str:
        #         runstr += ",sortColumns='"+sortColumns+"'"
        #     elif type(sortColumns) == list:
        #         runstr += ",sortColumns=["
        #         for key in sortColumns:
        #             runstr += "'"+key+"',"
        #         runstr = runstr[:-1]+"]"

        if len(keepDuplicates) > 0 :
            runstr += ",keepDuplicates="+keepDuplicates
        runstr+=");"
        self.__session.run(runstr)
        return self.__session.loadTable(cptHandle)
