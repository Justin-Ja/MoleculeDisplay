#include "mol.h"

//Copies info from x,y,z and element into the atom stored at atom
//X,Y,Z,Element -> ATOM
void atomset( atom *atom, char element[3], double* x, double *y, double *z ){
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
    strcpy(atom->element, element);
}

//Copies the values in the atom (stored at atom) to the locations pointed at by element, z,y,x
//ATOM -> Element, x, y, z
void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

//Copies the values from arguments a1,a2 and pairs into BOND
//Variables -> BOND
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;
    compute_coords(bond);
}

//Copies the bond information into the argument variables
//BOND -> Values/Variables
//TODO: IS there more to be updated here? idk
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs ){
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
}

void compute_coords( bond *bond ){
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;
    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;
    bond->z = ((bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2.0);

    bond->len = sqrt(pow((bond->x2 - bond->x1), 2) + pow((bond->y2 - bond->y1), 2));

    bond->dx = (bond->atoms[bond->a2].x - bond->atoms[bond->a1].x) / bond->len;
    bond->dy = (bond->atoms[bond->a2].y - bond->atoms[bond->a1].y) / bond->len;
}


//Returns an malloc'd area of memory for a molecule (Creates a new molecule)
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){
    molecule *newMolecule = malloc(sizeof(struct molecule));
    if(newMolecule == NULL){
        return NULL;
    }
    newMolecule->atom_max = atom_max;
    newMolecule->bond_max = bond_max;
    newMolecule->atom_no = 0;
    newMolecule->bond_no = 0;
    newMolecule->atoms = (atom*)malloc(sizeof(struct atom) * atom_max);
    newMolecule->bonds = (bond*)malloc(sizeof(struct bond) * bond_max);
    newMolecule->atom_ptrs = (atom**)malloc(sizeof(struct atom*) * atom_max);
    newMolecule->bond_ptrs = (bond**)malloc(sizeof(struct bond*) * bond_max);
    return newMolecule;
}

//Function creates a deep copy of the src molecule
//Copied pointers are unsorted, ptr[0] -> atom[0] etc
molecule *molcopy( molecule *src ){
    molecule *copy = molmalloc(src->atom_max, src->bond_max);
    if(copy == NULL){
        return NULL;
    }
    copy->atom_no = src->atom_no;
    copy->bond_no = src->bond_no;

    //Set each atom in the array with info from the src, point ptr arrays to coresponding atom
    for(int i = 0; i < copy->atom_no; i++){
        atomset(&copy->atoms[i], src->atoms[i].element, &src->atoms[i].x, &src->atoms[i].y, &src->atoms[i].z);
        copy->atom_ptrs[i] = &copy->atoms[i];
    }
    //Separate array for bonds, otherwise invalid writing occures
    for(int i = 0; i < copy->bond_no; i++){
        bondset(&copy->bonds[i], &src->bonds->a1, &src->bonds[i].a2, &src->atoms, &src->bonds->epairs);
        copy->bond_ptrs[i] = &copy->bonds[i];
    }

    return copy;
}

//Free's a molecule structure starting with inner arrays, then the struct.
void molfree( molecule *ptr ){
    free(ptr->atoms);
    free(ptr->bonds);
    free(ptr->atom_ptrs);
    free(ptr->bond_ptrs);
    free(ptr);
}

//Append a new atom to a molecule's atom list and point to it in the atom_ptr list
//Append atom based on value of atom_no . IF atom_no >= atom_max, realloc more space, then append
void molappend_atom( molecule *molecule, atom *atom ){
    //If there is enough space, append the atom
    if(molecule->atom_no < molecule->atom_max){
        molecule->atoms[molecule->atom_no] = *atom;
        molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
        molecule->atom_no++;
    } else{
        //Re-allocating enough space, recursively call function until it hits the original if statement and exits
        if(molecule->atom_max == 0){
            //Atom_max++, all malloc'd arrays get one extra 'space'
            //With max = 0, no atoms in arrays, no need to recalc pointers
            molecule->atom_max++;
            molecule->atoms = realloc(molecule->atoms, (sizeof(struct atom) * molecule->atom_max));
            molecule->atom_ptrs = realloc(molecule->atom_ptrs, (sizeof(struct atom*) * molecule->atom_max));
            //Realloc failure state
            if(molecule->atoms == NULL || molecule->atom_ptrs == NULL){
                fprintf(stderr, "ERROR: Realloc returned NULL. Failure to reallocate memory for atoms.");
                exit(-1);
            }
            molappend_atom(molecule, atom);
        } else{
            //Atom_max *= 2; All arrays get realloc'd double the space
            molecule->atom_max *= 2;
            molecule->atoms = realloc(molecule->atoms, (sizeof(struct atom) * molecule->atom_max));
            molecule->atom_ptrs = realloc(molecule->atom_ptrs, (sizeof(struct atom*) * molecule->atom_max));
            //Realloc failure state
            if(molecule->atoms == NULL || molecule->atom_ptrs == NULL){
                fprintf(stderr, "ERROR: Realloc returned NULL. Failure to reallocate memory for atoms.");
                exit(-1);
            }
            //Recalcuating pointers
            for(int i = 0; i < molecule->atom_no; i++){
                molecule->atom_ptrs[i] = &molecule->atoms[i];
            }
            molappend_atom(molecule, atom);
        }
    }
    return;
}

