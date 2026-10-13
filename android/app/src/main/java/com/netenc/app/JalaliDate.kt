package com.netenc.app

import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.Locale

/**
 * Persian/Jalali date adapter implemented without a third-party calendar class.
 * Deadlines are persisted in ISO local date-time for compatibility with existing data.
 */
object JalaliDate {
    private val dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss")
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm")
    private val faLocale = Locale("fa", "IR")

    fun today(): String = formatJalali(LocalDate.now())

    fun currentTime(): String = LocalDateTime.now().format(timeFormatter)

    fun daysInMonth(year: Int, month: Int): Int {
        require(month in 1..12)
        return when (month) {
            in 1..6 -> 31
            in 7..11 -> 30
            else -> {
                val start = jalaliToGregorian(year, 1, 1)
                val nextStart = jalaliToGregorian(year + 1, 1, 1)
                if (java.time.temporal.ChronoUnit.DAYS.between(start, nextStart) == 366L) 30 else 29
            }
        }
    }

    fun datePartStored(value: String): String = formatJalali(parseStored(value).toLocalDate())

    fun timePartStored(value: String): String = parseStored(value).format(timeFormatter)

    fun formatStored(value: String): String {
        if (value.isBlank()) return ""
        return try {
            val local = parseStored(value)
            val date = local.toLocalDate()
            val weekday = date.dayOfWeek.getDisplayName(TextStyle.FULL, faLocale)
            "$weekday ${formatJalali(date)} · ${local.format(timeFormatter)}"
        } catch (_: Exception) {
            value
        }
    }

    fun parseJalali(date: String, time: String): String {
        val normalizedDate = normalizeDigits(date)
        val normalizedTime = normalizeDigits(time)
        val parts = normalizedDate.trim().replace('-', '/').split('/')
        require(parts.size == 3) { "تاریخ را به‌شکل ۱۴۰۵/۰۷/۲۱ وارد کنید." }
        val year = parts[0].toInt()
        val month = parts[1].toInt()
        val day = parts[2].toInt()
        require(month in 1..12 && day in 1..daysInMonth(year, month)) {
            "تاریخ شمسی خارج از محدوده یا نامعتبر است."
        }
        val hm = normalizedTime.trim().split(':')
        require(hm.size == 2) { "ساعت را به‌شکل ۱۴:۳۰ وارد کنید." }
        val hour = hm[0].toInt()
        val minute = hm[1].toInt()
        require(hour in 0..23 && minute in 0..59) { "ساعت خارج از محدوده است." }
        return jalaliToGregorian(year, month, day).atTime(hour, minute, 0).format(dateFormatter)
    }

    fun parseStored(value: String): LocalDateTime {
        val clean = value.trim()
        return try {
            LocalDateTime.parse(clean, DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        } catch (_: Exception) {
            LocalDateTime.ofInstant(Instant.parse(clean), ZoneId.systemDefault())
        }
    }

    private fun formatJalali(date: LocalDate): String {
        val (year, month, day) = gregorianToJalali(date.year, date.monthValue, date.dayOfMonth)
        return "%04d/%02d/%02d".format(Locale.ROOT, year, month, day)
    }

    /** Gregorian -> Jalali conversion using the 33-year Jalali cycle. */
    private fun gregorianToJalali(gYear: Int, gMonth: Int, gDay: Int): Triple<Int, Int, Int> {
        val monthOffsets = intArrayOf(0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
        var jy: Int
        var gy = gYear
        if (gy > 1600) {
            jy = 979
            gy -= 1600
        } else {
            jy = 0
            gy -= 621
        }
        val gy2 = if (gMonth > 2) gy + 1 else gy
        var days = 365 * gy + (gy2 + 3) / 4 - (gy2 + 99) / 100 +
            (gy2 + 399) / 400 - 80 + gDay + monthOffsets[gMonth - 1]
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

    /** Jalali -> Gregorian conversion using the 33-year Jalali cycle. */
    private fun jalaliToGregorian(jYear: Int, jMonth: Int, jDay: Int): LocalDate {
        var jy = jYear + 1595
        var days = -355668 + 365 * jy + (jy / 33) * 8 + ((jy % 33 + 3) / 4) + jDay
        days += if (jMonth < 7) (jMonth - 1) * 31 else (jMonth - 7) * 30 + 186

        var gy = 400 * (days / 146097)
        days %= 146097
        if (days > 36524) {
            gy += 100 * ((days - 1) / 36524)
            days = (days - 1) % 36524
            if (days >= 365) days++
        }
        gy += 4 * (days / 1461)
        days %= 1461
        if (days > 365) {
            gy += (days - 1) / 365
            days = (days - 1) % 365
        }
        var gd = days + 1
        val leap = gy % 4 == 0 && (gy % 100 != 0 || gy % 400 == 0)
        val monthLengths = intArrayOf(0, 31, if (leap) 29 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        var gm = 1
        while (gm <= 12 && gd > monthLengths[gm]) {
            gd -= monthLengths[gm]
            gm++
        }
        return LocalDate.of(gy, gm, gd)
    }

    private fun normalizeDigits(value: String): String = buildString(value.length) {
        value.forEach { ch ->
            append(when (ch) {
                in '۰'..'۹' -> ('0'.code + (ch.code - '۰'.code)).toChar()
                in '٠'..'٩' -> ('0'.code + (ch.code - '٠'.code)).toChar()
                else -> ch
            })
        }
    }
}
