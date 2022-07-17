import omni.graph.core as og
import numpy as np
import omni.replicator.core as rep


frame = 0

"""
This function uses the AutoNode feature to create a node from a function
This node output the point from a circle in 3D space
"""
# TODO Use AutoClass instead and have the frame variable be internal to the class.
# Not easy to implement since class based node can only be run once, looking for a work around
@og.AutoFunc(module_name="omni.replicator")
def ComputeCameraPos(distance: float, elevation: float, angle: float, numSamples: int = 1) -> og.Bundle:
    # Note 1: numSamples input currently required
    # Note 2: Only bundle output currently supported, this will be expanded in the future.
    global frame

    # Compute the coordinates
    azimuth = frame * np.radians(angle)
    elevation = np.radians(elevation)
    frame += 1
    x = np.cos(azimuth) * np.cos(elevation) * distance
    y = np.sin(azimuth) * np.cos(elevation) * distance
    z = np.sin(elevation) * distance

    # prepare output in a Bundle
    bundle = og.Bundle("return", False)
    bundle.create_attribute("values", og.Type(og.BaseDataType.DOUBLE, 3, 1)).value = [[x, y, z]]
    return bundle

# This step is needed to automatically map the output of the above node to the *pose* node
rep.utils.ATTRIBUTE_MAPPINGS.add(rep.utils.AttrMap("outputs_out_0", "inputs:values"))
# Register this node as randomizer so it can be easily used with Replicator
def compute_camera_pos(distance: float, elevation: float, angle: float):
    return rep.utils.create_node("omni.replicator.ComputeCameraPos", distance=distance, elevation=elevation, angle=angle)
rep.randomizer.register(compute_camera_pos)