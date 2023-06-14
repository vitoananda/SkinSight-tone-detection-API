# How to use
clone repository dengan 
```
  git clone https://github.com/vitoananda/SkinSight-disease-detection-API.git
```

Kemudian masukan file keyfile.json yang anda dapatkan dari service account anda yang memiliki role Cloud Storage Admin, Cloud Storage Creator, dan Cloud Storage Viewer

Kemudian masukan juga file serviceAccount.json yang didapatkan dari console project firebase anda

Kemudian ubah isi file .env anda dengan konfigurasi project firebase dan google cloud console anda

# Endpoints

| Method | Endpoint           |
| ------ | ------------------ |  
| POST   | /detect-tone/{uid}           | 




<hr>

### <b>POST /detect-disease/{uid}</b>
Melakukan upload foto kemudian mendapatkan result prediction yang dihasilkan setelah image diproses. 

Request parameter:
uid: uid user

Request body: 
<p align="left"> <img src="./documentation asset/Skin Tone body.jpg" width="700" height="300" /> </p>
Response: 

```json
{
    "type" : "Skin Tone Identification",
    "status": "Success",
    "message": "Deteksi Skin Tone berhasil",
    "detection_img": "{public_url}",
    "class" : "{predicted_class}"
}
```
200 Jika deteksi Skin Tone berhasil

```json
{
  "status": "Failed",
  "message": "Tidak ada file yang ditambahkan"
}
```
400 Jika tidak ada file yang ditambahkan






