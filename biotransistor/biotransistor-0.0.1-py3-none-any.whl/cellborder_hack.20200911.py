'''
1. i get intenisty values one tiff per one marker
2. i get guilaume like segmentation mask
3. split 2d segmentation mask into 3d segemetation mask,
   one cell per level
4. do border form segemenation 3d mask
5. expand border
6. get intensity values for each border pixel
7. caluclate requested metrices from boder pixels (e.g. mean, median, quantile)
8. pack output dictionary that maps cell number to metric value
   (carfull, some cell ids might be missing)
'''
'''
# library
import numpy as np

# const
ich = np.array([
    [[True,True],
     [True,True],
     [True,True],
     [True,True]],

    [[False,True],
     [True,False],
     [True, False],
     [False,True]],

    [[False,False],
     [False,False],
     [False, False],
     [False, False]],
])

du = np.array([
    [0,1],
    [2,3],
    [4,5],
    [6,7],
])

ich.shape

er = ich * du

sie = np.array([
    [[1, 1],
     [1, 1],
     [1, 1],
     [1, 1]],
    [[2, 2],
     [2, 2],
     [2, 2],
     [2, 2]],
    [[3, 3],
     [3, 3],
     [3, 3],
     [3, 3]]
])


   ...: du = np.array([                                                                     
   ...:     [0,0,1,1], 
   ...:     [0,0,1,1], 
   ...:     [2,2,3,3], 
   ...:     [2,2,3,3], 
   ...:     [4,4,5,5], 
   ...:     [4,4,5,5], 
   ...:     [6,6,7,7], 
   ...:     [6,6,7,7], 
   ...: ])           


sie.mean(1).mean(1)
np.mean(sie,axis=1)
np.quantile(sie,axis=1).mean(1)

np.mean(sie,axis=1)

a3d = numpy.array([a2d, b2d, c2d])
'''

s_ipath = '/media/bue/G-Drive/data/her2_data/'

# library
import imagine
import numpy as np
from skimage import io
import time


s_ifile_value = 'Registered-R2_PCNA.HER2.ER.Ecad_HER2B-K174-Scene-02_SubR5Qc3_c3_ORG.tiff'
ai_value_tiff = io.imread(f'{s_ipath}{s_ifile_value}')
dai_value = {'HER2': ai_value_tiff}

s_ifile_value = 'Registered-R3_aSMA.AR.pAKT.CD44_HER2B-K174-Scene-02_SubR5Qc2_c2_ORG.tiff'
ai_value_tiff = io.imread(f'{s_ipath}{s_ifile_value}')
dai_value = {'aSMA': ai_value_tiff}


s_ifile_segment = 'Scene_02_matchedcell25_Cell_Segmentation_Basins.tiff'
ai_segment_tiff = io.imread(f'{s_ipath}{s_ifile_segment}')

#plt.imshow(a_tiff)

ei_cell = set(ai_segment_tiff.flatten())
#ei_cell.discard(0)  # background
i_total = len(ei_cell) - 1

ddlr_membran = {}
i_step = 3
t0 = time.time()


ai_segment_border = ai_segment_tiff.copy()
ab_border = imagine.get_border(ai_segment_tiff).astype(bool)
ai_segment_border[~ab_border] = 0
for i, i_cell in enumerate(ei_cell):
    print(f'cell {i_cell}: {i} / {i_total}')

    # get membran segment
    #ai_border = (ai_segment_border == i_cell).astype(int)
    if (i_cell != 0):
        ta_coor = np.where(ai_segment_border == i_cell)
        i_ymin = np.array([ta_coor[0].min() - i_step]).clip(min=0)[0]
        i_xmin = np.array([ta_coor[1].min() - i_step]).clip(min=0)[0]
        i_ymax = np.array([ta_coor[0].max() + i_step]).clip(max=ai_segment_border.shape[0])[0]
        i_xmax = np.array([ta_coor[1].max() + i_step]).clip(max=ai_segment_border.shape[1])[0]
        ai_border = (ai_segment_border == i_cell)[i_ymin:i_ymax,i_xmin:i_xmax].astype(int)
        ab_membran = imagine.grow(ai_border, i_step=3).astype(bool)

    else:
        i_ymin = 0
        i_xmin = 0
        i_ymax = ai_segment_tiff.shape[0]
        i_xmax = ai_segment_tiff.shape[1]
        ai_border = (ai_segment_tiff == i_cell).astype(int)
        ab_membran = ai_border.astype(bool)

    # get value
    dlr_membran = {}
    for s_sensor, ai_value in dai_value.items():
        #ai_membran = ai_value[ab_membran]
        ai_membran = ai_value[i_ymin:i_ymax,i_xmin:i_xmax][ab_membran]
        lr_membran = [
            np.mean(ai_membran),
            np.min(ai_membran),
            np.quantile(ai_membran, 0.01),
            np.quantile(ai_membran, 0.05),
            np.quantile(ai_membran, 0.1),
            np.quantile(ai_membran, 0.2),
            np.quantile(ai_membran, 0.3),
            np.quantile(ai_membran, 0.4),
            np.quantile(ai_membran, 0.5),
            np.quantile(ai_membran, 0.6),
            np.quantile(ai_membran, 0.7),
            np.quantile(ai_membran, 0.8),
            np.quantile(ai_membran, 0.9),
            np.quantile(ai_membran, 0.95),
            np.quantile(ai_membran, 0.99),
            np.max(ai_membran),
        ]
        dlr_membran.update({s_sensor: lr_membran})

    # update output
    ddlr_membran.update({i_cell: dlr_membran})


    #ai_value = tiff_value[i_ymin:i_ymax, i_xmin:i_xmax]
    #lai_segment.append(ai_segment)
    #lai_value.append(ai_value)

t1 = time.time()
td = (t1 - t0) / 60

# note: extract membran  58.043981516361235 [min]
# note: only collecting images  51.85294676224391 [min]

#ai_membran_value =
#r_sum = ai_membran.sum()
#dr_membran.update({i_cell: r_sum})

