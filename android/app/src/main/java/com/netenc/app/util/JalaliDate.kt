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

    private fun digits(value: String): String = value.map { ch ->
        if (ch in '0'..'9') ('۰'.code + (ch - '0')).toChar() else ch
    }.joinToString("")
}
