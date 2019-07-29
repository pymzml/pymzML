import sqlite3
import xml.etree.ElementTree as et
from pymzml import spec
from pymzml.run import Reader


def create_database_from_file(db_name, file_path):
    conn = sqlite3.connect(db_name + ".db")
    Run = Reader("./tests/data/example.mzML")
    with conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE Spectra(ID INT, xml TEXT)")
        for spectrum in Run:
            params = (spectrum.ID, spectrum.to_string())
            cursor.execute("INSERT INTO Spectra VALUES(?, ?)", params)
    return True


class SQLiteDatabase(object):
    """
    Example implementation of a database Connector,
    which can be used to make :py:func:`pymzml.run.Reader` accept paths to
    sqlite db files.

    We initialize with a path to a database and implement
    a custom __getitem__ function to retrieve the spectra
    """

    def __init__(self, path):
        """
        """
        connection = sqlite3.connect(path)
        self.cursor = connection.cursor()

    def __getitem__(self, key):
        """
        Execute a SQL request, process the data and return a spectrum object.

        Args:
            key (str or int): unique identifier for the given spectrum in the
            database
        """
        self.cursor.execute("SELECT * FROM spectra WHERE id=?", key)
        ID, element = self.cursor.fetchone()

        element = et.XML(element)
        if "spectrum" in element.tag:
            spectrum = spec.Spectrum(element)
        elif "chromatogram" in element.tag:
            spectrum = spec.Chromatogram(element)
        return spectrum

    def get_spectrum_count(self):
        self.cursor.execute("SELECT COUNT(*) from spectra")
        num = self.cursor.fetchone()[0]
        return num

    def read(self, size=-1):
        # implement read so it starts reading in first ID,
        # if end reached switches to next id and so on ...

        return '<spectrum index="0" id="controllerType=0 controllerNumber=1 scan=1" defaultArrayLength="917"></spectrum>\n'


if __name__ == "__main__":
    # This is what the Reader class does
    my_iter = iter(et.iterparse(SQLiteDatabase("test.db")))
    # Now you can iter your database
    for x in my_iter:
        print(x)

    # Retrieve a specific spectrum from your database
    db = SQLiteDatabase("test.db")
    unique_id = 5
    my_spec = db[unique_id]