//Appends a new Bond to a molecule struct. Same steps as molappend_atom, just with bonds
void molappend_bond( molecule *molecule, bond *bond ){
    //If there is enough space, appen the bond to the molecule struct
    if(molecule->bond_no < molecule->bond_max){
        molecule->bonds[molecule->bond_no] = *bond;
        molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
        molecule->bond_no++;
    } else{
        //Not enough space, re-allocates enough space
        //Recursively call function until it hits the original if statement and exits
        if(molecule->bond_max == 0){
            //Bond_max++, all bond arrays get one extra space
            //With max = 0, no bonds in arrays, no need to recalc pointers (no pointers to recalc)
            molecule->bond_max++;
            molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
            molecule->bond_ptrs = realloc(molecule->bond_ptrs, (sizeof(struct bond*) * molecule->bond_max));
            //Realloc Fail state
            if(molecule->bonds == NULL || molecule->bond_ptrs == NULL){
                fprintf(stderr, "ERROR: Realloc returned NULL. Failure to reallocate memory for bonds.");
                exit(-1);
            }
            molappend_bond(molecule, bond);
        } else{
            //Bond_max *= 2; all bond arrays get double the space
            molecule->bond_max *= 2;
            molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
            molecule->bond_ptrs = realloc(molecule->bond_ptrs, (sizeof(struct bond*) * molecule->bond_max));
            //Realloc Fail state
            if(molecule->bonds == NULL || molecule->bond_ptrs == NULL){
                fprintf(stderr, "ERROR: Realloc returned NULL. Failure to reallocate memory for bonds.");
                exit(-1);
            }
            //Recaculating pointers
            for(int i = 0; i < molecule->bond_no; i++){
                molecule->bond_ptrs[i] = &molecule->bonds[i];
            }
            molappend_bond(molecule, bond);
        }
    }
    return;
}


//Sorting: Pointer 0 will point to smallest z value, Pointer [n-1] should point to greatest z value
//Similar job with BONDS, however, bonds' z value is the average of the 2 atoms z value bonded together
void molsort( molecule *molecule ){
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom*), atomComparator);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond*), bondComparator);
}

int atomComparator(const void *left, const void *right){
    struct atom *leftPtr = *(struct atom **)left;
    struct atom *rightPtr = *(struct atom **)right;

    if(leftPtr->z > rightPtr->z){
        return 1;
    } else if(leftPtr->z < rightPtr->z){
        return -1;
    } else {
        return 0;
    }
}

int bondComparator(const void *left, const void *right){
    struct bond *leftBond = *(struct bond **)left;
    struct bond *rightBond = *(struct bond **)right;

    if(leftBond->z > rightBond->z){
        return 1;
    } else if (leftBond->z < rightBond->z){
        return -1;
    } else{
        return 0;
    }
}

//see lab/wiki article
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rads = deg * (PI / 180.0);
    xform_matrix[0][0] = 1;
    xform_matrix[2][1] = sin(rads);
    xform_matrix[1][2] = -sin(rads);
    for(int i = 1; i <= 2; i++){
        xform_matrix[i][0] = 0;
        xform_matrix[0][i] = 0;
        xform_matrix[i][i] = cos(rads);
    }
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rads = deg * (PI / 180.0);
    xform_matrix[0][0] = cos(rads);
    xform_matrix[0][2] = sin(rads);
    xform_matrix[1][1] = 1;
    xform_matrix[2][0] = -(sin(rads));
    xform_matrix[2][2] = cos(rads);
    for(int i = 0; i <=1; i++){
        xform_matrix[i][i+1] = 0;
        xform_matrix[i+1][i] = 0;
    }
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rads = deg * (PI / 180.0);
    xform_matrix[2][2] = 1;
    xform_matrix[0][1] = -sin(rads);
    xform_matrix[1][0] = sin(rads);
    for(int i = 1; i >=0; i--){
        xform_matrix[2][i] = 0;
        xform_matrix[i][2] = 0;
        xform_matrix[i][i] = cos(rads);
    }
}

//Performs a matrix multiplication on each atom in the molecule's x,y,z coords. AKA rotating the molecule
void mol_xform( molecule *molecule, xform_matrix matrix ){
    float tempX = 0;
    float tempY = 0;
    float tempZ = 0;

    for(int i = 0; i < molecule->atom_no; i++){
        tempX = molecule->atoms[i].x;
        tempY = molecule->atoms[i].y;
        tempZ = molecule->atoms[i].z;

        //Matrix multiplication, row by row
        molecule->atoms[i].x = ((matrix[0][0] * tempX) + (matrix[0][1] * tempY) + (matrix[0][2] * tempZ));
        molecule->atoms[i].y = ((matrix[1][0] * tempX) + (matrix[1][1] * tempY) + (matrix[1][2] * tempZ));
        molecule->atoms[i].z = ((matrix[2][0] * tempX) + (matrix[2][1] * tempY) + (matrix[2][2] * tempZ));
    }

    //Recompute the bond numbers after rotation
    for(int i = 0; i < molecule->bond_no; i++){
        bondset(&molecule->bonds[i], &molecule->bonds[i].a1, &molecule->bonds[i].a2, &molecule->atoms, &molecule->bonds[i].epairs);
        compute_coords(molecule->bond_ptrs[i]);
    }
}
