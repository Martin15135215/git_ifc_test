import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings



class Obj2Ifc:
  
        
    def execute(self, path,  faces, vertices):
        ifc_faces = []
        for face in faces:
            ifc_faces.append(self.file.createIfcFace([self.file.createIfcFaceOuterBound(self.file.createIfcPolyLoop([self.file.createIfcCartesianPoint(vertices[index]) for index in face]),True,)]))
        representation = self.file.createIfcProductDefinitionShape(None,None,[self.file.createIfcShapeRepresentation(self.context,"Body","Brep",[self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(ifc_faces))],)],)
        
        product = self.file.create_entity(
            "IfcBuildingElementProxy",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "Name": path.split(".")[0],
                "ObjectPlacement": self.placement,
                "Representation": representation,
            }
        )
        ifcopenshell.api.run("spatial.assign_container", self.file, product=product, relating_structure=self.storey)
        #self.file.write("testest" + ".ifc")

    

    def create_ifc_file(self):
        self.file = ifcopenshell.api.run("project.create_file", version="IFC4")
        person = ifcopenshell.api.run("owner.add_person", self.file)
        person[0] = person.GivenName = None
        person.FamilyName = "user"
        org = ifcopenshell.api.run("owner.add_organisation", self.file)
        org[0] = None
        org.Name = "template"
        user = ifcopenshell.api.run("owner.add_person_and_organisation", self.file, person=person, organisation=org)
        application = ifcopenshell.api.run("owner.add_application", self.file)
        ifcopenshell.api.owner.settings.get_user = lambda ifc: user
        ifcopenshell.api.owner.settings.get_application = lambda ifc: application
        self.basename = "hallo"
        project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name=self.basename)
        lengthunit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", name="METRE")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[lengthunit])
        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        self.context = ifcopenshell.api.run(
            "context.add_context",
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )
        site = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite", name="My Site")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding", name="My Building")
        self.storey = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcBuildingStorey", name="My Storey"
        )
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=site, relating_object=project)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=building, relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=self.storey, relating_object=building)

        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
        self.placement = self.file.createIfcLocalPlacement(None, self.origin)
        self.history = ifcopenshell.api.run("owner.create_owner_history", self.file)
