import omni.replicator.core as rep
from pxr import Usd

from typing import List


def camera_validator(prim: Usd.Prim):
    """
    Check if the prim is a valid camera
    """
    try:
        return prim_validator(prim) and prim.GetTypeName() == "Camera"
    except RuntimeError:
        return False

def path_validator(prim: Usd.Prim):
    """
    Check if the prim is a valid curve/path
    """
    try:
        return prim_validator(prim) and prim.GetTypeName() == "BasisCurves"
    except RuntimeError:
        return False

def prim_validator(prim: Usd.Prim):
    """
    Check if the prim is a valid prim
    """
    try:
        return prim.IsValid()
    except RuntimeError:
        return False

def generate_graph(randomizer, look_at: List[str]):
    """
    A generic function to create a camera, append movement/randomization to it, prepare a writter
    This function prepares everything we need to start generating synthetic data with Replicator
    """
    # Create the camera and render product
    # TODO Render resolution is hard coded !
    camera = rep.create.camera()
    rp = rep.create.render_product(camera, (1024, 1024))

    # Camera movement
    with camera:
        rep.modify.pose(
            position=randomizer,
            look_at=look_at
        )
    
    # Setup writer
    # TODO Output path is hard coded !
    # TODO Project idea: Create a custom writer class to output the format we want directly
    # Check this: https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_replicator/custom_writer.html
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize( output_dir="C:\\Users\\antho\\Downloads\\output", rgb=True,   bounding_box_2d_tight=True)
    writer.attach([rp])