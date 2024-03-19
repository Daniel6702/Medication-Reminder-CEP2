# To Do

# Useful Commands

## **Web Server**

### **Run Django App**
1. **Connect to same local network as Pi**
```shell
name: Pixel_6106
password: 11111111
```

2. **Activate Virtual Python Environment:**
```shell
#linux:
source ~/CEP2/venvs/Virtual_Python_Environment/bin/activate

#windows (powershell):
& ".\venvs\windows_venv\Scripts\Activate.ps1"
```

3. **Start Server:**
```shell
cd '.\Django Webserver\'   
python manage.py runserver 0.0.0.0:8000
http://localhost:8000/
```

### **Server Management Commands**
- **Database Migrations:**
```shell
python manage.py makemigrations
python manage.py migrate
```

- **Test User:**
```shell
TESTUSER1
p8uaDACb5e.iS$i
```

- **Deactivate Environment:**
```shell
deactivate
```

## **Github**

- **Setup repository for ssh:**

```shell
git remote set-url origin git@github.com:Daniel6702/Medication-Reminder-CEP2.git
```

- **Push changes to github**

```shell
git add .
git commit -m "commit message"
git push -u origin master
```

- **Pull changes from github**

```shell
git pull origin master
```

## **General Commands**

- **Install python libraries**
```shell
pip install Django djangorestframework mysqlclient paho-mqtt==1.6.1
```

### **File and Directory Operations**
- **Allow file to be saved:**

```shell
chmod 777 filename.py
```

- **Copy file to a new location:** 

```shell
cp file.txt /path/to/destination/directory/
```

- **Copy folder to a different location:**

```shell
cp -r /path/to/source/folder /path/to/destination/folder
```

- **Delete file:**

```shell
sudo rm file.txt
```

- **Delete folder:**

```shell
rm -rf /path/to/folder
```

- **Rename folder or file:**

```shell
mv oldfile.txt newfile.txt
```

### **Login Command**

```shell
ssh peder@192.168.60.160
password: password
```

## **Zigbee2mqtt Commands**

```shell
cd /opt/zigbee2mqtt
```
```shell
npm start
```

## **Database Operations**

### **MySQL Commands**
- **Open MySQL shell:**

```shell
sudo mysql -u root -p
```

- **Show Users:**

```shell
SELECT User, Host FROM mysql.user WHERE User = 'cep2';
```

- **Grant PRIVILEGES:**

```shell
GRANT ALL PRIVILEGES ON django_db.* TO 'django_user'@'%' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
```

- **Database Operations:**
  
```shell
SHOW DATABASES; # shows available databases
USE cep2; # select database
SHOW TABLES; # show database tables
DESCRIBE events; # describe 'events' table fields
```

### **Database Backup and Restoration**
- **Export the Database:**

```shell
mysqldump -u django_user -p django_db > django_db_backup.sql
```

- **Import the Database:**

```shell
mysql -u django_user -p new_django_db < django_db_backup.sql
```

### **MariaDB Service Management**
- **Start Service:**

```shell
sudo systemctl start mariadb
```

- **Stop Service:**

```shell
sudo systemctl stop mariadb
```

- **Restart Service:**

```shell
sudo systemctl restart mariadb
```

- **Check Service Status:**

```shell
sudo systemctl status mariadb
```

- **Enable Start on Boot:**

```shell
sudo systemctl enable mariadb
```

- **Disable Start on Boot:**

```shell
sudo systemctl disable mariadb
```























