import omni.ext
import omni.ui as ui
import omni.kit.commands
import omni.replicator.core as rep

from .utils import *
from .const import FIELDS, FieldType


class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[bmw.techoffice.anthonyyaghi.camera_mvt] startup")

        # Register custom randomizers
        from . import custom_nodes

        # Class wide variables
        self.stage = omni.usd.get_context().get_stage()
        self.prims = {}

        # UI
        self._window = ui.Window("Image collector", width=300, height=300)
        with self._window.frame:
            def check(m, error_label:ui.Label, prim: str, validator=None):
                """ 
                This function is called to check that the value of a field is valid and points to a valid prim
                """
                self.prims[prim] = self.stage.GetPrimAtPath(m.get_value_as_string())
                if validator is not None and not validator(self.prims[prim]):
                    error_label.text = "Invalid Object!"
                else:
                    error_label.text = ""

            def val_labeled_field(label: str, type: FieldType, validator=None, prim:str=None):
                """ 
                Create a label and a field of a given type
                """
                # Label-------------Field
                # Error
                with ui.VStack():
                    with ui.HStack(height=15):
                        ui.Label(label)
                        field = FIELDS[type]()
                    error_label = ui.Label("", style={"color": "red"}, height=15)
                
                if validator is not None and prim is not None:
                    field.model.add_value_changed_fn(lambda m, label=error_label: check(m, label, 
                                                                                        validator=validator, prim=prim))
                return field
            
            def multi_labeled_field(label: str, type: FieldType, *args):
                """ 
                Create a label and multiple field of a given type
                """
                # TODO use MultiField instead of manually creating each field (documentation isn't clear yet)
                # *args is here to use with MultiField later on

                # Label
                # Field1---Field2---Field3...
                with ui.VStack():
                    ui.Label(label, height=15)
                    with ui.HStack(height=15, style={"margin": 1}):
                        field = []
                        for _ in args:
                            field.append(FIELDS[type](height=15))
                return field

            # We start by puting everything inside a scrolling frame
            with ui.ScrollingFrame():
                # Vertically stack the different camear movement options in collapsable frames
                # TODO Frame collapse but leaves and empty space behind it, other frames are not moving up...
                # TODO Input validation before allowing OG generation to start (buttons clicked)
                with ui.VStack(style={"margin": 1}):
                    # Circular Path
                    with ui.CollapsableFrame(title="Circular Path"):
                        with ui.VStack(style={"margin": 1}):
                            val_labeled_field("Look At", FieldType.STRING_FIELD, validator=prim_validator, prim="lookat")
                            self.distance_field = val_labeled_field("Distance", FieldType.FLOAT_FIELD)
                            self.elevation_field = val_labeled_field("Elevation", FieldType.FLOAT_FIELD)
                            self.circular_frames_field = val_labeled_field("Number of frames", FieldType.INT_FIELD)
                            ui.Button("Create", height=15, clicked_fn=self.create_circular_path)
                    # Bounding Region
                    with ui.CollapsableFrame(title="Bounding Region"):
                        with ui.VStack(style={"margin": 1}):
                            val_labeled_field("Look At", FieldType.STRING_FIELD, validator=prim_validator, prim="lookat")
                            self.from_field = multi_labeled_field("From", FieldType.FLOAT_FIELD, 0.0, 0.0, 0.0)
                            self.to_field = multi_labeled_field("To", FieldType.FLOAT_FIELD, 0.0, 0.0, 0.0)
                            self.region_frames_field = val_labeled_field("Number of frames", FieldType.INT_FIELD)
                            ui.Button("Create", height=15, clicked_fn=self.create_bounding_region)
                    # Reset Button
                    ui.Button("Reset", height=15, clicked_fn=self.delete_replicator_prim)
                
    def create_circular_path(self):
        """ 
        This function uses the Replicator API to create a OG that moves the camera on a circular path during
        synthetic data collection
        """
        # Collect the path parameters from UI elements
        look_at = str(self.prims["lookat"].GetPath())
        distance = self.distance_field.model.get_value_as_int()
        elevation = self.elevation_field.model.get_value_as_int()
        frames = self.circular_frames_field.model.get_value_as_int()
        angle = 360.0/frames
        # Trigger randomization and rendering on each frame
        with rep.trigger.on_frame(num_frames=frames):
            randomizer = rep.randomizer.compute_camera_pos(distance, elevation, angle)
            generate_graph(randomizer, [look_at])
    
    def create_bounding_region(self):
        """ 
        This function uses the Replicator API to create a OG that moves the camera randomly in a cube like region
        during synthetic data collection
        """
        # Collect the path parameters from UI elements
        look_at = str(self.prims["lookat"].GetPath())
        from_point = tuple([v.model.get_value_as_float() for v in self.from_field])
        to_point = tuple([v.model.get_value_as_float() for v in self.to_field])
        frames = self.region_frames_field.model.get_value_as_int()
        # Trigger randomization and rendering on each frame
        with rep.trigger.on_frame(num_frames=frames):
            randomizer = rep.distribution.uniform(from_point, to_point)
            generate_graph(randomizer, [look_at])
    
    def delete_replicator_prim(self, ):
        """
        Will delete the replication prim and all its subchildren including the OG and camera we created
        """
        try:
            omni.kit.commands.execute('DeletePrims', paths=['/Replicator'])
        except:
            pass
