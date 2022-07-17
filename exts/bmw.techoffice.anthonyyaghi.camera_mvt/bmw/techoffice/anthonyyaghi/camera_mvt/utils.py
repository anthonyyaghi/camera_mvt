import omni.replicator.core as rep


def camera_validator(prim):
    try:
        return prim_validator(prim) and prim.GetTypeName() == "Camera"
    except RuntimeError:
        return False

def path_validator(prim):
    try:
        return prim_validator(prim) and prim.GetTypeName() == "BasisCurves"
    except RuntimeError:
        return False

def prim_validator(prim):
    try:
        return prim.IsValid()
    except RuntimeError:
        return False

def generate_graph(randomizer, look_at):
    # Create the camera and render product
    camera = rep.create.camera()
    rp = rep.create.render_product(camera, (1024, 1024))

    # Camera movement
    with camera:
        rep.modify.pose(
            position=randomizer,
            look_at=look_at
        )
    
    # Setup writer
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize( output_dir="C:\\Users\\antho\\Downloads\\output", rgb=True,   bounding_box_2d_tight=True)
    writer.attach([rp])