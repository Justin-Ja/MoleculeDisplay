import os;
import sqlite3;
import MolDisplay;

class Database:

    #Constructor, reset determines whether to start with a new DB or not
    def __init__(self, reset=False):
        if(reset == True):
            if(os.path.exists("database.db")):
                os.remove("database.db");

        self.conn = sqlite3.connect("database.db");

    #Method for setting up all tables
    def create_tables(self):
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Elements(
                        ELEMENT_NO   INTEGER     NOT NULL,
                        ELEMENT_CODE VARCHAR(3)  NOT NULL,
                        ELEMENT_NAME VARCHAR(32) NOT NULL,
                        COLOUR1      CHAR(6)     NOT NULL,
                        COLOUR2      CHAR(6)     NOT NULL,
                        COLOUR3      CHAR(6)     NOT NULL,
                        RADIUS       DECIMAL(3)  NOT NULL,
                        PRIMARY KEY (ELEMENT_NAME) );""");

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Atoms(
                        ATOM_ID      INTEGER      PRIMARY KEY,
                        ELEMENT_CODE VARCHAR(3)   NOT NULL,
                        X            DECIMAL(7,4) NOT NULL,
                        Y            DECIMAL(7,4) NOT NULL,
                        Z            DECIMAL(7,4) NOT NULL,
                        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements );""");

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Bonds(
                        BOND_ID INTEGER PRIMARY KEY,
                        A1      INTEGER NOT NULL,
                        A2      INTEGER NOT NULL,
                        EPAIRS  INTEGER NOT NULL);""");

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Molecules(
                        MOLECULE_ID INTEGER PRIMARY KEY,
                        NAME        TEXT    NOT NULL UNIQUE);""");

        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeAtom(
                        MOLECULE_ID INTEGER NOT NULL,
                        ATOM_ID     INTEGER NOT NULL,
                        PRIMARY KEY (MOLECULE_ID, ATOM_ID)
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules
                        FOREIGN key (ATOM_ID)     REFERENCES Atoms);""");

        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeBond(
                        MOLECULE_ID INTEGER NOT NULL,
                        BOND_ID     INTEGER NOT NULL,
                        PRIMARY KEY (MOLECULE_ID, BOND_ID)
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules
                        FOREIGN key (BOND_ID)     REFERENCES BOND);""");

    def __setitem__(self, table, values):
        #ALL VALUES TO BE SET IN ROW MUST BE IN VALUES ELSE THERE WILL BE BUG
        sqlStr = ''' INSERT INTO %s VALUES(''' % (table);

        length = len(values);
        for i in range(length):
            if(i + 1 == length):
                sqlStr = sqlStr + "?)";
            else:
                sqlStr = sqlStr + "?, ";

        self.conn.execute(sqlStr, values);
        self.conn.execute("COMMIT;");

    def add_atom(self, molname, atom):
        #insert information into Atoms Table
        sqlStr = ''' INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?); ''';
        data = (atom.atom.element, atom.atom.x, atom.atom.y, atom.z);
        self.conn.execute(sqlStr, data);

        #Grab IDs from atom and Molecules tables
        molID = self.conn.execute("SELECT Molecules.MOLECULE_ID FROM Molecules WHERE Molecules.NAME=?", (molname,));
        atomID = self.conn.execute('''SELECT Atoms.ATOM_ID FROM Atoms WHERE
                                   Atoms.ELEMENT_CODE=? AND Atoms.X=? AND Atoms.Y=? AND Atoms.z=?'''
                                   , (atom.atom.element, atom.atom.x, atom.atom.y, atom.z));

        #Set id's into M0leculeAtom Table
        sqlStr2 = ''' INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)''';
        data2 = (molID.fetchone()[0], atomID.fetchone()[0]);
        self.conn.execute(sqlStr2, data2);

    def add_bond(self, molname, bond):
        sqlStr = ''' INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?); ''';
        data = (bond.bond.a1, bond.bond.a2, bond.bond.epairs);
        self.conn.execute(sqlStr, data);

        molID = self.conn.execute("SELECT Molecules.MOLECULE_ID FROM Molecules WHERE Molecules.NAME=?", (molname,));
        bondID = self.conn.execute('''SELECT Bonds.BOND_ID FROM Bonds WHERE
                                   Bonds.A1=? AND Bonds.A2=? AND Bonds.EPAIRS=?'''
                                   , (bond.bond.a1, bond.bond.a2, bond.bond.epairs));

        sqlStr2 = '''INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)''';
        data2 = (molID.fetchone()[0], bondID.fetchone()[0]);
        self.conn.execute(sqlStr2, data2);

    #Adds a molecule and its associated atoms/bonds to the database
    def add_molecule(self, name, fp):
        mol = MolDisplay.Molecule();
        mol.parse(fp);
        tempTuple = (name,);
        self.conn.execute(''' INSERT INTO Molecules (NAME) VALUES(?);''', (tempTuple));

        for i in range(mol.atom_no):
            atom = MolDisplay.Atom(mol.get_atom(i));
            self.add_atom(name, atom);

        for i in range(mol.bond_no):
            bond = MolDisplay.Bond(mol.get_bond(i));
            self.add_bond(name, bond);

        self.conn.execute("""COMMIT;""");

    #Loads all atoms and bonds related to a molecule and returns a Molecule() object
    def load_mol(self, name):
        mol = MolDisplay.Molecule();
        #GET MOLECULE_ID FROM Name in Molecules, get Atom_ID from Mol_ID From MoleculeAtom, get atoms in order from ATOMS
        cursor = self.conn.execute("""SELECT * FROM Atoms
                             INNER JOIN MoleculeAtom
                             ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                             WHERE MoleculeAtom.MOLECULE_ID = (
                             SELECT Molecules.MOLECULE_ID FROM Molecules WHERE NAME = ?
                             )""", (name,));

        temp = cursor.fetchall();
        #Append atoms
        for i in range(len(temp)):
            mol.append_atom(temp[i][1], temp[i][2], temp[i][3], temp[i][4]);
            #atom = MolDisplay.Atom(mol.get_atom(i));

        cursor = self.conn.execute("""SELECT * FROM Bonds
                                  INNER JOIN MoleculeBond
                                  ON MoleculeBond.BOND_ID = Bonds.BOND_ID
                                  WHERE MoleculeBond.MOLECULE_ID = (
                                  SELECT Molecules.MOLECULE_ID FROM Molecules WHERE NAME = ?
                                  )""", (name,));

        temp = cursor.fetchall();
        for i in range(len(temp)):
            mol.append_bond(temp[i][1], temp[i][2], temp[i][3]);

        return mol;

    #Returns a radius dict
    def radius(self):
        radiusDict = {};

        #Grab a list of both radi and elements in current database from Elements table
        #tempCursor = self.conn.execute("""SELECT RADIUS FROM Elements""");
        #radi = tempCursor.fetchall();
        tempCursor = self.conn.execute("""SELECT ELEMENT_CODE FROM Elements""");
        elementCodes = tempCursor.fetchall();

        length = len(elementCodes);
        for i in range(length):
            tempCursor = self.conn.execute(""" SELECT RADIUS FROM Elements WHERE ELEMENT_CODE=?""", (elementCodes[i]) );
            radi = tempCursor.fetchall();
            radiusDict[ (elementCodes[i][0]) ] = radi[0][0];

        return radiusDict;

    #Returns a dict of element codes to element names
    def element_name(self):
        nameDict = {};

        tempCursor = self.conn.execute("""SELECT ELEMENT_CODE FROM Elements""");
        elementCodes = tempCursor.fetchall();
        
        length = len(elementCodes);
        for i in range(length):
            tempCursor = self.conn.execute("""SELECT ELEMENT_NAME FROM Elements WHERE ELEMENT_CODE=?""", (elementCodes[i]) );
            names = tempCursor.fetchall();
            nameDict[ elementCodes[i][0] ] = names[0][0];

        return nameDict;

    #Returns a svg string of radial gradients of all molecules
    def radial_gradients(self):
        #For each element in Elements, fill out string
        finalSVGStr = """""";
        tempCursor = self.conn.execute("""SELECT ELEMENT_CODE FROM Elements""");
        elementCodes = tempCursor.fetchall();

        for i in range(len(elementCodes)):
            cursor = self.conn.execute("""SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3
                                          FROM Elements WHERE ELEMENT_CODE=?""", (elementCodes[i]));
            names = cursor.fetchall();
            #Fill out string header. Colour will always have 3 numbers so can hardcode it
            finalSVGStr = finalSVGStr + """
<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
    <stop offset="0%%" stop-color="#%s"/>
    <stop offset="50%%" stop-color="#%s"/>
    <stop offset="100%%" stop-color="#%s"/>
</radialGradient>""" % (names[0][0], names[0][1], names[0][2], names[0][3]);

        return finalSVGStr;


if __name__ == "__main__":
    print("Hello World!");
    # db = Database(reset=False); # or use default
    # db.create_tables();

    db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
    db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
    db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
    db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );

    # fp = open( 'water-3D-structure-CT1000292221.sdf' );
    # db.add_molecule( 'Water', fp );
    # fp = open( 'caffeine-3D-structure-CT1001987571.sdf' );
    # db.add_molecule( 'Caffeine', fp );
    # fp = open( 'CID_31260.sdf' );
    # db.add_molecule( 'Isopentanol', fp );

    # display tables
    print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
    # print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() );
    # print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() );
    # print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() );
    # print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() );
    # print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() );

    # MolDisplay.radius = db.radius();
    # MolDisplay.element_name = db.element_name();
    # MolDisplay.header += db.radial_gradients();
    #
    # print(MolDisplay.radius, MolDisplay.element_name, MolDisplay.header)
    # #
    # for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
    #     mol = db.load_mol( molecule );
    #     mol.sort();
    #
    #     fp = open( molecule + ".svg", "w" );
    #     fp.write( mol.svg() );
    #     fp.close();
