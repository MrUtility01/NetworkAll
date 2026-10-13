package com.netenc.app.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

@Database(
    entities = [
        LessonEntity::class, SyncMetaEntity::class, ScenarioEntity::class, StudyEntity::class,
        TaskEntity::class, NoteEntity::class, VaultEntity::class
    ],
    version = 8,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun lessonDao(): LessonDao
    abstract fun scenarioDao(): ScenarioDao
    abstract fun studyDao(): StudyDao
    abstract fun workspaceDao(): WorkspaceDao

    companion object {
        // Rebuild the lessons table while adding tree columns so the SQLite schema
        // exactly matches Room (no phantom SQL defaults) and all old lesson rows survive.
        private val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    """
                    CREATE TABLE lessons_new (
                        uid TEXT NOT NULL,
                        entity TEXT NOT NULL,
                        titleFa TEXT NOT NULL,
                        titleEn TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        fullContent TEXT NOT NULL,
                        commands TEXT NOT NULL,
                        examples TEXT NOT NULL,
                        notes TEXT NOT NULL,
                        metaJson TEXT NOT NULL,
                        searchQuery TEXT NOT NULL,
                        learningObjectives TEXT NOT NULL,
                        sourceStatus TEXT NOT NULL,
                        lastUpdated TEXT NOT NULL,
                        contentHash TEXT NOT NULL,
                        deviceId TEXT NOT NULL,
                        deleted INTEGER NOT NULL,
                        chapterOrder INTEGER NOT NULL,
                        chapterTitle TEXT NOT NULL,
                        subTitle TEXT NOT NULL,
                        lessonOrder INTEGER NOT NULL,
                        PRIMARY KEY(uid)
                    )
                    """.trimIndent()
                )
                db.execSQL(
                    """
                    INSERT INTO lessons_new (
                        uid, entity, titleFa, titleEn, tags, summary, fullContent, commands,
                        examples, notes, metaJson, searchQuery, learningObjectives, sourceStatus,
                        lastUpdated, contentHash, deviceId, deleted,
                        chapterOrder, chapterTitle, subTitle, lessonOrder
                    )
                    SELECT
                        uid, entity, titleFa, titleEn, tags, summary, fullContent, commands,
                        examples, notes, metaJson, searchQuery, learningObjectives, sourceStatus,
                        lastUpdated, contentHash, deviceId, deleted, 0, '', '', 0
                    FROM lessons
                    """.trimIndent()
                )
                db.execSQL("DROP TABLE lessons")
                db.execSQL("ALTER TABLE lessons_new RENAME TO lessons")
            }
        }

        private val MIGRATION_2_3 = object : Migration(2, 3) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS scenarios (
                        code TEXT NOT NULL,
                        titleFa TEXT NOT NULL,
                        titleEn TEXT NOT NULL,
                        category TEXT NOT NULL,
                        level TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        users INTEGER NOT NULL,
                        sites INTEGER NOT NULL,
                        vendors TEXT NOT NULL,
                        businessContext TEXT NOT NULL,
                        requirements TEXT NOT NULL,
                        constraintsText TEXT NOT NULL,
                        initialState TEXT NOT NULL,
                        incident TEXT NOT NULL,
                        symptoms TEXT NOT NULL,
                        objectives TEXT NOT NULL,
                        tasks TEXT NOT NULL,
                        hints TEXT NOT NULL,
                        expectedResult TEXT NOT NULL,
                        solution TEXT NOT NULL,
                        verification TEXT NOT NULL,
                        skillsRequired TEXT NOT NULL,
                        estimatedHours INTEGER NOT NULL,
                        PRIMARY KEY(code)
                    )
                    """.trimIndent()
                )
            }
        }

        private val MIGRATION_3_4 = object : Migration(3, 4) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS study_progress (
                        lessonUid TEXT NOT NULL,
                        status TEXT NOT NULL,
                        ease REAL NOT NULL,
                        intervalHours INTEGER NOT NULL,
                        lastStudied TEXT NOT NULL,
                        nextReview TEXT NOT NULL,
                        timesStudied INTEGER NOT NULL,
                        notes TEXT NOT NULL,
                        PRIMARY KEY(lessonUid)
                    )
                    """.trimIndent()
                )
            }
        }

        private val MIGRATION_4_5 = object : Migration(4, 5) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        uid TEXT NOT NULL,
                        title TEXT NOT NULL,
                        body TEXT NOT NULL,
                        done INTEGER NOT NULL,
                        dueAt TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        lastUpdated TEXT NOT NULL,
                        deviceId TEXT NOT NULL,
                        PRIMARY KEY(uid)
                    )
                    """.trimIndent()
                )
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        uid TEXT NOT NULL,
                        title TEXT NOT NULL,
                        body TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        lastUpdated TEXT NOT NULL,
                        deviceId TEXT NOT NULL,
                        PRIMARY KEY(uid)
                    )
                    """.trimIndent()
                )
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS vault_items (
                        uid TEXT NOT NULL,
                        title TEXT NOT NULL,
                        username TEXT NOT NULL,
                        secretEnc TEXT NOT NULL,
                        url TEXT NOT NULL,
                        notes TEXT NOT NULL,
                        lastUpdated TEXT NOT NULL,
                        deviceId TEXT NOT NULL,
                        PRIMARY KEY(uid)
                    )
                    """.trimIndent()
                )
            }
        }

        private val MIGRATION_5_6 = object : Migration(5, 6) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE tasks ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
                db.execSQL("ALTER TABLE notes ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
                db.execSQL("ALTER TABLE scenarios ADD COLUMN lastUpdated TEXT NOT NULL DEFAULT ''")
                db.execSQL("ALTER TABLE scenarios ADD COLUMN contentHash TEXT NOT NULL DEFAULT ''")
                db.execSQL("ALTER TABLE scenarios ADD COLUMN deviceId TEXT NOT NULL DEFAULT 'android'")
                db.execSQL("ALTER TABLE scenarios ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
            }
        }

        private val MIGRATION_6_7 = object : Migration(6, 7) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE study_progress ADD COLUMN lastUpdated TEXT NOT NULL DEFAULT ''")
                db.execSQL("ALTER TABLE study_progress ADD COLUMN deviceId TEXT NOT NULL DEFAULT 'android'")
                db.execSQL("ALTER TABLE study_progress ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
                // Existing phone progress predates lastUpdated. Backfill from lastStudied
                // before the first sync so older local progress isn't overwritten by a
                // server record simply because the new field starts empty.
                db.execSQL("UPDATE study_progress SET lastUpdated = lastStudied WHERE lastUpdated = '' AND lastStudied IS NOT NULL AND lastStudied != ''")
            }
        }

        private val MIGRATION_7_8 = object : Migration(7, 8) {
            override fun migrate(db: SupportSQLiteDatabase) {
                // Reminder time is synced. Delivery history stays local to each device.
                db.execSQL("ALTER TABLE tasks ADD COLUMN remindAt TEXT NOT NULL DEFAULT ''")
                db.execSQL("ALTER TABLE tasks ADD COLUMN remindedAt TEXT NOT NULL DEFAULT ''")
            }
        }

        @Volatile private var INSTANCE: AppDatabase? = null

        fun get(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "netenc.db"
                )
                    // Never wipe notes, tasks, study history, or Vault on an unknown upgrade.
                    // Add explicit Room migrations before increasing the database version.
                    .addMigrations(MIGRATION_1_2, MIGRATION_2_3, MIGRATION_3_4, MIGRATION_4_5, MIGRATION_5_6, MIGRATION_6_7, MIGRATION_7_8)
                    .fallbackToDestructiveMigrationOnDowngrade()
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
