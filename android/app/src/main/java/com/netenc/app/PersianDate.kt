package com.netenc.app

import java.time.LocalDate

/** Gregorian/Solar Hijri conversion for modern dates; no external calendar dependency. */
object PersianDate {
    data class JalaliDate(val year: Int, val month: Int, val day: Int)

    fun toGregorian(jy: Int, jm: Int, jd: Int): LocalDate {
        require(jm in 1..12 && jd in 1..31) { "تاریخ شمسی خارج از محدوده است." }
        var y = jy + 1595
        var days = -355668L + 365L * y + (y / 33) * 8L + ((y % 33 + 3) / 4) + jd
        days += if (jm < 7) (jm - 1) * 31L else (jm - 7) * 30L + 186L

        var gy = 400L * (days / 146097L)
        days %= 146097L
        if (days > 36524L) {
            gy += 100L * ((days - 1L) / 36524L)
            days = (days - 1L) % 36524L
            if (days >= 365L) days++
        }
        gy += 4L * (days / 1461L)
        days %= 1461L
        if (days > 365L) {
            gy += (days - 1L) / 365L
            days = (days - 1L) % 365L
        }
        var gd = (days + 1L).toInt()
        val year = gy.toInt()
        val leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)
        val monthDays = intArrayOf(31, if (leap) 29 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        var gm = 1
        while (gm <= 12 && gd > monthDays[gm - 1]) {
            gd -= monthDays[gm - 1]
            gm++
        }
        val result = LocalDate.of(year, gm, gd)
        require(fromGregorian(result) == JalaliDate(jy, jm, jd)) { "این تاریخ شمسی معتبر نیست." }
        return result
    }

    fun fromGregorian(date: LocalDate): JalaliDate {
        val originalYear = date.year
        var gy = date.year - 1600
        val gm = date.monthValue - 1
        val gd = date.dayOfMonth - 1
        val monthDays = intArrayOf(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        var dayNo = 365L * gy + (gy + 3) / 4 - (gy + 99) / 100 + (gy + 399) / 400
        for (i in 0 until gm) dayNo += monthDays[i]
        val leap = originalYear % 4 == 0 && (originalYear % 100 != 0 || originalYear % 400 == 0)
        if (gm > 1 && leap) dayNo++
        dayNo += gd

        var jDayNo = dayNo - 79L
        val jNp = jDayNo / 12053L
        jDayNo %= 12053L
        var jy = 979L + 33L * jNp + 4L * (jDayNo / 1461L)
        jDayNo %= 1461L
        if (jDayNo >= 366L) {
            jy += (jDayNo - 1L) / 365L
            jDayNo = (jDayNo - 1L) % 365L
        }
        val jm: Int
        val jd: Int
        if (jDayNo < 186L) {
            jm = 1 + (jDayNo / 31L).toInt()
            jd = 1 + (jDayNo % 31L).toInt()
        } else {
            jm = 7 + ((jDayNo - 186L) / 30L).toInt()
            jd = 1 + ((jDayNo - 186L) % 30L).toInt()
        }
        return JalaliDate(jy.toInt(), jm, jd)
    }
}
