package com.netenc.app.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface StudyDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(row: StudyEntity)

    @Query("SELECT * FROM study_progress WHERE lessonUid = :uid LIMIT 1")
    suspend fun byUid(uid: String): StudyEntity?

    @Query("SELECT * FROM study_progress WHERE deleted = 0 AND nextReview != '' AND nextReview <= :now ORDER BY nextReview LIMIT :limit")
    suspend fun due(now: String, limit: Int = 50): List<StudyEntity>

    @Query("SELECT * FROM study_progress ORDER BY lastUpdated DESC")
    suspend fun allForSync(): List<StudyEntity>

    @Query("SELECT COUNT(*) FROM study_progress WHERE deleted = 0 AND status = :st")
    suspend fun countStatus(st: String): Int

    @Query("SELECT COUNT(*) FROM study_progress WHERE deleted = 0")
    suspend fun countAll(): Int

    @Query("SELECT * FROM study_progress WHERE deleted = 0 AND status IN ('new','learning','review') ORDER BY nextReview LIMIT :limit")
    suspend fun queue(limit: Int = 30): List<StudyEntity>
}
