# 🔍 Buscador de Duplicados

Encuentra imágenes **duplicadas** o **parecidas** en tus carpetas y te ayuda a limpiarlas
**sin miedo a perder nada**: lo que borras va a la **Papelera de reciclaje**, no se elimina
para siempre.

Autor: **KALEVI LATVA AIJO ALEGRIA** · Windows · 100 % local

---

## ✨ Qué hace

- **Dos modos de búsqueda:**
  - 🟦 **Exactos** — archivos **idénticos** byte a byte (hash SHA-256). Muy rápido y seguro.
  - 🟪 **Similares** — imágenes **parecidas** aunque estén **redimensionadas, recomprimidas o
    guardadas en otro formato** (hash perceptual). Con un control de "qué tan parecidas".
- **Elige por ti la mejor copia a conservar:** la de **mayor resolución** (luego la de más peso,
  luego la más antigua). El resto queda marcado para borrar — tú decides.
- **Te dice cuánto espacio vas a recuperar** antes de borrar nada.
- **Seguro:** envía a la **Papelera** (recuperable) y **nunca** te deja borrar todas las copias de
  un grupo: siempre conserva al menos una.

## ▶️ Cómo usarlo

1. Ejecuta **`instalar.bat`** una vez (prepara el entorno).
2. Abre la app con **`Buscar-duplicados.bat`**.
3. **📂 Elige carpeta** → elige el **modo** (Exactos o Similares) → **🔎 Escanear**.
4. Revisa cada **grupo**: la copia con borde **verde** se conserva; las de borde **rojo** se
   enviarán a la papelera (puedes marcar/desmarcar cada una).
5. Pulsa **🗑 Enviar marcados a la papelera**.

> En modo **Similares**, sube el control *Parecido* si quieres agrupar imágenes menos idénticas
> (más flexible), o bájalo para ser más exigente.

## 🧠 Cómo funciona (breve)

- **Exactos:** calcula el SHA-256 de cada archivo; los que tienen el mismo hash son idénticos.
- **Similares:** calcula una *huella perceptual* (dHash) de cada imagen y agrupa las que se
  diferencian en menos que el umbral (distancia de Hamming), usando *union-find* para juntar
  todas las variantes de una misma imagen en un solo grupo.

## 📦 Formatos

`.png` · `.jpg` · `.jpeg` · `.bmp` · `.gif` · `.tiff` · `.webp`

## 🔨 Generar el .exe

`crear_exe.bat` → `dist\BuscadorDuplicados\`. Portátil, sin consola, con icono.

## 🧩 Tecnología

**Python** · **PySide6** (Qt 6) · **Pillow** · **imagehash** (pHash) · **send2trash** (papelera).

---

Hecho con cariño para no volver a perder tiempo (ni espacio) — **KALEVI LATVA AIJO ALEGRIA**
