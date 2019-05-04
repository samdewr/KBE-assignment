# KBE_Assignment
This is the KBE application developed by Sam de Wringer and Roel Thijssen 
for the course in Knowledge Based Engineering at the Delft University of 
Technology. 

The main goal of this KBE application is to optimise the fuel tank 
scheduling of a parametric aircraft model, such that the trim drag of the 
aircraft is minimised. That is, this app sets a fuel tank as the fuel tank 
that is used as an engine fuel supplier during the next time interval in 
such a way, that the c.g. range of the aircraft is minimised. As a result 
hereof, the trim drag is minimised. 

Moreover, an integral main wing placement and horizontal tail sizing 
algorithm is included in the app. That is, given certain main wing and 
horizontal tail parameters, the app places the main wing in the longitudinal
position that renders the smallest horizontal tail surface. Subsequently, 
the horizontal tail surface is adjusted in such a way, that it meets the 
tail surface requirement.

![Box-wing aircraft](https://lessonslearned.faa.gov/AirTransat236/Fuel_tanks.jpg)

## Usage 
The KBE app can be run by:
 1. Specifying an aircraft geometry in the`input/aircraft_config.xlsx` Excel
 file. Each variable is described extensively here.
 1. Run the `main` object 
**TODO FINISH THIS PART**.

## Program elements
### Airfoils
Airfoils can be specified in the `airfoils` folder. Accepted inputs are `.dat`
files, where the airfoil coordinates are:
1. Normalised (`x/c`, `y/c`)
1. Running from trailing edge over the upper surface, then lower surface back
to the trailing edge again. 

### Documentation
The `sphinx` auto-generated documentation for this application can be found 
in the `docs` folder. Specifically, in `docs/build/html`, the `.html` pages 
can be found. 

### Input
The `input` folder contains the Excel files which can be used for inputting 
aircraft geometries, specifying constants, etc. These files will then be 
read in the appropriate classes in the application.

### Tools
The `tools` folder contains some generic tools which are used throughout the
program. These tools include a tool for generating NACA airfoil coordinates 
from a NACA name specification and a wrapper utility for AVL in ParaPy.

### ParaPy aircraft classes
ParaPy aircraft classes are structured in several folders, such as 
`wing_primitives` and **SHOULD ADD THE APPROPRIATE AIRCRAFT AND FUSELAGE 
FOLDERS HERE**. The folder names are rather self-explanatory. For a more 
specific description of what the application can do, and which aircraft 
parts and objects have been included, see 

## Description
Currently, the application supports conventional aircraft configurations and
box-wing aircraft configurations. Moreover, the wing structural elements 
that are incorporated are:
* Leading edge riblets
* Wing-box ribs
* Trailing edge riblets
* Spars (they *always* run from the root until a specified spanwise 
stopping point)

![Spar](https://qph.fs.quoracdn.net/main-qimg-534e03e3d6f8c2ad03815320c2accc64)

Other objects contained in the wing are:
* Fuel tanks (defined by the starting and ending wing-box ribs, always 
running from the front to the rear spar)
* Fuel (contained within a fuel tank)

![Fuel tanks](https://i.stack.imgur.com/3dKuE.jpg)

Moreover, a generic "movable" class has been implemented. This movable may 
represent either a flap, rudder, aileron, etc. due to its simplicity.
 

 
## Requirements
* Python 2.7
* ParaPy 1.3.0
* parapy-lib-avl 1.1.4
* parapy-lib-cst 1.0.1
* parapy-lib-xfoil 1.0.1
* wheel 0.30.0
* OCC 7.1.0.5
* KBEUtilities 0.1.0
* wxPython-common 3.0.2.0
* wxPython 3.0.2.0
* numpy 1.16.2
* matplotlib 2.2.2
* pandas 0.24.2
 
## Project structure
```
│   .gitattributes
│   .gitignore
│   README.md
│
├───.idea
│   │   assignment.iml
│   │   encodings.xml
│   │   misc.xml
│   │   modules.xml
│   │   vcs.xml
│   │   workspace.xml
│   │
│   ├───dictionaries
│   │       TUDelft_SID.xml
│   │
│   └───inspectionProfiles
│           Project_Default.xml
│
├───aircraft
│   │   aircraft.py
│   │
│   ├───analysis
│   │       scissor_plot.py
│   │       __init__.py
│   │
│   ├───engines
│   │       engine.py
│   │       __init__.py
│   │
│   ├───fuselage_primitives
│   │       cabin.py
│   │       fuselage.py
│   │       nose.py
│   │       tail.py
│   │
│   └───wing_primitives
│       │
│       ├───external
│       │       airfoil.py
│       │       connecting_element.py
│       │       lifting_surface.py
│       │       movable.py
│       │       wing.py
│       │       __init__.py
│       │
│       ├───fuel
│       │       fuel.py
│       │       fuel_tank.py
│       │
│       └───structural_elements
│               rib.py
│               rib_backup.py
│               spar.py
│               __init__.py
│
├───airfoils
│       whitcomb.dat
│
├───docs
│       ...
│   
├───input
│       aircraft_config.xlsx
│       constants.xlsx
│
├───output
│       ... 
│
└───tools
        naca.py
```