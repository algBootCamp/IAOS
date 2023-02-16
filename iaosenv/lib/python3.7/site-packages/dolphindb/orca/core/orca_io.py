import pandas as pd

class ExcelFile:
    def __init__(self, io, engine=None,*args,**kwargs):
        self.file = pd.ExcelFile(io,engine=engine,*args, **kwargs)

    def parse(
        self,
        sheet_name=0,
        header=0,
        names=None,
        index_col=None,
        usecols=None,
        squeeze=False,
        converters=None,
        true_values=None,
        false_values=None,
        skiprows=None,
        nrows=None,
        na_values=None,
        parse_dates=False,
        date_parser=None,
        thousands=None,
        comment=None,
        skipfooter=0,
        convert_float=True,
        mangle_dupe_cols=True,
        *args, **kwargs
    ):
        return self.file.parse( sheet_name=sheet_name,
        header=header,
        names=names,
        index_col=index_col,
        usecols=usecols,
        squeeze=squeeze,
        converters=converters,
        true_values=true_values,
        false_values=false_values,
        skiprows=skiprows,
        nrows=nrows,
        na_values=na_values,
        parse_dates=parse_dates,
        date_parser=date_parser,
        thousands=thousands,
        comment=comment,
        skipfooter=skipfooter,
        convert_float=convert_float,
        mangle_dupe_cols=mangle_dupe_cols,
        *args, **kwargs)

    @property
    def book(self):
        return self.file.book

    @property
    def sheet_names(self):
        return self.file.sheet_names

    def close(self):
        self.file.close()

class HDFStore:
    def __init__(
            self, path, mode=None, complevel=None, complib=None, fletcher32=False,*args, **kwargs
    ):
        self.file = pd.HDFStore(path,mode=mode,complevel=complevel,complib=complib,fletcher32=fletcher32,
                                *args, **kwargs)

    @property
    def root(self):

        return self.file.root

    @property
    def filename(self):
        return self.file.filename

    def keys(self):
        return self.file.keys()

    def items(self):
        return self.file.items()

    def open(self, mode="a", *args, **kwargs):
        return self.file.open(mode=mode,*args, **kwargs)

    def close(self):
        return self.file.close()

    @property
    def is_open(self):
        return self.file.is_open

    def flush(self, fsync=False):
        return self.flush(fsync=fsync)

    def get(self, key):
        return self.file.get(key)

    def select(
        self,
        key,
        where=None,
        start=None,
        stop=None,
        columns=None,
        iterator=False,
        chunksize=None,
        auto_close=False,
        *args,
        **kwargs
    ):
        return self.file.select(
        key,
        where=where,
        start=start,
        stop=stop,
        columns=columns,
        iterator=iterator,
        chunksize=chunksize,
        auto_close=auto_close,
        *args,
        **kwargs
    )


    def select_as_coordinates(self, key, where=None, start=None, stop=None, *args, **kwargs):
        return self.file.select_as_coordinates(key,where=where,start=start,stop=stop,*args,**kwargs)

    def select_column(self, key, column, *args, **kwargs):
        return self.file.select_column(key,column,*args,**kwargs)

    def select_as_multiple(
        self,
        keys,
        where=None,
        selector=None,
        columns=None,
        start=None,
        stop=None,
        iterator=False,
        chunksize=None,
        auto_close=False,
        *args,
        **kwargs
    ):
        return self.file.select_as_multiple(keys,
                                            where=where,
                                            selector=selector,
                                            columns=columns,
                                            start= start,
                                            stop=stop,
                                            iterator=iterator,
                                            chunksize=chunksize,
                                            auto_close=auto_close,
                                            *args,
                                            **kwargs)

    def put(self, key, value, format=None, append=False, *args, **kwargs):
        return self.file.put(key,value,format=format,append=append,*args,**kwargs)

    def remove(self, key, where=None, start=None, stop=None,*args, **kwargs):
        return self.file.remove(key,where=where,start=start,stop=stop,*args,**kwargs)

    def append(
        self, key, value, format=None, append=True, columns=None, dropna=None, *args, **kwargs
    ):
        return self.file.append(key,value,format=format,append=append,columns=columns,dropna=dropna,*args,**kwargs)

    def append_to_multiple(
        self, d, value, selector, data_columns=None, axes=None, dropna=False,*args, **kwargs
    ):
        return self.file.append_to_multiple(d,value,selector,data_columns=data_columns,axes=axes,dropna=dropna,*args,**kwargs)

    def create_table_index(self, key, *args, **kwargs):
        return self.file.create_table_index(key,*args,**kwargs)

    def groups(self):
        return self.file.groups()

    def walk(self, where="/", *args, **kwargs):
        return self.file.walk(where=where, *args, **kwargs)

    def get_node(self, key, *args, **kwargs):
        return self.file.get_node(key, *args, **kwargs)

    def get_storer(self, key, *args, **kwargs):
        return self.file.get_storer(key,*args, **kwargs)

    def copy(
        self,
        file,
        mode="w",
        propindexes=True,
        keys=None,
        complib=None,
        complevel=None,
        fletcher32=False,
        overwrite=True,
        *args, **kwargs
    ):
        return self.file.copy(file,mode=mode,propindexes=propindexes,keys=keys,complib=complib,
                              complevel=complevel,
                              fletcher32=fletcher32,
                              overwrite=overwrite
                              , *args, **kwargs)

    def info(self):
        return self.file.info()

