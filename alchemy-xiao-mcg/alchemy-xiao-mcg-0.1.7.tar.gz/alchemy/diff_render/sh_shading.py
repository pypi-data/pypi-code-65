# Extend Pytorch3D for computing SH shading.
# The SH definiation and shading algorithm are consistent with
# "Y. Deng, J. Yang, S. Xu, D. Chen, Y. Jia, and X. Tong, Accurate 3D Face Reconstruction with Weakly-Supervised Learning: From Single Image to Image Set",
# (https://github.com/microsoft/Deep3DFaceReconstruction)
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

from typing import Optional, Union

from pytorch3d.renderer.utils import convert_to_tensors_and_broadcast
from pytorch3d.ops import interpolate_face_attributes
from pytorch3d.renderer import TexturesVertex, Materials
from pytorch3d.renderer import BlendParams, softmax_rgb_blend

# Constant define for SH basis
a0 = math.pi
a1 = 2.0 * math.pi / math.sqrt(3.0)
a2 = 2.0 * math.pi / math.sqrt(8.0)
c0 = 1.0 / math.sqrt(4.0 * math.pi)
c1 = math.sqrt(3.0) / math.sqrt(4.0 * math.pi)
c2 = 3.0 * math.sqrt(5.0) / math.sqrt(12.0 * math.pi)


def _sh_shading(normals: torch.Tensor, sh_coeffs: torch.Tensor, ambient_coeff: Optional[Union[float, torch.Tensor]] = None):
    '''
    Args:
        normals: (N, ..., 3) xyz normal vectors. Normals and points are
            expected to have the same shape.
        sh_coeffs: (1, 9, 3) or (N, 9, 3) coefficent of SH shading.
        ambient_coeff: Optional ambient lighting coeffiecnt.

    Returns:
        colors: (N, ..., 3), same shape as the input points.
    '''
    if(ambient_coeff is not None):
        sh_coeffs = sh_coeffs.clone()
        sh_coeffs[..., 0, :] += ambient_coeff
        normals, sh_coeffs, ambient_coeff = convert_to_tensors_and_broadcast(normals, sh_coeffs, ambient_coeff, device=normals.device)
    else:
        normals, sh_coeffs = convert_to_tensors_and_broadcast(normals, sh_coeffs, device=normals.device)

    # Reshape SH coeff so they have all the arbitrary intermediate
    # dimensions as normals. Assume first dim = batch dim and last dim = 9 * 3.
    points_dims = normals.shape[1:-1]
    expand_dims = (-1,) + (1,) * len(points_dims) + (9, 3,)
    if sh_coeffs.shape != normals.shape:
        sh_coeffs = sh_coeffs.view(expand_dims)

    # Renormalize the normals in case they have been interpolated.
    # We tried to replace the following with F.cosine_similarity, but it wasn't faster.
    normals = F.normalize(normals, p=2, dim=-1, eps=1e-6)

    # Compute SH shading.
    Y = torch.stack([
        torch.tensor(a0 * c0, device=normals.device, dtype=torch.float32).expand(normals.shape[0:-1]),
        -a1 * c1 * normals[..., 1],
        a1 * c1 * normals[..., 2],
        -a1 * c1 * normals[..., 0],
        a2 * c2 * normals[..., 0] * normals[..., 1],
        -a2 * c2 * normals[..., 1] * normals[..., 2],
        a2 * c2 * 0.5 / math.sqrt(3.0) * (3.0 * torch.square(normals[..., 2]) - 1.0),
        -a2 * c2 * normals[..., 0] * normals[..., 2],
        a2 * c2 * 0.5 * (torch.square(normals[..., 0]) - torch.square(normals[..., 1]))
    ], axis=-1)

    colors = torch.matmul(Y.unsqueeze(-2), sh_coeffs).squeeze(-2)

    # If given packed inputs remove batch dim in output.
    if(normals.dim() == 2):
        colors = colors.squeeze(0)

    return colors


def vertex_sh_shading(meshes, fragments, sh_coeffs):
    """
    Apply per vertex SH shading.
    This function is only supported for meshes with texture type `TexturesVertex`.
    This is because the illumination is applied to the vertex colors.

    Args:
        meshes: Batch of meshes
        fragments: Fragments named tuple with the outputs of rasterization
        sh_coeffs: SH coeffs of lighting.  (N, 9, 3) or (1, 9, 3)
        materials: Materials class containing a batch of material properties

    Returns:
        colors: (N, H, W, K, 3)
    """
    if not isinstance(meshes.textures, TexturesVertex):
        raise ValueError("Mesh textures must be an instance of TexturesVertex")

    faces = meshes.faces_packed()  # (F, 3)
    verts_normals = meshes.verts_normals_packed()  # (V, 3)
    verts_colors = meshes.textures.verts_features_packed()  # (V, D)
    vert_to_mesh_idx = meshes.verts_packed_to_mesh_idx()

    # Format properties of lights and materials so they are compatible
    # with the packed representation of the vertices. This transforms
    # all tensor properties in the class from shape (N, ...) -> (V, ...) where
    # V is the number of packed vertices. If the number of meshes in the
    # batch is one then this is not necessary.
    if(len(meshes) > 1 and sh_coeffs.shape[0] != 1):
        sh_coeffs = sh_coeffs[vert_to_mesh_idx, ...]

    # print('Vertice Normal NaN stat: {}'.format(torch.isnan(verts_normals).any()))
    # apply shading
    shading = _sh_shading(verts_normals, sh_coeffs, ambient_coeff=0.8)      # 0.8 is from Yu's paper
    # print('Shading NaN stat: {}'.format(torch.isnan(shading).any()))
    verts_colors_shaded = verts_colors * shading
    # print('vert_colors_shaded stat: {}'.format(torch.isnan(verts_colors_shaded).any()))
    face_colors = verts_colors_shaded[faces]
    # print('face_colors stat: {}'.format(torch.isnan(face_colors).any()))
    colors = interpolate_face_attributes(
        fragments.pix_to_face, fragments.bary_coords, face_colors
    )
    return colors


