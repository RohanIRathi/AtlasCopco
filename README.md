# AtlasCopco
Repository for the Atlas Copco project

run `pip install -r requirements.txt` before starting to work on the project.
<br /><br /><br />
The `visitor_booking.html` for booking a visitor and `visitor_entry.html` for allowing entry for a visitor files are present in *entry/templates/entry* folder
<br /><br />
The `login.html` and `signup.html` files for login and signup respectively are present in *home/templates/registration* folder
<br /><br />
The `home.html` file for home template is present in *home/templates/home* folder
<br /><br />
All the static files (images, css, js) are present in *home/templates/registration*
<br>
Make sure to run `python3 manage.py makemigrations`, `python3 manage.py migrate` and `python3 manage.py collectstatic` before testing the project


pyzbar installation is required
<br>
>Note: This part is optional only if you want to test deployment on IIS servers<br>
Added the `web.config` file for deployment on IIS. copy the file present in the main directory which contains the *manage.py* file, just outside the directory. Keep the `web.config` file in the static folder as it is.