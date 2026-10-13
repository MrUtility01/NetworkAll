package com.netenc.app

import android.icu.util.PersianCalendar
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import java.util.TimeZone

/** Persian/Jalali date adapter for Android API 26+. Deadlines are persisted in ISO local date-time. */
object JalaliDate {
    private val dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss")
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm")

    fun today(): String {
        val c = calendar()
        c.timeInMillis = System.currentTimeMillis()
        return "%04d/%02d/%02d".format(Locale.ROOT,
            c.get(PersianCalendar.YEAR), c.get(PersianCalendar.MONTH) + 1,
            c.get(PersianCalendar.DAY_OF_MONTH))
    }

    fun currentTime(): String = LocalDateTime.now().format(timeFormatter)

    fun formatStored(value: String): String {
        if (value.isBlank()) return ""
        return try {
            val local = parseStored(value)
            val c = calendar()
            c.timeInMillis = local.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
            val date = "%04d/%02d/%02d".format(Locale.ROOT,
                c.get(PersianCalendar.YEAR), c.get(PersianCalendar.MONTH) + 1,
                c.get(PersianCalendar.DAY_OF_MONTH))
            "$date · ${local.format(timeFormatter)}"
        } catch (_: Exception) { value }
    }

    fun parseJalali(date: String, time: String): String {
        val normalizedDate = normalizeDigits(date)
        val normalizedTime = normalizeDigits(time)
        val parts = normalizedDate.trim().replace('-', '/').split('/')
        require(parts.size == 3) { "تاریخ را به‌شکل ۱۴۰۵/۰۷/۲۱ وارد کنید." }
        val year = parts[0].toInt()
        val month = parts[1].toInt()
        val day = parts[2].toInt()
        val hm = normalizedTime.trim().split(':')
        require(hm.size == 2) { "ساعت را به‌شکل ۱۴:۳۰ وارد کنید." }
        val hour = hm[0].toInt()
        val minute = hm[1].toInt()
        require(month in 1..12 && day in 1..31 && hour in 0..23 && minute in 0..59) {
            "تاریخ یا ساعت خارج از محدوده است."
        }
        val c = calendar()
        c.clear()
        c.set(PersianCalendar.YEAR, year)
        c.set(PersianCalendar.MONTH, month - 1)
        c.set(PersianCalendar.DAY_OF_MONTH, day)
        c.set(PersianCalendar.HOUR_OF_DAY, hour)
        c.set(PersianCalendar.MINUTE, minute)
        c.set(PersianCalendar.SECOND, 0)
        c.set(PersianCalendar.MILLISECOND, 0)
        val millis = c.timeInMillis
        val check = calendar().apply { timeInMillis = millis }
        require(check.get(PersianCalendar.YEAR) == year &&
            check.get(PersianCalendar.MONTH) == month - 1 &&
            check.get(PersianCalendar.DAY_OF_MONTH) == day) {
            "این تاریخ در تقویم شمسی معتبر نیست."
        }
        return LocalDateTime.ofInstant(Instant.ofEpochMilli(millis), ZoneId.systemDefault())
            .format(dateFormatter)
    }

    fun parseStored(value: String): LocalDateTime {
        val clean = value.trim()
        return try {
            LocalDateTime.parse(clean, DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        } catch (_: Exception) {
            LocalDateTime.ofInstant(Instant.parse(clean), ZoneId.systemDefault())
        }
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

    private fun calendar() = PersianCalendar(TimeZone.getDefault(), Locale("fa", "IR"))
}
