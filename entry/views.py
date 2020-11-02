from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings

import os
from datetime import datetime
from PIL import Image
from .forms import *
import cv2
import numpy as np
import pyzbar.pyzbar as pb


# Create your views here.
@login_required
def new_visitor(request):
    employees = Employee.objects.all()
    form = NewVisitorForm()
    if request.method == 'POST':
        form = NewVisitorForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            if form.cleaned_data.get('photo_id'):
                visitor = form.save(commit=False)
                visitor.in_time = datetime.now()
                visitor.save()
                qrcodeimg = generateQR(visitor.id)
                visitor.qrcode = qrcodeimg
                send_qrcode_email(visitor.email, qrcodeimg) # email to send the qr code to the visitor
                visitor.save()
                messages.success(request, 'QR Code has been sent to the visitor\'s email-id')
                return redirect('/')
            else:
                form.save()
                messages.success(request, f'The Visitor has been booked for entry')
                return redirect(reverse('home'))
        else:
            messages.error(request, 'Error!')
    context = {'form': form, 'employees': employees}
    return render(request, 'entry/visitor_booking.html', context)


def generateQR(id):
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4
    )
    visitor = Visitor.objects.get(id=id)  # visitors id
    qr.add_data(id)  # visitors id
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qrname = visitor.name + "_" + str(visitor.in_time.date())
    img.save("./media/qrcodes/" + qrname + ".png")
    
    return "/media/qrcodes/" + qrname + ".png"
    
    # visitor.qrcode = "/media/qrcodes/" + qrname + ".png"
    # visitor.save()
@csrf_exempt
@login_required()
def scanQR(request, **kwargs):
    visitor = Visitor.objects.get(id=kwargs.get('id'))  # visitors id
    print('id', visitor.id)
    cam = cv2.VideoCapture(0)
    br = True
    while br:
        _, frame = cam.read()
        Read = pb.decode(frame)
        for ob in Read:
            readData = int(ob.data.rstrip().decode('utf-8'))
            print('readData',readData)
            if readData == visitor.id:
                br = False
                visitor.out_time = datetime.now()
                visitor.save()
                messages.success(request, f'QR Code scanned successfully!')
                cv2.destroyAllWindows()
                return redirect(f'{reverse("home")}')

        key = cv2.waitKey(1)
        if key == 27:
            break
        
        template_name = 'home/home.html'
        
def send_qrcode_email(to_email, qrcodeimg):
    subject = 'QR Code for entry in Atlas Copco'
    message = '''Hello!\nYou have been granted the permission to visit Atlas Copco as a visitor!\n 
            PFA an attached QR Code which you will have to show when you leave our premises!'''
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to_email])
    email.content_subtype='html'
    
    with open(os.path.join(settings.BASE_DIR, '') + qrcodeimg, mode='rb') as file:
        email.attach(os.path.join(settings.BASE_DIR, '') + qrcodeimg, file.read(), 'image/png')
    
    email.send(fail_silently=False)
    
class VisitorUpdateView(LoginRequiredMixin, UpdateView):
    model = Visitor
    fields = ['name', 'purpose', 'no_of_people', 'email', 'mobile', 'photo_id_number', 'photo_id', 'user']
    success_url = reverse_lazy('home')
    template_name = 'entry/visitor_booking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['employees'] = Employee.objects.all()
        
        return context