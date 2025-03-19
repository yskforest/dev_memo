
enable_viewer_3d = False
if config["viewer_3d_setting"]["enable"]:
    viewer_3d = Viewer3D(config["viewer_3d_setting"])
    viewer_3d.add_pcd("human")
    viewer_3d.add_pcd("patient")
    viewer_3d.add_lineset("table_roi")
    viewer_3d.add_lineset("table_calib_roi")
    enable_viewer_3d = True
else:
    viewer_3d = None

x, y, z, w, h, z_range = table_calib_roi["x"], table_calib_roi["y"], table_calib_roi[
"z"], table_calib_roi["w"], table_calib_roi["h"], table_calib_roi["table_calib_z_range"]
measure_patient.set_table_calib_roi(x, y, z, w, h, z_range)
viewer_3d.update_lineset_from_2points("table_calib_roi", (x, y, z - z_range),
                                    (x + w, y + h, z + z_range), (0, 0, 1))

for lineset in self.lineset_dict.values():
    self.vis.add_geometry(lineset)