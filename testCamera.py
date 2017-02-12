from picamera import PiCamera
from io import BytesIO

def captureImage():

    camera = None
    
    try:
        image = BytesIO()
        camera = PiCamera()
        camera.resolution = (640,480)
        camera.capture(image, 'png')
    except Exception as e:
        print(e)
    finally:
        if camera!=None:
            camera.close()

    imageFile = open("test.png", "wb")
    imageFile.write(image.getvalue())
    imageFile.close()

if __name__ == "__main__":
    captureImage()


