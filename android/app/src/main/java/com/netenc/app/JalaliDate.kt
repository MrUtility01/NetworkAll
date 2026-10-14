package com.netenc.app

import java.time.Instant
import java.time.OffsetDateTime
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.util.Date
import java.util.Locale

/**
 * قالب تاریخ نمایشی شمسی.
 * زمان‌های ذخیره‌سازی و Sync همچنان ISO-8601 باقی می‌مانند.
 */
object JalaliDate {
    fun today(): String = format(Date())

    fun formatIso(value: String?): String {
        if (value.isNullOrBlank()) return "—"
        val date = try {
            Date.from(Instant.parse(value))
        } catch (_: Exception) {
            try {
                Date.from(OffsetDateTime.parse(value).toInstant())
            } catch (_: Exception) {
                try {
                    Date.from(LocalDateTime.parse(value).atZone(ZoneId.systemDefault()).toInstant())
                } catch (_: Exception) {
                    return "—"
                }
            }
        }
        return format(date)
    }

    fun format(date: Date): String {
        val day = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate()
        val (jy, jm, jd) = gregorianToJalali(day)
        val ascii = String.format(Locale.ROOT, "%04d/%02d/%02d", jy, jm, jd)
        return ascii.map { ch ->
            if (ch in '0'..'9') ('۰'.code + (ch.code - '0'.code)).toChar() else ch
        }.joinToString("")
    }

    /**
     * Gregorian-to-Jalali civil-date conversion (common 33-year-cycle algorithm).
     * All calculations are integer based; no device locale/calendar dependency.
     */
    private fun gregorianToJalali(date: LocalDate): Triple<Int, Int, Int> {
        var gy = date.year
        val gm = date.monthValue
        val gd = date.dayOfMonth
        val gMonthDays = intArrayOf(0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)

        var jy: Int
        if (gy > 1600) {
            jy = 979
            gy -= 1600
        } else {
            jy = 0
            gy -= 621
        }

        val gy2 = if (gm > 2) gy + 1 else gy
        var days = 365 * gy +
            (gy2 + 3) / 4 -
            (gy2 + 99) / 100 +
            (gy2 + 399) / 400 -
            80 + gd + gMonthDays[gm - 1]

        jy += 33 * (days / 12053)
        days %= 12053
        jy += 4 * (days / 1461)
        days %= 1461

        if (days > 365) {
            jy += (days - 1) / 365
            days = (days - 1) % 365
        }

        val jm: Int
        val jd: Int
        if (days < 186) {
            jm = 1 + days / 31
            jd = 1 + days % 31
        } else {
            jm = 7 + (days - 186) / 30
            jd = 1 + (days - 186) % 30
        }
        return Triple(jy, jm, jd)
    }
}
