package com.netenc.app.util

import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

/** Small dependency-free Gregorian -> Jalali formatter for task dates. */
object JalaliDate {
    fun formatIso(iso: String, zone: ZoneId = ZoneId.systemDefault()): String {
        if (iso.isBlank()) return "بدون موعد"
        return try {
            val date = Instant.parse(iso).atZone(zone).toLocalDate()
            val parts = fromGregorian(date)
            digits(parts.first.toString()) + "/" +
                digits(parts.second.toString().padStart(2, '0')) + "/" +
                digits(parts.third.toString().padStart(2, '0'))
        } catch (_: Exception) {
            iso
        }
    }

    fun fromGregorian(date: LocalDate): Triple<Int, Int, Int> {
        val gy = date.year - 1600
        val gm = date.monthValue - 1
        val gd = date.dayOfMonth - 1
        val gdm = intArrayOf(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        var dayNo = 365 * gy + (gy + 3) / 4 - (gy + 99) / 100 + (gy + 399) / 400
        for (i in 0 until gm) dayNo += gdm[i]
        if (gm > 1 && ((date.year % 4 == 0 && date.year % 100 != 0) || date.year % 400 == 0)) dayNo++
        dayNo += gd
        var jDayNo = dayNo - 79
        val jNp = jDayNo / 12053
        jDayNo %= 12053
        var jy = 979 + 33 * jNp + 4 * (jDayNo / 1461)
        jDayNo %= 1461
        if (jDayNo >= 366) {
            jy += (jDayNo - 1) / 365
            jDayNo = (jDayNo - 1) % 365
        }
        val jm: Int
        val jd: Int
        if (jDayNo < 186) {
            jm = 1 + jDayNo / 31
            jd = 1 + jDayNo % 31
        } else {
            jm = 7 + (jDayNo - 186) / 30
            jd = 1 + (jDayNo - 186) % 30
        }
        return Triple(jy, jm, jd)
    }

    fun toGregorian(jy: Int, jm: Int, jd: Int): LocalDate {
        require(jm in 1..12) { "Jalali month must be 1..12" }
        require(jd in 1..31) { "Jalali day must be 1..31" }
        var jYear = jy - 979
        var jDayNo = 365 * jYear + (jYear / 33) * 8 + ((jYear % 33) + 3) / 4
        jDayNo += if (jm <= 6) (jm - 1) * 31 else 186 + (jm - 7) * 30
        jDayNo += jd - 1

        var gDayNo = jDayNo + 79
        var gy = 1600 + 400 * (gDayNo / 146097)
        gDayNo %= 146097
        var leap = true
        if (gDayNo >= 36525) {
            gDayNo--
            gy += 100 * (gDayNo / 36524)
            gDayNo %= 36524
            if (gDayNo >= 365) gDayNo++ else leap = false
        }
        gy += 4 * (gDayNo / 1461)
        gDayNo %= 1461
        if (gDayNo >= 366) {
            leap = false
            gDayNo--
            gy += gDayNo / 365
            gDayNo %= 365
        }
        val monthDays = intArrayOf(31, if (leap) 29 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        var gm = 0
        while (gm < 12 && gDayNo >= monthDays[gm]) {
            gDayNo -= monthDays[gm]
            gm++
        }
        return LocalDate.of(gy, gm + 1, gDayNo + 1)
    }

    fun monthLength(jy: Int, jm: Int): Int {
        val first = toGregorian(jy, jm, 1)
        val nextYear = if (jm == 12) jy + 1 else jy
        val nextMonth = if (jm == 12) 1 else jm + 1
        return java.time.temporal.ChronoUnit.DAYS.between(first, toGregorian(nextYear, nextMonth, 1)).toInt()
    }

    fun monthName(jm: Int): String = listOf(
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ).getOrElse(jm - 1) { "ماه" }

    fun persianDigits(value: String): String = digits(value)

    private fun digits(value: String): String = value.map { ch ->
        if (ch in '0'..'9') ('۰'.code + (ch - '0')).toChar() else ch
    }.joinToString("")
}
