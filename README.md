# 🔍 Buscador de Duplicados

Autor / Author / Tekijä: **KALEVI LATVA AIJO ALEGRIA** · Windows · 100 % local

> 🇪🇸 Español · 🇬🇧 English · 🇫🇮 Suomi — el mismo documento en tres idiomas más abajo.

---

## 🇪🇸 Español

Encuentra imágenes **duplicadas** o **parecidas** en tus carpetas y te ayuda a limpiarlas
**sin miedo a perder nada**: lo que borras va a la **Papelera de reciclaje**, no se elimina
para siempre.

### ✨ Qué hace
- **Dos modos:**
  - 🟦 **Exactos** — archivos **idénticos** byte a byte (hash SHA-256). Rápido y seguro.
  - 🟪 **Similares** — imágenes **parecidas** aunque estén **redimensionadas, recomprimidas o
    en otro formato** (hash perceptual), con un control de "qué tan parecidas".
- **Elige por ti la mejor copia a conservar** (mayor resolución → más peso → más antigua).
- **Te dice cuánto espacio recuperas** antes de borrar nada.
- **Seguro:** envía a la **Papelera** y **nunca** deja borrar todas las copias de un grupo.

### ▶️ Cómo usarlo
1. Ejecuta **`instalar.bat`** una vez.
2. Abre la app con **`Buscar-duplicados.bat`**.
3. **📂 Elige carpeta** → elige el **modo** → **🔎 Escanear**.
4. Revisa cada grupo: la copia con borde **verde** se conserva; las de borde **rojo** se van a
   la papelera (puedes marcar/desmarcar). Pulsa **🗑 Enviar marcados a la papelera**.

### 📦 Formatos
`.png` · `.jpg` · `.jpeg` · `.bmp` · `.gif` · `.tiff` · `.webp`

### 🔨 Generar el .exe
`crear_exe.bat` crea **dos** versiones: la de **carpeta** (`dist\BuscadorDuplicados\`, arranca
rápido) y la **empaquetada** en un solo archivo (`dist\BuscadorDuplicados.exe`, portátil).

---

## 🇬🇧 English

Finds **duplicate** or **similar** images in your folders and helps you clean them up
**without fear of losing anything**: whatever you delete goes to the **Recycle Bin**, it is not
erased forever.

### ✨ What it does
- **Two modes:**
  - 🟦 **Exact** — **byte-identical** files (SHA-256 hash). Fast and safe.
  - 🟪 **Similar** — **look-alike** images even if **resized, recompressed or in another format**
    (perceptual hash), with a "how similar" control.
- **Picks the best copy to keep for you** (highest resolution → largest size → oldest).
- **Tells you how much space you'll recover** before deleting anything.
- **Safe:** sends files to the **Recycle Bin** and **never** lets you delete every copy in a group.

### ▶️ How to use
1. Run **`instalar.bat`** once.
2. Open the app with **`Buscar-duplicados.bat`**.
3. **📂 Choose folder** → pick the **mode** → **🔎 Scan**.
4. Review each group: the **green**-bordered copy is kept; the **red**-bordered ones go to the
   Recycle Bin (toggle as you like). Press **🗑 Send marked to the Recycle Bin**.

### 📦 Formats
`.png` · `.jpg` · `.jpeg` · `.bmp` · `.gif` · `.tiff` · `.webp`

### 🔨 Build the .exe
`crear_exe.bat` builds **two** versions: the **folder** one (`dist\BuscadorDuplicados\`, fast
startup) and the **single-file** one (`dist\BuscadorDuplicados.exe`, portable).

---

## 🇫🇮 Suomi

Etsii **kaksoiskappaleita** tai **samankaltaisia** kuvia kansioistasi ja auttaa siivoamaan ne
**pelkäämättä menettäväsi mitään**: poistettu menee **roskakoriin**, sitä ei tuhota lopullisesti.

### ✨ Mitä se tekee
- **Kaksi tilaa:**
  - 🟦 **Tarkat** — **tavulleen identtiset** tiedostot (SHA-256-tiiviste). Nopea ja turvallinen.
  - 🟪 **Samankaltaiset** — **samannäköiset** kuvat vaikka niitä olisi **skaalattu, pakattu
    uudelleen tai tallennettu toiseen muotoon** (havaintotiiviste), säädettävällä herkkyydellä.
- **Valitsee puolestasi parhaan säilytettävän** (suurin tarkkuus → suurin koko → vanhin).
- **Kertoo kuinka paljon tilaa vapautuu** ennen kuin mitään poistetaan.
- **Turvallinen:** lähettää tiedostot **roskakoriin** eikä **koskaan** anna poistaa ryhmän kaikkia
  kopioita.

### ▶️ Käyttö
1. Aja **`instalar.bat`** kerran.
2. Avaa sovellus **`Buscar-duplicados.bat`**-tiedostolla.
3. **📂 Valitse kansio** → valitse **tila** → **🔎 Skannaa**.
4. Käy ryhmät läpi: **vihreä**reunainen säilyy; **puna**reunaiset menevät roskakoriin (voit
   valita/poistaa valinnan). Paina **🗑 Lähetä merkityt roskakoriin**.

### 📦 Muodot
`.png` · `.jpg` · `.jpeg` · `.bmp` · `.gif` · `.tiff` · `.webp`

### 🔨 Luo .exe
`crear_exe.bat` luo **kaksi** versiota: **kansio**version (`dist\BuscadorDuplicados\`, nopea
käynnistys) ja **yhden tiedoston** version (`dist\BuscadorDuplicados.exe`, siirrettävä).

---

## 🧩 Tecnología / Technology / Teknologia

**Python** · **PySide6** (Qt 6) · **Pillow** · **imagehash** (dHash) · **send2trash** (papelera).

## 🌐 Web / Pages

Hay una **versión web** (`web/`) que escanea una carpeta en el navegador (File System Access API,
Chrome/Edge) — **solo muestra** los duplicados, **no puede borrarlos** (límite del navegador).
La página de presentación está en `docs/` (GitHub Pages).

---

Hecho con cariño para no volver a perder tiempo (ni espacio) — **KALEVI LATVA AIJO ALEGRIA**
