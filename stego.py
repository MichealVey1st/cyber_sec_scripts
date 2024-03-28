from PIL import Image

def main():
    response = int(input("---- STEGO ----\n 1 Encode\n 2 Decode \n 0 Exit\n\n"))

    if (response == 1):
        imagepath = input("Please enter the path to the image relative to this file:\n")
        secret = input("Please enter message:\n")
        fileName = input("Please enter what you want the filename to be it must end with \".png\":\n")
        encode(imagepath, secret, fileName)
    elif (response == 2):
        imagepath = input("Please enter the path to the image relative to this file:\n")
        decode(imagepath)
    elif (response == 0):
        print("Goodbye!")
        exit()
    else:
        print("\n!! Please enter a valid input !!\n")
        main()

# convert to 8 bit binary form from acii value
def binTranslate(data):
    # list for the binary
    newData = []
    
    for i in data:
        newData.append(format(ord(i), '08b'))

    return newData

def modifyPixel(pix, data):
    dataList = binTranslate(data)
    dataLength = len(dataList)
    imageData = iter(pix)

    for i in range(dataLength):


        pix = [value for value in imageData.__next__()[:3] +
                                imageData.__next__()[:3] +
                                imageData.__next__()[:3]]
        
        # pixel value odd=1 even=0
        for j in range(0, 8):
            if (dataList[i][j] == '0' and pix[j]% 2 != 0):
                pix[j] -= 1
 
            elif (dataList[i][j] == '1' and pix[j] % 2 == 0):
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if (i == dataLength - 1):
            if (pix[-1] % 2 == 0):
                if(pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def encode_image(newImage, data):
    w = newImage.size[0]
    (x,y) = (0,0)

    for pixel in modifyPixel(newImage.getdata(), data):

        # adding pixels to the image copy
        newImage.putpixel((x,y), pixel)
        # iterate through the pixels in a row updating x and y
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1



def encode(imagePath, msg, name):
    print("Starting encoding now.....\n")
    img = Image.open(imagePath, 'r')
    data = msg
    # check if the message actually holds something if not send back to beginning
    if (len(data) == 0):
        print("Message has nothing in it! Lets try that again!\n")
        main()

    newImg = img.copy()
    encode_image(newImg, data)
    newImg.save(name, str(name.split(".")[1].upper()))

    print("DONE!\n")
    main() 

def decode(imagePath):
    print("Starting decoding now.....")
    img = Image.open(imagePath, 'r')

    message = ''
    imageData = iter(img.getdata())

    while (True):
        pixels = [value for value in imageData.__next__()[:3] +
                                        imageData.__next__()[:3]+
                                        imageData.__next__()[:3]]
        
        binaryString = ''

        for i in pixels[:8]:
            if(i % 2 == 0):
                binaryString += '0'
            else:
                binaryString += '1'

        message += chr(int(binaryString, 2))
        if (pixels[-1] % 2 != 0):
            print("The message and maybe extra:\n\n" + message + "\n")
            main()



if __name__ == '__main__':
    main()