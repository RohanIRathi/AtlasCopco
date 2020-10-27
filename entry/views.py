from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import *
import cv2
import numpy as np
import pyzbar.pyzbar as pb


# Create your views here.
def new_visitor(request):
    if request.method == 'POST':
        form = NewVisitorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was created ')
            return redirect('/')
        else:
            messages.error(request, 'Error!')
    context = {'form': form}
    return render('home/newvisitor.html', context)


def generateQR(request, id):
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4
    )
    visitor =Visitor.objects.get(id=id)
    img_name = visitor.name + "_" + visitor.in_time
    qr.add_data(id)  # visitors id
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("./media/qrcodes/" + img_name + ".png")
    visitor = Visitor.objects.get(id=id)  # visitors id
    visitor.qrcode = "/media/qrcodes/" + img_name + ".png"
    visitor.save()

    if scanQR(request, id):
        messages.success(request,"Scanning Successful!")
        return redirect('/home/')


def scanQR(request,id):
    visitor = Visitor.objects.get(id=id)  # visitors id
    print('id',id)
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_PLAIN
    br = True
    while br:
        _, frame = cam.read()
        Read = pb.decode(frame)
        for ob in Read:
            readData = int(ob.data.rstrip().decode('utf-8'))
            print('readData',readData)
            if readData == id:
                br = False
                return True

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
