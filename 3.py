from detectron2.engine import DefaultPredictor
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
from detectron2.utils.video_visualizer import VideoVisualizer
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2 import model_zoo
from PIL import Image 
import PIL 
import cv2
import numpy as np
import tqdm
import os
from detectron2.utils.visualizer import ColorMode


class Detector:

    def __init__(self, model_type = "objectDetection"):
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
        self.cfg.MODEL.DEVICE = "cpu" # cpu or cuda

        self.predictor = DefaultPredictor(self.cfg)

    def onImage(self, imagePath):
        image = cv2.imread(imagePath)
        predictions = self.predictor(image)

        viz = Visualizer(image[:,:,::-1],metadata= MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]),scale=1.2)#instance_mode=ColorMode.IMAGE_BW)
        
        output = viz.draw_instance_predictions(predictions['instances'].to('cpu'))
        filename = 'result.jpg'
        cv2.imwrite(filename, output.get_image()[:,:,::-1])
        #cv2.imshow("Result",output.get_image()[:,:,::-1])
        cv2.waitKey(0)
        cv2.destroyAllWindows()


        






    def onVideo(self,videoPath):
        video = cv2.VideoCapture(videoPath)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames_per_second = video.get(cv2.CAP_PROP_FPS)
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        #fourcc = cv2.VideoWriter_fourcc(*'mpv4')
        #out = cv2.VideoWriter("detected_video.mp4", fourcc, 20.0, (w, h))

        #initializing videoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mpv4')
        video_writer = cv2.VideoWriter("output.mp4", fourcc , fps=float(frames_per_second), frameSize=(width, height), isColor=True)

       
        v = VideoVisualizer(MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), ColorMode.IMAGE)

        def runOnVideo(video,maxFrames):# this is for debugging

            readFrames = 0
            while True:
                hasFrame , frame = video.read()
                if not hasFrame:
                    break
                outputs = self.predictor(frame)
                

                frame  = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                visualization = v.draw_instance_predictions(frame, outputs['instances'].to('cpu'))
                visualization = cv2.cvtColor(visualization.get_image(),cv2.COLOR_RGB2BGR)
                yield visualization
                
                readFrames += 1
                if readFrames > maxFrames:
                    break
        num_frames = 200 # here  we reinitialize the number of frames because  of it'll take hours to write the detectedVideos to our video_file and since we don't have a gpu
        # if num_frames is not re-inititialized. the entire frames of the video will be taken into account.. usually taking hours to detect since a 'cpu' and not'gpu' is used
        for visualization in tqdm.tqdm(runOnVideo(video, num_frames), total = num_frames):
            #cv2.imwrite("detected_image.png", visualization)

            video_writer.write(visualization)
        video.release()
        video_writer.release()
        cv2.destroyAllWindows()

import streamlit as st
#from objectDetection import *
#detector = Detector(model_type='keypointsDetection')

#detector.onVideo("pexels-tima-miroshnichenko-6388396.mp4")
#@st.cache
def func_1(x):
    detector = Detector(model_type=x)
    image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg'])
    if image_file is not None:
        file_details = {"FileName":image_file.name,"FileType":image_file.type}
        st.write(file_details)
        img = Image.open(image_file)
        st.image(img, caption='Uploaded Image.')
        with open(image_file.name,mode = "wb") as f: 
            f.write(image_file.getbuffer())         
        st.success("Saved File")
        detector.onImage(image_file.name)
        img_ = Image.open("result.jpg")
        st.image(img_, caption='Proccesed Image.')

def func_2(x):
    detector = Detector(model_type=x)
    uploaded_video = st.file_uploader("Upload Video", type = ['mp4','mpeg','mov'])
    if uploaded_video != None:
        
        vid = uploaded_video.name
        with open(vid, mode='wb') as f:
            f.write(uploaded_video.read()) # save video to disk
    
        st_video = open(vid,'rb')
        video_bytes = st_video.read()
        st.video(video_bytes)
        st.write("Uploaded Video")
        detector.onVideo(vid)
        st_video = open('output.mp4','rb')
        video_bytes = st_video.read()
        st.video(video_bytes)
        st.write("Detected Video") 



def main():
    with st.expander("About the App"):
        st.markdown( '<p style="font-size: 30px;"><strong>Welcome to my Object Detection App!</strong></p>', unsafe_allow_html= True)
        st.markdown('<p style = "font-size : 20px; color : white;">This app was built using Streamlit, Detectron2 and OpenCv to demonstrate <strong>Object Detection</strong> in both videos (pre-recorded) and images.</p>', unsafe_allow_html=True)
        


    option = st.selectbox(
     'What Type of File do you want to work with?',
     ('Images', 'Videos'))

    #st.write('You selected:', option)
    if option == "Images":
        st.title('Object Detection for Images')
        st.subheader("""
This takes in an image and outputs the image with bounding boxes created around the objects in the image.
""")
        func_1('objectDetection')
    else:
        st.title('Object Detection for Videos')
        st.subheader("""
This takes in a video and outputs the video with bounding boxes created around the objects in the video.
""")
        func_2('objectDetection')


if __name__ == '__main__':
		main()