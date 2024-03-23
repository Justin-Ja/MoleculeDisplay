# MoleculeDisplay

## Running the program
This example assumes you are on Linux

First, ensure that you have python3.8 downloaded. 
You can use other versions of Python (Above 2.7) but you will have to edit the makefile yourself (Replace all 3.8 with whatever version you want).
Next, you'll need to set the library path to check the current folder for .so files.
Run the following to do that (assuming you are in the folder containing all the source files):
```
export LD_LIBRARY_PATH=.
```
Next you'll need to compile the C files and make the .so files with
```
make all
```
Finally, you're ready to start up the server! Use the following:
```
python3 server.py 3000
```
Note that you can pass in any integer value for the port (Don't be dumb and use a low port like 80 and interfere with other services)
To actually access the webpage you'll need to head to the following link (assuming port = 3000)

> localhost:3000/home.html

Finally when you are all done, you can clean up temporary files with the following:
```
make clean
```

## Description
A fullstack project that allows a user to display and rotate a molecule in 3D.

This web app allows the user to upload a .sdf file to be saved within the database.
The user can also fill out a form to color each element to be a specific color.
Finally the user can display the molecule and then rotate it in three dimensions.

Example image of a caffiene moecule that the app would display:
![Caffeine](https://github.com/Justin-Ja/MoleculeDisplay/assets/95664856/0a599951-6ceb-4813-b019-d68e53eb1b8b)

##Issues and Problems

Not sure how or what happened, but some features have become debunked. Might have happened when changing python version, but app isn't fully working as intended :(
Filename and name of the uploaded molecule don't work and are hardcoded for the caffeine file right now. 

