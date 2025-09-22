# 📊 DSE Voetbal Data Project

Interactieve topscorerspagina in **DSE-stijl**, automatisch gegenereerd vanuit Google Sheets en voetbal.nl data.  
De HTML wordt direct naar GitHub gepusht zodat deze online te bekijken is.  

![Voorbeeld weergave](assets/screenshot.png)

---

## ⚙️ Vereisten

### Software
- [Python 3.10+](https://www.python.org/downloads/)  
- [Google Chrome](https://www.google.com/chrome/)  
- [ChromeDriver](https://chromedriver.chromium.org/downloads) (zelfde versie als je Chrome)  
- [Git](https://git-scm.com/downloads)  

---

## 📦 Installatie

### Python dependencies installeren
Gebruik het meegeleverde `requirements.txt` bestand:

```bash
pip install -r requirements.txt

Handmatig installeren kan ook:

```bash
pip install selenium gspread oauth2client plotly

--- 

## 🔑 Google API credentials

1. Ga naar Google Cloud Console
2. Maak een nieuw project aan en activeer:
3. Google Sheets API
4. Google Drive API
5. Maak een Service Account aan en download de credentials.json
6. Zet credentials.json in de hoofdmap van dit project
7. Deel de juiste Google Sheets met het service account e-mailadres (meestal iets als xxxx@xxxx.iam.gserviceaccount.com) met bewerkerrechten

## ⚙️ Configuratie
config.json

Hierin staat de login- en teamconfiguratie:

```json
{
  "chrome": {
    "chromedriver_path": "C:/Data/voetbal/chromedriver.exe",
    "chrome_binary_path": "C:/Program Files/Google/Chrome/Application/chrome.exe"
  },
  "teams": [
    {
      "name": "JO13-1",
      "username": "voorbeeld@dse.nl",
      "password": "geheim",
      "spreadsheet_id": "xxxxxxxxxxxxxxxxxxxx",
      "sheet_name_uitslagen": "Uitslagen",
      "sheet_name_aanwezigheid": "Aanwezigheid",
      "team_url": "https://www.voetbal.nl/team/T123456789/uitslagen"
    }
  ]
}