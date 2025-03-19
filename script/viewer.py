
   def __init__(self, viewer_3d_setting: dict[str] = {}) -> None:
        self.vis = o3d.visualization.Visualizer()

        if "width" in viewer_3d_setting and "height" in viewer_3d_setting:
            self.vis.create_window("3d viewer", width=viewer_3d_setting["width"], height=viewer_3d_setting["height"])
        else:
            self.vis.create_window("3d viewer", width=640, height=480)

        if "background_color" in viewer_3d_setting:
            render_option = self.vis.get_render_option()
            render_option.background_color = viewer_3d_setting["background_color"]
            # render_option.mesh_show_wireframe = True
            # render_option.point_size = 1.0
            # render_option.line_width = 50.0
            render_option.show_coordinate_frame = True
        else:
            render_option = self.vis.get_render_option()
            render_option.background_color = (0, 0, 0.1)

        self.pcd_dict = {}
        self.lineset_dict = {}

        self.lineset = o3d.geometry.LineSet()
        points = [(3000, 3000, 0), (3000, 3000, 3000)]
        self.lineset.points = o3d.utility.Vector3dVector(points)
        lines = np.array([[0, 1]])
        self.lineset.lines = o3d.utility.Vector2iVector(lines)
        self.lineset.paint_uniform_color((0.5, 0.5, 0.5))

        self.geom_added = False
        # mesh = o3d.geometry.TriangleMesh.create_sphere()
        self.vis.add_geometry(self.gen_grid(1000, 3))
        self.vis.add_geometry(self.gen_circle(1000))
        # self.vis.add_geometry(self.lineset)
        self.vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=500))

    def add_mesh(self, filepath):
        pati_mesh = o3d.io.read_triangle_mesh(filepath)
        self.vis.add_geometry(pati_mesh)

    def add_camera_tf(self, x, y, z):
        self.vis.add_geometry(self.gen_grid(o3d.geometry.TriangleMesh.create_sphere()))

    def add_pcd(self, key: str):
        self.pcd_dict[key] = o3d.geometry.PointCloud()
        self.vis.add_geometry(self.pcd_dict[key])

    def add_lineset(self, key: str):
        self.lineset_dict[key] = o3d.geometry.LineSet()
        self.vis.add_geometry(self.lineset_dict[key])

    def update_pcd(self, key: str, vertices: list[tuple[float, float, float]]):
        if key in self.pcd_dict:
            self.pcd_dict[key].points = o3d.utility.Vector3dVector(vertices)
        else:
            print("warnig: update_pcd() unknown key")

    def update_lineset(self, key: str, vertices: list[tuple[float, float, float]], lines, line_color=(1, 0, 0)):
        if key in self.lineset_dict:
            lineset = self.lineset_dict[key]
            lineset.points = o3d.utility.Vector3dVector(vertices)
            lineset.lines = o3d.utility.Vector2iVector(lines)
            lineset.paint_uniform_color(line_color)
        else:
            print("warnig: update_lineset() unknown key")

    def update_lineset_from_2points(self, key: str, pt_min: tuple[float, float, float],
                                    pt_max: tuple[float, float, float],
                                    line_color: tuple[float, float, float] = (1, 0, 0)):
        vertices = [
            # top surface
            (pt_max[0], pt_max[1], pt_max[2]),  # pt_max
            (pt_min[0], pt_max[1], pt_max[2]),
            (pt_min[0], pt_min[1], pt_max[2]),
            (pt_max[0], pt_min[1], pt_max[2]),
            # bottom surface
            (pt_max[0], pt_max[1], pt_min[2]),
            (pt_min[0], pt_max[1], pt_min[2]),
            (pt_min[0], pt_min[1], pt_min[2]),  # pt_min
            (pt_max[0], pt_min[1], pt_min[2]),
        ]

        lines = np.array([[0, 1], [1, 2], [2, 3], [3, 0],
                          [4, 5], [5, 6], [6, 7], [7, 4],
                          [0, 4], [1, 5], [2, 6], [3, 7],])

        self.update_lineset(key, vertices, lines, line_color)

    def render(self):
        if not self.geom_added:
            self.vis.add_geometry(self.lineset)
            self.geom_added = True

        view_control = self.vis.get_view_control()
        view_control.set_constant_z_near(1)
        view_control.set_constant_z_far(10000.0)
        view_control.set_zoom(2, )  # ここでズームの限界を拡張します

        for pcd in self.pcd_dict.values():
            self.vis.update_geometry(pcd)

        # for lineset in self.lineset_dict.values():
        #     self.vis.update_geometry(lineset)

        self.vis.update_geometry(self.lineset)
        # render_option = self.vis.get_render_option()
        # render_option.line_width = 5.0
        self.vis.poll_events()
        self.vis.update_renderer()
