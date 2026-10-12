package com.netenc.app.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface WorkspaceDao {
    @Query("SELECT * FROM tasks WHERE deleted = 0 ORDER BY done ASC, priority DESC, lastUpdated DESC")
    suspend fun allTasks(): List<TaskEntity>

    /** Includes soft-deleted rows so tombstones are not lost during sync. */
    @Query("SELECT * FROM tasks ORDER BY lastUpdated DESC")
    suspend fun allTasksForSync(): List<TaskEntity>

    @Query("SELECT * FROM tasks WHERE uid = :uid LIMIT 1")
    suspend fun taskByUid(uid: String): TaskEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertTask(item: TaskEntity)

    @Query("UPDATE tasks SET deleted = 1, lastUpdated = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE uid = :uid")
    suspend fun deleteTask(uid: String)

    @Query("SELECT * FROM notes WHERE deleted = 0 ORDER BY lastUpdated DESC")
    suspend fun allNotes(): List<NoteEntity>

    @Query("SELECT * FROM notes WHERE uid = :uid LIMIT 1")
    suspend fun noteByUid(uid: String): NoteEntity?

    /** Includes soft-deleted rows so tombstones are not lost during sync. */
    @Query("SELECT * FROM notes ORDER BY lastUpdated DESC")
    suspend fun allNotesForSync(): List<NoteEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertNote(item: NoteEntity)

    @Query("UPDATE notes SET deleted = 1, lastUpdated = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE uid = :uid")
    suspend fun deleteNote(uid: String)

    @Query("SELECT * FROM vault_items ORDER BY title ASC")
    suspend fun allVault(): List<VaultEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertVault(item: VaultEntity)

    @Query("DELETE FROM vault_items WHERE uid = :uid")
    suspend fun deleteVault(uid: String)
}
