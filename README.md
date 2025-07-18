# EdgeFusion

## Prerequisites 
Python 3.7 - 3.12 (above or below that, spaCy is not compatible yet)


- #### pyenv can be used to manage Python versions.

### Install pyenv for Windows:

Follow instructions here:
👉 https://github.com/pyenv-win/pyenv-win#installation

Make sure you restart your terminal after installation.

---
# Project Setup
### Clone the Repository

```
git clone https://github.com/hackatronbits/EdgeFusion.git
cd EdgeFusion
```


### Set Up Virtual Environment
1. Create a virtual environment
```
python -m venv venv
```
2. Activate the virtual environment
Windows:
```
.\venv\Scripts\activate 
```
or (if above doesn't work)
```
source venv/Scripts/activate
```

### Install Required Libraries
```
pip install -r requirements.txt
```
---
### To run the project:
```
python main.py
```
---
# Git Workflow
#### 1. Sync the latest changes before you start working
```
git pull origin main
```


#### 2. Create a new branch 
```
git checkout -b your-feature-name
```
#### 3. Make your changes
#### 4. Check status and stage changes
```
git status         # See what’s changed
git add .          # Stage all changes
```
#### 5. Commit your changes
```
git commit -m "Add: brief description of what you did"
```
#### 6. Push your changes
```
git push origin your-feature-name  # if on a separate branch
```
#### OR
```
git push origin main               # if working directly on main
```
#### 7. Sync again if others pushed meanwhile

```
git pull origin main
```
---
If conflicts occur, fix them, then:
```
git add .
git commit -m "Fix: merge conflicts"
git push origin main
```
