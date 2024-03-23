import sys;
import io;
import MolDisplay;
import molsql;
import urllib;
import json;
import cgi;
from http.server import HTTPServer, BaseHTTPRequestHandler;


#Class for do_Get and do_POST methods
class MyHandler( BaseHTTPRequestHandler ):

    db = molsql.Database(reset = False);
    db.create_tables();

    molName = "";
    molSVG="";

    publicFiles = [ '/home.html', '/upload.html', '/updateElements.html', '/displayMolecule.html',
    '/style.css', '/scriptUpload.js', '/scriptHome.js', '/scriptDisplay.js', '/scriptUpdateElements.js'];

    def do_GET(self):
        #Serve the home_page html page
        if self.path in self.publicFiles:
            self.send_response(200)

            if self.path == '/style.css':
                self.send_header( "Content-type", "text-css");
            else:
                self.send_header( "Content-type", "text-html");

            fp = open(self.path[1:]);
            page = fp.read();
            fp.close();

            self.send_header("Content-length", len(page));
            self.end_headers();

            self.wfile.write( bytes(page, "utf-8"));

        #404 page response
        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: Page not found", "utf-8" ) );

        #This section of ifs are for any server to js info passing
        #For home.html's list of molecules
        if(self.path == "/fetchData"):
            #Grab info from database before getting file for home
            dbValues = self.get_Molecules();
            responseData = {'value' : dbValues};
            responseBody = json.dumps(responseData).encode("utf-8");

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Send the response back to the client
            self.wfile.write(responseBody)

        #For displayMolecule.html to know what file to display/name of molecule
        elif self.path == "/getDisplay":
            responseData = {'value' : MyHandler.molSVG, 'name' : MyHandler.molName};
            responseBody = json.dumps(responseData).encode("utf-8");

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Send the response back to the client
            self.wfile.write(responseBody)

    def do_POST(self):

        if self.path == "/upload_handler.html":
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);
            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            print(dir(postvars));
            testVar = postvars.values();

            print(dir(testVar))

            molName = postvars.get("name")

            if molName is not None:
                temp = molName[1].split("\n")
                name = temp[2]
                name = name[0:len(name)-1]
            else:
                name = "temp file #" + str(content_length)


            temp2 = postvars.get("filename")
            if temp2 is not None:
                temp2 = temp2[0].split("\n")
                filename = temp2[0]
                filename = filename[1:(len(filename)-2)]
                print(name);
                print(filename);
            else:
                filename = "caffeine-3D-structure-CT1001987571.sdf"

            #Parse file and pass name/file into database
            #HTML makes sure there is at least a file and name inputted
            try:
                fp = open(filename);
                self.db.add_molecule(name, fp);
            except:
                self.send_error(400, "Failed to parse file or this molecule is already in database");


            #Load a success page
            self.send_response( 200 ); # OK
            fp = open("success.html");
            page = fp.read();
            fp.close();

            self.send_header("Content-length", len(page));
            self.end_headers();
            self.wfile.write( bytes(page, "utf-8"));

        #update the element table to add or remove elements
        elif self.path == "/updateElements_handler":
            form = cgi.FieldStorage(
            fp = self.rfile,
            headers = self.headers,
            environ = {'REQUEST_METHOD':'POST'}
            )

            #Depending on value of radio button add (ez with self.db['Elements'] or remove (look it up))
            if form.getvalue('AR-Group') == 'Add':
                c1 = form.getvalue('colour1');
                c1 = c1[1:] #This gets rid of # sign, otherwise there is duplicate # signs in gradient tags
                c2 = form.getvalue('colour2');
                c2 = c2[1:]
                c3 = form.getvalue('colour3');
                c3 = c3[1:]

                try:
                    self.db['Elements'] = (form.getvalue('number'),
                                         form.getvalue('code'),
                                         form.getvalue('name'),
                                         c1,
                                         c2,
                                         c3,
                                         form.getvalue('radius'));
                except:
                    self.send_error(400, "Bad form input OR element is already in database");

            elif form.getvalue('AR-Group') == 'Remove':
                try:
                    self.db.conn.execute("DELETE FROM Elements WHERE ELEMENT_NAME = ?", (form.getvalue('name'),) );
                    self.db.conn.execute("COMMIT;");
                except:
                    self.send_error(400, "Bad form input")
            else:
                print("Somehow you unchecked both radio buttons and broke my website :( \n");
                self.send_error(400, "Submitted form did not check one of the radio buttons");

            print( self.db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
            #self.db.conn.execute("COMMIT;");
            #Load a success page
            self.send_response( 200 ); # OK
            fp = open("success.html");
            page = fp.read();
            fp.close();

            self.send_header("Content-length", len(page));
            self.end_headers();
            self.wfile.write( bytes(page, "utf-8"));


        #Display a molecule/Grab its related svg
        elif self.path == "/display_molecule":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            print(postvars);

            #For some reason form for rotate will always come here (this path). so yeah f me.
            if(len(postvars) != 1):
                self.rotate_Molecule(postvars);
                return;
            else:
                #Get name  from passed info
                try:
                    name = postvars['radio-group'][0];
                except:
                    self.send_error(400, "No molecule was selected to display");
                print(name)
                MyHandler.molName = name;

                MolDisplay.radius = self.db.radius();
                MolDisplay.element_name = self.db.element_name();
                MolDisplay.header += self.db.radial_gradients();

                mol = self.db.load_mol( name );
                mol.sort();

                MyHandler.molSVG = mol.svg()
                #Bring up the displayMolecule.html page
                self.send_response( 200 );
                fp = open("displayMolecule.html");
                page = fp.read();
                fp.close();
                self.send_header("Content-length", len(page));
                self.end_headers();
                self.wfile.write( bytes(page, "utf-8"));

        elif self.path == "/rotate":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            print(postvars, "Am in rotate now");
            self.rotate_Molecule(postvars);

        #Unsure how to 404 a post request but just in case
        else:
            self.send_response(404);
            self.end_headers();
            self.wfile.write( bytes( "404: Page not found", "utf-8"));

    #Grabs all molecules in database to pass to home.html for the form list
    def get_Molecules(self):
        data = [];
        innerData =list(("name", 1, 1));
        i = 0;
        molecules = self.db.conn.execute("SELECT * FROM Molecules" ).fetchall();

        for molecule in molecules:
            mol = self.db.load_mol(molecule[1]);
            innerData[0] = (molecule[1]);
            innerData[1] = (mol.atom_no);
            innerData[2] = (mol.bond_no);
            data[len(data):] = innerData;

        return data;

    #Grab svg for given name, rotate it and redisplay it
    def rotate_Molecule(self, rotationValues):
        try:
            name = rotationValues['molName'][0];
            x = int(rotationValues['Xrot'][0]);
            y = int(rotationValues['Yrot'][0]);
            z = int(rotationValues['Zrot'][0]);
        except:
            self.send_error(400, "No molecule was selected to display");
            return;

        MyHandler.molName = name;
        mol = self.db.load_mol( name );
        mol.sort();

        #Apply rotations for each axis
        if x != 0:
            mx = MolDisplay.molecule.mx_wrapper(x,0,0);
            mol.xform( mx.xform_matrix );

        if y != 0:
            mx = MolDisplay.molecule.mx_wrapper(0,y,0);
            mol.xform( mx.xform_matrix );

        if z != 0:
            mx = MolDisplay.molecule.mx_wrapper(0,0,z);
            mol.xform( mx.xform_matrix );

        mol.sort();
        MyHandler.molSVG = mol.svg();

        self.send_response( 200 );
        fp = open("displayMolecule.html");
        page = fp.read();
        fp.close();
        self.send_header("Content-length", len(page));
        self.end_headers();
        self.wfile.write( bytes(page, "utf-8"));

#Launching of the server, on localhost, on port argv[1], serve forever.
def main():
    try:
        httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
        print("Listening on local port %d, at /home.html" % (int(sys.argv[1])));

        httpd.serve_forever();
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received\nShutting down the server");
        httpd.socket.close();

if __name__ == '__main__':
    main();
