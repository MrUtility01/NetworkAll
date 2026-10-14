package com.netenc.app

import android.icu.util.PersianCalendar
import android.icu.util.ULocale
import java.time.Instant
import java.time.OffsetDateTime
import java.time.LocalDateTime
import java.time.ZoneId
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/** قالب تاریخ نمایشی شمسی؛ timestamp ذخیره‌سازی و Sync همچنان ISO-8601 باقی می‌ماند. */
object JalaliDate {
    private val locale = ULocale("fa_IR@calendar=persian")
    fun today(): String = format(Date())
    fun formatIso(value: String?): String {
        if (value.isNullOrBlank()) return "—"
        val date = try { Date.from(Instant.parse(value)) } catch (_: Exception) {
            try { Date.from(OffsetDateTime.parse(value).toInstant()) } catch (_: Exception) {
                try { Date.from(LocalDateTime.parse(value).atZone(ZoneId.systemDefault()).toInstant()) }
                catch (_: Exception) { return "—" }
            }
        }
        return format(date)
    }
    fun format(date: Date): String {
        val calendar = PersianCalendar(TimeZone.getDefault(), locale)
        calendar.time = date
        val digits = String.format(Locale.ROOT, "%04d/%02d/%02d",
            calendar.get(PersianCalendar.YEAR), calendar.get(PersianCalendar.MONTH) + 1,
            calendar.get(PersianCalendar.DAY_OF_MONTH))
        return digits.map { ch ->
            if (ch in '0'..'9') ('۰'.code + (ch.code - '0'.code)).toChar() else ch
        }.joinToString("")
    }
}
