#include "ui.h"
#include "app.h"
#include "hal_display.h"
#include <stdio.h>
#include <string.h>

static const char* MENU_ITEMS[] = {
    "Grid", "Step", "Mode", "Squelch", "RIT step", "RIT autoreset", "Backlight", "Factory reset"
};

static void renderBoot(App& app);
static void renderVfo(App& app);
static void renderTx(App& app);
static void renderMenu(App& app);
static void renderRit(App& app);

void Ui::render(App& app) {
    switch (app.state()) {
        case AppState::BOOT: renderBoot(app); break;
        case AppState::VFO:  renderVfo(app); break;
        case AppState::TX:   renderTx(app); break;
        case AppState::MENU: renderMenu(app); break;
        case AppState::RIT:  renderRit(app); break;
    }
}

static void renderBoot(App& app) {
    Display& d = app.display();
    d.clear(RGB565_BLACK);
    d.setText(RGB565_WHITE, 3);
    d.text(40, 90, "TRX 27 MHz");
    d.setText(RGB565_WHITE, 1);
    d.text(60, 130, "control board");
}

static void renderVfo(App& app) {
    Display& d = app.display();
    d.clear(RGB565_BLACK);

    char buf[40];
    snprintf(buf, sizeof(buf), "%.3f", app.rfHz() / 1e6f);
    d.setText(RGB565_WHITE, 3);
    d.text(4, 8, buf);

    d.setText(RGB565_WHITE, 2);
    snprintf(buf, sizeof(buf), "CH %u  %s", app.channel(), app.gridEu() ? "EU" : "RUS");
    d.text(150, 8, buf);

    d.setText(RGB565_WHITE, 1);
    snprintf(buf, sizeof(buf), "%s  RIT %+d Hz  STEP %s",
             app.mode() == Mode::SSB ? "SSB" : "AM",
             (int)app.ritHz(),
             app.step() == 0 ? "5k" : "10k");
    d.text(4, 42, buf);

    d.bar(4, 60, 200, 14, 0.5f, RGB565_GREEN, RGB565_BLACK); // S-метр (placeholder)

    d.setText(RGB565_WHITE, 1);
    snprintf(buf, sizeof(buf), "SQL %u   %s   U/I ---", app.squelch(),
             app.limitSw() ? "LIM" : "FULL");
    d.text(4, 90, buf);

    // Предупреждение по контракту control_pa.md: тумблер FULL при AM.
    if (app.mode() == Mode::AM && !app.limitSw()) {
        d.setText(RGB565_RED, 2);
        d.text(4, 140, "FULL @ AM!");
    }

    d.text(4, 112, "up/dn ch  l/r mode  push menu  enc freq");
}

static void renderTx(App& app) {
    Display& d = app.display();
    d.clear(RGB565_BLACK);

    char buf[40];
    snprintf(buf, sizeof(buf), "%.3f", app.rfHz() / 1e6f);
    d.setText(RGB565_WHITE, 3);
    d.text(4, 8, buf);

    d.setText(RGB565_RED, 2);
    d.text(200, 8, "TX");

    d.setText(RGB565_WHITE, 1);
    snprintf(buf, sizeof(buf), "%s  PWR %.1f W  SWR %.1f",
             app.mode() == Mode::AM ? "AM" : "SSB", app.powerW(), app.swr());
    d.text(4, 42, buf);

    d.bar(4, 60, 250, 12, app.powerW() / 10.0f, RGB565_RED, RGB565_BLACK);
    d.text(4, 90, "MIC-LINE ok");

    // Предупреждение: тумблер FULL при AM (контракт control_pa.md).
    if (app.mode() == Mode::AM && !app.limitSw()) {
        d.setText(RGB565_RED, 2);
        d.text(4, 112, "FULL @ AM!");
    }
}

static void renderMenu(App& app) {
    Display& d = app.display();
    d.clear(RGB565_BLACK);

    d.setText(RGB565_WHITE, 2);
    d.text(4, 4, "MENU");

    const Settings& s = app.settings();
    char val[16];
    char line[40];
    for (uint8_t i = 0; i < 8; i++) {
        switch (i) {
            case 0: strcpy(val, s.grid == 0 ? "EU" : "RUS"); break;
            case 1: strcpy(val, s.step == 0 ? "5 kHz" : "10 kHz"); break;
            case 2: strcpy(val, s.mode == 0 ? "SSB" : "AM"); break;
            case 3: snprintf(val, sizeof(val), "%u", s.squelch); break;
            case 4: strcpy(val, s.ritStep == 0 ? "10 Hz" : "100 Hz"); break;
            case 5: strcpy(val, s.ritAutoreset ? "on" : "off"); break;
            case 6: snprintf(val, sizeof(val), "%u %%", s.brightness); break;
            case 7: strcpy(val, "reset"); break;
        }

        bool sel = (i == app.menuSel());
        d.setText(sel ? RGB565_YELLOW : RGB565_WHITE, 1);
        snprintf(line, sizeof(line), "%s %-14s %s", sel ? ">" : " ", MENU_ITEMS[i], val);
        d.text(4, 26 + i * 20, line);
    }

    d.setText(RGB565_WHITE, 1);
    d.text(4, 200, app.menuEditing() ? "[enc] edit  [enc/push] ok" : "[enc] nav  [enc] select");
}

static void renderRit(App& app) {
    Display& d = app.display();
    d.clear(RGB565_BLACK);

    char buf[40];
    snprintf(buf, sizeof(buf), "RIT %+d Hz", (int)app.ritHz());
    d.setText(RGB565_WHITE, 3);
    d.text(4, 60, buf);

    d.setText(RGB565_WHITE, 1);
    d.text(4, 110, "enc: adjust  RIT: save  dbl: 0");
}
