from __future__ import annotations

import open3d as o3d
import numpy as np


def gen_grid(pitch: float, length: int) -> o3d.geometry.LineSet:
    line_set = o3d.geometry.LineSet()
    max_value = length * pitch
    x = np.arange(-max_value, max_value + pitch, pitch)
    x = np.repeat(x, 2)
    y = np.full_like(x, -max_value)
    y[::2] = max_value
    z = np.zeros_like(x)
    points_Y = np.vstack((x, y, z)).T

    y = np.arange(-max_value, max_value + pitch, pitch)
    y = np.repeat(y, 2)
    x = np.full_like(y, -max_value)
    x[::2] = max_value
    z = np.zeros_like(y)
    points_X = np.vstack((x, y, z)).T

    points = np.vstack((points_X, points_Y))
    line_set.points = o3d.utility.Vector3dVector(points)
    lines = np.arange(points.shape[0]).reshape(-1, 2)
    line_set.lines = o3d.utility.Vector2iVector(lines)

    line_set.paint_uniform_color((0.5, 0.5, 0.5))

    return line_set


def gen_circle(r: float, points: int = 100) -> o3d.geometry.LineSet:
    theta = np.linspace(0, 2 * np.pi, points)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.zeros_like(x)

    points = np.vstack((x, y, z)).T
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    lines = np.zeros((points.shape[0] - 1, 2), dtype=int)
    lines[:, 0] = np.arange(points.shape[0] - 1)
    lines[:, 1] = np.arange(points.shape[0] - 1) + 1
    line_set.lines = o3d.utility.Vector2iVector(lines)

    line_set.paint_uniform_color((0.5, 0.5, 0.5))

    return line_set


def gen_3d_box(
    pt_min: tuple[float, float, float],
    pt_max: tuple[float, float, float],
    human_lineset: o3d.geometry.LineSet, 
    line_color: tuple[float, float, float] = (1, 0, 0),
) -> o3d.geometry.LineSet:

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

    lines = np.array(
        [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],
        ]
    )

    # line_set = o3d.geometry.LineSet()
    human_lineset.points = o3d.utility.Vector3dVector(vertices)
    human_lineset.lines = o3d.utility.Vector2iVector(lines)
    human_lineset.paint_uniform_color(line_color)

    return human_lineset


        # resNormals = []
        # for vnlist in verNormals:
        #     x = y = z = 0
        #     vector = np.zeros(3)
        #     for vn in vnlist:
        #         if vn:
        #             for vec in vn:
        #                 vector += vec

        #     resNormals.append(tuple(vector.tolist()))

