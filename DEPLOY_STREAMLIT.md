# Déployer sur Streamlit Cloud

## Étapes

### 1. Créer un dépôt GitHub

1. Va sur [github.com](https://github.com) et connecte-toi
2. Clique sur **New repository**
3. Nom : `babs-leye-assistant` (ou autre)
4. Public, sans README
5. Crée le dépôt

### 2. Pousser ton code

Dans le terminal, depuis le dossier `bot` :

```powershell
cd "c:\Users\Mr LEYE\Downloads\bot"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/babs-leye-assistant.git
git push -u origin main
```

Remplace `TON_USERNAME` par ton nom d'utilisateur GitHub.

### 3. Déployer sur Streamlit Cloud

1. Va sur [share.streamlit.io](https://share.streamlit.io)
2. Connecte-toi avec GitHub
3. Clique sur **New app**
4. Remplis :
   - **Repository** : `TON_USERNAME/babs-leye-assistant`
   - **Branch** : `main`
   - **Main file path** : `app.py`
   - **App URL** (optionnel) : `babs-leye-assistant` pour avoir `babs-leye-assistant.streamlit.app`
5. Clique sur **Advanced settings**
6. Dans **Secrets**, colle :

```
GOOGLE_API_KEY = "ta-cle-api-gemini-ici"
```

7. Clique sur **Deploy**

### 4. Lien de ton app

Après le déploiement (2–5 min), ton app sera disponible à :

**https://babs-leye-assistant.streamlit.app**

(ou l’URL indiquée par Streamlit si tu n’as pas choisi de sous-domaine personnalisé)
