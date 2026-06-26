# Lizard — Frontend Specification (Brownfield)

**Agent:** @ux-design-expert (Uma)  
**Date:** 2026-04-17  
**Version:** 1.0  
**Framework:** PyQt6 (Desktop, Linux/X11)

---

## 1. Application Overview

**Type:** Industrial desktop operator interface — full-screen, single-window  
**Target user:** Factory floor operator (Viposa SA) — non-technical, Portuguese-speaking  
**Context:** Real-time leather hide grading station with 4-camera vision system  
**Platform:** Linux + X11 (`QT_QPA_PLATFORM=xcb`), full-screen mode  
**Language:** Portuguese (BR) — all labels and instructions in PT-BR

---

## 2. Layout Architecture

### Single Window: `GradingWindow(QMainWindow)`

```
┌──────────────────────────────────────────────────────────────────┐
│  [SAIR]  [Classe Errada]          │  Status label (current file) │  ← Control Bar (QHBoxLayout)
├──────────────────────────────────────────────────────────────────┤
│  "Tecle ESPAÇO ou clique em 'Classe Errada' se a classe estiver  │  ← Instruction Label
│   errada"                                                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│              VIDEO PREVIEW (fixedHeight=120px)                    │  ← Live camera feed (black bg)
│                                                                    │
├────────────────────────────────────┬──────────┬──────────────────┤
│                                    │          │  [OP]  [Item]    │  ← Summary Cards
│                                    │ Defeitos │  ─────────────── │
│                                    │ (Legend) │  Classe          │  ← Metric Cards
│   RESULT IMAGE                     │          │  Aproveitamento  │
│   (minHeight=400px, black bg)      │  ● name  │  Área            │
│                                    │  ● name  │  ─────────────── │
│                                    │  ● name  │  Resumo da OP    │
│                                    │          │  Couros/Média m²/│
│                                    │          │  Aprov.          │
│                                    │          │  Distribuição    │
│                                    │          │  por classe      │
└────────────────────────────────────┴──────────┴──────────────────┘
```

**Stretch ratios:**
- Result image: `stretch=4`
- Legend panel: `stretch=1` (min 180px, max 220px)
- Metrics panel: `stretch=1` (min 320px)

---

## 3. Design Tokens (Hardcoded — Technical Debt)

All colors are **module-level Python constants** in `pyqt_gui.py`. No design token system exists.

| Token Name | Value | Usage |
|-----------|-------|-------|
| `light_background` | `#E7EDF1` | Card gradient top stop |
| `dark_background` | `#939797` | Card gradient bottom stop |
| `highlight` | `#EC4F16` | Summary values (Viposa orange) |
| `titles` | `#000000` | All header/label text |
| `metrics` | `#131540` | Metric values (dark navy) |

**Technical Debt TD-UI-01:** All 5 color values are hardcoded strings in source. No theming, no design token file.

---

## 4. Component Inventory

### 4.1 Control Bar Components

| Component | Widget | Style | Action |
|-----------|--------|-------|--------|
| Exit Button | `QPushButton("SAIR")` | `background: red; color: white` | Triggers graceful shutdown |
| Mark Button | `QPushButton("Classe Errada")` | Default Qt style | Marks current hide as misclassified |
| Status Label | `QLabel` | Default, left-aligned | Shows current filename being displayed |
| Instruction Label | `QLabel` | Center-aligned | Static user instruction text |

**Technical Debt TD-UI-02:** Exit button uses inline style `background-color: red` — not part of the stylesheet system.

### 4.2 Video Preview

| Property | Value |
|----------|-------|
| Widget | `QLabel` |
| Height | Fixed 120px |
| Background | Black |
| Content | Live camera feed (numpy array → QPixmap) |
| Update rate | 30ms timer (~33fps) |
| Scaling | `KeepAspectRatio + SmoothTransformation` |

### 4.3 Result Image Panel

| Property | Value |
|----------|-------|
| Widget | `QLabel` |
| Min height | 400px |
| Background | Black |
| Content | Processed hide image with defect overlays |
| Scaling | `KeepAspectRatio + SmoothTransformation` |
| Mark overlay | Black banner (50px) + white bold text when marked |

### 4.4 Legend Panel (`QFrame[legendCard]`)

| Property | Value |
|----------|-------|
| Min width | 180px / Max width | 220px |
| Background | Gradient (`light_background` → `dark_background`) |
| Border | `border-radius: 16px` |
| Shadow | `blurRadius=18, offset=(0,4), color=rgba(0,0,0,140)` |
| Content | Title "Defeitos" + per-defect color swatches |

**Legend Item (`QFrame[legendItem]`):**
- Color swatch: 22×22px, `border-radius: 4px`
- Name label: `font-size: 15px; font-weight: 500`
- Data source: `defects.json` (hardcoded path: `/home/viposa/lizard/defects.json`)

**Technical Debt TD-UI-03:** `defects.json` path is **hardcoded absolute path** (`/home/viposa/lizard/defects.json`). Fails on any non-production environment.

### 4.5 Summary Cards (`QFrame[summaryCard]`)

Displays: **OP** (production order number) and **Item** (item description)

| Property | Value |
|----------|-------|
| Background | Gradient |
| Border radius | 16px |
| Header font | 16px, weight 600, `titles` color |
| Value font | 20px, weight 600, `highlight` color (orange) |
| Shadow | `blurRadius=24, offset=(0,6)` |

### 4.6 Metric Cards (`QFrame[metricCard]`)

Displays: **Classe**, **Aproveitamento**, **Área**

