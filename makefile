CC = clang
CFLAGS = -std=c99 -Wall -pedantic -g

all: mol.o libmol.so _molecule.so

clean:
	rm -f *.o *.so testprog molecule_wrap.c molecule.py

#IGNORE WARNING OF UNUSED ARGUMENT -dynamiclib
_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o  -L. -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -l:libmol.so -lpython3.7m -shared  -dynamiclib -o _molecule.so

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -I/usr/include/python3.7m -c molecule_wrap.c -fPIC -o molecule_wrap.o

molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i

libmol.so: mol.o
	$(CC) mol.o -lm -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

# main.o:  main.c mol.h
# 	$(CC) $(FLAGS) -c main.c -o main.o
#
# testprog: main.o libmol.so
# 	$(CC) main.o -L. -l:libmol.so -o testprog
