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
    version = 6,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun lessonDao(): LessonDao
    abstract fun scenarioDao(): ScenarioDao
    abstract fun studyDao(): StudyDao
    abstract fun workspaceDao(): WorkspaceDao

    companion object {
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
                    .addMigrations(MIGRATION_5_6)
                    .fallbackToDestructiveMigrationOnDowngrade()
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