class StataReader():

    def __init__(
        self,
        path_or_buf,
        convert_dates=True,
        convert_categoricals=True,
        index_col=None,
        convert_missing=False,
        preserve_dtypes=True,
        columns=None,
        order_categoricals=True,
        encoding=None,
        chunksize=None,
        *args,
        **kwargs
    ):
        from pandas.io.stata import StataReader as pdStataReader
        self.file = pdStataReader(path_or_buf,
        convert_dates=convert_dates,
        convert_categoricals=convert_categoricals,
        index_col=index_col,
        convert_missing=convert_missing,
        preserve_dtypes=preserve_dtypes,
        columns=columns,
        order_categoricals=order_categoricals,
        encoding=encoding,
        chunksize=chunksize,
        *args,
        **kwargs)

    def close(self):
        return self.file.close()

    def data(self, **kwargs):
        self.file.data(**kwargs)

    def get_chunk(self, size=None):
        return self.file.get_chunk(size=size)

    def read(
        self,
        nrows=None,
        convert_dates=None,
        convert_categoricals=None,
        index_col=None,
        convert_missing=None,
        preserve_dtypes=None,
        columns=None,
        order_categoricals=None,
            *args,
            **kwargs
    ):
        return self.file.read(nrows=nrows,
                            convert_dates=convert_dates,
                            convert_categoricals=convert_categoricals,
                            index_col=index_col,
                            convert_missing=convert_missing,
                            preserve_dtypes=preserve_dtypes,
                            columns=columns,
                            order_categoricals=order_categoricals,
                              *args,
                              **kwargs)

    @property
    def data_label(self):
        return self.file.data_label

    def variable_labels(self):
        return self.file.variable_labels()

    def value_labels(self):
        return self.file.value_labels()

class StataWriter():
    def __init__(
        self,
        fname,
        data,
        convert_dates=None,
        write_index=True,
        encoding="latin-1",
        byteorder=None,
        time_stamp=None,
        data_label=None,
        variable_labels=None,
            *args,
            **kwargs
    ):
        from pandas.io.stata import StataWriter as pdStataWriter
        self.file=pdStataWriter(fname=fname,
        data=data,
        convert_dates=convert_dates,
        write_index=write_index,
        encoding=encoding,
        byteorder=byteorder,
        time_stamp=time_stamp,
        data_label=data_label,
        variable_labels=variable_labels,
            *args,
            **kwargs)

    def write_file(self):
        self.file.write_file()