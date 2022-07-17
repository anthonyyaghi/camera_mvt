import omni.ext
import omni.ui as ui
import omni.kit.commands
import omni.replicator.core as rep

from pxr import Usd, UsdGeom, Gf, Sdf

from .utils import *


fields = {"string": ui.StringField, "int": ui.IntDrag, "float": ui.FloatDrag, "multi_float": ui.MultiFloatField}

class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[bmw.techoffice.anthonyyaghi.camera_mvt] startup")

        # Register custom randomizers
        from .custom_nodes import CreateCircularPathRandomizer
        CreateCircularPathRandomizer()

        # Class wide variables
        self.stage = omni.usd.get_context().get_stage()
        self.prims = {}

        # UI
        self._window = ui.Window("Image collector", width=300, height=300)
        with self._window.frame:
            def check(m, error_label, prim, validator=None, ):
                self.prims[prim] = self.stage.GetPrimAtPath(m.get_value_as_string())
                if validator is not None and not validator(self.prims[prim]):
                    error_label.text = "Invalid Object!"
                else:
                    error_label.text = ""

            def val_labeled_field(label, type, validator=None, prim=None):
                with ui.VStack():
                    with ui.HStack(height=15):
                        ui.Label(label)
                        field = fields[type]()
                    error_label = ui.Label("", style={"color": "red"}, height=15)
                
                if validator is not None and prim is not None:
                    field.model.add_value_changed_fn(lambda m, label=error_label: check(m, label, 
                                                                                        validator=validator, prim=prim))
                return field
            
            def multi_labeled_field(label, type, *args):
                with ui.VStack():
                    ui.Label(label, height=15)
                    field = fields[type](*args, height=15)
                return field

            with ui.ScrollingFrame():
                with ui.VStack(style={"margin": 1}):
                    # Circular Path UI
                    with ui.CollapsableFrame(title="Circular Path"):
                        with ui.VStack(style={"margin": 1}):
                            val_labeled_field("Look At", "string", validator=prim_validator, prim="lookat")
                            self.distance_field = val_labeled_field("Distance", "float")
                            self.elevation_field = val_labeled_field("Elevation", "float")
                            self.circular_frames_field = val_labeled_field("Number of frames", "int")
                            ui.Button("Create", height=15, clicked_fn=self.create_circular_path)
                    # Bounding Region UI
                    with ui.CollapsableFrame(title="Bounding Region"):
                        with ui.VStack(style={"margin": 1}):
                            val_labeled_field("Look At", "string", validator=prim_validator, prim="lookat")
                            self.from_field = multi_labeled_field("From", "multi_float", 0.0, 0.0, 0.0)
                            self.to_field = multi_labeled_field("To", "multi_float", 0.0, 0.0, 0.0)
                            self.region_frames_field = val_labeled_field("Number of frames", "int")
                            ui.Button("Create", height=15, clicked_fn=self.create_bounding_region)
                    # Reset Button
                    ui.Button("Reset", height=15, clicked_fn=self.delete_replicator_prim)
                

    def create_circular_path(self):
        look_at = str(self.prims["lookat"].GetPath())
        distance = self.distance_field.model.get_value_as_int()
        elevation = self.elevation_field.model.get_value_as_int()
        frames = self.circular_frames_field.model.get_value_as_int()
        angle = 360.0/frames

        with rep.trigger.on_frame(num_frames=frames):
            randomizer = rep.randomizer.compute_camera_pos(distance, elevation, angle)
            generate_graph(randomizer, [look_at])
    
    def create_bounding_region(self):
        look_at = str(self.prims["lookat"].GetPath())
        from_point = self.from_field
        to_point = self.to_field
        frames = self.region_frames_field.model.get_value_as_int()

        with rep.trigger.on_frame(num_frames=frames):
            randomizer = rep.distribution.uniform(from_point, to_point)
            generate_graph(randomizer, [look_at])
        
    
    def delete_replicator_prim(self, ):
        try:
            omni.kit.commands.execute('DeletePrims', paths=['/Replicator'])
        except:
            pass
