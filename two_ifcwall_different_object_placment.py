# -*- coding: utf-8 -*-

#### code from https://blenderbim.org/docs-python/ifcopenshell-python/code_examples.html#create-a-simple-model-from-scratch
#### and from here https://github.com/C-Claus/BlenderScripts/blob/master/BlenderBIMGrid/create_grid_with_slabs_and_walls.py


import ifcopenshell
from ifcopenshell.api import run
import bpy


#######################################################################################################
###################################   Config parameters   #############################################
#######################################################################################################
filename                    = "\demo.ifc"
folder_path                 = r"C:\Users\martin"
length                      =1
height                      =0.1
thickness                   =0.2
wall_count                  =3


# Create a blank model
model = ifcopenshell.file()

# All projects must have one IFC Project element
project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")

# Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
# Assigning without arguments defaults to metric units
run("unit.assign_unit", model, length = {"is_metric": True, "raw": "METERS"})

# Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
context = run("context.add_context", model, context_type="Model")
# In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
body = run(
    "context.add_context", model,
    context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", 
)

# Create a site, building, and storey. Many hierarchies are possible.
site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")
building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

# Since the site is our top level location, assign it to the project
# Then place our building on the site, and our storey in the building
run("aggregate.assign_object", model, relating_object=project, product=site)
run("aggregate.assign_object", model, relating_object=site, product=building)
run("aggregate.assign_object", model, relating_object=building, product=storey)


# Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
representation = run("geometry.add_wall_representation", model, context=body, length=length, height=height, thickness=thickness)


zdir = model.createIfcDirection((0.0, 0.0, 1.0))
xdir = model.createIfcDirection((1.0, 0.0, 0.0))


for i in range(wall_count):   
    # Let's create a new wall
    wall = run("root.create_entity", model, ifc_class="IfcWall")
    
    # Assign our new body geometry back to our wall
    run("geometry.assign_representation", model, product=wall, representation=representation)
    
    # Place our wall in the ground floor
    run("spatial.assign_container", model, relating_structure=storey, product=wall)
    origin = model.createIfcAxis2Placement3D(
                model.createIfcCartesianPoint((0.0, 0.0, float(i))),
                zdir,
                xdir,
            )
    placement = model.createIfcLocalPlacement(None, origin)

    wall.ObjectPlacement = placement
             
#########################################################
### Removing the IFC from BlenderBIM and reloading it ###
#########################################################

file_path = (folder_path + filename)
model.write(file_path)

def load_ifc_automatically():

    if (bool(model)) == True:
        project = model.by_type('IfcProject')
        
        if project is not None:
            for i in project:
                collection_name = 'IfcProject/' + i.Name
                
            collection = bpy.data.collections.get(str(collection_name))
             
            if collection is not None:
                for obj in collection.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                    
                bpy.data.collections.remove(collection)
                
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)         
        bpy.ops.bim.load_project(filepath=file_path)
               
load_ifc_automatically()
