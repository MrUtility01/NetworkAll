package com.netenc.app.data

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey val uid: String,
    val title: String,
    val body: String = "",
    val done: Boolean = false,
    val dueAt: String = "",
    val priority: Int = 1,
    val lastUpdated: String = "",
    val deviceId: String = "android",
    @ColumnInfo(defaultValue = "0") val deleted: Boolean = false,
    @ColumnInfo(defaultValue = "''") val remindAt: String = "",
    // Device-local delivery state; never included in cross-device sync.
    @ColumnInfo(defaultValue = "''") val remindedAt: String = ""
)

@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val uid: String,
    val title: String,
    val body: String = "",
    val tags: String = "",
    val lastUpdated: String = "",
    val deviceId: String = "android",
    @ColumnInfo(defaultValue = "0") val deleted: Boolean = false,
    // Synchronizes with Windows so both devices can schedule the same reminder.
    @ColumnInfo(defaultValue = "''") val remindAt: String = "",
    // Local delivery guard. Deliberately excluded from synchronization.
    @ColumnInfo(defaultValue = "''") val remindedAt: String = ""
)

@Entity(tableName = "vault_items")
data class VaultEntity(
    @PrimaryKey val uid: String,
    val title: String,
    val username: String = "",
    val secretEnc: String = "",
    val url: String = "",
    val notes: String = "",
    val lastUpdated: String = "",
    val deviceId: String = "android"
)
