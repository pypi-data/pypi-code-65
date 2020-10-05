import os
import cv2
import torch
import torch.nn.functional as F
import numpy as np
from scipy.io import loadmat

from torch import autograd

import sys
root_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(root_folder, 'avatar'))

from Face import BFMDecoder

# Util function for loading meshes
from pytorch3d.io import load_objs_as_meshes, save_obj

from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    OpenGLPerspectiveCameras,
    look_at_view_transform,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader,
    SoftGouraudShader,
    SoftSilhouetteShader,
    TexturesVertex
)

from sh_shading import SoftPerVertexSHShader


def setup_renderer(device='cpu'):
    camera_R, camera_T = look_at_view_transform(eye=((0, 0, 10.),), at=((0, 0, 0.),), up=((0, 1, 0),))
    #camera = OpenGLPerspectiveCameras(device=device, R=camera_R, T=camera_T, znear=1, zfar=100., fov=60, degrees=True)
    camera = OpenGLPerspectiveCameras(device=device, R=camera_R, T=camera_T, znear=0.1, zfar=20., fov=12.5936, degrees=True)

    # Rasterization Settings
    sigma = 1e-4
    raster_settings = RasterizationSettings(
        image_size=224,
        blur_radius=np.log(1. / 1e-4 - 1.) * sigma,
        faces_per_pixel=10,
        perspective_correct=True,
    )

    renderer = MeshRenderer(
        rasterizer=MeshRasterizer(
            cameras=camera,
            raster_settings=raster_settings
        ),
        shader=SoftPerVertexSHShader(
            device=device,
            cameras=camera,
        )
    )

    return renderer, camera


coeff = torch.tensor(loadmat('./test_assets/frame0.mat')['coeff'], dtype=torch.float32, device='cuda')
print(coeff.shape)
light = torch.reshape(coeff[:, 227:254], (1, 3, 9))
light = torch.transpose(light, 1, 2)
rot = coeff[:, 224:227]
rot = rot[:, [2, 1, 0]]
print(rot)

face_decoder = BFMDecoder().cuda()
decoder_out = face_decoder.forward(coeff[:, :80], coeff[:, 80:144], coeff[:, 144:224], rot, coeff[:, 254:257], return_3d_landmarks=True)

# # Load obj file
# mesh = load_objs_as_meshes(['./bug_mesh.obj'], device='cuda')

# We scale normalize and center the target mesh to fit in a sphere of radius 1 
# centered at (0,0,0). (scale, center) will be used to bring the predicted mesh 
# to its original center and scale.  Note that normalizing the target mesh, 
# speeds up the optimization but is not necessary!
# verts = mesh.verts_packed()
# N = verts.shape[0]
# center = verts.mean(0)
# scale = max((verts - center).abs().max(0)[0])
# mesh.offset_verts_(-center.expand(N, 3))
# mesh.scale_verts_((1.0 / float(scale)))
# meshes = mesh.extend(1)

# renderer, camera = setup_renderer(device='cuda')
# textures = TexturesVertex(verts_features=decoder_out['vertice_color'])
# mesh.textures = textures
# # mesh = Meshes(verts=decoder_out['vertice'], faces=decoder_out['faces'].expand(1, -1, 3), textures=textures)

# # landmark_3d = decoder_out['landmarks_3d']
# # landmark_2d = camera.transform_points_screen(landmark_3d, [[224, 224]])[..., 0:2]
# # landmark_2d = landmark_2d.reshape(landmark_2d.shape[0], -1, 2)


# mesh_images, bg_mask = renderer(mesh, lights=light, return_bg_mask=True)
# mesh_images = mesh_images[..., 0:3]
# mesh_images = mesh_images.detach().squeeze().cpu().numpy()
# bg_mask = bg_mask.detach().squeeze().cpu().numpy().astype(np.float32)
# cv2.imwrite('test.png', mesh_images[..., ::-1])
# cv2.imwrite('result_mask.png', bg_mask * 255)

# np.save('landmark_gt.npy', landmark_2d.detach().cpu().numpy())

# print('Done.')
# input()


