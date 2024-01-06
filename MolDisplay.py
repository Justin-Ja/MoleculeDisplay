#Global vars/dictionaries
import molecule;

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">""";

footer = """</svg>""";

offsetx = 500;
offsety = 500;

class Atom:
    #Constructor class
    def __init__ (self, atom):
        self.atom = atom;
        self.z = atom.z;

    #For debugging purposes
    def __str__ (self):
        return '''%s %f %f %f\n''' % (self.atom.element, self.atom.x, self.atom.y, self.z);

    #Returns an SVG string
    def svg(self):
        xSVG = ((self.atom.x * 100.0) + offsetx);
        ySVG = ((self.atom.y * 100.0) + offsety);
        try:
            radi = radius[self.atom.element];
        except:
            radi = 20;
            print("Bad radius, using default\n");
        try:
            colour = element_name[self.atom.element];
        except:
            print("Bad colour, using default\n");
            colour = "black";
            return' <circle cx="%.2f" cy="%.2f" r="%d" fill="%s"/>\n' % (xSVG, ySVG, radi, colour)

        return """'  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n'""" % (xSVG, ySVG, radi, colour);

class Bond:
    def __init__(self, bond):
        self.bond = bond;
        self.z = bond.z;

    def __str__ (self):
        return ''' %d %d %d %f %f %f %f %f %f %f %f\n\n''' % (self.bond.a1, self.bond.a2, self.bond.epairs,
            self.bond.x1, self.bond.x2, self.bond.y1, self.bond.y2, self.z, self.bond.len, self.bond.dx, self.bond.dy);

    def svg(self):
        #Use all combinations of x1,x2,y1,y2, may have to update values ot include dx somehow
        x1 = ((self.bond.x1 * 100.0) + offsetx);
        x2 = ((self.bond.x2 * 100.0) + offsetx);
        y1 = (((self.bond.y1 * 100.0) + offsety));
        y2 = (((self.bond.y2 * 100.0) + offsety));


        if self.bond.epairs == 0:
            colour = "limegreen";
        elif self.bond.epairs == 1:
            colour = "forestgreen";
        else:
            colour = "olive";

        return """'  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="%s"/>\n'""" % (
         (x1 + self.bond.dy * 10), (y1 - self.bond.dx * 10), (x1 - self.bond.dy * 10), (y1 + self.bond.dx * 10),
         (x2 - self.bond.dy * 10), (y2 + self.bond.dx * 10), (x2 + self.bond.dy * 10), (y2 - self.bond.dx * 10), colour);

class Molecule (molecule.molecule):
    def __str__ (self):
        return '''%d %d ''' % (int(self.atom_no), int(self.bond_no));

    def svg(self):
        str = header;
        atomsI = int(0);
        bondsI = int(0);
        #Append atom and bond svg's strings

        #Loop until we reach atomsI or bondsI
        while atomsI < self.atom_no and bondsI < self.bond_no:
            if Atom(self.get_atom(atomsI)).z < Bond(self.get_bond(bondsI)).z:
                str = str + Atom(self.get_atom(atomsI)).svg();
                atomsI = atomsI + 1;
            else: #bond.z < atom.z
                str = str + Bond(self.get_bond(bondsI)).svg()
                bondsI = bondsI + 1;

        #Get the rest of the atoms or bonds
        while atomsI < self.atom_no:
            str = str + Atom(self.get_atom(atomsI)).svg();
            atomsI = atomsI + 1;

        while bondsI < self.bond_no:
            str = str + Bond(self.get_bond(bondsI)).svg()
            bondsI = bondsI + 1;

        str = str + footer;
        return str;

    def parse(self, file_obj):
        #mol = molecule.molecue();
        lines = "";
        numAtoms = int(0);
        numBonds = int(0);

        #Read file, call append atom/bond
        #First skip first 3 lines
        for i in range(3):
            lines = file_obj.readline();

        #Get number of atoms and bonds
        lines = file_obj.readline();
        lines = " ".join(lines.split()); #removes duplicate spaces
        field = lines.split(); #splits into str arr based on where spaces are
        numAtoms = int(field[0]);
        numBonds = int(field[1]);

        #Appending all of the atoms
        for i in range(numAtoms):
            lines = file_obj.readline();
            lines = " ".join(lines.split());
            field = lines.split();
            #field 0-3 represent x,y,z and element symbol
            self.append_atom(field[3], float(field[0]), float(field[1]), float(field[2]));

        for i in range(numBonds):
            lines = file_obj.readline();
            lines = " ".join(lines.split());
            field = lines.split();
            self.append_bond((int(field[0]) - 1), (int(field[1]) - 1), (int(field[2]) - 1));

        return;

if __name__ == "__main__":
    mol = Molecule(); # create a new molecule object
    # create 3 atoms
    # mol.append_atom( "O", 2.5369, -0.1550, 0.0000 );
    # mol.append_atom( "H", 0.5, 0, 0.0000 );
    # mol.append_atom( "H", -0.5, 0, 0.0000 );
    # mol.append_atom( "C", 0, 2, 0.0000 );
    # mol.append_atom( "N", 0, -2, 0.0000 );
    # #
    # # # caution atom references in append_bond start at 1 NOT 0
    # mol.append_bond( 1, 2, 1 );
    # mol.append_bond( 3, 4, 1 );
    # mol.append_bond( 1, 3, 1 );
    #
    # for i in range(3):
    # 	#atom = mol.get_atom(i);
    # 	atom = Atom(mol.get_atom(i))
    # 	print(atom.__str__())
    # 	print(atom.svg())
    # 	#print( atom.element, atom.x, atom.y, atom.z );
    #
    # for i in range(2):
    # 	#bond = mol.get_bond(i);
    # 	bond = Bond(mol.get_bond(i))
    # 	print(bond.__str__())
    # 	print(bond.svg());


    # BE CAREFUL: PARSING A FILE WITH ADD ONTO THE PREVIOUS ATOMS AND BONDS ADDED ABOVE!!
    # file1 = open("water-3D-structure-CT1000292221.sdf", "r");
    # mol.parse(file1);
    # file1.close();

    # file2 = open("CID_31260.sdf", "r");
    # mol.parse(file2);
    # file2.close();
    file3 = open("caffeine-3D-structure-CT1001987571.sdf", "r");
    mol.parse(file3);
    file3.close();

    print(mol);
    mol.sort();
    print("\n\n\n");
    print(mol.svg());

    # print(molecule.molecule.atom_max);
    # print(molecule.molecule.atom_no);
    # print(type(molecule.molecule.atom_max), type(molecule.molecule.atom_no));
    # print(test);
    # print(dir(molecule));
    # print("\n\n\n\n\n");
    # print(dir(molecule.molecule));
