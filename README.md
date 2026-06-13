# dnie-firmador

**[ES]** Aplicación de escritorio para firmar digitalmente documentos PDF usando el DNIe peruano (Documento Nacional de Identidad Electrónico) en Linux.  
**[EN]** Desktop application to digitally sign PDF documents using the Peruvian DNIe (Electronic National Identity Document) on Linux.

---

## ¿Qué hace? / What does it do?

**[ES]**  
Permite firmar PDFs con tu DNIe peruano directamente desde Linux, sin necesidad de Windows ni Refirma. El sello visual es compatible con el formato de Refirma (RENIEC) y totalmente personalizable.

**[EN]**  
Sign PDFs with your Peruvian DNIe directly from Linux, without needing Windows or Refirma. The visual stamp is compatible with Refirma's format (RENIEC) and fully customizable.

### Características / Features

- 📄 Visor de PDF interactivo — arrastra y posiciona la firma donde quieras / Interactive PDF viewer — drag and drop the signature anywhere
- 🖋️ Firma digital con DNIe peruano vía lector USB / Digital signature with Peruvian DNIe via USB reader
- 🎨 Apariencia personalizable: escudo nacional o imagen propia, motivo, datos / Customizable appearance: national coat of arms or custom image, reason, data
- 🔐 Ingreso seguro de PIN / Secure PIN entry
- ✅ Compatible con estándar PAdES (PDF Advanced Electronic Signatures)
- 🐧 Nativo en Linux (Debian/Ubuntu)

---

## Requisitos / Requirements

**Hardware:**
- Lector USB de tarjetas inteligentes compatible con PC/SC / PC/SC-compatible USB smart card reader  
  *(Probado con / Tested with: bit4id miniLector-EVO)*
- DNIe peruano v2

**Software:**
- Python 3.11+
- `pcscd` (PC/SC daemon)
- `libpcsclite1`

```bash
sudo apt install pcscd libpcsclite1
```

---

## Instalación / Installation

```bash
pip install dnie-firmador
```

O desde el código fuente / Or from source:

```bash
git clone https://github.com/dlocmot/dnie-firmador.git
cd dnie-firmador
pip install -e ".[dev]"
```

---

## Uso / Usage

```bash
dnie-firmador
```

1. **[ES]** Abre un PDF → Selecciona la página y posición de la firma → Configura la apariencia → Haz clic en "Firmar" → Ingresa tu PIN → Guarda el PDF firmado.  
   **[EN]** Open a PDF → Select the page and signature position → Configure appearance → Click "Sign" → Enter your PIN → Save the signed PDF.

---

## Arquitectura / Architecture

```
src/dnie_firmador/
├── card/        # Comunicación con el DNIe vía pyscard / DNIe communication via pyscard
├── signing/     # Firma PDF con pyHanko / PDF signing with pyHanko
├── ui/          # Interfaz gráfica PyQt6 / PyQt6 GUI
└── assets/      # Recursos gráficos / Graphic assets
```

---

## Compatibilidad de lectores / Reader compatibility

| Lector / Reader         | Estado / Status |
|------------------------|-----------------|
| bit4id miniLector-EVO  | ✅ Probado / Tested |
| ACR122U (NFC)          | 🔬 Por probar / To test |
| Otros PC/SC / Other    | 🔬 Por probar / To test |

---

## Contribuir / Contributing

**[ES]** Las contribuciones son bienvenidas. Por favor abre un issue antes de enviar un PR para discutir los cambios.  
**[EN]** Contributions are welcome. Please open an issue before submitting a PR to discuss changes.

---

## Licencia / License

MIT © 2026 dlocmot@gmail.com

---

## Reconocimientos / Acknowledgments

- [peru-dnie](https://github.com/edeustua/peru-dnie) — Comunicación con DNIe peruano / Peruvian DNIe communication
- [pyHanko](https://github.com/MatthiasValvekens/pyHanko) — Firma PDF / PDF signing
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) — Renderizado de PDF / PDF rendering
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — Interfaz gráfica / GUI
- Escudo Nacional del Perú — [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Escudo_nacional_del_Per%C3%BA.svg) (Dominio público / Public domain)