# def remove_nan_hook(grad):
#     print('Grad nan status: {}'.format(torch.isnan(grad).any()))
#     grad = grad.clone()
#     grad[torch.isnan(grad)] = 0
#     return grad


img_gt = cv2.imread('gt.png')
img_gt = np.ascontiguousarray(img_gt[..., ::-1]).astype(np.float32)
lmk_gt = np.load('landmark_gt.npy')

gt_img = torch.tensor(img_gt, dtype=torch.float32, device='cuda').unsqueeze(0)
gt_lmk = torch.tensor(lmk_gt, dtype=torch.float32, device='cuda')

coeff[..., :80] = 0.
coeff[..., 224:227] = 0.
param = torch.nn.Parameter(coeff)
param = param.cuda()

renderer, camera = setup_renderer(device='cuda')
optim = torch.optim.Adam([param], lr=0.01)
# try:
#     with autograd.detect_anomaly():
for i in range(1000):
    print(f'Iteration {i}')
    if((i + 1) % 10 == 0):
        renderer.rasterizer.raster_settings.blur_radius = renderer.rasterizer.raster_settings.blur_radius * 0.8
        print(renderer.rasterizer.raster_settings.blur_radius)
    optim.zero_grad()
    light = param[:, 227:254]
    light = torch.reshape(light, (1, 3, 9)).transpose(1, 2)
    rot = param[:, 224:227]
    rot = rot[:, [2, 1, 0]]
    decoder_out = face_decoder.forward(param[:, :80], param[:, 80:144], param[:, 144:224], rot, param[:, 254:257], return_3d_landmarks=True)
    textures = TexturesVertex(verts_features=decoder_out['vertice_color'])
    # print('Vertice NaN stat: {}'.format(torch.isnan(decoder_out['vertice']).any()))
    # print('Tex NaN stat: {}'.format(torch.isnan(decoder_out['vertice_color']).any()))

    mesh = Meshes(verts=decoder_out['vertice'], faces=decoder_out['faces'].expand(1, -1, 3), textures=textures)
    mesh_images, bg_mask = renderer(mesh, lights=light, return_bg_mask=True)
    mesh_images = mesh_images[..., 0:3]
    # # mesh_images.register_hook(remove_nan_hook)
    mesh_images_safe = mesh_images#torch.where(torch.isnan(mesh_images), torch.zeros_like(mesh_images), mesh_images)
    # print('Images NaN stat: {}'.format(torch.isnan(mesh_images_safe).any()))

    gt_img_curr = gt_img.clone()
    gt_img[bg_mask] = 0
    mesh_images_safe[bg_mask] = 0

    landmark_3d = decoder_out['landmarks_3d']
    landmark_2d = camera.transform_points_screen(landmark_3d, [[224, 224]])[..., 0:2]
    landmark_2d = landmark_2d.reshape(landmark_2d.shape[0], -1, 2)

    if(i % 10 == 0):
        vis_image = mesh_images_safe.detach().squeeze().cpu().numpy()
        cv2.imwrite(f'result_before_backward_{i}.png', vis_image[..., ::-1])
    loss_img = F.mse_loss(mesh_images_safe, gt_img)
    # loss_img = 0.
    loss_lmk = F.mse_loss(gt_lmk, landmark_2d)
    loss = loss_img + 1000 * loss_lmk
    # print(loss_img)
    # print(loss_lmk)
    print(loss)
    loss.backward()
    optim.step()

final_image = renderer(mesh, lights=light, blur_radius=0, faces_per_pixel=1)
final_image = final_image[..., 0:3]
vis_image = final_image.detach().squeeze().cpu().numpy()
cv2.imwrite('result_final.png', vis_image[..., ::-1])
# except RuntimeError:
#     print('Cached Error')
#     vis_image = mesh_images.detach().squeeze().cpu().numpy()
#     cv2.imwrite(f'bug_at_{i}.png', vis_image[..., ::-1])
#     save_obj(f'bug_at_{i}.obj', decoder_out['vertice'][0], decoder_out['faces'])
#     np.save(f'bug_at_{i}.npy', param.detach().cpu().squeeze().numpy())
