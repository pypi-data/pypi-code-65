import pickle

from PIL import Image
import numpy as np
from scipy.sparse.csr import csr_matrix
from sklearn.preprocessing import normalize


class Three60Cube:
    def __init__(self, cache_fp=None):

        # The Image
        # =========
        self.image = None
        self.image_array = None
        self.width = None
        self.height = None
        self.cache_fp = cache_fp
        self.cache_loaded = False
        self.transformations = {}

    def open_image(self, path):
        self.image = Image.open(path)
        self.image_array = np.array(self.image)
        self.width = self.image.size[0]
        self.height = self.image.size[1]

    def get_pane(self, pane=0, dim=512):
        if not self.cache_loaded and self.cache_fp is not None:
            self._load_cache()

        transformation = self._get_transformation(pane=pane, dim=dim)
        image = self._transform(transformation, dim=dim)
        return image

    def save_pane(self, fp, pane=0, dim=512):
        image = self.get_pane(pane=pane, dim=dim)
        image.save(fp)

    def _compute_template(self):
        # The Sphere
        # ==========
        # radius image sphere
        self.R = self.width / (2 * np.pi)
        self.offset = int(self.R + 100)

        # create projection template
        self.cube_pane_normals = {
            0: np.array([1, 0, 0]),
            1: np.array([0, -1, 0]),
            2: np.array([-1, 0, 0]),
            3: np.array([0, 1, 0]),
            4: np.array([0, 0, 1]),
            5: np.array([0, 0, -1])
        }

        # pane side and 3D coordinates sphere
        self.XYZ = self._get_spherical_coordinates()
        # get nearest panes of all spherical coordinates
        self.projection_panes = self._detect_nearest_pane()

        # project 3D to 2D
        self.projections = self._project_to_cube()

        template = np.stack((
            self.projection_panes,
            self.projections[:, :, 0],
            self.projections[:, :, 1]
        ), axis=2)

        return template

    def _get_spherical_coordinates(self):
        # 180 deg over <height> pixels, divide angles
        # in vertical plane
        ver_res = np.pi / self.height
        phi = np.tile(
            np.linspace(0, np.pi, num=self.height).reshape(-1, 1),
            (1, self.width)
        )
        # angles in horizontal plane
        theta = np.tile(
            np.linspace(0.25*np.pi, -1.75*np.pi, num=self.width+1),
            (self.height, 1)
        )[:, :-1]
        X, Y, Z = self._sphere_to_cartesian(self.R, theta, phi)

        # reshape for concatenation <r, c> -> <r, c, 1>
        X = X[:, :, np.newaxis]
        Y = Y[:, :, np.newaxis]
        Z = Z[:, :, np.newaxis]

        return np.concatenate((X, Y, Z), axis=2)

    def _detect_nearest_pane(self):
        """Detect which pane a ray from the sphere will intersect with.
        Method: closest distance between sphere point and normal
        vectors of cube panes. These normal vectors are the midpoints
        of the panes
        """
        rows = self.XYZ.shape[0]
        cols = self.XYZ.shape[1]
        # 6 distances
        distances = np.zeros((rows, cols, 6))

        for pane in sorted(self.cube_pane_normals.keys()):
            mid_point = self.cube_pane_normals[pane]
            distances[:, :, pane] = np.linalg.norm(
                self.XYZ[:, :, :] - np.tile(mid_point, (rows, cols, 1)),
                axis=2
            )

        # convert into 3d matrix
        return np.argmin(distances, axis=2)

    @staticmethod
    def _sphere_to_cartesian(R, theta, phi):
        # convert spherical to cartesian
        X = R * np.sin(phi) * np.cos(theta)
        Y = R * np.sin(phi) * np.sin(theta)
        Z = R * np.cos(phi)
        return (X, Y, Z)

    def _load_cache(self):
        try:
            with open(self.cache_fp, "rb") as f:
                self.transformations = pickle.load(f)
        except BaseException:
            self.transformations = {}
        self.cache_loaded = True

    def _save_cache(self):
        with open(self.cache_fp, "wb") as f:
            pickle.dump(self.transformations, f)
    # https://gist.github.com/TimSC/8c25ca941d614bf48ebba6b473747d72
    # vectorized line plane collision
    # XYZ: points on sphere, NORMS: normal vectors of plane where 
    # XYZ will intersect, PLANEP: plane-points in which XYZ
    # will intersect
    @staticmethod
    def vec_line_plane_collision(XYZ, NORMS, PLANEP):
        # dot product between 3d matrixes
        ndotu = np.einsum('ijk,ijk->ij', XYZ, NORMS)
        w = XYZ - PLANEP
        # again, einsum is dot-product
        si = (np.einsum('ijk,ijk->ij', -NORMS, w) / ndotu)[:, :, np.newaxis]
        psi = w + si * XYZ + PLANEP
        return psi

    def _project_to_cube(self):
        # create 3d cube projections first
        shape = self.XYZ.shape
        projections = np.zeros((shape[0], shape[1], 2))

        for pane in sorted(self.cube_pane_normals.keys()):
            # copy XYZ
            XYZ_copy = np.copy(self.XYZ)
            # create a mask for all vectors that are
            # projecting on the pane in question
            mask = self.projection_panes == pane

            # create normal vectors of pane and a vector
            # that exists on the pane to define the projection
            # pane
            normal = self.cube_pane_normals[pane]
            # now I need a point on the pane: take the absolute 
            # normal and see where it is 1 (->bool), reverse it
            # and add to normal
            pane_point = normal + ~(np.abs(normal) == True)

            # create a self.image_array-shape of normals and pane_points
            normal_vecs = np.tile(normal, (self.XYZ.shape[0], self.XYZ.shape[1], 1))
            pane_point_vecs = np.tile(pane_point, (self.XYZ.shape[0], self.XYZ.shape[1], 1))

            # in xyz exist points who will not intersect with 
            # the currect pane, set all irrelevant sphere coordinates
            # to normal vector
            XYZ_copy[~mask] = np.tile(normal * 2, (XYZ_copy[~mask].shape[0], 1))

            # create the projections
            projections_3d = self.vec_line_plane_collision(
                XYZ_copy,
                normal_vecs,
                pane_point_vecs
            )

            # convert into 2d and transform, the np.abs everywehere are a bit much
            if pane == 0:
                projections_3d = projections_3d[:, :, [2, 1]]
                projections_3d[:, :, 0] = np.abs(projections_3d[:, :, 0] - 1)
                projections_3d[:, :, 1] = np.abs(projections_3d[:, :, 1] - 1)
                projections[mask] = projections_3d[mask]
            elif pane == 1:
                projections_3d = projections_3d[:, :, [2, 0]]
                projections_3d[:, :, 0] = np.abs(projections_3d[:, :, 0] - 1)
                projections_3d[:, :, 1] = np.abs(projections_3d[:, :, 1] - 1)
                projections[mask] = projections_3d[mask]
            elif pane == 2:
                projections_3d = projections_3d[:, :, [2, 1]]
                projections_3d[:, :, 0] = np.abs(projections_3d[:, :, 0] - 1)
                projections_3d[:, :, 1] = np.abs(projections_3d[:, :, 1] + 1)
                projections[mask] = projections_3d[mask]
            elif pane == 3:
                projections_3d = projections_3d[:, :, [2, 0]]
                projections_3d[:, :, 0] = np.abs(projections_3d[:, :, 0] - 1)
                projections_3d[:, :, 1] = np.abs(projections_3d[:, :, 1] + 1)
                projections[mask] = projections_3d[mask]
            elif pane == 4:
                projections_3d = projections_3d[:, :, [0, 1]]
                projections_3d[:, :, 0] = np.abs(projections_3d[:, :, 0] + 1)
                projections_3d[:, :, 1] = np.abs(projections_3d[:, :, 1] - 1)
                projections[mask] = projections_3d[mask]
            elif pane == 5:
                projections_3d = projections_3d[:, :, [0, 1]]
                projections_3d[:, :, 0] = np.abs(projections_3d[:, :, 0] - 1)
                projections_3d[:, :, 1] = np.abs(projections_3d[:, :, 1] - 1)
                projections[mask] = projections_3d[mask]

        return projections

    def _transform(self, transformer, dim=512):
        flat_image = self.image_array.reshape(-1, 3)
        red = transformer.dot(flat_image[:, 0]).reshape(dim, dim)
        green = transformer.dot(flat_image[:, 1]).reshape(dim, dim)
        blue = transformer.dot(flat_image[:, 2]).reshape(dim, dim)
        output_image = np.dstack((red, green, blue)).astype(np.uint8)
        return Image.fromarray(output_image)

    def _get_transformation(self, pane=0, dim=512):
        start_trans_id = f"{self.width}x{self.height}"
        final_trans_id = f"{start_trans_id}x{pane}x{dim}"
        try:
            transformation = self.transformations[final_trans_id]
            return transformation
        except KeyError:
            pass
        try:
            template = self.transformations[start_trans_id]
        except KeyError:
            template = self._compute_template()
            self.transformations[start_trans_id] = template

        transformation = self._create_transformation(
            template, pane=pane, dim=dim)
        self.transformations[final_trans_id] = transformation
        if self.cache_fp is not None:
            self._save_cache()
        return transformation

    def _create_transformation(self, template, pane=0, dim=512):
        # projection cube has size 2
        res = 2.0 / dim
        # create new image
        mask = template[:, :, 0] == pane
        projections = template[:, :, 1:][mask]
        rows = np.floor_divide(projections[:, 0], res).astype(int)
        cols = np.floor_divide(projections[:, 1], res).astype(int)

        bound_mask = ((rows < dim) & (cols < dim))
        input_rows, input_cols = np.where(mask)

        input_rows = input_rows[bound_mask]
        input_cols = input_cols[bound_mask]
        rows = rows[bound_mask]
        cols = cols[bound_mask]

        trans_rows = input_rows*self.width+input_cols
        trans_cols = rows*dim+cols
        trans_data = np.ones_like(trans_rows)
        transformer = csr_matrix((trans_data, (trans_cols, trans_rows)),
                                 shape=(dim*dim,
                                 self.height*self.width))

        return normalize(transformer, norm='l1', axis=1, copy=False)
