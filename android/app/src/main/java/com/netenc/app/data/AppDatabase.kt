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
    version = 5,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun lessonDao(): LessonDao
    abstract fun scenarioDao(): ScenarioDao
    abstract fun studyDao(): StudyDao
    abstract fun workspaceDao(): WorkspaceDao

    companion object {
        /**
         * Version 4 already contains lessons, sync_meta, scenarios and study_progress.
         * Add workspace tables without rebuilding or clearing those existing records.
         */
        private val MIGRATION_4_5 = object : Migration(4, 5) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL(
                    """CREATE TABLE IF NOT EXISTS `tasks` (
                        `uid` TEXT NOT NULL,
                        `title` TEXT NOT NULL,
                        `body` TEXT NOT NULL,
                        `done` INTEGER NOT NULL,
                        `dueAt` TEXT NOT NULL,
                        `priority` INTEGER NOT NULL,
                        `lastUpdated` TEXT NOT NULL,
                        `deviceId` TEXT NOT NULL,
                        PRIMARY KEY(`uid`)
                    )"""
                )
                database.execSQL(
                    """CREATE TABLE IF NOT EXISTS `notes` (
                        `uid` TEXT NOT NULL,
                        `title` TEXT NOT NULL,
                        `body` TEXT NOT NULL,
                        `tags` TEXT NOT NULL,
                        `lastUpdated` TEXT NOT NULL,
                        `deviceId` TEXT NOT NULL,
                        PRIMARY KEY(`uid`)
                    )"""
                )
                database.execSQL(
                    """CREATE TABLE IF NOT EXISTS `vault_items` (
                        `uid` TEXT NOT NULL,
                        `title` TEXT NOT NULL,
                        `username` TEXT NOT NULL,
                        `secretEnc` TEXT NOT NULL,
                        `url` TEXT NOT NULL,
                        `notes` TEXT NOT NULL,
                        `lastUpdated` TEXT NOT NULL,
                        `deviceId` TEXT NOT NULL,
                        PRIMARY KEY(`uid`)
                    )"""
                )
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
                    .addMigrations(MIGRATION_4_5)
                    // No destructive fallback: future schema changes must define a migration.
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
