// Native-тесты чистой логики (без железа): каналы + энкодер + кнопки.
// Запуск: pio test -e native
#include <string.h>
#include <unity.h>
#include <Arduino.h>            // шам test/support/Arduino.h (setPin/HIGH/LOW)
#include "channels.h"
#include "../src/inputs.cpp"    // реальная реализация Button/Encoder

void setUp(void) {
    memset(g_testPins, 0, sizeof(g_testPins)); // все пины LOW
}

void tearDown(void) {}

// ---- Каналы ----

void test_channels_count(void) {
    TEST_ASSERT_EQUAL_UINT8(40, CHANNEL_COUNT);
}

void test_channel_eu_bounds(void) {
    TEST_ASSERT_EQUAL_UINT32(26965000UL, channelFreq(1, true));
    TEST_ASSERT_EQUAL_UINT32(27405000UL, channelFreq(40, true));
}

void test_channel_rus_minus_5k(void) {
    TEST_ASSERT_EQUAL_UINT32(26960000UL, channelFreq(1, false));
    TEST_ASSERT_EQUAL_UINT32(27400000UL, channelFreq(40, false));
}

void test_channel_clamp(void) {
    TEST_ASSERT_EQUAL_UINT32(26965000UL, channelFreq(0, true));    // ниже → ch1
    TEST_ASSERT_EQUAL_UINT32(27405000UL, channelFreq(41, true));   // выше → ch40
}

void test_freq_to_channel_roundtrip(void) {
    TEST_ASSERT_EQUAL_UINT8(15, freqToChannel(27135000UL, true));   // 27.135 МГц
    TEST_ASSERT_EQUAL_UINT8(1,  freqToChannel(26960000UL, false));  // RUS ch1
}

void test_freq_to_channel_nearest(void) {
    TEST_ASSERT_EQUAL_UINT8(15, freqToChannel(27134000UL, true));   // ближе к ch15
}

// ---- Энкодер ----

void test_encoder_plus_one(void) {
    Encoder e; e.assign(1, 2, 3);
    setPin(1, HIGH); setPin(2, HIGH);
    e.update(0);                       // A=0, B=0, нет фронта
    setPin(2, LOW); setPin(1, LOW);    // фронт A при B==A → +1
    e.update(10);
    TEST_ASSERT_EQUAL_INT16(1, e.readDelta());
}

void test_encoder_minus_one(void) {
    Encoder e; e.assign(1, 2, 3);
    setPin(1, HIGH); setPin(2, HIGH);
    e.update(0);
    setPin(2, HIGH); setPin(1, LOW);   // фронт A при B!=A → -1
    e.update(10);
    TEST_ASSERT_EQUAL_INT16(-1, e.readDelta());
}

void test_encoder_accumulates_and_resets(void) {
    Encoder e; e.assign(1, 2, 3);
    setPin(1, HIGH); setPin(2, HIGH); e.update(0);
    for (int i = 0; i < 3; i++) {
        setPin(1, HIGH); setPin(2, LOW); e.update(20 + i * 10);
        setPin(1, LOW);                  e.update(25 + i * 10);
    }
    TEST_ASSERT_EQUAL_INT16(3, e.readDelta());
    TEST_ASSERT_EQUAL_INT16(0, e.readDelta()); // после чтения — сброс
}

// ---- Кнопки ----

void test_button_click(void) {
    Button b; b.assign(1);
    setPin(1, HIGH); b.update(0);          // отпущена
    setPin(1, LOW);  b.update(5);          // нажатие (дебаунс 5 мс)
    setPin(1, HIGH); b.update(10);         // отпускание
    b.update(10 + DOUBLE_MS + 5);          // окно двойного прошло → CLICK
    TEST_ASSERT_EQUAL_INT((int)BtnEvent::CLICK, (int)b.event());
}

void test_button_double_click(void) {
    Button b; b.assign(1);
    setPin(1, HIGH); b.update(0);
    setPin(1, LOW);  b.update(5);
    setPin(1, HIGH); b.update(10);
    setPin(1, LOW);  b.update(20);         // второй клик в окне
    setPin(1, HIGH); b.update(30);
    TEST_ASSERT_EQUAL_INT((int)BtnEvent::DOUBLE, (int)b.event());
}

void test_button_long_press(void) {
    Button b; b.assign(1);
    setPin(1, HIGH); b.update(0);
    setPin(1, LOW);  b.update(5);          // _tDown = 5
    b.update(5 + LONG_MS + 5);             // удержание ≥ LONG_MS → LONG
    TEST_ASSERT_EQUAL_INT((int)BtnEvent::LONG, (int)b.event());
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(test_channels_count);
    RUN_TEST(test_channel_eu_bounds);
    RUN_TEST(test_channel_rus_minus_5k);
    RUN_TEST(test_channel_clamp);
    RUN_TEST(test_freq_to_channel_roundtrip);
    RUN_TEST(test_freq_to_channel_nearest);
    RUN_TEST(test_encoder_plus_one);
    RUN_TEST(test_encoder_minus_one);
    RUN_TEST(test_encoder_accumulates_and_resets);
    RUN_TEST(test_button_click);
    RUN_TEST(test_button_double_click);
    RUN_TEST(test_button_long_press);
    return UNITY_END();
}
