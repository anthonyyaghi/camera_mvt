import omni.ext
import omni.ui as ui
import omni.replicator.core as rep


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[bmw.techoffice.anthonyyaghi.camera_mvt] startup")
        self.stage = omni.usd.get_context().get_stage()
        self.prims = {"camera": None, "lookat": None, "path": None}

        self._window = ui.Window("Image collector", width=300, height=300)
        with self._window.frame:
            def drop_accept(url):
                """Called to check the drag data is acceptable."""
                return True

            def drop(event, widget, prim, error_label, validator=None, ):
                """Called when dropping the data."""
                widget.model.set_value(event.mime_data)
                self.prims[prim] = self.stage.GetPrimAtPath(widget.model.as_string)
                if validator is not None and not validator(self.prims[prim]):
                    error_label.text = "Invalid Object!"
                else:
                    error_label.text = ""

            def drop_area(label, prim, validator=None):
                """A drop area that shows object path when droped"""
                with ui.HStack(height=15):
                    ui.Label(label)
                    field = ui.StringField()
                    error_label = ui.Label("", style={"color": "red"})

                field.enabled = False
                field.set_accept_drop_fn(drop_accept)
                field.set_drop_fn(lambda event, widget=field: drop(event, widget, prim, error_label,
                                                                   validator=validator))
                return field

            with ui.VStack(style={"margin": 1}):
                drop_area("Camera", "camera", validator=self.camera_validator)
                drop_area("Look At", "lookat", validator=self.prim_validator)
                drop_area("Camera Path", "path", validator=self.path_validator)
                ui.Button("Create", height=15, clicked_fn=self.get_path_points)

    def on_shutdown(self):
        print("[bmw.techoffice.anthonyyaghi.camera_mvt] shutdown")

    def camera_validator(self, prim):
        try:
            return self.prim_validator(prim) and prim.GetTypeName() == "Camera"
        except RuntimeError:
            return False

    def path_validator(self, prim):
        try:
            return self.prim_validator(prim) and prim.GetTypeName() == "BasisCurves"
        except RuntimeError:
            return False

    def prim_validator(self, prim):
        try:
            return prim.IsValid()
        except RuntimeError:
            return False

    def get_path_points(self):
        points = [tuple(point) for point in self.prims["path"].GetAttribute("points").Get()]
        # MyExtension.define_path_lookat_obj(self.prims["camera"], points, [self.prims["lookat"]])
        with rep.new_layer():
            camera = rep.create.camera(position=(0, 0, 1000))
            render_product = rep.create.render_product(camera, (1024, 1024))
            # torus = rep.create.torus(semantics=[('class', 'torus')] , position=(0, -200 , 100))
            # sphere = rep.create.sphere(semantics=[('class', 'sphere')], position=(0, 100, 100))
            # cube = rep.create.cube(semantics=[('class', 'cube')],  position=(100, -200 , 100) )

            with rep.trigger.on_frame(num_frames=10):
                with rep.create.group([camera]):
                    rep.modify.pose(
                        position=rep.distribution.uniform((-100, -100, -100), (200, 200, 200)),
                        look_at=[str(self.prims["lookat"].GetPath())])

            # Initialize and attach writer
            # writer = rep.WriterRegistry.get("BasicWriter")

            # writer.initialize( output_dir="C:\Users\antho\Downloads\output", rgb=True,   bounding_box_2d_tight=True)

            # writer.attach([render_product])

            rep.orchestrator.preview()


    @staticmethod
    def define_path_lookat_obj(name_path, coord, lookat):
        # Create DR transform component
        result, prim = omni.kit.commands.execute(
            "CreateTransformComponentCommand",
            prim_paths=[name_path],
            target_points=coord,
            target_paths=lookat,
            enable_sequential_behavior=True
        )
        return prim

    @staticmethod
    def define_path_lookat_points(name_path, coord, lookat):
        # Create DR transform component
        result, prim = omni.kit.commands.execute(
            "CreateTransformComponentCommand",
            prim_paths=[name_path],
            target_points=coord,
            lookat_target_points=lookat,
            enable_sequential_behavior=True
        )
        return prim
