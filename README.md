# To Do

# Useful Commands

## **Github**

- **Setup repository for ssh:**
git remote set-url origin git@github.com:Daniel6702/Medication-Reminder-CEP2.git

- **Push changes to github**
git add .
git commit -m "commit message"
git push -u origin master

- **Pull changes from github**
git pull origin master

## **Web Server Management**
### **Virtual Environment**
- **Activate Environment:**
source ~/CEP2/Django\ Webserver/Virtual_Python_Environment/bin/activate

- **Deactivate Environment:**
deactivate

### **Django Server Commands**
- **Start Server:**
python manage.py runserver 0.0.0.0:8000

- **Database Migrations:**
python manage.py makemigrations
python manage.py migrate

## **General Commands**

### **File and Directory Operations**
- **Allow file to be saved:**
chmod 777 filename.py

- **Copy file to a new location:** 
cp file.txt /path/to/destination/directory/

- **Copy folder to a different location:**
cp -r /path/to/source/folder /path/to/destination/folder

- **Delete file:**
sudo rm file.txt

- **Delete folder:**
rm -rf /path/to/virtualenv

- **Rename folder or file:**
mv oldfile.txt newfile.txt

### **Software Installation**
- **Install Python MQTT library:**
sudo apt install python3-paho-mqtt

### **Login Command**
ssh peder@192.168.60.160
password: password

## **Zigbee2mqtt Commands**
cd /opt/zigbee2mqtt
npm start

## **Database Operations**

### **MySQL Commands**
- **Open MySQL shell:**

sudo mysql -u root -p

- **Show Users:**
SELECT User, Host FROM mysql.user WHERE User = 'cep2';

- **Database Operations:**
SHOW DATABASES; # shows available databases
USE cep2; # select database
SHOW TABLES; # show database tables
DESCRIBE events; # describe 'events' table fields

### **Database Backup and Restoration**
- **Export the Database:**
mysqldump -u django_user -p django_db > django_db_backup.sql

- **Import the Database:**
mysql -u django_user -p new_django_db < django_db_backup.sql

### **MariaDB Service Management**
- **Start Service:**
sudo systemctl start mariadb

- **Stop Service:**
sudo systemctl stop mariadb

- **Check Service Status:**
sudo systemctl status mariadb

- **Enable Start on Boot:**
sudo systemctl enable mariadb

- **Disable Start on Boot:**
sudo systemctl disable mariadb























