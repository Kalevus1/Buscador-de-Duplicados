# -*- coding: utf-8 -*-
"""
Buscador de Duplicados — Día 11
Encuentra imágenes duplicadas o parecidas y te ayuda a limpiar sin perder nada.

Dos modos:
  • Exactos   — archivos idénticos byte a byte (hash SHA-256). Rápido y seguro.
  • Similares — imágenes parecidas aunque estén redimensionadas o recomprimidas
                (hash perceptual). Umbral ajustable.

Seguridad: lo que borras va a la PAPELERA de reciclaje (recuperable), no se borra
para siempre. Siempre se conserva al menos una copia por grupo (la de mejor calidad).

Autor: KALEVI LATVA AIJO ALEGRIA
"""
import os
import sys
import hashlib
from collections import defaultdict
from datetime import datetime

from PySide6.QtCore import Qt, QObject, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout,
    QScrollArea, QListWidget, QListWidgetItem, QProgressBar, QFileDialog, QMessageBox,
    QCheckBox, QComboBox, QSlider, QFrame,
)

EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")


def _guard_pythonw():
    if sys.stdout is None or sys.stderr is None:
        d = open(os.devnull, "w")
        sys.stdout = sys.stdout or d
        sys.stderr = sys.stderr or d


def human_size(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024


def info_archivo(path):
    """(tamaño_bytes, (w,h) o None, fecha_mtime)."""
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0
    dims = None
    try:
        from PIL import Image
        with Image.open(path) as im:
            dims = im.size
    except Exception:
        pass
    try:
        fecha = datetime.fromtimestamp(os.path.getmtime(path))
    except OSError:
        fecha = None
    return size, dims, fecha


def _calidad(path):
    """Puntaje para elegir qué copia CONSERVAR: más resolución > más peso > más antigua."""
    size, dims, fecha = info_archivo(path)
    px = (dims[0] * dims[1]) if dims else 0
    antig = -fecha.timestamp() if fecha else 0   # más antigua = mayor puntaje
    return (px, size, antig)


# --------------------------------------------------------------------------- scan
class ScanWorker(QObject):
    progreso = Signal(int, int, str)     # hechos, total, texto
    terminado = Signal(list)             # lista de grupos (cada grupo = lista de rutas)
    cancelado = Signal()                 # el escaneo se detuvo a petición del usuario
    error = Signal(str)

    def __init__(self, carpeta, modo, umbral):
        super().__init__()
        self.carpeta = carpeta
        self.modo = modo          # "exactos" | "similares"
        self.umbral = umbral
        self._cancelar = False

    def cancelar(self):
        self._cancelar = True

    def run(self):
        try:
            archivos = []
            for base, _dirs, files in os.walk(self.carpeta):
                for f in files:
                    if f.lower().endswith(EXTS):
                        archivos.append(os.path.join(base, f))
            if not archivos:
                self.terminado.emit([])
                return
            if self.modo == "exactos":
                grupos = self._exactos(archivos)
            else:
                grupos = self._similares(archivos)
            if self._cancelar:
                self.cancelado.emit()
                return
            # ordenar: más archivos primero
            grupos.sort(key=lambda g: len(g), reverse=True)
            self.terminado.emit(grupos)
        except Exception as e:
            self.error.emit(str(e))

    def _exactos(self, archivos):
        total = len(archivos)
        buckets = defaultdict(list)
        for i, ruta in enumerate(archivos):
            if self._cancelar:
                return []
            try:
                h = hashlib.sha256()
                with open(ruta, "rb") as fp:
                    for chunk in iter(lambda: fp.read(1 << 20), b""):
                        h.update(chunk)
                buckets[h.hexdigest()].append(ruta)
            except Exception:
                pass
            if i % 15 == 0 or i == total - 1:
                self.progreso.emit(i + 1, total, f"Analizando {i + 1}/{total}…")
        return [p for p in buckets.values() if len(p) > 1]

    def _similares(self, archivos):
        import imagehash
        from PIL import Image
        total = len(archivos)
        hashes = []   # (hash, ruta)
        for i, ruta in enumerate(archivos):
            if self._cancelar:
                return []
            try:
                with Image.open(ruta) as im:
                    hashes.append((imagehash.dhash(im, hash_size=8), ruta))
            except Exception:
                pass
            if i % 10 == 0 or i == total - 1:
                self.progreso.emit(i + 1, total, f"Calculando huellas {i + 1}/{total}…")

        n = len(hashes)
        self.progreso.emit(n, n, "Agrupando imágenes parecidas…")
        # union-find sobre todas las parejas con distancia <= umbral
        padre = list(range(n))

        def find(x):
            while padre[x] != x:
                padre[x] = padre[padre[x]]
                x = padre[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                padre[ra] = rb

        for a in range(n):
            if self._cancelar:
                return []
            ha = hashes[a][0]
            for b in range(a + 1, n):
                if (ha - hashes[b][0]) <= self.umbral:
                    union(a, b)
            if a % 25 == 0:
                self.progreso.emit(a + 1, n, f"Comparando {a + 1}/{n}…")

        comp = defaultdict(list)
        for idx in range(n):
            comp[find(idx)].append(hashes[idx][1])
        return [rutas for rutas in comp.values() if len(rutas) > 1]


# --------------------------------------------------------------------------- tarjeta
class Tarjeta(QFrame):
    """Miniatura de un archivo con su info y checkbox de borrar."""
    def __init__(self, ruta, conservar=False):
        super().__init__()
        self.ruta = ruta
        self.setObjectName("tarjeta")
        self.setFixedWidth(230)
        v = QVBoxLayout(self); v.setContentsMargins(8, 8, 8, 8); v.setSpacing(6)

        thumb = QLabel(); thumb.setFixedSize(214, 150); thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setObjectName("thumb")
        pm = QPixmap(ruta)
        if not pm.isNull():
            thumb.setPixmap(pm.scaled(214, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation))
        else:
            thumb.setText("sin vista previa")
        v.addWidget(thumb)

        size, dims, fecha = info_archivo(ruta)
        nombre = QLabel(os.path.basename(ruta)); nombre.setObjectName("nombre")
        nombre.setWordWrap(True); nombre.setMaximumHeight(34)
        v.addWidget(nombre)
        dim_txt = f"{dims[0]}×{dims[1]}" if dims else "—"
        f_txt = fecha.strftime("%Y-%m-%d") if fecha else "—"
        meta = QLabel(f"{dim_txt} · {human_size(size)} · {f_txt}"); meta.setObjectName("meta")
        v.addWidget(meta)

        if conservar:
            badge = QLabel("✓ CONSERVAR"); badge.setObjectName("badge_keep")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(badge)
            self.chk = None
            self.setProperty("keep", True)
        else:
            self.chk = QCheckBox("🗑  Enviar a papelera")
            self.chk.setChecked(True)
            self.chk.toggled.connect(self._on_toggle)
            v.addWidget(self.chk)
        self._sync_estilo()

    def _on_toggle(self, _):
        self._sync_estilo()

    def _sync_estilo(self):
        marcado = self.marcado()
        self.setProperty("marcado", marcado)
        self.style().unpolish(self); self.style().polish(self)

    def marcado(self):
        return self.chk is not None and self.chk.isChecked()


# --------------------------------------------------------------------------- ventana
class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buscador de Duplicados")
        self.resize(1180, 780)
        self.setStyleSheet(QSS)
        self.grupos = []
        self.carpeta = ""
        self.hilo = None
        self.worker = None
        self.tarjetas = []
        self._ui()

    def _ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # barra superior
        top = QFrame(); top.setObjectName("top")
        tl = QHBoxLayout(top); tl.setContentsMargins(16, 12, 16, 12); tl.setSpacing(10)
        # controles tipo "reproductor": Abrir · Escanear · Cancelar
        self.btn_carpeta = QPushButton("📂  Abrir carpeta"); self.btn_carpeta.setObjectName("accent")
        self.btn_carpeta.clicked.connect(self._elegir)
        self.btn_scan = QPushButton("🔎  Escanear"); self.btn_scan.setObjectName("accent")
        self.btn_scan.clicked.connect(self._escanear); self.btn_scan.setEnabled(False)
        self.btn_cancel = QPushButton("⏹  Cancelar"); self.btn_cancel.setObjectName("danger")
        self.btn_cancel.clicked.connect(self._cancelar_scan); self.btn_cancel.setEnabled(False)
        self.lbl_carpeta = QLabel("Ninguna carpeta seleccionada"); self.lbl_carpeta.setObjectName("ruta")
        tl.addWidget(self.btn_carpeta)
        tl.addWidget(self.btn_scan)
        tl.addWidget(self.btn_cancel)
        tl.addWidget(self.lbl_carpeta, 1)

        tl.addWidget(QLabel("Modo:"))
        self.combo = QComboBox()
        self.combo.addItem("Exactos · idénticos 100%", "exactos")
        self.combo.addItem("Similares · parecidos 95%", "similares")
        self.combo.currentIndexChanged.connect(self._modo_cambio)
        tl.addWidget(self.combo)
        self.btn_info = QPushButton("ℹ️"); self.btn_info.setObjectName("info")
        self.btn_info.setFixedWidth(40); self.btn_info.setToolTip("¿Qué es cada modo?")
        self.btn_info.clicked.connect(self._info_modos)
        tl.addWidget(self.btn_info)

        self.umbral_wrap = QWidget(); self.umbral_wrap.setObjectName("transp")
        uw = QHBoxLayout(self.umbral_wrap); uw.setContentsMargins(0, 0, 0, 0)
        uw.addWidget(QLabel("Parecido:"))
        self.slider = QSlider(Qt.Orientation.Horizontal); self.slider.setFixedWidth(110)
        self.slider.setRange(0, 16); self.slider.setValue(5)
        self.slider.valueChanged.connect(lambda v: self.lbl_umbral.setText(self._texto_umbral(v)))
        self.lbl_umbral = QLabel(self._texto_umbral(5)); self.lbl_umbral.setObjectName("meta")
        uw.addWidget(self.slider); uw.addWidget(self.lbl_umbral)
        tl.addWidget(self.umbral_wrap)
        self.umbral_wrap.hide()
        root.addWidget(top)

        # progreso
        pf = QFrame(); pf.setObjectName("progbar")
        pl = QHBoxLayout(pf); pl.setContentsMargins(16, 8, 16, 8); pl.setSpacing(12)
        self.estado = QLabel("Elige una carpeta para empezar."); self.estado.setObjectName("estado")
        self.barra = QProgressBar(); self.barra.setTextVisible(False); self.barra.setFixedHeight(8)
        pl.addWidget(self.estado, 1); pl.addWidget(self.barra, 1)
        root.addWidget(pf)

        # cuerpo
        body = QHBoxLayout(); body.setContentsMargins(16, 12, 16, 0); body.setSpacing(12)
        izq = QVBoxLayout(); izq.setSpacing(6)
        izq.addWidget(QLabel("Grupos encontrados:"))
        self.lista = QListWidget(); self.lista.setObjectName("lista"); self.lista.setFixedWidth(260)
        self.lista.currentRowChanged.connect(self._grupo_sel)
        izq.addWidget(self.lista, 1)
        self.resumen = QLabel(""); self.resumen.setObjectName("meta"); self.resumen.setWordWrap(True)
        izq.addWidget(self.resumen)
        body.addLayout(izq)

        self.scroll = QScrollArea(); self.scroll.setObjectName("scroll"); self.scroll.setWidgetResizable(True)
        self.cards_host = QWidget(); self.grid = QGridLayout(self.cards_host)
        self.grid.setContentsMargins(6, 6, 6, 6); self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.cards_host)
        body.addWidget(self.scroll, 1)
        root.addLayout(body, 1)

        # barra inferior de acciones
        bottom = QFrame(); bottom.setObjectName("bottom")
        bl = QHBoxLayout(bottom); bl.setContentsMargins(16, 10, 16, 10); bl.setSpacing(10)
        self.info_sel = QLabel(""); self.info_sel.setObjectName("meta")
        bl.addWidget(self.info_sel, 1)
        self.chk_todos = QPushButton("Marcar todas menos la mejor"); self.chk_todos.setObjectName("ghost")
        self.chk_todos.clicked.connect(self._marcar_todas); self.chk_todos.setEnabled(False)
        bl.addWidget(self.chk_todos)
        self.btn_borrar = QPushButton("🗑  Enviar marcados a la papelera"); self.btn_borrar.setObjectName("danger")
        self.btn_borrar.clicked.connect(self._borrar); self.btn_borrar.setEnabled(False)
        bl.addWidget(self.btn_borrar)
        root.addWidget(bottom)

    # ---------- helpers de modo/umbral
    def _texto_umbral(self, v):
        if v <= 2: return f"exigente ({v})"
        if v <= 6: return f"normal ({v})"
        if v <= 10: return f"flexible ({v})"
        return f"muy flexible ({v})"

    def _modo_cambio(self):
        self.umbral_wrap.setVisible(self.combo.currentData() == "similares")

    def _info_modos(self):
        m = QMessageBox(self)
        m.setWindowTitle("¿Qué modo elegir?")
        m.setTextFormat(Qt.TextFormat.RichText)
        m.setText(
            "<h3>🟦 Exactos · idénticos 100%</h3>"
            "<p>Encuentra archivos <b>exactamente iguales</b>, byte a byte: la misma imagen copiada "
            "tal cual. Segurísimo — si coinciden, es literalmente el mismo archivo.</p>"
            "<h3>🟪 Similares · parecidos 95%</h3>"
            "<p>Encuentra imágenes que <b>se parecen</b> aunque no sean idénticas: redimensionadas, "
            "recomprimidas, guardadas en otro formato o con pequeños retoques.<br>"
            "Usa el control <b>«Parecido»</b> para exigir más (menos resultados, más idénticas) "
            "o menos (más resultados, algo más distintas).</p>")
        m.exec()

    # ---------- flujo
    def _elegir(self):
        d = QFileDialog.getExistingDirectory(self, "Elige la carpeta a revisar")
        if d:
            self.carpeta = d
            self.lbl_carpeta.setText(d)
            self.btn_scan.setEnabled(True)
            self.estado.setText("Carpeta lista. Pulsa «Escanear».")
            self._limpiar_resultados()

    def _escanear(self):
        if not self.carpeta or not os.path.isdir(self.carpeta):
            QMessageBox.warning(self, "Atención", "Elige una carpeta válida.")
            return
        self._limpiar_resultados()
        self.btn_scan.setEnabled(False); self.btn_carpeta.setEnabled(False); self.combo.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.barra.setRange(0, 0)   # indeterminada hasta el primer progreso
        self.estado.setText("Escaneando…")

        self.worker = ScanWorker(self.carpeta, self.combo.currentData(), self.slider.value())
        self.hilo = QThread()
        self.worker.moveToThread(self.hilo)
        self.hilo.started.connect(self.worker.run)
        self.worker.progreso.connect(self._on_progreso)
        self.worker.terminado.connect(self._on_terminado)
        self.worker.cancelado.connect(self._on_cancelado)
        self.worker.error.connect(self._on_error)
        self.hilo.start()

    def _cancelar_scan(self):
        """Detiene el escaneo en curso para poder empezar otro."""
        if self.worker:
            self.worker.cancelar()
            self.btn_cancel.setEnabled(False)
            self.estado.setText("Cancelando…")

    def _on_cancelado(self):
        self._fin_hilo()
        self.barra.setRange(0, 100); self.barra.setValue(0)
        self.estado.setText("⏹  Escaneo cancelado. Puedes empezar otro.")

    def _on_progreso(self, hechos, total, texto):
        if self.barra.maximum() != total:
            self.barra.setRange(0, max(1, total))
        self.barra.setValue(hechos)
        self.estado.setText(texto)

    def _on_error(self, msg):
        self._fin_hilo()
        QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{msg}")

    def _on_terminado(self, grupos):
        self._fin_hilo()
        self.grupos = grupos
        self.barra.setRange(0, 100); self.barra.setValue(0)
        if not grupos:
            self.estado.setText("✅ No se encontraron duplicados. ¡Todo limpio!")
            self.resumen.setText("")
            return
        total_arch = sum(len(g) for g in grupos)
        recuperable = sum(self._recuperable(g) for g in grupos)
        self.estado.setText(f"✅ {len(grupos)} grupos · {total_arch} archivos.")
        self.resumen.setText(f"Espacio recuperable estimado:\n<b>{human_size(recuperable)}</b> "
                             f"(borrando las copias, conservando la mejor de cada grupo).")
        self.lista.clear()
        for i, g in enumerate(grupos):
            it = QListWidgetItem(f"Grupo {i + 1}  ·  {len(g)} archivos  ·  {human_size(self._recuperable(g))}")
            self.lista.addItem(it)
        self.lista.setCurrentRow(0)

    def _fin_hilo(self):
        if self.hilo:
            self.hilo.quit(); self.hilo.wait()
        self.hilo = None; self.worker = None
        self.btn_scan.setEnabled(True); self.btn_carpeta.setEnabled(True); self.combo.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _recuperable(self, grupo):
        """Bytes que se recuperan si borramos todo menos la mejor copia."""
        mejor = max(grupo, key=_calidad)
        return sum(os.path.getsize(p) for p in grupo if p != mejor and os.path.exists(p))

    # ---------- vista de un grupo
    def _grupo_sel(self, row):
        self._vaciar_grid()
        if row < 0 or row >= len(self.grupos):
            self.btn_borrar.setEnabled(False); self.chk_todos.setEnabled(False)
            return
        grupo = self.grupos[row]
        mejor = max(grupo, key=_calidad)
        # mejor primero
        ordenado = [mejor] + [p for p in grupo if p != mejor]
        cols = max(1, (self.scroll.width() - 40) // 246)
        for i, ruta in enumerate(ordenado):
            t = Tarjeta(ruta, conservar=(ruta == mejor))
            if t.chk:
                t.chk.toggled.connect(self._actualizar_info)
            self.tarjetas.append(t)
            self.grid.addWidget(t, i // cols, i % cols)
        self.btn_borrar.setEnabled(True); self.chk_todos.setEnabled(True)
        self._actualizar_info()

    def _marcar_todas(self):
        for t in self.tarjetas:
            if t.chk:
                t.chk.setChecked(True)
        self._actualizar_info()

    def _actualizar_info(self, *_):
        marcados = [t for t in self.tarjetas if t.marcado()]
        bytes_ = sum(os.path.getsize(t.ruta) for t in marcados if os.path.exists(t.ruta))
        self.info_sel.setText(f"{len(marcados)} archivo(s) marcado(s) · se recuperarán {human_size(bytes_)}")

    # ---------- borrado (a papelera)
    def _borrar(self):
        marcados = [t.ruta for t in self.tarjetas if t.marcado()]
        if not marcados:
            QMessageBox.information(self, "Nada marcado", "Marca al menos un archivo para enviar a la papelera.")
            return
        # nunca dejar el grupo vacío
        if len(marcados) >= len(self.tarjetas):
            QMessageBox.warning(self, "Atención",
                                "No puedes borrar TODOS los del grupo. Deja al menos una copia (la marcada como CONSERVAR).")
            return
        lista = "\n".join(f"• {os.path.basename(p)}" for p in marcados[:12])
        if len(marcados) > 12:
            lista += f"\n… y {len(marcados) - 12} más"
        r = QMessageBox.question(
            self, "Enviar a la papelera",
            f"Se enviarán {len(marcados)} archivo(s) a la Papelera de reciclaje "
            f"(podrás recuperarlos desde ahí):\n\n{lista}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes:
            return
        from send2trash import send2trash
        ok, fallos = 0, []
        for p in marcados:
            try:
                send2trash(os.path.abspath(p))
                ok += 1
            except Exception as e:
                fallos.append(f"{os.path.basename(p)}: {e}")
        # actualizar estructura
        row = self.lista.currentRow()
        borrados = set(marcados)
        self.grupos[row] = [p for p in self.grupos[row] if p not in borrados]
        self.grupos = [g for g in self.grupos if len(g) > 1]
        self.estado.setText(f"✅ {ok} archivo(s) enviados a la papelera.")
        if fallos:
            QMessageBox.warning(self, "Algunos no se pudieron mover", "\n".join(fallos))
        # refrescar lista
        cur = min(row, len(self.grupos) - 1)
        self.lista.clear()
        for i, g in enumerate(self.grupos):
            self.lista.addItem(f"Grupo {i + 1}  ·  {len(g)} archivos  ·  {human_size(self._recuperable(g))}")
        if self.grupos:
            self.lista.setCurrentRow(max(0, cur))
        else:
            self._vaciar_grid()
            self.estado.setText("✅ ¡No quedan más duplicados!")
            self.resumen.setText("")
            self.btn_borrar.setEnabled(False); self.chk_todos.setEnabled(False)

    # ---------- utilidades UI
    def _vaciar_grid(self):
        self.tarjetas = []
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        self.info_sel.setText("")

    def _limpiar_resultados(self):
        self.grupos = []
        self.lista.clear()
        self._vaciar_grid()
        self.resumen.setText("")
        self.btn_borrar.setEnabled(False); self.chk_todos.setEnabled(False)


QSS = """
* { font-family: 'Segoe UI'; font-size: 13px; }
QWidget { background: #0f1420; color: #ffffff; }
/* Las etiquetas NO pintan fondo: heredan el del panel donde están (evita los recuadros). */
QLabel { background: transparent; color: #ffffff; }
QWidget#transp { background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QLabel#ruta { color: #cbd3e6; }
QLabel#estado { color: #ffffff; }
QLabel#meta { color: #aeb7d1; font-size: 12px; }
QFrame#top, QFrame#bottom { background: #141b2b; border: none; }
QFrame#progbar { background: #0f1420; }
QPushButton { background: #263149; color: #ffffff; border: none; border-radius: 9px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #30405f; }
QPushButton:disabled { background: #1a2233; color: #c3ccdf; }
QPushButton#accent { background: #3b82f6; color: #ffffff; }
QPushButton#accent:hover { background: #2f6fe0; }
QPushButton#accent:disabled { background: #2b3f66; color: #ffffff; }
QPushButton#danger { background: #e0424d; color: #ffffff; }
QPushButton#danger:hover { background: #c8303b; }
QPushButton#danger:disabled { background: #5e2b30; color: #ffffff; }
QPushButton#info { background: #1a2233; color: #ffffff; font-size: 15px; padding: 8px 4px; }
QPushButton#info:hover { background: #263149; }
QPushButton#ghost { background: transparent; border: 1px solid #2c3852; color: #b9c3dc; }
QPushButton#ghost:hover { background: #1a2233; }
QComboBox { background: #1a2233; border: 1px solid #2c3852; border-radius: 8px; padding: 6px 10px; }
QComboBox QAbstractItemView { background: #1a2233; selection-background-color: #3b82f6; }
QListWidget#lista { background: #141b2b; border: 1px solid #232f47; border-radius: 10px; padding: 4px; }
QListWidget#lista::item { padding: 8px; border-radius: 6px; }
QListWidget#lista::item:selected { background: #3b82f6; color: #fff; }
QScrollArea#scroll { background: #0f1420; border: none; }
QProgressBar { background: #1a2233; border: none; border-radius: 4px; }
QProgressBar::chunk { background: #3b82f6; border-radius: 4px; }
QFrame#tarjeta { background: #141b2b; border: 1px solid #232f47; border-radius: 12px; }
QFrame#tarjeta[marcado="true"] { border: 2px solid #e0424d; background: #1b1622; }
QFrame#tarjeta[keep="true"] { border: 2px solid #22c55e; }
QLabel#thumb { background: #0b0f19; border-radius: 8px; color: #55607a; }
QLabel#nombre { color: #ffffff; font-weight: 600; font-size: 12px; }
QLabel#badge_keep { background: #16351f; color: #6ee7a0; border-radius: 6px; padding: 5px; font-weight: 700; }
QCheckBox { color: #ffffff; font-weight: 600; background: transparent; }
QCheckBox::indicator { width: 16px; height: 16px; }
QSlider::groove:horizontal { height: 5px; background: #2c3852; border-radius: 2px; }
QSlider::handle:horizontal { background: #3b82f6; width: 15px; margin: -6px 0; border-radius: 7px; }
"""


def main():
    _guard_pythonw()
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    v = Ventana(); v.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