def pixel_sh_shading(meshes, fragments, sh_coeffs, texels):
    """
    Apply per pixel sh shading.

    Args:
        meshes: Batch of meshes
        fragments: Fragments named tuple with the outputs of rasterization
        sh_coeffs: SH coeffs of lighting.  (N, 9, 3) or (1, 9, 3)
        materials: Materials class containing a batch of material properties
        texels: texture per pixel of shape (N, H, W, K, 3)

    Returns:
        colors: (N, H, W, K, 3)
    """
    faces = meshes.faces_packed()  # (F, 3)
    vertex_normals = meshes.verts_normals_packed()  # (V, 3)

    faces_normals = vertex_normals[faces]
    pixel_normals = interpolate_face_attributes(
        fragments.pix_to_face, fragments.bary_coords, faces_normals
    )
    shading = _sh_shading(pixel_normals, sh_coeffs, ambient_coeff=0.8)   # 0.8 is from Yu's paper

    colors = shading * texels
    return colors


def _get_default_sh(device):
    ambient_sh = torch.ones([1, 9, 3], device=device)
    ambient_sh[0, 0] = 0.5
    return ambient_sh


# SH shaders
class SoftPerVertexSHShader(nn.Module):
    """
    Per-vertex SH shader.
    """
    def __init__(self, device="cpu", cameras=None, lights=None, materials=None, blend_params=None):
        super().__init__()
        self.sh_coeffs = lights if lights is not None else _get_default_sh(device)
        self.materials = (
            materials if materials is not None else Materials(device=device)
        )
        self.cameras = cameras
        self.blend_params = blend_params if blend_params is not None else BlendParams()

    def forward(self, fragments, meshes, **kwargs) -> torch.Tensor:
        cameras = kwargs.get("cameras", self.cameras)
        if cameras is None:
            msg = "Cameras must be specified either at initialization \
                or in the forward pass of SoftGouraudShader"
            raise ValueError(msg)

        sh_coeffs = kwargs.get("lights", self.sh_coeffs)
        return_bg_mask = kwargs.get('return_bg_mask', False)
        if(return_bg_mask):
            bg_mask = fragments.pix_to_face[..., 0] < 0  # (N, H, W)

        colors = vertex_sh_shading(
            meshes=meshes,
            fragments=fragments,
            sh_coeffs=sh_coeffs
        )

        znear = kwargs.get("znear", getattr(cameras, "znear", 1.0))
        zfar = kwargs.get("zfar", getattr(cameras, "zfar", 100.0))
        images = softmax_rgb_blend(
            colors, fragments, self.blend_params, znear=znear, zfar=zfar
        )

        if(return_bg_mask):
            return images, bg_mask
        else:
            return images


class SoftPerPixelSHShader(nn.Module):
    """
    Per-pixel SH shader.
    """

    def __init__(
        self, device="cpu", cameras=None, lights=None, materials=None, blend_params=None
    ):
        super().__init__()
        self.sh_coeffs = lights if lights is not None else _get_default_sh(device)
        self.materials = (
            materials if materials is not None else Materials(device=device)
        )
        self.cameras = cameras
        self.blend_params = blend_params if blend_params is not None else BlendParams()

    def forward(self, fragments, meshes, **kwargs):
        cameras = kwargs.get("cameras", self.cameras)
        if cameras is None:
            msg = "Cameras must be specified either at initialization \
                or in the forward pass of SoftGouraudShader"
            raise ValueError(msg)

        texels = meshes.sample_textures(fragments)
        sh_coeffs = kwargs.get("lights", self.sh_coeffs)
        colors = pixel_sh_shading(
            meshes=meshes,
            fragments=fragments,
            texels=texels,
            sh_coeffs=sh_coeffs
        )
        return_bg_mask = kwargs.get('return_bg_mask', False)
        if(return_bg_mask):
            bg_mask = fragments.pix_to_face[..., 0] < 0  # (N, H, W)

        znear = kwargs.get("znear", getattr(cameras, "znear", 1.0))
        zfar = kwargs.get("zfar", getattr(cameras, "zfar", 100.0))
        images = softmax_rgb_blend(
            colors, fragments, self.blend_params, znear=znear, zfar=zfar
        )
        if(return_bg_mask):
            return images, bg_mask
        else:
            return images
