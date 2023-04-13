import cv2
import time
import os
import moviepy.editor as moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment


def extract_audio(inputFileName):
    mp4_file = f'{inputFileName}.mp4'
    mp3_file = 'output.mp3'

    videoClip = VideoFileClip(mp4_file)
    audioClip = videoClip.audio

    audioClip.write_audiofile(mp3_file)

    audioClip.close()
    videoClip.close()

    # convert mp3 file to wav
    sound = AudioSegment.from_mp3("output.mp3")
    sound.export("output.wav", format="wav")

    # transcribe audio file
    AUDIO_FILE = "output.wav"

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
        transcript = r.recognize_google(audio)

    texttomp3 = gTTS(text=transcript, lang='en', tld='com')
    texttomp3.save("output.mp3")


def extract_video(inputFileName):
    cascade_classifier = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    source = cv2.VideoCapture(f'{inputFileName}.mp4')

    frame_width = int(source.get(3))
    frame_height = int(source.get(4))

    size = (frame_width, frame_height)

    result = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, size, 1)

    while True:
        ret, img = source.read()

        if img is None:
            break

        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        detected_faces = cascade_classifier.detectMultiScale(gray_image, scaleFactor=1.2, minNeighbors=5,
                                                             minSize=(20, 20))

        for (x, y, width, height) in detected_faces:
            cv2.rectangle(img, (x, y), (x + width, y + height), (0, 0, 0), 0)

        for (x, y, width, height) in detected_faces:
            topLeft = (x, y)
            bottomRight = (x + width, y + height)
            x, y = topLeft[0], topLeft[1]
            w, h = bottomRight[0] - topLeft[0], bottomRight[1] - topLeft[1]

            ROI = img[y:y + height, x:x + width]
            blur = cv2.GaussianBlur(ROI, (281, 281), 0)

            img[y:y + height, x:x + width] = blur

        result.write(img)

    source.release()
    cv2.destroyAllWindows()


def convert_video():
    fileExists = os.path.isfile('output.avi')
    if fileExists:
        clip = moviepy.VideoFileClip('output.avi')
        clip.write_videofile('output.mp4')
    else:
        convert_video()



def combine_audio_video(outputFileName):
    cmd = f"ffmpeg -i output.mp4 -i output.mp3 -c:v copy -c:a aac {outputFileName}.mp4"
    os.system(cmd)

    os.remove('output.avi')
    os.remove('output.wav')
    os.remove('output.mp3')
    os.remove('output.mp4')


if __name__ == '__main__':
    inputFileName = input('Name input MP4 file: ')
    outputFileName = input('Name output MP4 file: ')

    print('Extracting and Anonymizing Audio...')
    extract_audio(inputFileName)
    print('Extracting and Anonymizing Video... (this may take several minutes)')
    extract_video(inputFileName)
    convert_video()
    print('Creating Complete Video...')
    combine_audio_video(outputFileName)
    print(f'Process Complete. Video is saved as {outputFileName}.mp4')
