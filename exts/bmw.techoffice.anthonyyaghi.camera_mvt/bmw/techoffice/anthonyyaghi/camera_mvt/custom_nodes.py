import omni.graph.core as og
import numpy as np
import omni.replicator.core as rep
frame = 0

class CreateCircularPathRandomizer:
    @og.AutoFunc(module_name="omni.replicator")
    def ComputeCameraPos(distance: float, elevation: float, angle: float, numSamples: int = 1) -> og.Bundle:
        # Note 1: numSamples input currently required
        # Note 2: Only bundle output currently supported, this will be expanded in the future.
        global frame
        print(frame)
        p = [0, 0, 0]
        azimuth = frame * np.radians(angle)
        elevation = np.radians(elevation)
        frame += 1
        x = np.cos(azimuth) * np.cos(elevation) * distance
        y = np.sin(azimuth) * np.cos(elevation) * distance
        z = np.sin(elevation) * distance

        bundle = og.Bundle("return", False)
        bundle.create_attribute("values", og.Type(og.BaseDataType.DOUBLE, 3, 1)).value = [[x + p[0], y + p[1], z + p[2]]]
        return bundle

    # Register randomizer into replicator
    rep.utils.ATTRIBUTE_MAPPINGS.add(rep.utils.AttrMap("outputs_out_0", "inputs:values"))
    def compute_camera_pos(distance: float, elevation: float, angle: float):
        return rep.utils.create_node("omni.replicator.ComputeCameraPos", distance=distance, elevation=elevation, angle=angle)
    rep.randomizer.register(compute_camera_pos)