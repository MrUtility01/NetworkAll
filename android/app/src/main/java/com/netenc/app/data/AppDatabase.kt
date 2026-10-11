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
    version = 7,
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
                db.execSQL("ALTER TABLE tasks ADD COLUMN recurrence TEXT NOT NULL DEFAULT 'none'")
            }
        }

        private val MIGRATION_6_7 = object : Migration(6, 7) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE tasks ADD COLUMN lastNotifiedAt TEXT NOT NULL DEFAULT ''")
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
                    .addMigrations(MIGRATION_5_6, MIGRATION_6_7)
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
