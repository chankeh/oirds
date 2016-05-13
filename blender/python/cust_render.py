import bpy
import math
import numpy as np
import random
import img_meta
from SceneControl import SceneControl

config = dict(line.strip().split('=') for line in open('config.properties') if line.find("=")>0)
iterations = int(config['image.count'])
image_factor = float(config['image.factor'])
imp = img_meta.ImgMetaProcess()
imp.openFile('img_desc.csv')

sc = SceneControl(image_name=config['obj.image_name'],lamp_name=config['obj.lamp_name'],scene_name=config['obj.scene_name'],car_name=config['obj.car_name'],car_rotation_axis=config['obj.car_rotation_axis'])

count = 0
for i in range(iterations):
  for imageName, imageMetaList in imp.images.items():
     for imd in imageMetaList:
        count+=1
        sc.set_image_path(imd.name)

        off_nadir = imd.offnadir
        sun_azimuth = imd.azimuth
        sun_elev = imd.elevation
        placement = imd.getImagePlace()

        car_object = bpy.data.objects[config['obj.car_name']] 

        # 180 and 90 assumes the camera is aligned to the y axis
        sc.move_lamp(sun_elev, sun_azimuth, 30)
        sc.move_car(placement[1][0]*image_factor,placement[1][1]*image_factor,car_object.location[2]+0.05,math.radians(placement[0]))
        sc.scale_car(imd.zoom_factor)

        # Render Scene and store the scene
        bpy.data.scenes[config['obj.scene_name']].render.image_settings.file_format = 'PNG'
        bpy.data.scenes[config['obj.scene_name']].render.filepath = 'o_' +  imageName[0:imageName.find('.')] + '_' + str(count)
        bpy.ops.render.render( write_still=True ,use_viewport=True)