| Property | Value |
|----------|-------|
| Background | Gradient |
| Border radius | 16px |
| Header font | 18px, weight 600, `titles` color |
| Value font | 24px, weight 600, `metrics` color (dark navy) |
| Shadow | `blurRadius=20, offset=(0,5)` |

### 4.7 Measurement Card (`QFrame[measurementCard]`)

"Resumo da OP" — aggregate stats for the active production order.

**Sub-components:**
- **Measurement Metric Cards** (3 inline): Couros / Média m² / Aprov.
  - Font: title 14px/600, value 22px/700
  - Border radius: 14px
- **Class Distribution Cards**: Per-class percentage rows
  - Title: `Classe {N}`, Value: `{pct:.1f} %`
  - Font: title 14px/600, value 18px/600

---

## 5. Interaction Patterns

| Interaction | Trigger | Handler | Effect |
|-------------|---------|---------|--------|
| Exit | Button click | `request_shutdown()` | Puts `True` to `shutdown_request_queue`, disables button |
| Exit | `Escape` key | `keyPressEvent` | Same as button |
| Mark wrong class | Button click | `mark_current_image()` | Appends filename to mark file + shows overlay |
| Mark wrong class | `Space` key | `keyPressEvent` | Same as button |
| Window resize | `resizeEvent` | Rescales both pixmaps | Maintains aspect ratio |
| Shutdown from pipeline | `command_queue` message | `check_commands()` | Graceful close (`_closing_from_command=True`) |

**Timers:**
- `update_timer`: 30ms — polls `video_queue` and `result_queue`, updates display
- `command_timer`: 100ms — polls `command_queue` for pipeline commands

---

## 6. Data Flow

```
grading.py (orchestrator)
    ├── video_queue       → pyqt_gui: live camera preview (latest frame only)
    ├── result_queue      → pyqt_gui: grading result dict
    │     ├── image (ndarray)
    │     ├── name (str)
    │     ├── classification (str)
    │     ├── usable_percentage (float)
    │     ├── area (float)
    │     ├── po_num (str)
    │     ├── hide_num (str)
    │     ├── item_name (str)
    │     ├── measurement_summary (dict)
    │     └── detect_end_monotonic (float)
    ├── shutdown_request_queue ← pyqt_gui: operator exit signal
    └── command_queue     → pyqt_gui: pipeline commands ("shutdown")
```

**Queue consumption:** `_pull_latest()` drains queue to always show newest frame — older frames are discarded.

---

## 7. UX Issues and Debt

| ID | Issue | Severity | User Impact |
|----|-------|----------|-------------|
| UX-01 | No loading/startup state shown | MEDIUM | Operator unaware system is initializing |
| UX-02 | No error states displayed | HIGH | Pipeline failures are invisible to operator |
| UX-03 | No visual feedback when Triton is unavailable | HIGH | Blank screen with no explanation |
| UX-04 | `defects.json` hardcoded path | HIGH | Breaks on any non-production machine |
| UX-05 | Instruction label is always visible | LOW | Screen real estate wasted after operator learns system |
| UX-06 | No confirmation dialog for SAIR | MEDIUM | Accidental exits possible |
| UX-07 | Mark button has no visual feedback beyond status label | LOW | Operator may double-press |
| UX-08 | No accessibility (a11y) support | MEDIUM | WCAG not considered; keyboard only partially |
| UX-09 | Full-screen only — no windowed mode | LOW | Debug/dev difficult |
| UX-10 | No internationalization (i18n) layer | LOW | All strings hardcoded in PT-BR |
| UX-11 | Legend re-reads `defects.json` on every result update | MEDIUM | Unnecessary file I/O in hot path |
| UX-12 | No keyboard shortcut documentation visible to user | LOW | Space/Escape shortcuts undiscoverable |

---

## 8. Component Hierarchy (Atomic Design)

```
Pages
└── GradingWindow (single page app)
    │
    Organisms
    ├── ControlBar (buttons + status)
    ├── VideoPreview (live feed strip)
    ├── ResultPanel (image + legend + metrics)
    │
    Molecules
    ├── SummaryCardGroup (OP + Item cards)
    ├── MetricCardGroup (Classe + Aproveitamento + Área)
    ├── MeasurementCard (Resumo da OP)
    ├── LegendPanel (defect swatches)
    └── ClassDistributionList (per-class rows)
    │
    Atoms
    ├── GradientCard (reused by all card types)
    ├── ColorSwatch (legend item dot)
    ├── MetricLabel (header + value pair)
    └── StatusBadge (status text)
```

---

## 9. Recommendations for Improvement

### Priority 1 — Critical UX Fixes
1. **Add error/loading states** — Show operator when system is starting or has failed
2. **Fix hardcoded file path** — Use `BASE_DIR` relative path for `defects.json`
3. **Add SAIR confirmation** — `QMessageBox` to prevent accidental exit

### Priority 2 — Design System Foundation
4. **Extract design tokens** — Move 5 color constants to `ui_tokens.py` or `tokens.json`
5. **Create stylesheet file** — Move inline QSS to external `.qss` file loaded at startup
6. **Cache legend data** — Load `defects.json` once at init, not on every result

### Priority 3 — Operator Experience
7. **Startup screen** — Show "Sistema iniciando..." while Triton loads
8. **Keyboard shortcut help** — Tooltip or overlay showing Space/Escape actions
9. **Mark button feedback** — Visual state change (green border) after marking

---

*Generated by @ux-design-expert (Uma) — Brownfield Discovery Phase 3 — 2026-04-17*
