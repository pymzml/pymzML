Implementing an own file class
===============================

In  order to make pymzML accept other kinds of mzML data (e.g databases), one can 
implement an own wrapper similiar to the ones discussed before.
In the following, an example for building and accessing a SQL database containing single spectra will be shown.


Creating the wrapper
---------------------

At first, a database with a specific layout needs to be created. Here, we use a single mzML file and store each spectrum in a table with 2 columns, one for the identifier and one for the xml element of the spectrum in form of a string.

Database creation::
    
    import sqlite3
    import os
    from pymzml import spec
    from pymzml.run import Reader

    def create_database_from_file(db_name, mzml_path):
        conn = sqlite3.connect(db_name+'.db')
        Run = Reader(os.path.abspath(mzml_path))
        with conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE Spectra(ID INT, xml TEXT)")
            for spec in Run:
                params = (spec.ID, spec.to_string())
                cursor.execute("INSERT INTO Spectra VALUES(?, ?)", params)
        return True

After this, we need to implement a class, which needs to implement the __getitem__ function for random access, and 
a read function used to sequentiallly read in data for iterating the database.
In this simple approach, the read function always returns a whole spectra xml string.
One obvious optimization would be, to read in smaller chunks of a spec string and jump to the next spectrum, as soon as the end of the current spectrum is reached (as exercise for the interested reader ;) ) .

Wrapper for accessing the database::

    import sqlite3
    import os
    from pymzml import spec
    import xml.etree.ElementTree as et
    from pymzml.run import Reader

    class SQLiteDatabase(object):
        """
        Example implementation of a database Connector,
        which can be used to make run accept paths to
        sqlite db files.

        We initialize with a path to a database and implement
        a custom __getitem__ function to retrieve the spectra
        """
        def __init__(self, path):
            """
            """
            connection = sqlite3.connect(path)
            self.cursor = connection.cursor()
            self.curr_spec_id = 0

        def __getitem__(self, key):
            """
            """
            self.cursor.execute('SELECT * FROM spectra WHERE id=?', key)
            ID, element = self.cursor.fetchone()
            
            element = et.XML(element)
            if 'spectrum' in element.tag:
                spectrum = spec.Spectrum(element)
            elif 'chromatogram' in element.tag:
                spectrum = spec.Chromatogram(element)
            return spectrum

        def get_spectrum_count(self):
            self.cursor.execute("SELECT COUNT(*) from spectra")
            num = self.cursor.fetchone()[0]
            return num

        def read(self, size=-1):
            # implement read so it starts reading in first ID,
            # if end reached switches to next id and so on ...
            key = self.current_spectrum_id
            self.cursor.execute('SELECT * FROM spectra WHERE id=?', key)
            ID, element = self.cursor.fetchone()[0]
            self.current_spectrum_id += 1
            return element

    if __name__ == '__main__':
        # This is what the Reader class does
        my_iter = iter(et.iterparse(SQLiteDatabase('test.db')))
        # Now you can iter your database
        for x in my_iter:
            print(x)

        # Retrieve a specific spectrum from your database
        db = SQLiteDatabase('test.db')
        unique_id = 5
        my_spec = db[unique_id]



Enabling the wrapper
----------------------

In order to allow pymzML to use this new file class, the filehandler needs to be able to detect when to use this class.
The easiest way is, to add another elif statement which decides which handler to use based on the file path.
For this, edit the :py:func:`~pymzml.file_interface.FileInterface._open` method as shown in the following:


Code::
 
    def _open(self, path):
        """
        Open a file like object resp. a wrapper for a file like object.

        Arguments:
            path (str): path to the mzml file

        Returns:
            file_handler: instance of 
            :py:class:`~pymzml.file_classes.standardGzip.StandardGzip`,
            :py:class:`~pymzml.file_classes.indexedGzip.IndexedGzip` or
            :py:class:`~pymzml.file_classes.standardMzml.StandardMzml`, 
            based on the file ending of 'path'
        """
        if path.endswith('.gz'):
            if self._indexed_gzip(path):
                # set offset_names and self.offsets
                self.file_handler = indexedGzip.IndexedGzip(path, self.encoding)
                # for k, v in self.file_handler.index.items():
                #     self.offset_names.append( k )
                #     self.offsets.append( v )
                # self.offset_names   = [key for key in ra_reader.index.keys()]
                # self.offsets        = [off for off in ra_reader.index.values()]
                #, self.as_numpy
            else:
                self.file_handler = standardGzip.StandardGzip(path, self.encoding)
        # add your new elif statement here
        elif path.endswith('db'):
            from SQLiteConnector import SQLiteDatabase
            self.file_handler = SQLiteDatabase(path, encoding)
        else:
            self.file_handler     = standardMzml.StandardMzml(path, self.encoding)
        return self.file_handler

